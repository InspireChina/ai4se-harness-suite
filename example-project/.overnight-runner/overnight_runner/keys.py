"""跨平台按键读取：POSIX 用 termios，Windows 用 msvcrt。

只依赖标准库，不需要 prompt_toolkit 之类的重依赖。
"""

from __future__ import annotations

import os
import sys
import threading
from typing import Callable

from .util import is_windows

# 规范化按键名
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
ENTER = "enter"
ESC = "esc"
BACKSPACE = "backspace"
TAB = "tab"
CTRL_C = "ctrl-c"
NONE = ""

KEYBOARD_HELP = (
    "↑↓ 选择   a 追加 plan   r 重试   p 暂停/恢复   d 移除   "
    "Enter 查看日志   Esc 返回   c 清屏   q 退出"
)

DECISION_HELP = (
    "待决策时: Enter 提交答案 · Esc 用默认决策 · Ctrl-C 退出"
)

_WIN_SPECIAL = {
    "H": UP,
    "P": DOWN,
    "K": LEFT,
    "M": RIGHT,
    "G": ENTER,
    "S": LEFT,
    "R": RIGHT,
    "\x0d": ENTER,
    "\x1b": ESC,
    "\x08": BACKSPACE,
    "\x09": TAB,
}

# 按下 ESC 后等这么久还等不到后续字节，就认为用户是单独按了 ESC
ESC_TIMEOUT = 0.05
# 轮询间隔（秒）：让读线程能及时响应 stop()
POLL_INTERVAL = 0.2


class RawMode:
    """进入原始模式（按键立即返回，不回显），退出时恢复。"""

    def __init__(self) -> None:
        self._fd = None
        self._old = None
        self._active = False

    def __enter__(self) -> "RawMode":
        if is_windows():
            self._active = True
            return self
        try:
            import termios
            import tty

            self._fd = sys.stdin.fileno()
            self._old = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)
            self._active = True
        except Exception:  # noqa: BLE001 - 没有 tty 时降级为行模式
            self._active = False
        return self

    def __exit__(self, *exc) -> None:
        if not self._active or self._fd is None or self._old is None:
            return
        try:
            import termios

            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)
        except Exception:  # noqa: BLE001
            pass


def _utf8_seq_len(lead: int) -> int:
    """按 UTF-8 首字节判断这个字符总共占几个字节。

    汉字 3 字节、emoji 4 字节。读键盘必须 **按字节凑齐再解**，
    否则一个汉字会被拆成 3 次读、每次都解码失败 → 中文全变问号。
    """
    if lead < 0x80:
        return 1
    if lead >= 0xF0:
        return 4
    if lead >= 0xE0:
        return 3
    if lead >= 0xC0:
        return 2
    return 1  # 非法首字节（续字节开头）—— 当 1 字节处理，别死循环


def _normalize_key(ch: str) -> str:
    """把一个字符归一成按键名（控制键给名字，其余原样返回）。"""
    if ch in ("\r", "\n"):
        return ENTER
    if ch in ("\x7f", "\x08"):
        return BACKSPACE
    if ch == "\x03":
        return CTRL_C
    if ch == "\t":
        return TAB
    return ch


_CSI_KEYS = {
    "[A": UP,
    "[B": DOWN,
    "[C": RIGHT,
    "[D": LEFT,
    "[H": UP,
    "[F": DOWN,
}


class PosixKeyReader:
    """POSIX 下的按键读取：懂 UTF-8 多字节字符，也懂 ESC 序列。

    为什么不用"一次 os.read(fd, 1)"：那样会把一个汉字的 3 个字节
    拆成 3 次读，每次 `decode(errors="replace")` 都失败 → 中文全变问号
    （实测：决策窗口里输入"先修 Bug"，落盘变成"??? Bug"）。

    做法：字节先进缓冲区，按 UTF-8 首字节凑齐长度再整体解码。
    """

    def __init__(self) -> None:
        self._buf = bytearray()
        self._eof = False

    # ── 字节层 ──────────────────────────────────────────────────────
    def _pump(self, fd: int, timeout: float | None) -> bool:
        """把 fd 里的可用字节读进缓冲区。返回是否读到东西。"""
        import select

        try:
            ready, _, _ = select.select([fd], [], [], timeout)
        except (OSError, ValueError):
            return False
        if not ready:
            return False
        try:
            data = os.read(fd, 1024)
        except OSError:
            return False
        if not data:
            self._eof = True
            return False
        self._buf.extend(data)
        return True

    def _take_char(self) -> str | None:
        """从缓冲区头部取一个完整字符；字节还不够返回 None。"""
        if not self._buf:
            return None
        need = _utf8_seq_len(self._buf[0])
        if len(self._buf) < need:
            return None
        raw = bytes(self._buf[:need])
        del self._buf[:need]
        return raw.decode("utf-8", errors="replace")

    def _find_csi_final(self) -> int | None:
        """在缓冲区里找 CSI 序列的结束字节下标。

        缓冲区形如 b"[A" / b"[1;5C"（下标 0 是 '['）。
        返回 None 表示"还没收全"；返回 -1 表示"非法序列"。
        """
        for i in range(1, len(self._buf)):
            b = self._buf[i]
            if 0x40 <= b <= 0x7E:
                return i
            if not (0x20 <= b <= 0x3F):
                return -1
        return None

    # ── ESC 序列 ────────────────────────────────────────────────────
    def _read_escape(self, fd: int) -> str:
        """已经读到 ESC，判断它是单独按键还是某个序列的开头。"""
        if not self._buf:
            self._pump(fd, ESC_TIMEOUT)
        if not self._buf or self._buf[0] != 0x5B:  # '['
            return ESC  # 后面的字节留给下一次读
        while True:
            idx = self._find_csi_final()
            if idx is not None and idx >= 0:
                seq = bytes(self._buf[: idx + 1])
                del self._buf[: idx + 1]
                return _CSI_KEYS.get(seq.decode("ascii", errors="replace"), NONE)
            if idx == -1:  # 非法序列，丢掉 ESC[ 别把后面的正文吃掉
                del self._buf[:1]
                return NONE
            if not self._pump(fd, ESC_TIMEOUT):
                del self._buf[:1]
                return NONE

    # ── 对外 ────────────────────────────────────────────────────────
    def read_key(self, fd: int) -> str:
        """读一个按键（控制键给名字，其余返回原字符）。

        返回 NONE 表示"暂时没读到"（超时或输入流结束）。
        """
        while True:
            ch = self._take_char()
            if ch is None:
                if self._eof:
                    return NONE
                self._pump(fd, POLL_INTERVAL)
                continue
            if ch == "\x1b":
                return self._read_escape(fd)
            return _normalize_key(ch)


_POSIX_READER = PosixKeyReader()


def _read_posix_key(fd: int) -> str:
    """读一个按键（POSIX）。保留函数形式，内部共用一个带缓冲的读取器。"""
    return _POSIX_READER.read_key(fd)


def _read_win_key() -> str:
    import msvcrt

    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()
        return _WIN_SPECIAL.get(ch2, NONE)
    if ch in ("\r", "\n"):
        return ENTER
    if ch in ("\x7f", "\x08"):
        return BACKSPACE
    if ch == "\x03":
        return CTRL_C
    if ch == "\t":
        return TAB
    return ch


class KeyReader:
    """后台线程读按键，交给回调。"""

    def __init__(self, on_key: Callable[[str], None]) -> None:
        self.on_key = on_key
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._raw = RawMode()
        self._posix = PosixKeyReader()

    def start(self) -> None:
        self._raw.__enter__()
        self._thread = threading.Thread(target=self._loop, name="key-reader", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._raw.__exit__()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                if is_windows():
                    key = _read_win_key()
                else:
                    fd = sys.stdin.fileno()
                    key = self._posix.read_key(fd)
            except Exception:  # noqa: BLE001
                break
            if key == NONE:
                continue
            try:
                self.on_key(key)
            except Exception:  # noqa: BLE001
                pass
            if key == CTRL_C:
                break


def read_line(prompt: str = "") -> str:
    """行模式读一行（用于非 TUI 场景）。"""
    if prompt:
        print(prompt, end="", flush=True)
    try:
        return sys.stdin.readline().strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def confirm(prompt: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    ans = read_line(f"{prompt} {suffix} ").lower()
    if not ans:
        return default
    return ans in ("y", "yes")


__all__ = [
    "BACKSPACE",
    "CTRL_C",
    "DOWN",
    "ENTER",
    "ESC",
    "KEYBOARD_HELP",
    "KeyReader",
    "LEFT",
    "NONE",
    "PosixKeyReader",
    "RawMode",
    "RIGHT",
    "TAB",
    "UP",
    "confirm",
    "read_line",
]
