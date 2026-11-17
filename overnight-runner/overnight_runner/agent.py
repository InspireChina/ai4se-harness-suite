"""调用 coding agent 子进程，实时收集输出。"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .util import is_windows

LineCallback = Callable[[str], None]


def extract_session_id(line: str, pattern: str) -> str:
    """用正则从 agent 输出里抓 session id（text 模式的兜底）。"""
    if not pattern:
        return ""
    try:
        m = re.search(pattern, line)
    except re.error:
        return ""
    return m.group(1) if m else ""


def _render_tool(part: dict) -> list[str]:
    """把一次工具调用渲染成几行可读文本。"""
    state = part.get("state") or {}
    inp = state.get("input") or {}
    tool = part.get("tool") or "tool"
    title = state.get("title") or ""
    cmd = inp.get("command") or inp.get("filePath") or inp.get("path") or ""
    output = state.get("output") or ""

    lines: list[str] = []
    head = title or cmd or tool
    lines.append(f"$ {head}")
    if cmd and cmd != head:
        lines.append(f"  {cmd}")
    for ln in str(output).splitlines():
        lines.append(ln)
    return lines


def parse_agent_output(line: str, output_format: str) -> tuple[list[str], str]:
    """把 agent 的一行原始输出解析成 (显示用的行列表, session_id)。

    - `text` 模式：原样返回，session id 交给正则抓
    - `json` 模式：解析事件 —— `part.type=text` 取文本，`part.type=tool` 取工具摘要，
      session id 从事件顶层的 `sessionID` 拿
    """
    if output_format != "json":
        return [line], ""

    s = line.strip()
    if not (s.startswith("{") and s.endswith("}")):
        # 不是 json（agent 的 stderr 混进来了）—— 原样透传
        return [line], ""

    try:
        obj = json.loads(s)
    except json.JSONDecodeError:
        return [line], ""

    if not isinstance(obj, dict):
        return [], ""

    session_id = str(obj.get("sessionID") or "")
    part = obj.get("part") or {}
    ptype = part.get("type")

    if ptype == "text":
        text = str(part.get("text") or "")
        return (text.splitlines() or [""]), session_id
    if ptype == "tool":
        return _render_tool(part), session_id
    return [], session_id



@dataclass
class AgentResult:
    exit_code: int | None = None
    timed_out: bool = False
    timeout_kind: str = ""      # idle | total | ""
    killed: bool = False
    error: str = ""
    duration_sec: float = 0.0


@dataclass
class AgentProcess:
    """一次 agent 调用。"""

    command: list[str]
    cwd: Path
    env: dict[str, str] = field(default_factory=dict)
    on_line: LineCallback | None = None
    idle_timeout_sec: int = 1800
    total_timeout_sec: int = 7200
    kill_grace_sec: int = 15
    output_format: str = "text"
    session_pattern: str = ""

    _proc: subprocess.Popen | None = field(default=None, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _last_output_at: float = field(default_factory=time.monotonic, init=False)
    _started_at: float = field(default_factory=time.monotonic, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _session_id: str = field(default="", init=False)

    # ── 生命周期 ────────────────────────────────────────────────────
    def start(self) -> None:
        env = os.environ.copy()
        env.update(self.env)
        env.setdefault("PYTHONIOENCODING", "utf-8")
        # 让 agent 认得非交互终端
        env.setdefault("CI", "1")

        kwargs: dict = dict(
            cwd=str(self.cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        if is_windows():
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True

        self._started_at = time.monotonic()
        self._last_output_at = self._started_at
        self._proc = subprocess.Popen(self.command, **kwargs)
        self._thread = threading.Thread(target=self._pump, name="agent-reader", daemon=True)
        self._thread.start()

    def _pump(self) -> None:
        proc = self._proc
        if proc is None or proc.stdout is None:
            return
        try:
            for raw in proc.stdout:
                line = raw.rstrip("\n").rstrip("\r")
                with self._lock:
                    self._last_output_at = time.monotonic()
                for out in self._expand(line):
                    if self.on_line is not None:
                        try:
                            self.on_line(out)
                        except Exception:  # noqa: BLE001 - UI 回调不该拖垮 agent
                            pass
        except (ValueError, OSError):
            pass
        finally:
            try:
                proc.stdout.close()
            except (OSError, AttributeError):
                pass

    def _expand(self, line: str) -> list[str]:
        """把一行原始输出展开成若干行可读文本，并顺手抓 session id。"""
        lines, session_id = parse_agent_output(line, self.output_format)
        if session_id:
            self._remember_session(session_id)
        elif self.output_format != "json" and self.session_pattern:
            found = extract_session_id(line, self.session_pattern)
            if found:
                self._remember_session(found)
        return lines

    def _remember_session(self, session_id: str) -> None:
        with self._lock:
            if not self._session_id:
                self._session_id = session_id

    @property
    def session_id(self) -> str:
        """抓到的 agent session id（用于 `--session` 续跑）。"""
        with self._lock:
            return self._session_id

    @property
    def alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    @property
    def idle_seconds(self) -> float:
        with self._lock:
            return time.monotonic() - self._last_output_at

    @property
    def total_seconds(self) -> float:
        return time.monotonic() - self._started_at

    def poll(self) -> int | None:
        return self._proc.poll() if self._proc else None

    def wait(self, timeout: float | None = None) -> int | None:
        if self._proc is None:
            return None
        try:
            return self._proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None

    # ── 超时判定 ────────────────────────────────────────────────────
    def check_timeout(self) -> tuple[bool, str]:
        """返回 (是否超时, 超时类型)。"""
        if self.total_timeout_sec and self.total_seconds > self.total_timeout_sec:
            return True, "total"
        if self.idle_timeout_sec and self.idle_seconds > self.idle_timeout_sec:
            return True, "idle"
        return False, ""

    # ── 终止 ────────────────────────────────────────────────────────
    def terminate(self) -> bool:
        """优雅终止：先 TERM，宽限期后 KILL。返回是否真的杀掉了。"""
        proc = self._proc
        if proc is None or proc.poll() is not None:
            return False

        killed = False
        try:
            if is_windows():
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            killed = True
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.terminate()
                killed = True
            except OSError:
                pass

        try:
            proc.wait(timeout=self.kill_grace_sec)
        except subprocess.TimeoutExpired:
            try:
                if is_windows():
                    proc.kill()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                try:
                    proc.kill()
                except OSError:
                    pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        return killed


def build_command(
    agent_command: str,
    agent_args: list[str],
    prompt: str,
    prompt_file: Path | None = None,
) -> list[str]:
    """组装 agent 命令行。

    提示词优先通过文件传（避免超长命令行在 Windows 上炸掉）；
    只有当 agent 明确支持时才用 stdin。
    """
    cmd = [agent_command, *agent_args]
    if prompt_file is not None:
        cmd += ["--prompt-file", str(prompt_file)]
    else:
        cmd.append(prompt)
    return cmd


def check_agent_available(agent_command: str) -> tuple[bool, str]:
    """检查 agent 命令是否可用。"""
    import shutil

    if shutil.which(agent_command):
        return True, ""
    # 允许写成 "python -m foo" 这种形式，取第一段做 which
    first = agent_command.split()[0] if agent_command.split() else agent_command
    if shutil.which(first):
        return True, ""
    return False, f"找不到 agent 命令: {agent_command}"


def platform_hint() -> str:
    return f"{sys.platform} / {'Windows' if is_windows() else 'POSIX'}"
