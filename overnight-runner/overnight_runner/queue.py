"""任务队列：加载 / 追加 / 状态跟踪。

队列定义在 `.overnight-runner/queue/<name>/queue.yaml`（可提交进仓库），
运行时状态放在同目录的 `state.json`（不提交）。

每条队列一个独立目录 —— 多人可以在同一个项目里各跑各的队列，互不干扰。
"""

from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from . import yaml_lite as yaml
from .config import QueuePaths
from .util import atomic_write, now, now_iso, slugify, today_stamp

# 任务状态
PENDING = "pending"
RUNNING = "running"
RETRYING = "retrying"
SUCCESS = "success"
FAILED = "failed"
STOPPED = "stopped"
BLOCKED = "blocked"

STATUSES = (PENDING, RUNNING, RETRYING, SUCCESS, FAILED, STOPPED, BLOCKED)

# plan 文件名常带日期前缀（YYYYMMDD-xxx / YYYY-MM-DD-xxx），别再拼一遍
DATE_PREFIX_RE = re.compile(r"^\d{4}-?\d{2}-?\d{2}[-_]")



@dataclass
class Task:
    id: str
    plan: str
    prompt: str = ""
    priority: int = 100
    enabled: bool = True
    role: str = ""          # BA / DEV / QA —— 只是标签，用于分组显示
    depends_on: list[str] = field(default_factory=list)

    # 运行时状态
    status: str = PENDING
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None
    last_error: str = ""
    summary: str = ""
    log_path: str = ""

    @property
    def plan_path(self) -> Path:
        return Path(self.plan)

    @property
    def duration_sec(self) -> float | None:
        if self.started_at is None:
            return None
        end = self.finished_at or now()
        # 状态文件是手改过的，可能写了不带时区的时间 —— 别让渲染循环炸掉
        if end.tzinfo is None and self.started_at.tzinfo is not None:
            end = end.replace(tzinfo=self.started_at.tzinfo)
        elif end.tzinfo is not None and self.started_at.tzinfo is None:
            self.started_at = self.started_at.replace(tzinfo=end.tzinfo)
        return (end - self.started_at).total_seconds()

    def to_def(self) -> dict:
        """写回 YAML 的定义部分。"""
        data: dict[str, Any] = {"id": self.id, "plan": self.plan}
        if self.prompt:
            data["prompt"] = self.prompt
        if self.priority != 100:
            data["priority"] = self.priority
        if self.role:
            data["role"] = self.role
        if self.depends_on:
            data["depends_on"] = self.depends_on
        if not self.enabled:
            data["enabled"] = False
        return data

    def to_state(self) -> dict:
        return {
            "id": self.id,
            "plan": self.plan,
            "status": self.status,
            "attempts": self.attempts,
            "started_at": self.started_at.isoformat(timespec="seconds") if self.started_at else None,
            "finished_at": self.finished_at.isoformat(timespec="seconds") if self.finished_at else None,
            "exit_code": self.exit_code,
            "last_error": self.last_error,
            "summary": self.summary,
            "log_path": self.log_path,
        }


class Queue:
    """线程安全的任务队列。"""

    def __init__(self, tasks: list[Task] | None = None) -> None:
        self._tasks: list[Task] = tasks or []
        self._lock = threading.RLock()

    # ── 基本访问 ────────────────────────────────────────────────────
    @property
    def tasks(self) -> list[Task]:
        with self._lock:
            return list(self._tasks)

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            for t in self._tasks:
                if t.id == task_id:
                    return t
            return None

    def __len__(self) -> int:
        with self._lock:
            return len(self._tasks)

    # ── 变更 ────────────────────────────────────────────────────────
    def add(self, task: Task) -> Task:
        with self._lock:
            if self.get(task.id) is not None:
                raise ValueError(f"任务 id 已存在: {task.id}")
            self._tasks.append(task)
            self._tasks.sort(key=lambda t: (t.priority, t.id))
            return task

    def remove(self, task_id: str) -> bool:
        with self._lock:
            before = len(self._tasks)
            self._tasks = [t for t in self._tasks if t.id != task_id]
            return len(self._tasks) != before

    def update(self, task_id: str, **fields) -> Task | None:
        with self._lock:
            task = self.get(task_id)
            if task is None:
                return None
            for key, value in fields.items():
                setattr(task, key, value)
            return task

    # ── 调度 ────────────────────────────────────────────────────────
    def next_ready(self) -> Task | None:
        """下一个可以跑的任务：enabled + pending + 依赖已完成 + 优先级最高。"""
        with self._lock:
            done = {t.id for t in self._tasks if t.status == SUCCESS}
            candidates = [
                t
                for t in self._tasks
                if t.enabled and t.status == PENDING and all(d in done for d in t.depends_on)
            ]
            if not candidates:
                return None
            candidates.sort(key=lambda t: (t.priority, t.id))
            return candidates[0]

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for t in self._tasks if t.status in (PENDING, RUNNING, RETRYING))

    def has_unfinished(self) -> bool:
        with self._lock:
            return any(t.status in (PENDING, RUNNING, RETRYING) for t in self._tasks)

    def stats(self) -> dict[str, int]:
        with self._lock:
            out = {s: 0 for s in STATUSES}
            for t in self._tasks:
                out[t.status] = out.get(t.status, 0) + 1
            return out


def build_task(
    project_root: Path,
    plan: str,
    prompt: str = "",
    role: str = "",
    priority: int = 100,
    task_id: str | None = None,
    existing_ids: set[str] | None = None,
) -> Task:
    """由 plan 路径构造任务；plan 相对项目根目录。

    id 默认取 plan 文件名（去掉日期前缀）—— 同一个 plan 可以在同一天被排多次，
    冲突时自动加 `-2` / `-3` 序号。
    """
    plan_rel = _normalize_rel(project_root, plan)
    if task_id is None:
        # plan 文件名通常已经带日期前缀（20261106-xxx），别再拼一遍变成双日期
        stem = DATE_PREFIX_RE.sub("", Path(plan_rel).stem)
        base = slugify(stem, fallback="task")
        task_id = f"{today_stamp()}-{base}"
        taken = existing_ids or set()
        if task_id in taken:
            n = 2
            while f"{task_id}-{n}" in taken:
                n += 1
            task_id = f"{task_id}-{n}"
    return Task(
        id=task_id,
        plan=plan_rel,
        prompt=prompt,
        role=role,
        priority=priority,
    )


def _normalize_rel(project_root: Path, plan: str) -> str:
    """把 plan 路径规范成相对项目根的 POSIX 风格路径。"""
    p = Path(plan)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(project_root.resolve())
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def task_from_def(defs: dict, index: int = 0) -> Task:
    plan = defs.get("plan") or ""
    task_id = defs.get("id") or f"task-{index + 1}"
    return Task(
        id=str(task_id),
        plan=plan,
        prompt=defs.get("prompt") or "",
        priority=int(defs.get("priority", 100)),
        enabled=bool(defs.get("enabled", True)),
        role=defs.get("role") or "",
        depends_on=list(defs.get("depends_on") or []),
    )


def load_queue(paths: QueuePaths, queue_defs: list[dict]) -> Queue:
    """把 YAML 定义与运行时状态合并成队列。"""
    tasks = [task_from_def(d, i) for i, d in enumerate(queue_defs)]
    queue = Queue(tasks)

    for st in _read_states(paths):
        task = queue.get(st.get("id", ""))
        if task is None:
            # 兼容老 id（如 20261106-20261106-xxx）—— 退化成按 plan 路径匹配
            task = next(
                (t for t in queue.tasks if t.plan == st.get("plan", "")), None
            )
            if task is None:
                continue
        task.status = st.get("status", PENDING)
        task.attempts = int(st.get("attempts", 0))
        task.exit_code = st.get("exit_code")
        task.last_error = st.get("last_error", "")
        task.summary = st.get("summary", "")
        task.log_path = st.get("log_path", "")
        started = st.get("started_at")
        finished = st.get("finished_at")
        task.started_at = datetime.fromisoformat(started) if started else None
        task.finished_at = datetime.fromisoformat(finished) if finished else None
    return queue


def _read_states(paths: QueuePaths) -> list[dict]:
    """读运行时状态。

    `state.json` 缺失或损坏时回落到 `state.json.bak` —— 避免误删状态文件
    就把已经跑完的任务全部重新排队。
    """
    for path in (paths.state, paths.state.with_name(paths.state.name + ".bak")):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict):
            return list(data.get("tasks") or [])
    return []


def save_state(paths: QueuePaths, queue: Queue) -> Path:
    """写运行时状态（同时留一份 .bak 兜底）。"""
    payload = {
        "updated_at": now_iso(),
        "tasks": [t.to_state() for t in queue.tasks],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    atomic_write(paths.state, text)
    try:
        atomic_write(paths.state.with_name(paths.state.name + ".bak"), text)
    except OSError:
        pass
    return paths.state


def load_queue_defs(paths: QueuePaths) -> list[dict]:
    """读队列定义（`.overnight-runner/queue/<name>/queue.yaml`）。"""
    if not paths.config.exists():
        return []
    try:
        data = yaml.loads(paths.config.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return []
    return list(data.get("queue") or [])


def save_queue_defs(paths: QueuePaths, queue: Queue) -> Path:
    """把队列定义写回 `queue.yaml`（追加 plan 用）。"""
    paths.dir.mkdir(parents=True, exist_ok=True)
    payload = {"queue": [t.to_def() for t in queue.tasks]}
    atomic_write(paths.config, yaml.dumps(payload))
    return paths.config
