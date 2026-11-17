"""默认决策：规则匹配 + 决策记录。

三种来源：
1. agent 自己按默认决策执行后输出 `DECISION: <问题> → <决策>`，我们解析并记录；
2. agent 抛出一个待决问题（输出 `QUESTION: <问题>`）—— 无人值守时用规则匹配给答案，
   有人值守时先问人（见 controller），答案最终都会回灌给 agent 并记录。

记录写在 `<queue>/decisions.jsonl`，一行一条，便于后续回溯。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import DECISION_MODE_ATTENDED, DecisionRule, ProjectConfig
from .util import append_jsonl, now_iso

DECISION_RE = re.compile(r"^\s*DECISION\s*[:：]\s*(.+?)\s*(?:→|->)\s*(.+?)\s*$")
QUESTION_RE = re.compile(r"^\s*QUESTION\s*[:：]\s*(.+?)\s*$")
BLOCKED_RE = re.compile(r"^\s*BLOCKED\s*[:：]\s*(.+?)\s*$")
DONE_RE = re.compile(r"^\s*DONE\s*[:：]\s*(.+?)\s*$")

# 决策来源
SOURCE_AGENT = "agent"        # agent 自己输出的 DECISION
SOURCE_RULE = "rule"          # 命中预设规则
SOURCE_FALLBACK = "fallback"  # 兜底策略（onUnknownDecision）
SOURCE_HUMAN = "human"        # 人在 TUI 里回答的
SOURCE_TIMEOUT = "timeout"    # 等待超时后自动兜底的


@dataclass
class DecisionEvent:
    task_id: str
    question: str
    answer: str
    source: str = SOURCE_AGENT
    rule_id: str = ""
    at: str = ""
    waited_sec: float | None = None
    session_id: str = ""

    def to_record(self) -> dict:
        return {
            "at": self.at or now_iso(),
            "task_id": self.task_id,
            "question": self.question,
            "answer": self.answer,
            "source": self.source,
            "rule_id": self.rule_id,
            "waited_sec": round(self.waited_sec, 1) if self.waited_sec is not None else 0.0,
            "session_id": self.session_id,
        }


class DecisionLog:
    """决策记录：JSONL 追加写 + 内存缓存。"""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._records: list[dict] = []

    def load(self) -> list[dict]:
        import json

        if not self.path.exists():
            self._records = []
            return self._records
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        self._records = out
        return out

    def record(self, event: DecisionEvent) -> dict:
        rec = event.to_record()
        append_jsonl(self.path, rec)
        self._records.append(rec)
        return rec

    @property
    def records(self) -> list[dict]:
        return list(self._records)

    def for_task(self, task_id: str) -> list[dict]:
        return [r for r in self._records if r.get("task_id") == task_id]


def match_rule(rules: list[DecisionRule], question: str) -> DecisionRule | None:
    """用关键词/正则匹配一条默认决策。"""
    q = question.strip()
    for rule in rules:
        if not rule.enabled:
            continue
        if rule.question and (rule.question.strip() == q or rule.question.strip() in q):
            return rule
        if rule.match:
            try:
                if re.search(rule.match, q):
                    return rule
            except re.error:
                if rule.match.lower() in q.lower():
                    return rule
    return None


def parse_agent_line(line: str) -> tuple[str, str]:
    """解析 agent 的一行输出。

    返回 (kind, value)，kind ∈ decision / question / blocked / done / ''。
    """
    m = DECISION_RE.match(line)
    if m:
        return "decision", (m.group(1).strip(), m.group(2).strip())  # type: ignore[return-value]
    m = QUESTION_RE.match(line)
    if m:
        return "question", m.group(1).strip()  # type: ignore[return-value]
    m = BLOCKED_RE.match(line)
    if m:
        return "blocked", m.group(1).strip()  # type: ignore[return-value]
    m = DONE_RE.match(line)
    if m:
        return "done", m.group(1).strip()  # type: ignore[return-value]
    return "", ""


def resolve_answer(project_cfg: ProjectConfig, question: str) -> tuple[str, str]:
    """算出（答案, rule_id）—— **纯函数，不写日志**。

    命中规则就用规则答案，否则用项目的兜底策略。
    """
    rule = match_rule(project_cfg.decisions, question)
    if rule is not None:
        return (rule.answer or project_cfg.on_unknown_decision), rule.id
    return project_cfg.on_unknown_decision, ""


def should_ask(mode: str) -> bool:
    """该模式下要不要问人。

    - `attended`（有人值守）：要问
    - `unattended`（无人值守）：不问
    """
    return mode == DECISION_MODE_ATTENDED


def decide(
    project_cfg: ProjectConfig,
    log: DecisionLog,
    task_id: str,
    question: str,
) -> tuple[str, str]:
    """给 agent 抛出的问题一个默认答案（无人值守路径）。

    返回 (answer, rule_id)。命中规则就用规则答案，否则用项目的兜底策略。
    """
    answer, rule_id = resolve_answer(project_cfg, question)
    log.record(
        DecisionEvent(
            task_id=task_id,
            question=question,
            answer=answer,
            source=SOURCE_RULE if rule_id else SOURCE_FALLBACK,
            rule_id=rule_id,
        )
    )
    return answer, rule_id
