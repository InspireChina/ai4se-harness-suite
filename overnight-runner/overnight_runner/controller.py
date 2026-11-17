"""调度器：取任务 → 跑 agent → 看门狗 → 决策 → 失败重试 → 落状态。

决策有两条路：

- **unattended（无人值守）**：agent 抛 `QUESTION:` 时当场按规则/兜底策略决策，
  **不打断** agent；决策会在下一次拉起 agent 时注入 prompt。
- **attended（有人值守）**：打断 agent，TUI 弹决策窗口问人；人答了就用
  `opencode run --session <sid>` 续跑；超时没人答就按规则/兜底策略兜底。
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .agent import AgentProcess, check_agent_available
from .config import ProjectConfig, QueuePaths, RunnerConfig
from .decisions import (
    SOURCE_AGENT,
    SOURCE_FALLBACK,
    SOURCE_HUMAN,
    SOURCE_RULE,
    SOURCE_TIMEOUT,
    DecisionEvent,
    DecisionLog,
    parse_agent_line,
    resolve_answer,
    should_ask,
)
from .prompts import build_prompt, build_resume_prompt
from .queue import (
    BLOCKED,
    FAILED,
    PENDING,
    RETRYING,
    RUNNING,
    STOPPED,
    SUCCESS,
    Queue,
    Task,
    save_state,
)
from .util import StopFlag, fmt_ts, now, sleep_interruptible

EventCallback = Callable[[str, Task], None]

# 单个任务最多被打断几次（防止 agent 无限提问拖死队列）
MAX_DECISIONS_PER_TASK = 10


@dataclass
class TaskOutcome:
    task_id: str
    status: str
    exit_code: int | None
    attempts: int
    duration_sec: float
    error: str = ""
    summary: str = ""
    decisions: int = 0


@dataclass
class WatchResult:
    """一次 agent 运行的观察结果。"""

    kind: str = "exited"      # exited | timeout | question | stopped
    timeout_kind: str = ""
    question: str = ""
    session_id: str = ""


class RunnerController:
    """把队列里的 plan 一个一个交给 coding agent 跑。"""

    def __init__(
        self,
        project_root: Path,
        runner_cfg: RunnerConfig,
        project_cfg: ProjectConfig,
        queue: Queue,
        paths: QueuePaths,
        stop: StopFlag | None = None,
        on_event: EventCallback | None = None,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self.project_root = project_root
        self.runner_cfg = runner_cfg
        self.project_cfg = project_cfg
        self.queue = queue
        self.paths = paths
        self.stop = stop or StopFlag()
        self.on_event = on_event
        self.on_log = on_log

        self.log_dir = paths.logs
        self.decision_log = DecisionLog(paths.decisions)
        self.decision_log.load()

        self._current: Task | None = None
        self._current_proc: AgentProcess | None = None
        self._current_lines: list[str] = []
        self._lock = threading.Lock()

        # 决策：agent 抛出的问题、等待人回答、已作出的决策
        self._ask_question: tuple[str, str] | None = None
        self._decisions_made: list[tuple[str, str]] = []
        self._decision_lock = threading.Lock()
        self._decision_event = threading.Event()
        self._pending: dict | None = None
        self._answer: str | None = None

    # ── 事件 ────────────────────────────────────────────────────────
    def _emit(self, kind: str, task: Task | None = None) -> None:
        if self.on_event is not None:
            try:
                self.on_event(kind, task or self._current)  # type: ignore[arg-type]
            except Exception:  # noqa: BLE001
                pass

    def _log(self, line: str) -> None:
        with self._lock:
            self._current_lines.append(line)
            if len(self._current_lines) > 2000:
                self._current_lines = self._current_lines[-1000:]
        if self.on_log is not None:
            try:
                self.on_log(line)
            except Exception:  # noqa: BLE001
                pass

    @property
    def current_lines(self) -> list[str]:
        with self._lock:
            return list(self._current_lines)

    def clear_log(self) -> None:
        with self._lock:
            self._current_lines = []

    # ── 决策：等待人回答 ────────────────────────────────────────────
    def pending_question(self) -> dict | None:
        """当前正在等人回答的问题（没有则 None）。UI 渲染决策窗口用。"""
        with self._decision_lock:
            if self._pending is None:
                return None
            pending = dict(self._pending)
        deadline = pending.get("deadline")
        pending["remaining"] = (
            max(0.0, deadline - time.monotonic()) if deadline else None
        )
        return pending

    def submit_decision(self, answer: str) -> None:
        """人在 TUI 里回答了问题。"""
        with self._decision_lock:
            self._answer = answer
        self._decision_event.set()

    def cancel_decision(self) -> None:
        """人按 Esc：不等了，直接用默认决策兜底。"""
        with self._decision_lock:
            self._answer = None
        self._decision_event.set()

    def _wait_for_human(
        self, task: Task, question: str, session_id: str
    ) -> tuple[str | None, float]:
        """等人回答。返回 (答案 or None, 等了多久秒)。"""
        timeout = self.runner_cfg.decision.timeout_sec
        started = time.monotonic()
        deadline = (started + timeout) if timeout else None

        with self._decision_lock:
            self._pending = {
                "task_id": task.id,
                "question": question,
                "session_id": session_id,
                "deadline": deadline,
                "timeout_sec": timeout,
            }
            self._answer = None
            self._decision_event.clear()

        self._emit("question_pending", task)
        answer: str | None = None
        try:
            while True:
                if self._decision_event.wait(timeout=0.2):
                    with self._decision_lock:
                        answer = self._answer
                    break
                if deadline is not None and time.monotonic() >= deadline:
                    answer = None
                    break
                if self.stop.is_set():
                    return None, time.monotonic() - started
        finally:
            with self._decision_lock:
                self._pending = None
            self._decision_event.clear()
        return answer, time.monotonic() - started

    def _resolve_question(
        self, task: Task, question: str, session_id: str
    ) -> tuple[str, str, float, str]:
        """有人值守模式下的决策：问人 → 答 / 超时兜底。"""
        answer, waited = self._wait_for_human(task, question, session_id)

        if answer is None:
            fallback, rule_id = resolve_answer(self.project_cfg, question)
            self.decision_log.record(
                DecisionEvent(
                    task_id=task.id,
                    question=question,
                    answer=fallback,
                    source=SOURCE_TIMEOUT,
                    rule_id=rule_id,
                    waited_sec=waited,
                    session_id=session_id,
                )
            )
            return fallback, SOURCE_TIMEOUT, waited, session_id

        self.decision_log.record(
            DecisionEvent(
                task_id=task.id,
                question=question,
                answer=answer,
                source=SOURCE_HUMAN,
                waited_sec=waited,
                session_id=session_id,
            )
        )
        return answer, SOURCE_HUMAN, waited, session_id

    def _append_decision(self, question: str, answer: str) -> None:
        with self._lock:
            self._decisions_made.append((question, answer))

    @property
    def decisions_made(self) -> list[tuple[str, str]]:
        with self._lock:
            return list(self._decisions_made)

    # ── 主循环 ──────────────────────────────────────────────────────
    def run_forever(self) -> None:
        """一直取任务跑，直到队列跑完或收到停止信号。"""
        self._emit("runner_started")
        while not self.stop.is_set():
            task = self.queue.next_ready()
            if task is None:
                if not self.queue.has_unfinished():
                    break
                # 有任务卡在依赖或重试等待里
                if not self._wait_for_retry():
                    break
                continue
            self.run_task(task)
        self._emit("runner_stopped")
        self._save()

    def _wait_for_retry(self) -> bool:
        """等一个正在重试等待中的任务到期。返回 False 表示应该退出。"""
        for t in self.queue.tasks:
            if t.status == RETRYING:
                wait = max(0.0, t.duration_sec or 0.0)
                if wait <= 0:
                    return True
                self._emit("retry_wait", t)
                sleep_interruptible(min(wait, 5), self.stop)
                return True
        # 没有在重试的任务，但还有未完成 —— 说明被依赖卡住了
        blocked = [t for t in self.queue.tasks if t.status == PENDING and not t.enabled]
        if blocked:
            self._emit("queue_blocked", blocked[0])
            return False
        return False

    # ── 单任务 ──────────────────────────────────────────────────────
    def run_task(self, task: Task) -> TaskOutcome:
        """跑一个任务（含看门狗、决策打断与重试）。"""
        self.clear_log()
        self._current = task
        with self._lock:
            self._decisions_made = []
        task.status = RUNNING
        task.started_at = now()
        task.finished_at = None
        task.exit_code = None
        task.last_error = ""
        task.summary = ""
        self._emit("task_started", task)

        max_attempts = self.runner_cfg.watchdog.max_retries + 1
        outcome = TaskOutcome(task.id, FAILED, None, 0, 0.0)

        for attempt in range(1, max_attempts + 1):
            if self.stop.is_set():
                task.status = STOPPED
                task.finished_at = now()
                break

            task.attempts = attempt
            self._save()

            kind, info = self._run_leg(task)

            if kind == "success":
                task.status = SUCCESS
                task.last_error = ""
                task.finished_at = now()
                self._emit("task_succeeded", task)
                break

            if kind == "timeout":
                task.last_error = (
                    f"{'总时长' if info == 'total' else '空闲'}超时 "
                    f"({info})，已终止 agent"
                )
                self._emit("task_timeout", task)
            elif kind == "stopped":
                task.status = STOPPED
                task.finished_at = now()
            elif kind == "blocked":
                task.status = BLOCKED
                task.finished_at = now()
            else:
                task.last_error = task.last_error or info
                self._emit("task_error", task)

            # 失败：决定是否重试
            task.finished_at = task.finished_at or now()
            if attempt < max_attempts and not self.stop.is_set():
                task.status = RETRYING
                self._emit("task_retrying", task)
                self._save()
                sleep_interruptible(self.runner_cfg.watchdog.backoff_sec, self.stop)
                if self.stop.is_set():
                    break
                task.status = RUNNING
                task.started_at = now()
                continue
            else:
                task.status = FAILED if task.status != BLOCKED else BLOCKED
                self._emit("task_failed", task)

        if task.status != SUCCESS:
            task.status = task.status if task.status != RUNNING else FAILED
            task.finished_at = task.finished_at or now()

        outcome = TaskOutcome(
            task.id,
            task.status,
            task.exit_code,
            task.attempts,
            task.duration_sec or 0.0,
            error=task.last_error,
            summary=task.summary,
            decisions=len(self.decisions_made),
        )
        self._save()
        self._emit("task_done", task)
        self._current = None
        self._current_proc = None
        return outcome

    # ── 一次 agent 运行（含决策打断与续跑）────────────────────────
    def _run_leg(self, task: Task) -> tuple[str, str]:
        """跑一次 agent。返回 (kind, info)。

        kind ∈ success / failed / timeout / stopped / blocked
        """
        session_id = ""
        resume_prompt = ""
        decision_count = 0

        while True:
            prompt, err = build_prompt(
                self.project_root,
                self.project_cfg,
                task.plan,
                task.prompt,
            )
            if err:
                task.last_error = err
                return "failed", err

            made = self.decisions_made
            if made:
                prompt += "\n已经做出的决策（不要重复询问）：\n" + "\n".join(
                    f"- {q} → {a}" for q, a in made
                ) + "\n"

            if resume_prompt:
                prompt = resume_prompt

            prompt_file = self.log_dir / f"{task.id}.prompt.md"
            prompt_file.parent.mkdir(parents=True, exist_ok=True)
            prompt_file.write_text(prompt, encoding="utf-8")

            ok, avail_err = check_agent_available(self.runner_cfg.agent_command)
            if not ok:
                task.last_error = avail_err
                return "failed", avail_err

            command = self._build_command(prompt, session_id)
            log_path = self.log_dir / f"{task.id}.log"
            task.log_path = str(log_path.relative_to(self.project_root))

            proc = AgentProcess(
                command=command,
                cwd=self.project_root / self.runner_cfg.workdir,
                env={**self.runner_cfg.agent_env, **self.project_cfg.agent_env},
                on_line=lambda line: self._on_agent_line(task, line),
                idle_timeout_sec=self.runner_cfg.watchdog.idle_timeout_sec,
                total_timeout_sec=self.runner_cfg.watchdog.total_timeout_sec,
                kill_grace_sec=self.runner_cfg.watchdog.kill_grace_sec,
                output_format=self.runner_cfg.decision.output_format,
                session_pattern=self.runner_cfg.decision.session_pattern,
            )
            self._current_proc = proc

            try:
                proc.start()
            except (OSError, ValueError) as exc:
                task.last_error = f"无法启动 agent: {exc}"
                return "failed", task.last_error

            result = self._watch(proc, task)
            exit_code = proc.wait(timeout=30)
            if exit_code is None:
                proc.terminate()
                exit_code = proc.wait(timeout=10)

            task.exit_code = exit_code
            self._write_log(task, log_path)

            # ── agent 抛了问题 ────────────────────────────────────
            if result.kind == "question":
                decision_count += 1
                if decision_count > MAX_DECISIONS_PER_TASK:
                    task.last_error = (
                        f"决策次数超过上限（{MAX_DECISIONS_PER_TASK} 次），任务中止"
                    )
                    return "failed", task.last_error

                answer, source, waited, sid = self._resolve_question(
                    task, result.question, result.session_id
                )
                self._append_decision(result.question, answer)
                self._log(f"  ↳ 决策[{source}]: {answer}")
                self._emit("decision", task)

                if (
                    self.runner_cfg.decision.resume == "session"
                    and sid
                    and self.runner_cfg.decision.session_args
                ):
                    # 用同一个 session 续跑，agent 的上下文不丢
                    session_id = sid
                    resume_prompt = build_resume_prompt(
                        result.question, answer, task.plan
                    )
                    continue
                # 拿不到 session（或配置成 restart）→ 重跑整个任务，
                # 决策历史会注入新一轮的 prompt
                session_id = ""
                resume_prompt = ""
                continue

            if result.kind == "timeout":
                return "timeout", result.timeout_kind
            if result.kind == "stopped":
                return "stopped", ""
            if task.status == BLOCKED:
                return "blocked", task.last_error
            if exit_code == 0:
                return "success", ""
            return "failed", f"agent 退出码 {exit_code}"

    def _build_command(self, prompt: str, session_id: str) -> list[str]:
        """组装 agent 命令行（含 json 输出格式与 session 续跑参数）。"""
        cfg = self.runner_cfg.decision
        command = [self.runner_cfg.agent_command, *self.runner_cfg.agent_args]
        if cfg.output_format == "json":
            command.extend(cfg.json_args)
        if session_id:
            command.extend(cfg.session_command(session_id))
        command.append(prompt)
        return command

    def _write_log(self, task: Task, log_path: Path) -> None:
        with self._lock:
            log_text = "\n".join(self._current_lines)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(log_text + "\n", encoding="utf-8")
        except OSError:
            pass

    # ── 看门狗 ──────────────────────────────────────────────────────
    def _watch(self, proc: AgentProcess, task: Task) -> WatchResult:
        """盯住 agent：空闲超时 / 总时长超时 / agent 抛问题 → 终止。"""
        while True:
            if self.stop.is_set():
                proc.terminate()
                return WatchResult(kind="stopped")

            asked = self._take_question()
            if asked is not None:
                proc.terminate()
                return WatchResult(
                    kind="question", question=asked[0], session_id=asked[1]
                )

            timed_out, kind = proc.check_timeout()
            if timed_out:
                proc.terminate()
                return WatchResult(kind="timeout", timeout_kind=kind)

            if not proc.alive:
                # agent 可能问完就退出了 —— 再查一次标志，别漏掉
                asked = self._take_question()
                if asked is not None:
                    return WatchResult(
                        kind="question", question=asked[0], session_id=asked[1]
                    )
                return WatchResult(kind="exited")

            time.sleep(0.1)

    # ── agent 输出处理 ──────────────────────────────────────────────
    def _take_question(self) -> tuple[str, str] | None:
        with self._lock:
            asked = self._ask_question
            self._ask_question = None
        return asked

    def _on_agent_line(self, task: Task, line: str) -> None:
        self._log(line)
        kind, value = parse_agent_line(line)
        if kind == "decision":
            question, answer = value  # type: ignore[misc]
            self.decision_log.record(
                DecisionEvent(
                    task_id=task.id,
                    question=question,
                    answer=answer,
                    source=SOURCE_AGENT,
                    session_id=self._session_id(),
                )
            )
            self._append_decision(question, answer)
            self._emit("decision", task)
        elif kind == "question":
            if should_ask(self.runner_cfg.decision.mode):
                # 有人值守：打断 agent，等人来答
                with self._lock:
                    self._ask_question = (value, self._session_id())  # type: ignore[assignment]
                return
            # 无人值守：当场按规则/兜底策略决策，agent 继续跑
            answer, rule_id = resolve_answer(self.project_cfg, value)  # type: ignore[arg-type]
            self.decision_log.record(
                DecisionEvent(
                    task_id=task.id,
                    question=value,  # type: ignore[arg-type]
                    answer=answer,
                    source=SOURCE_RULE if rule_id else SOURCE_FALLBACK,
                    rule_id=rule_id,
                    session_id=self._session_id(),
                )
            )
            self._append_decision(value, answer)  # type: ignore[arg-type]
            self._log(f"  ↳ 默认决策[{rule_id or 'fallback'}]: {answer}")
            self._emit("decision", task)
        elif kind == "done":
            task.summary = value  # type: ignore[assignment]
            self._emit("task_summary", task)
        elif kind == "blocked":
            task.last_error = value  # type: ignore[assignment]
            task.status = BLOCKED
            self._emit("task_blocked", task)

    def _session_id(self) -> str:
        proc = self._current_proc
        return proc.session_id if proc is not None else ""

    # ── 状态持久化 ──────────────────────────────────────────────────
    def _save(self) -> None:
        try:
            save_state(self.paths, self.queue)
        except OSError:
            pass

    def snapshot(self) -> str:
        stats = self.queue.stats()
        return (
            f"{fmt_ts(now())}  总 {len(self.queue)} · "
            f"待跑 {stats.get(PENDING, 0)} · 运行 {stats.get(RUNNING, 0)} · "
            f"成功 {stats.get(SUCCESS, 0)} · 失败 {stats.get(FAILED, 0)}"
        )
