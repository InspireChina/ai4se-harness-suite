"""本模块自带的 YAML 子集解析器。

与 overnight-runner 的实现相同，但是一份拷贝：两个模块不许互相 import。
零第三方依赖，Python 3.9+。
"""

from __future__ import annotations

from typing import Any

__all__ = ["loads", "dumps", "YamlError"]


class YamlError(ValueError):
    """YAML 解析失败。消息里带行号，便于定位。"""


# 序列项标记（用不可能出现在正文里的字符，避免与缩进层级混淆）
_SEQ = "\x00seq"


# ── 行处理 ──────────────────────────────────────────────────────────
class _Line:
    __slots__ = ("indent", "text", "lineno", "raw_idx")

    def __init__(self, indent: int, text: str, lineno: int, raw_idx: int) -> None:
        self.indent = indent
        self.text = text
        self.lineno = lineno
        self.raw_idx = raw_idx

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"_Line({self.indent}, {self.text!r}, line={self.lineno})"


def _strip_comment(text: str) -> str:
    """去掉引号外的注释。"""
    out = []
    quote = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "#" and (not out or out[-1] in " \t"):
            break
        out.append(ch)
        i += 1
    return "".join(out).rstrip()


def _split_key(text: str) -> tuple[str, str, str]:
    """拆 ``key: value``。

    返回 (key, sep, value)。sep 为空表示这一行不是映射项。
    引号内的冒号不算分隔符。
    """
    quote = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        if ch in "[{":
            break
        if ch == ":":
            rest = text[i + 1:]
            if rest == "" or rest[0] in " \t":
                return text[:i].strip(), ":", rest.strip()
        i += 1
    return text.strip(), "", ""


def _unterminated(text: str) -> bool:
    """引号没闭合（只关心行尾的引号状态）。"""
    t = text.rstrip()
    if len(t) >= 1 and t[-1] in ("'", '"'):
        # 可能闭合了，也可能是转义过的
        return t.count(t[-1]) % 2 == 1
    if t.startswith("'") or t.startswith('"'):
        return True
    return False


def _fold(parts: list[str]) -> str:
    """多行引号标量的折行规则：单换行折成空格，空行保留为换行。"""
    result = ""
    prev_blank = False
    for i, ln in enumerate(parts):
        if i == 0:
            result = ln
            continue
        if ln.strip() == "":
            result += "\n"
            prev_blank = True
            continue
        if not prev_blank:
            result += " "
        result += ln
        prev_blank = False
    return result


def _preprocess(raw_lines: list[str]) -> list[_Line]:
    """把原始行变成逻辑行。

    做三件事：
    1. 跳过空行、整行注释、``---``
    2. 把 ``- key: value`` 拆成序列标记 + 内容行
    3. 把跨行的引号标量合并成一行
    """
    out: list[_Line] = []
    idx = 0
    total = len(raw_lines)
    while idx < total:
        raw = raw_lines[idx]
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlError(f"第 {idx + 1} 行：YAML 缩进不能用 Tab")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            idx += 1
            continue
        if stripped == "---":
            idx += 1
            continue
        if stripped in ("...",):
            break
        indent = len(raw) - len(raw.lstrip(" "))
        text = _strip_comment(raw[indent:])

        if text == "-" or text.startswith("- "):
            rest = text[1:].strip()
            key, sep, _ = _split_key(rest)
            # 统一拆成：序列标记 + 内容行
            out.append(_Line(indent, _SEQ, idx + 1, idx))
            if rest:
                content_indent = indent + 2 if (sep and key) else indent
                out.append(_Line(content_indent, rest, idx + 1, idx))
            idx += 1
            continue

        # 跨行的引号标量（PyYAML 会把带换行的字符串写成这种形式）
        key, sep, val = _split_key(text)
        if sep and val and _unterminated(val):
            prefix = text[: len(text) - len(val)]
            parts = [val]
            j = idx + 1
            while j < total and _unterminated(_fold(parts)):
                parts.append(raw_lines[j].strip())
                j += 1
            out.append(_Line(indent, prefix + _fold(parts), idx + 1, idx))
            idx = j
            continue

        out.append(_Line(indent, text, idx + 1, idx))
        idx += 1
    return out


# ── 标量 ────────────────────────────────────────────────────────────
_TRUE = {"true", "True", "TRUE"}
_FALSE = {"false", "False", "FALSE"}
_NULL = {"", "~", "null", "Null", "NULL"}


def _parse_scalar(text: str, lineno: int) -> Any:
    t = text.strip()
    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        return _unescape_double(t[1:-1], lineno)
    if len(t) >= 2 and t[0] == "'" and t[-1] == "'":
        return t[1:-1].replace("''", "'")
    if t.startswith("[") and t.endswith("]"):
        return _parse_flow_seq(t[1:-1], lineno)
    if t.startswith("{") and t.endswith("}"):
        return _parse_flow_map(t[1:-1], lineno)
    if t in _TRUE:
        return True
    if t in _FALSE:
        return False
    if t in _NULL:
        return None
    try:
        if t.lstrip("+-").isdigit():
            return int(t)
    except ValueError:
        pass
    try:
        if any(c in t for c in ".eE") and t.lstrip("+-").replace(".", "", 1).isdigit():
            return float(t)
    except ValueError:
        pass
    return t


def _unescape_double(s: str, lineno: int) -> str:
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "0": "\0"}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt == "u" and i + 5 < len(s) + 1:
                try:
                    out.append(chr(int(s[i + 2: i + 6], 16)))
                    i += 6
                    continue
                except ValueError:
                    raise YamlError(f"第 {lineno} 行：非法的 \\u 转义")
            raise YamlError(f"第 {lineno} 行：未知的转义 \\{nxt}")
        out.append(ch)
        i += 1
    return "".join(out)


def _split_flow(body: str, lineno: int) -> list[str]:
    """按顶层逗号切分流式集合的内容。"""
    parts = []
    buf = []
    depth = 0
    quote = ""
    for ch in body:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf)
    if tail.strip() or parts:
        parts.append(tail)
    return [p.strip() for p in parts]


def _parse_flow_seq(body: str, lineno: int) -> list:
    body = body.strip()
    if not body:
        return []
    return [_parse_scalar(p, lineno) for p in _split_flow(body, lineno)]


def _parse_flow_map(body: str, lineno: int) -> dict:
    body = body.strip()
    if not body:
        return {}
    out = {}
    for part in _split_flow(body, lineno):
        key, sep, value = _split_key(part)
        if not sep:
            raise YamlError(f"第 {lineno} 行：流式映射项格式错误: {part!r}")
        out[_parse_scalar(key, lineno)] = _parse_scalar(value, lineno)
    return out


# ── 块标量 ──────────────────────────────────────────────────────────
def _read_block_scalar(
    raw_lines: list[str], start_raw: int, key_indent: int, style: str, lineno: int
) -> tuple[str, int]:
    """读块标量（| 或 >）。返回 (文本, 消耗到的 raw 索引)。"""
    folded = style[0] == ">"
    chomp = "clip"
    if style.endswith("-"):
        chomp = "strip"
    elif style.endswith("+"):
        chomp = "keep"

    body: list[str] = []
    i = start_raw
    block_indent: int | None = None
    while i < len(raw_lines):
        raw = raw_lines[i]
        if raw.strip() == "":
            body.append("")
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= key_indent:
            break
        if block_indent is None:
            block_indent = indent
        body.append(raw[block_indent:] if len(raw) >= block_indent else "")
        i += 1

    # 去掉尾部空行（按 chomp 策略再决定加不加回来）
    while body and body[-1] == "":
        body.pop()
        i -= 1

    if folded:
        text = ""
        for idx, ln in enumerate(body):
            if idx == 0:
                text = ln
            elif ln == "" or body[idx - 1] == "":
                text += "\n" + ln
            else:
                text += " " + ln
    else:
        text = "\n".join(body)

    if chomp == "strip":
        return text, i
    if chomp == "keep":
        return text + "\n", i
    return (text + "\n") if text else "", i


# ── 主解析 ──────────────────────────────────────────────────────────
def loads(text: str) -> Any:
    """解析 YAML 文本。"""
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = _preprocess(raw_lines)
    if not lines:
        return None
    value, idx = _parse_node(lines, 0, lines[0].indent, raw_lines)
    if idx < len(lines):
        raise YamlError(f"第 {lines[idx].lineno} 行：缩进异常")
    return value


def _parse_node(lines: list[_Line], i: int, indent: int, raw_lines: list[str]) -> tuple[Any, int]:
    if lines[i].text == _SEQ:
        return _parse_sequence(lines, i, indent, raw_lines)
    return _parse_mapping(lines, i, indent, raw_lines)


def _parse_mapping(
    lines: list[_Line], i: int, indent: int, raw_lines: list[str]
) -> tuple[dict, int]:
    result: dict = {}
    while i < len(lines) and lines[i].indent == indent:
        line = lines[i]
        if line.text == _SEQ:
            break
        key, sep, rest = _split_key(line.text)
        if not sep:
            raise YamlError(f"第 {line.lineno} 行：期望 `key: value`，得到 {line.text!r}")
        if key.startswith("&") or key.startswith("*") or key.startswith("!"):
            raise YamlError(f"第 {line.lineno} 行：不支持锚点/别名/标签")
        key_value = _parse_scalar(key, line.lineno)

        if rest and rest[0] in "|>":
            value, consumed = _read_block_scalar(
                raw_lines, line.raw_idx + 1, indent, rest, line.lineno
            )
            result[key_value] = value
            # 跳到块标量之后的第一条逻辑行
            i += 1
            while i < len(lines) and lines[i].raw_idx < consumed:
                i += 1
            continue

        if rest == "":
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            # 块序列可以与它的 key 同缩进（PyYAML 的写法），也可以更深
            if nxt is not None and (
                nxt.indent > indent
                or (nxt.indent == indent and nxt.text == _SEQ)
            ):
                value, i = _parse_node(lines, i + 1, nxt.indent, raw_lines)
            else:
                value = None
                i += 1
        else:
            value = _parse_scalar(rest, line.lineno)
            i += 1
        result[key_value] = value
    return result, i


def _parse_sequence(
    lines: list[_Line], i: int, indent: int, raw_lines: list[str]
) -> tuple[list, int]:
    result: list = []
    while i < len(lines) and lines[i].indent == indent and lines[i].text == _SEQ:
        marker = lines[i]
        i += 1

        if i >= len(lines):
            result.append(None)
            break

        content = lines[i]
        if content.indent == indent + 2:
            # 序列项是映射
            value, i = _parse_mapping(lines, i, content.indent, raw_lines)
            result.append(value)
            continue

        if content.indent != indent:
            # 空项 / 嵌套块
            value, i = _parse_node(lines, i, content.indent, raw_lines)
            result.append(value)
            continue

        rest = content.text
        if rest and rest[0] in "|>":
            value, consumed = _read_block_scalar(
                raw_lines, marker.raw_idx + 1, indent, rest, marker.lineno
            )
            result.append(value)
            i += 1
            while i < len(lines) and lines[i].raw_idx < consumed:
                i += 1
            continue

        result.append(_parse_scalar(rest, marker.lineno))
        i += 1
    return result, i


# ── 序列化 ──────────────────────────────────────────────────────────
_PLAIN_SAFE = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./+@"
)


def _needs_quote(s: str) -> bool:
    if s == "":
        return True
    if s.strip() != s:
        return True
    if s[0] in "-?:,[]{}#&*!|>'\"%@`":
        return True
    if ": " in s or " #" in s or s.endswith(":"):
        return True
    if "\n" in s or "\t" in s:
        return True
    if any(c not in _PLAIN_SAFE for c in s):
        # 含中文、空格等 —— 加引号更安全
        return True
    if s in _TRUE or s in _FALSE or s in _NULL:
        return True
    try:
        float(s)
        return True
    except ValueError:
        return False


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if "\n" in s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if _needs_quote(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def dumps(data: Any, indent: int = 0) -> str:
    """把数据序列化成 YAML 子集文本。"""
    lines: list[str] = []

    def emit(node: Any, level: int) -> None:
        pad = " " * (level * 2)
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, dict) and value:
                    lines.append(f"{pad}{key}:")
                    emit(value, level + 1)
                elif isinstance(value, list) and value:
                    lines.append(f"{pad}{key}:")
                    emit(value, level + 1)
                elif isinstance(value, dict):
                    lines.append(f"{pad}{key}: {{}}")
                elif isinstance(value, list):
                    lines.append(f"{pad}{key}: []")
                elif isinstance(value, str) and "\n" in value:
                    lines.append(f"{pad}{key}: |")
                    for ln in value.rstrip("\n").split("\n"):
                        lines.append(f"{pad}  {ln}")
                else:
                    lines.append(f"{pad}{key}: {_dump_scalar(value)}")
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, dict) and item:
                    first = True
                    for key, value in item.items():
                        prefix = f"{pad}- " if first else f"{pad}  "
                        first = False
                        if isinstance(value, dict) and value:
                            lines.append(f"{prefix}{key}:")
                            emit(value, level + 2)
                        elif isinstance(value, list) and value:
                            lines.append(f"{prefix}{key}:")
                            emit(value, level + 2)
                        elif isinstance(value, str) and "\n" in value:
                            lines.append(f"{prefix}{key}: |")
                            for ln in value.rstrip("\n").split("\n"):
                                lines.append(f"{pad}    {ln}")
                        else:
                            lines.append(f"{prefix}{key}: {_dump_scalar(value)}")
                elif isinstance(item, (list, dict)):
                    lines.append(f"{pad}-")
                    emit(item, level + 1)
                else:
                    lines.append(f"{pad}- {_dump_scalar(item)}")
        else:
            lines.append(f"{pad}{_dump_scalar(node)}")

    emit(data, indent)
    return "\n".join(lines) + "\n"
