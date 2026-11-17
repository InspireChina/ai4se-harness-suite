"""跨平台小工具：时间、时长、原子写、终端宽度。"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def now() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def now_iso() -> str:
    return now().isoformat(timespec="seconds")


def fmt_ts(dt: datetime | None) -> str:
    if dt is None:
        return "-"
    return dt.strftime("%m-%d %H:%M:%S")


def fmt_duration(seconds: float | None) -> str:
    if seconds is None:
        return "-"
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def atomic_write(path: Path, text: str) -> None:
    """同目录临时文件 + rename，避免读到写了一半的内容。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def append_jsonl(path: Path, record: dict) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=False)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(100, 30))
    return size.columns, size.lines


def is_windows() -> bool:
    return os.name == "nt"


def slugify(text: str, fallback: str = "task") -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum() or ch in "-_":
            keep.append(ch)
        elif ch in " /\\":
            keep.append("-")
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:48] or fallback


def today_stamp() -> str:
    return now().strftime("%Y%m%d")


def sleep_interruptible(seconds: float, stop: "StopFlag") -> None:
    """可被 stop 打断的 sleep。"""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if stop.is_set():
            return
        time.sleep(min(0.25, max(0.0, deadline - time.monotonic())))


class StopFlag:
    """线程安全的停止标志。"""

    def __init__(self) -> None:
        import threading

        self._event = threading.Event()

    def set(self) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout)


def pid_alive(pid: int) -> bool:
    """进程还活着吗？

    Windows 上不能用 `os.kill(pid, 0)` —— 那会真的把进程杀掉，
    所以 Windows 走心跳判断（见 QueueLock）。
    """
    if pid <= 0:
        return False
    if is_windows():
        return True  # Windows 上无法安全探测，交给心跳
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


class QueueLock:
    """队列级单实例锁。

    同一个队列同时跑两个 runner 会把同一个 pending 任务跑两遍（白烧 agent），
    所以每条队列目录放一个锁文件。

    锁文件内容：{"pid": 12345, "started_at": "...", "heartbeat": 1793...}
    判定为 stale 的条件：pid 已死（POSIX）或心跳超过 STALE_SEC（Windows / 兜底）。
    """

    STALE_SEC = 120.0

    def __init__(self, path: Path) -> None:
        self.path = path
        self._held = False

    # ── 内部 ────────────────────────────────────────────────────────
    def _read(self) -> dict:
        import json

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _write(self, data: dict) -> None:
        import json

        atomic_write(self.path, json.dumps(data, ensure_ascii=False) + "\n")

    def _is_stale(self, data: dict) -> bool:
        pid = int(data.get("pid") or 0)
        if pid and not pid_alive(pid):
            return True
        if is_windows():
            heartbeat = float(data.get("heartbeat") or 0)
            if heartbeat and (time.time() - heartbeat) > self.STALE_SEC:
                return True
        return False

    # ── 对外 ────────────────────────────────────────────────────────
    def acquire(self) -> tuple[bool, str]:
        """拿锁。返回 (是否成功, 失败原因)。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            data = self._read()
            if not self._is_stale(data):
                pid = int(data.get("pid") or 0)
                return False, f"队列已被 pid {pid} 占用"
            # 残留锁，清掉重建
            try:
                self.path.unlink()
            except OSError:
                pass
        self._write(
            {
                "pid": os.getpid(),
                "started_at": now_iso(),
                "heartbeat": time.time(),
            }
        )
        self._held = True
        return True, ""

    def touch(self) -> None:
        """更新心跳（长跑时定期调）。"""
        if not self._held:
            return
        data = self._read()
        data["heartbeat"] = time.time()
        try:
            self._write(data)
        except OSError:
            pass

    def release(self) -> None:
        if not self._held:
            return
        self._held = False
        try:
            self.path.unlink()
        except OSError:
            pass

    def __enter__(self) -> "QueueLock":
        ok, err = self.acquire()
        if not ok:
            raise RuntimeError(err)
        return self

    def __exit__(self, *exc) -> None:
        self.release()
