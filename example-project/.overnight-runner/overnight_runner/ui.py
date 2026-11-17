"""分屏面板：左边任务队列，右边 coding agent 输出。

零第三方依赖 —— 用 ANSI 转义序列直接画（见 term.py）。
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

from .config import QueuePaths, RunnerConfig
from .controller import RunnerController
from .keys import (
    BACKSPACE,
    CTRL_C,
    DECISION_HELP,
    DOWN,
    ENTER,
    ESC,
    KEYBOARD_HELP,
    UP,
)
from .queue import BLOCKED, FAILED, PENDING, RETRYING, RUNNING, SUCCESS, STOPPED, Queue, Task
from .term import Style, Term, dwidth, pad, truncate, wrap

STATUS_STYLE = {
    PENDING: Style.DIM,
    RUNNING: Style.BRIGHT_CYAN,
    RETRYING: Style.BRIGHT_YELLOW,
    SUCCESS: Style.BRIGHT_GREEN,
    FAILED: Style.BRIGHT_RED,
    BLOCKED: Style.BRIGHT_MAGENTA,
    STOPPED: Style.GREY,
}

STATUS_LABEL = {
    PENDING: "待跑",
    RUNNING: "运行中",
    RETRYING: "待重试",
    SUCCESS: "成功",
    FAILED: "失败",
    BLOCKED: "阻塞",
    STOPPED: "已停",
}

LEFT_WIDTH = 46
FOOTER_HEIGHT = 3


class RunnerUI:
    """overnight-runner 的分屏界面。"""

    def __init__(
        self,
        controller: RunnerController,
        queue: Queue,
        runner_cfg: RunnerConfig,
        project_root: Path,
        paths: QueuePaths | None = None,
    ) -> None:
        self.controller = controller
        self.queue = queue
        self.cfg = runner_cfg
        self.project_root = project_root
        self.paths = paths

        self.term = Term()
        self.selected = 0
        self.detail_task_id: str | None = None
        self.message = ""
        self.message_level = "info"
        self._quit = threading.Event()
        self._input: dict | None = None      # {"prompt": str, "buffer": str}
        self._log_lines: list[str] = []
        self._log_lock = threading.Lock()

        # 决策窗口：人正在回答 agent 的问题
        self._decision_buffer: str | None = None
        self._decision_lock = threading.Lock()

        controller.on_log = self._on_log
        controller.on_event = self._on_event

    # ── 回调 ────────────────────────────────────────────────────────
    def _on_log(self, line: str) -> None:
        with self._log_lock:
            self._log_lines.append(line)
            if len(self._log_lines) > 4000:
                self._log_lines = self._log_lines[-2000:]

    def _on_event(self, kind: str, task: Task | None) -> None:
        labels = {
            "task_started": f"▶ 开始 {task.id if task else ''}",
            "task_succeeded": f"✔ 成功 {task.id if task else ''}",
            "task_failed": f"✘ 失败 {task.id if task else ''}",
            "task_timeout": f"⏱ 超时 {task.id if task else ''}",
            "task_retrying": f"↻ 重试 {task.id if task else ''}",
            "task_blocked": f"⛔ 阻塞 {task.id if task else ''}",
            "task_done": f"— 结束 {task.id if task else ''}",
            "decision": f"◆ 决策已记录 {task.id if task else ''}",
            "retry_wait": f"⏳ 等待重试 {task.id if task else ''}",
            "runner_started": "启动 overnight-runner",
            "runner_stopped": "overnight-runner 已停止",
        }
        text = labels.get(kind)
        if text:
            self._set_message(text, "warn" if kind.endswith(("failed", "timeout", "blocked")) else "info")

    def _set_message(self, text: str, level: str = "info") -> None:
        self.message = text
        self.message_level = level

    # ── 交互 ────────────────────────────────────────────────────────
    def handle_key(self, key: str) -> None:
        # 决策窗口优先级最高 —— 它在阻塞 agent，等不起
        if self.controller.pending_question() is not None:
            self._handle_decision_key(key)
            return

        if self._input is not None:
            self._handle_input_key(key)
            return

        if key == CTRL_C or key == "q":
            self._quit.set()
            self.controller.stop.set()
        elif key == UP:
            self.selected = max(0, self.selected - 1)
        elif key == DOWN:
            self.selected = min(max(0, len(self.queue) - 1), self.selected + 1)
        elif key == "a":
            self._input = {"prompt": "追加 plan 路径：", "buffer": ""}
        elif key == "r":
            self._retry_selected()
        elif key == "p":
            self._toggle_pause()
        elif key == "d":
            self._delete_selected()
        elif key == ENTER:
            task = self._selected_task()
            if task is not None:
                self.detail_task_id = task.id
        elif key == ESC:
            self.detail_task_id = None
        elif key == "c":
            self.controller.clear_log()
            with self._log_lock:
                self._log_lines = []

    def _handle_decision_key(self, key: str) -> None:
        """决策窗口的按键处理。"""
        with self._decision_lock:
            if self._decision_buffer is None:
                self._decision_buffer = ""
            buffer = self._decision_buffer

        if key == CTRL_C:
            self._decision_buffer = None
            self._quit.set()
            self.controller.stop.set()
            return
        if key == ESC:
            self._decision_buffer = None
            self.controller.cancel_decision()
            self._set_message("已放弃回答，按默认决策继续", "warn")
            return
        if key == ENTER:
            answer = buffer.strip()
            self._decision_buffer = None
            if answer:
                self.controller.submit_decision(answer)
            else:
                self.controller.cancel_decision()
            return
        if key == BACKSPACE:
            self._decision_buffer = buffer[:-1]
            return
        if len(key) == 1 and key.isprintable():
            self._decision_buffer = buffer + key

    def _handle_input_key(self, key: str) -> None:
        assert self._input is not None
        if key == ESC:
            self._input = None
            return
        if key == ENTER:
            value = self._input["buffer"].strip()
            self._input = None
            if value:
                self._append_plan(value)
            return
        if key == BACKSPACE:
            self._input["buffer"] = self._input["buffer"][:-1]
            return
        if key == CTRL_C:
            self._input = None
            self._quit.set()
            self.controller.stop.set()
            return
        if len(key) == 1 and key.isprintable():
            self._input["buffer"] += key

    def _append_plan(self, plan: str) -> None:
        from .queue import build_task, save_queue_defs

        if self.paths is None:
            self._set_message("队列路径未设置，无法追加", "error")
            return
        task = build_task(
            self.project_root,
            plan,
            existing_ids={t.id for t in self.queue.tasks},
        )
        try:
            self.queue.add(task)
            save_queue_defs(self.paths, self.queue)
            self._set_message(f"已加入队列: {task.id} → {task.plan}", "ok")
        except ValueError as exc:
            self._set_message(str(exc), "error")

    def _selected_task(self) -> Task | None:
        tasks = self.queue.tasks
        if not tasks:
            return None
        self.selected = min(self.selected, len(tasks) - 1)
        return tasks[self.selected]

    def _running_task(self) -> Task | None:
        """当前正在跑的任务（可能没有）。"""
        for t in self.queue.tasks:
            if t.status == RUNNING:
                return t
        return None

    def _retry_selected(self) -> None:
        task = self._selected_task()
        if task is None:
            return
        task.status = PENDING
        task.attempts = 0
        task.last_error = ""
        task.exit_code = None
        task.finished_at = None
        self._set_message(f"已重置 {task.id}，将重新排队", "ok")

    def _toggle_pause(self) -> None:
        task = self._selected_task()
        if task is None:
            return
        task.enabled = not task.enabled
        self._set_message(f"{task.id} 已{'恢复' if task.enabled else '暂停'}", "ok")

    def _delete_selected(self) -> None:
        task = self._selected_task()
        if task is None:
            return
        if task.status == RUNNING:
            self._set_message("任务正在运行，不能删除", "error")
            return
        self.queue.remove(task.id)
        self.selected = max(0, self.selected - 1)
        self._set_message(f"已移除 {task.id}", "ok")

    # ── 渲染：左边 ──────────────────────────────────────────────────
    def _left_lines(self, width: int) -> list[str]:
        tasks = self.queue.tasks
        stats = self.queue.stats()

        if not tasks:
            body = ["", "队列为空", "", "按 a 追加 plan", ""]
        else:
            body = []
            id_w = max(8, min(18, width - 22))
            for idx, t in enumerate(tasks):
                marker = "▶" if idx == self.selected else " "
                name = truncate(t.id, id_w)
                status = STATUS_LABEL.get(t.status, t.status)
                line = f"{marker} {pad(name, id_w)} {pad(status, 6)} {t.attempts:>2}"
                if idx == self.selected:
                    line = Style.BRIGHT_WHITE + line + Style.RESET
                else:
                    line = f"{marker} {name}{' ' * max(0, id_w - dwidth(name))} " \
                           f"{STATUS_STYLE.get(t.status, '')}{pad(status, 6)}{Style.RESET} {t.attempts:>2}"
                body.append(line)
            body.append("")
            body.append(
                Style.DIM
                + f"待跑 {stats.get(PENDING, 0)} · 运行 {stats.get(RUNNING, 0)} · "
                + f"成功 {stats.get(SUCCESS, 0)} · 失败 {stats.get(FAILED, 0)}"
                + Style.RESET
            )
        return body

    # ── 渲染：决策窗口 ──────────────────────────────────────────────
    def _decision_lines(self, width: int) -> list[str]:
        """正在等人回答时的决策框（没有则空）。"""
        pending = self.controller.pending_question()
        if pending is None:
            self._decision_buffer = None
            return []

        with self._decision_lock:
            if self._decision_buffer is None:
                self._decision_buffer = ""
            buffer = self._decision_buffer

        remaining = pending.get("remaining")
        if remaining is None:
            countdown = "不限时"
        else:
            secs = int(max(0, remaining))
            countdown = f"剩余 {secs // 60}:{secs % 60:02d}"

        box: list[str] = [
            Style.BOLD + Style.BRIGHT_YELLOW + "◆ 待决策" + Style.RESET,
            Style.DIM + f"  任务: {pending.get('task_id', '')}" + Style.RESET,
        ]
        for ln in wrap(str(pending.get("question", "")), max(10, width - 4)):
            box.append("  " + ln)
        box.append("")
        box.append(Style.BOLD + "  你的决策：" + Style.RESET)
        box.append("  > " + Style.BRIGHT_WHITE + buffer + Style.RESET + "▏")
        box.append("")
        box.append(
            Style.DIM
            + f"  {countdown}   Enter 确认 · Esc 用默认决策 · Ctrl-C 退出"
            + Style.RESET
        )
        box.append("")
        return box

    # ── 渲染：右边 ──────────────────────────────────────────────────
    def _right_lines(self, width: int) -> list[str]:
        if self._input is not None:
            return [
                "",
                self._input["prompt"] + Style.BRIGHT_WHITE + self._input["buffer"] + Style.RESET + "▏",
                "",
                Style.DIM + "Enter 确认 · Esc 取消" + Style.RESET,
            ]

        detail = self.queue.get(self.detail_task_id) if self.detail_task_id else None

        lines: list[str] = self._decision_lines(width)
        if detail is not None:
            log_file = self.project_root / detail.log_path if detail.log_path else None
            if log_file and log_file.exists():
                raw = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
            else:
                raw = [f"（{detail.id} 还没有日志）"]
        else:
            with self._log_lock:
                raw = list(self._log_lines)
        raw = raw[-self.cfg.log_tail:]

        if self.message:
            style = {"error": Style.BRIGHT_RED, "warn": Style.BRIGHT_YELLOW, "ok": Style.BRIGHT_GREEN}.get(
                self.message_level, ""
            )
            lines.append(style + self.message + Style.RESET)
            lines.append("")

        for ln in raw:
            lines.extend(wrap(ln, width))

        decisions = self.controller.decision_log.records[-6:]
        if decisions:
            lines.append("")
            lines.append(Style.BOLD + Style.DIM + "最近决策" + Style.RESET)
            # 问题占 40%，答案占剩下的
            q_w = max(8, (width - 3) * 2 // 5)
            a_w = max(8, width - q_w - 3)
            for d in decisions:
                q = truncate(str(d.get("question", "")), q_w)
                a = truncate(str(d.get("answer", "")), a_w)
                lines.append(f"{Style.DIM}{q}{Style.RESET} → {a}")

        if not lines:
            lines = [Style.DIM + "等待任务开始…" + Style.RESET]
        return lines

    # ── 渲染：整体 ──────────────────────────────────────────────────
    def render(self) -> None:
        term = self.term
        cols, rows = term.size()
        left_w = min(LEFT_WIDTH, max(30, cols // 3))
        right_x = left_w + 1
        right_w = cols - left_w - 1
        body_h = max(3, rows - FOOTER_HEIGHT)

        term.clear()

        # 左：任务队列
        title = f"任务队列 ({len(self.queue)})"
        term.draw_box(
            x=1,
            y=1,
            w=left_w,
            h=body_h,
            title=title,
            lines=self._left_lines(left_w - 4),
            border=Style.CYAN,
            title_style=Style.BOLD + Style.CYAN,
        )

        # 右：agent 输出
        # 标题用 **正在跑** 的任务，而不是选中行 —— 否则按 ↓ 切行后标题和内容对不上
        running = self._running_task()
        if self._input is not None:
            right_title = "追加任务"
        elif self.detail_task_id:
            right_title = f"任务日志 · {self.detail_task_id}"
        elif running is not None:
            right_title = f"Coding Agent · {running.id}"
        else:
            right_title = "Coding Agent"

        term.draw_box(
            x=right_x,
            y=1,
            w=right_w,
            h=body_h,
            title=right_title,
            lines=self._right_lines(right_w - 4),
            border=Style.CYAN,
            title_style=Style.BOLD + Style.CYAN,
        )

        # 底：快捷键
        if self.controller.pending_question() is not None:
            hint = truncate(DECISION_HELP, cols - 4)
        else:
            hint = truncate(KEYBOARD_HELP, cols - 4)
        term.draw_box(
            x=1,
            y=body_h + 1,
            w=cols - 1,
            h=FOOTER_HEIGHT,
            lines=[Style.DIM + hint + Style.RESET],
            border=Style.GREY,
        )
        term.flush()

    # ── 主循环 ──────────────────────────────────────────────────────
    def run(self) -> None:
        from .keys import KeyReader

        reader = KeyReader(self.handle_key)
        self.term.enter()
        reader.start()
        try:
            while not self._quit.is_set():
                self.render()
                time.sleep(1.0 / max(1, self.cfg.refresh_hz))
        finally:
            reader.stop()
            self.term.leave()
            print(self.controller.snapshot())
