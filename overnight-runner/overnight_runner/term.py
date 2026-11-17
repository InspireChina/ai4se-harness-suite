"""纯 ANSI 终端绘制 —— 零第三方依赖。

只依赖标准库。用 ANSI 转义序列直接画：

- 备用屏幕（全屏面板）
- 光标定位 / 隐藏
- 颜色（SGR）
- 边框（圆角 / 直角）
- 中日韩宽字符的显示宽度计算

没有 TTY 时（管道 / CI）会自动降级：不做任何转义，只输出纯文本。
"""

from __future__ import annotations

import os
import shutil
import sys
import unicodedata
from typing import Iterable

# ── 转义序列 ────────────────────────────────────────────────────────
ESC = "\x1b"
CSI = ESC + "["

ALT_SCREEN_ON = CSI + "?1049h"
ALT_SCREEN_OFF = CSI + "?1049l"
CURSOR_HIDE = CSI + "?25l"
CURSOR_SHOW = CSI + "?25h"
CLEAR = CSI + "2J"
CURSOR_HOME = CSI + "H"
RESET = CSI + "0m"


def _sgr(*codes: int | str) -> str:
    return CSI + ";".join(str(c) for c in codes) + "m"


class Style:
    """语义色。"""

    RESET = _sgr(0)
    BOLD = _sgr(1)
    DIM = _sgr(2)
    ITALIC = _sgr(3)
    REVERSE = _sgr(7)

    BLACK = _sgr(30)
    RED = _sgr(31)
    GREEN = _sgr(32)
    YELLOW = _sgr(33)
    BLUE = _sgr(34)
    MAGENTA = _sgr(35)
    CYAN = _sgr(36)
    WHITE = _sgr(37)
    GREY = _sgr(90)

    BRIGHT_RED = _sgr(91)
    BRIGHT_GREEN = _sgr(92)
    BRIGHT_YELLOW = _sgr(93)
    BRIGHT_BLUE = _sgr(94)
    BRIGHT_MAGENTA = _sgr(95)
    BRIGHT_CYAN = _sgr(96)
    BRIGHT_WHITE = _sgr(97)


# ── 显示宽度 ────────────────────────────────────────────────────────
import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def char_width(ch: str) -> int:
    """字符的显示宽度（0 / 1 / 2）。"""
    if ch == "\t":
        return 4
    if unicodedata.combining(ch):
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def _tokens(text: str) -> list[tuple[str, int]]:
    """把文本切成 (片段, 显示宽度) 序列。

    ANSI 转义序列宽度算 0 —— 否则带颜色的文本会被算宽。
    """
    out: list[tuple[str, int]] = []
    i = 0
    while i < len(text):
        if text[i] == "\x1b":
            m = _ANSI_RE.match(text, i)
            if m:
                out.append((m.group(0), 0))
                i = m.end()
                continue
        out.append((text[i], char_width(text[i])))
        i += 1
    return out


def dwidth(text: str) -> int:
    """字符串的显示宽度（忽略 ANSI 转义序列）。"""
    return sum(w for _, w in _tokens(text))


def truncate(text: str, width: int, ellipsis: str = "…") -> str:
    """按显示宽度截断（不切断 ANSI 序列）。"""
    if width <= 0:
        return ""
    if dwidth(text) <= width:
        return text
    limit = width - dwidth(ellipsis)
    out: list[str] = []
    used = 0
    for tok, w in _tokens(text):
        if used + w > limit:
            break
        out.append(tok)
        used += w
    return "".join(out) + ellipsis + Style.RESET


def pad(text: str, width: int, align: str = "left") -> str:
    """按显示宽度补齐（忽略 ANSI 转义序列）。"""
    w = dwidth(text)
    if w >= width:
        return text
    space = " " * (width - w)
    if align == "right":
        return space + text
    if align == "center":
        left = (width - w) // 2
        return " " * left + text + " " * (width - w - left)
    return text + space


def wrap(text: str, width: int) -> list[str]:
    """按显示宽度折行（不打断宽字符，不切断 ANSI 序列）。"""
    if width <= 0:
        return [""]
    lines: list[str] = []
    for raw in text.split("\n"):
        if dwidth(raw) <= width:
            lines.append(raw)
            continue
        cur: list[str] = []
        used = 0
        for tok, w in _tokens(raw):
            if used + w > width and cur:
                lines.append("".join(cur))
                cur = []
                used = 0
            cur.append(tok)
            used += w
        lines.append("".join(cur))
    return lines or [""]


# ── 边框字符 ────────────────────────────────────────────────────────
class Box:
    ROUND = "┌┐└┘─│├┤┬┴┼"
    SQUARE = "┌┐└┘─│├┤┬┴┼"
    ASCII = "+-++|+++++"


class Term:
    """终端绘制器。"""

    def __init__(self, stream=None) -> None:
        self.out = stream or sys.stdout
        self.tty = bool(getattr(self.out, "isatty", lambda: False)())
        self._alt = False

    # ── 尺寸 ────────────────────────────────────────────────────────
    def size(self) -> tuple[int, int]:
        try:
            size = shutil.get_terminal_size(fallback=(120, 40))
            return max(40, size.columns), max(10, size.lines)
        except OSError:
            return 120, 40

    # ── 基础输出 ────────────────────────────────────────────────────
    def write(self, text: str) -> None:
        try:
            self.out.write(text)
        except (OSError, ValueError):
            pass

    def flush(self) -> None:
        try:
            self.out.flush()
        except (OSError, ValueError):
            pass

    def enter(self) -> None:
        """进备用屏幕 + 隐藏光标。"""
        if not self.tty:
            return
        self.write(ALT_SCREEN_ON + CURSOR_HIDE + CLEAR + CURSOR_HOME)
        self._alt = True
        self.flush()

    def leave(self) -> None:
        """退出备用屏幕 + 恢复光标。"""
        if not self.tty:
            self.flush()
            return
        self.write(CURSOR_SHOW + ALT_SCREEN_OFF)
        self._alt = False
        self.flush()

    def clear(self) -> None:
        if self.tty:
            self.write(CLEAR + CURSOR_HOME)

    def move(self, row: int, col: int) -> None:
        """移动光标（1-based）。"""
        if self.tty:
            self.write(f"{CSI}{row};{col}H")

    def style(self, code: str, text: str) -> str:
        if not self.tty or not code:
            return text
        return f"{code}{text}{Style.RESET}"

    # ── 画框 ────────────────────────────────────────────────────────
    def draw_box(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str = "",
        lines: Iterable[str] = (),
        border: str = Style.CYAN,
        title_style: str = Style.BOLD,
        footer: str = "",
    ) -> None:
        """在 (x, y) 处画一个 w×h 的框，内容放 lines。"""
        if w < 4 or h < 3:
            return
        b = Box.ROUND
        tl, tr, bl, br, hz, vt = b[0], b[1], b[2], b[3], b[4], b[5]

        # 上边框（带标题）
        self.move(y, x)
        if title:
            label = " " + truncate(title, max(0, w - 6)) + " "
            self.write(self.style(border, tl))
            self.write(self.style(title_style, label))
            self.write(self.style(border, hz * max(0, w - 2 - dwidth(label)) + tr))
        else:
            self.write(self.style(border, tl + hz * (w - 2) + tr))

        # 内容
        body = list(lines)
        for i in range(h - 2):
            content = body[i] if i < len(body) else ""
            self.move(y + 1 + i, x)
            self.write(self.style(border, vt))
            self.write(pad(truncate(content, w - 2), w - 2))
            self.write(self.style(border, vt))

        # 下边框（带 footer）
        self.move(y + h - 1, x)
        if footer:
            label = " " + truncate(footer, max(0, w - 6)) + " "
            self.write(self.style(border, bl))
            self.write(self.style(Style.DIM, label))
            self.write(self.style(border, hz * max(0, w - 2 - dwidth(label)) + br))
        else:
            self.write(self.style(border, bl + hz * (w - 2) + br))

    def draw_line(self, x: int, y: int, text: str, style: str = "") -> None:
        """在 (x, y) 处写一行（1-based 坐标）。"""
        self.move(y, x)
        self.write(self.style(style, text))
