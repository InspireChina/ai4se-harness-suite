"""配置加载：队列配置（overnight-runner.yaml）与项目配置（.overnight-runner/project.yaml）。

配置分三层：

- **runner 级**：`overnight-runner.yaml` —— agent 命令、看门狗、UI、决策策略（项目共享）
- **project 级**：`.overnight-runner/project.yaml` —— 默认提示词与默认决策规则（全队列共享）
- **queue 级**：`.overnight-runner/queue/<name>/queue.yaml` —— 队列里的任务列表（每条队列一份）
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import yaml_lite as yaml

from .util import atomic_write

QUEUE_CONFIG_NAME = "overnight-runner.yaml"
PROJECT_DIR_NAME = ".overnight-runner"
PROJECT_CONFIG_NAME = "project.yaml"

# 多队列：每条队列在 .overnight-runner/queue/<name>/ 下有一份独立目录
QUEUE_DIR_NAME = "queue"
DEFAULT_QUEUE_NAME = "default"
QUEUE_FILE_NAME = "queue.yaml"
STATE_FILE_NAME = "state.json"
LOGS_DIR_NAME = "logs"
DECISIONS_FILE_NAME = "decisions.jsonl"
LOCK_FILE_NAME = ".lock"

DEFAULT_AGENT_COMMAND = "opencode"
DEFAULT_AGENT_ARGS: list[str] = ["run"]

# 决策模式：attended = 有人值守（弹窗问人）；unattended = 无人值守（直接决策）
DECISION_MODE_ATTENDED = "attended"
DECISION_MODE_UNATTENDED = "unattended"
DECISION_MODES = (DECISION_MODE_ATTENDED, DECISION_MODE_UNATTENDED)

# 队列名白名单：不允许路径穿越
QUEUE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")



# ── 项目配置 ────────────────────────────────────────────────────────
@dataclass
class DecisionRule:
    """一条默认决策：命中问题类别就用预设答案，并且记一笔。"""

    id: str
    question: str = ""
    match: str = ""
    answer: str = ""
    enabled: bool = True

    def describe(self) -> str:
        return f"{self.id}: {self.question or self.match} → {self.answer}"


@dataclass
class ProjectConfig:
    name: str = ""
    agent_command: str = DEFAULT_AGENT_COMMAND
    agent_args: list[str] = field(default_factory=lambda: list(DEFAULT_AGENT_ARGS))
    agent_env: dict[str, str] = field(default_factory=dict)
    default_prompt: str = ""
    decisions: list[DecisionRule] = field(default_factory=list)
    on_unknown_decision: str = "跳过并记录到决策日志"
    source_path: Path | None = None

    def decision_text(self) -> str:
        if not self.decisions:
            return ""
        lines = [f"- [{d.id}] {d.question or d.match} → {d.answer}" for d in self.decisions]
        return "\n".join(lines)

    def to_yaml(self) -> str:
        data = {
            "project": {
                "name": self.name,
                "agent": {
                    "command": self.agent_command,
                    "args": self.agent_args,
                    "env": self.agent_env,
                },
            },
            "default": {
                "prompt": self.default_prompt,
                "onUnknownDecision": self.on_unknown_decision,
            },
            "decisions": [
                {
                    "id": d.id,
                    "question": d.question,
                    "match": d.match,
                    "answer": d.answer,
                    "enabled": d.enabled,
                }
                for d in self.decisions
            ],
        }
        return yaml.dumps(data)


DEFAULT_PROJECT_PROMPT = """\
你在无人值守模式下工作，不要停下来等待人工确认。

按下面的方案执行，遇到需要决策的问题，按"默认决策"处理：
{{DECISIONS}}

{{PLAN}}

执行要求：
1. 每做出一个决策，输出一行：DECISION: <问题> → <决策>
2. 全部完成后输出一行：DONE: <一句话总结>
3. 如果无法继续，输出一行：BLOCKED: <原因>
"""


def load_project_config(project_root: Path) -> ProjectConfig:
    path = project_root / PROJECT_DIR_NAME / PROJECT_CONFIG_NAME
    cfg = ProjectConfig(source_path=path)
    if not path.exists():
        cfg.default_prompt = DEFAULT_PROJECT_PROMPT
        return cfg

    data = yaml.loads(path.read_text(encoding="utf-8")) or {}
    proj = data.get("project") or {}
    cfg.name = proj.get("name") or project_root.name

    agent = proj.get("agent") or {}
    cfg.agent_command = agent.get("command") or DEFAULT_AGENT_COMMAND
    cfg.agent_args = list(agent.get("args") or DEFAULT_AGENT_ARGS)
    cfg.agent_env = dict(agent.get("env") or {})

    default = data.get("default") or {}
    cfg.default_prompt = default.get("prompt") or DEFAULT_PROJECT_PROMPT
    cfg.on_unknown_decision = default.get("onUnknownDecision") or cfg.on_unknown_decision

    for item in data.get("decisions") or []:
        cfg.decisions.append(
            DecisionRule(
                id=str(item.get("id") or f"rule-{len(cfg.decisions) + 1}"),
                question=item.get("question") or "",
                match=item.get("match") or "",
                answer=item.get("answer") or "",
                enabled=bool(item.get("enabled", True)),
            )
        )
    return cfg


def save_project_config(project_root: Path, cfg: ProjectConfig) -> Path:
    path = project_root / PROJECT_DIR_NAME / PROJECT_CONFIG_NAME
    atomic_write(path, cfg.to_yaml())
    return path


# ── 多队列：路径解析与老布局迁移 ────────────────────────────────────
@dataclass(frozen=True)
class QueuePaths:
    """一条队列在磁盘上的全部路径。"""

    root: Path
    name: str

    @property
    def dir(self) -> Path:
        return self.root / PROJECT_DIR_NAME / QUEUE_DIR_NAME / self.name

    @property
    def config(self) -> Path:
        """队列定义（进版本库）。"""
        return self.dir / QUEUE_FILE_NAME

    @property
    def state(self) -> Path:
        """运行时状态（不进版本库）。"""
        return self.dir / STATE_FILE_NAME

    @property
    def logs(self) -> Path:
        """agent 日志与 prompt 文件（不进版本库）。"""
        return self.dir / LOGS_DIR_NAME

    @property
    def decisions(self) -> Path:
        """决策记录（进版本库）。"""
        return self.dir / DECISIONS_FILE_NAME

    @property
    def lock(self) -> Path:
        """单实例锁（不进版本库）。"""
        return self.dir / LOCK_FILE_NAME


def queue_paths(project_root: Path, name: str = DEFAULT_QUEUE_NAME) -> QueuePaths:
    """解析一条队列的路径。队列名非法直接报错（防路径穿越）。"""
    if not name or not QUEUE_NAME_RE.match(name):
        raise ValueError(
            f"队列名不合法: {name!r}（只允许字母、数字、. _ -，且必须以字母或数字开头）"
        )
    return QueuePaths(root=project_root, name=name)


def queue_names(project_root: Path) -> list[str]:
    """列出磁盘上已有的队列名（按字典序）。"""
    base = project_root / PROJECT_DIR_NAME / QUEUE_DIR_NAME
    if not base.is_dir():
        return []
    out = [
        p.name
        for p in sorted(base.iterdir(), key=lambda x: x.name)
        if p.is_dir() and QUEUE_NAME_RE.match(p.name)
    ]
    return out


def strip_queue_section(text: str) -> str:
    """从 YAML 文本里删掉顶层的 `queue:` 段，**其余内容原样保留**。

    为什么不用"解析 → 改 → 重新序列化"：那样会把用户写的注释全弄丢。
    这里按行做手术，只动 `queue:` 那一段。

    - `queue:` 后面跟缩进内容（块序列）→ 整段删掉
    - `queue: []` 这种内联写法 → 改成 `queue: []`（保持只有一个空段）
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^queue\s*:(.*)$", line)
        if not m:
            out.append(line)
            i += 1
            continue

        tail = m.group(1).strip()
        if tail and not tail.startswith("#"):
            # 内联写法（queue: [] / queue: [...]）—— 归一成空列表
            out.append("queue: []")
            i += 1
            continue

        # 块序列：吃掉这一行 + 后面所有缩进行
        i += 1
        while i < n:
            nxt = lines[i]
            if nxt.strip() == "":
                # 空行：后面若还有缩进内容就一并吃掉
                j = i
                while j < n and lines[j].strip() == "":
                    j += 1
                if j < n and lines[j][:1] in (" ", "\t"):
                    i = j
                    continue
                break
            if nxt[:1] in (" ", "\t"):
                i += 1
                continue
            break
    return "\n".join(out)


def migrate_legacy_queue(project_root: Path) -> str:
    """把老布局迁移到 `.overnight-runner/queue/default/`。

    老布局：
        <root>/overnight-runner.yaml            的 queue: 段
        <root>/.overnight-runner/state.json
        <root>/.overnight-runner/logs/
        <root>/.overnight-runner/decisions.jsonl

    迁移是 **幂等** 的：源清空后第二次调用直接返回空串。
    用的是 move（rename）不是 copy，源文件不会留下两份。

    返回一句人类可读的迁移说明（没迁移则返回空串）。
    """
    notes: list[str] = []
    default = queue_paths(project_root, DEFAULT_QUEUE_NAME)

    # 1) 队列定义：根配置文件的 queue: 段 → queue/default/queue.yaml
    legacy_cfg_path = queue_config_path(project_root)
    if legacy_cfg_path.exists():
        raw = legacy_cfg_path.read_text(encoding="utf-8")
        data = yaml.loads(raw) or {}
        legacy_queue = list(data.get("queue") or [])
        if legacy_queue and not default.config.exists():
            default.dir.mkdir(parents=True, exist_ok=True)
            atomic_write(
                default.config,
                yaml.dumps({"queue": legacy_queue}),
            )
            notes.append(f"队列定义 → {default.config}")
            # 把根配置里的 queue: 段清空，保证只迁移一次。
            # 按行做手术，保留用户写的注释与排版。
            atomic_write(legacy_cfg_path, strip_queue_section(raw))

    # 2) 运行时状态 / 日志 / 决策记录：整体搬进 default 队列目录
    legacy_dir = project_root / PROJECT_DIR_NAME
    for name, dest in (
        (STATE_FILE_NAME, default.state),
        (LOGS_DIR_NAME, default.logs),
        (DECISIONS_FILE_NAME, default.decisions),
    ):
        src = legacy_dir / name
        if not src.exists():
            continue
        if dest.exists():
            continue
        default.dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        notes.append(f"{src} → {dest}")

    return "；".join(notes)


# ── 队列配置 ────────────────────────────────────────────────────────
@dataclass
class WatchdogConfig:
    max_retries: int = 2
    backoff_sec: int = 60
    idle_timeout_sec: int = 1800
    total_timeout_sec: int = 7200
    kill_grace_sec: int = 15

    @classmethod
    def from_dict(cls, data: dict | None) -> "WatchdogConfig":
        data = data or {}
        return cls(
            max_retries=int(data.get("maxRetries", 2)),
            backoff_sec=int(data.get("backoffSec", 60)),
            idle_timeout_sec=int(data.get("idleTimeoutSec", 1800)),
            total_timeout_sec=int(data.get("totalTimeoutSec", 7200)),
            kill_grace_sec=int(data.get("killGraceSec", 15)),
        )

    def to_dict(self) -> dict:
        return {
            "maxRetries": self.max_retries,
            "backoffSec": self.backoff_sec,
            "idleTimeoutSec": self.idle_timeout_sec,
            "totalTimeoutSec": self.total_timeout_sec,
            "killGraceSec": self.kill_grace_sec,
        }


@dataclass
class DecisionConfig:
    """决策策略。

    - `mode=attended`（有人值守）：agent 抛问题时打断它，TUI 弹决策窗口问人；
      超时没人答就按规则/兜底策略自动决策。
    - `mode=unattended`（无人值守）：不打断 agent，按规则/兜底策略直接决策。
    """

    mode: str = DECISION_MODE_ATTENDED
    timeout_sec: int = 600
    resume: str = "session"          # session | restart
    output_format: str = "json"      # json | text
    json_args: list[str] = field(default_factory=lambda: ["--format", "json"])
    session_args: list[str] = field(default_factory=lambda: ["--session", "{session}"])
    session_pattern: str = r'"sessionID"\s*:\s*"(ses_[A-Za-z0-9]+)"'

    @classmethod
    def from_dict(cls, data: dict | None) -> "DecisionConfig":
        data = data or {}
        mode = str(data.get("mode") or DECISION_MODE_ATTENDED)
        if mode not in DECISION_MODES:
            mode = DECISION_MODE_ATTENDED
        resume = str(data.get("resume") or "session")
        if resume not in ("session", "restart"):
            resume = "session"
        output_format = str(data.get("outputFormat") or "json")
        if output_format not in ("json", "text"):
            output_format = "json"
        args = data.get("sessionArgs")
        if not isinstance(args, list) or not args:
            args = ["--session", "{session}"]
        json_args = data.get("jsonArgs")
        if not isinstance(json_args, list) or not json_args:
            json_args = ["--format", "json"]
        return cls(
            mode=mode,
            timeout_sec=int(data.get("timeoutSec", 600)),
            resume=resume,
            output_format=output_format,
            json_args=[str(a) for a in json_args],
            session_args=[str(a) for a in args],
            session_pattern=str(
                data.get("sessionPattern")
                or r'"sessionID"\s*:\s*"(ses_[A-Za-z0-9]+)"'
            ),
        )

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "timeoutSec": self.timeout_sec,
            "resume": self.resume,
            "outputFormat": self.output_format,
            "jsonArgs": list(self.json_args),
            "sessionArgs": list(self.session_args),
            "sessionPattern": self.session_pattern,
        }

    def session_command(self, session_id: str) -> list[str]:
        """把 session_args 里的 {session} 占位符替换成真实 session id。"""
        return [a.replace("{session}", session_id) for a in self.session_args]


@dataclass
class RunnerConfig:
    """启动时用的队列配置（overnight-runner.yaml）。"""

    agent_command: str = DEFAULT_AGENT_COMMAND
    agent_args: list[str] = field(default_factory=lambda: list(DEFAULT_AGENT_ARGS))
    agent_env: dict[str, str] = field(default_factory=dict)
    watchdog: WatchdogConfig = field(default_factory=WatchdogConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    state_dir: str = PROJECT_DIR_NAME
    workdir: str = "."
    refresh_hz: int = 8
    log_tail: int = 400
    queue: list[dict] = field(default_factory=list)
    source_path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict, source_path: Path | None = None) -> "RunnerConfig":
        runner = data.get("runner") or {}
        agent = runner.get("agent") or {}
        cfg = cls(
            agent_command=agent.get("command") or DEFAULT_AGENT_COMMAND,
            agent_args=list(agent["args"]) if agent.get("args") is not None else list(DEFAULT_AGENT_ARGS),
            agent_env=dict(agent.get("env") or {}),
            watchdog=WatchdogConfig.from_dict(runner.get("watchdog")),
            decision=DecisionConfig.from_dict(runner.get("decision")),
            state_dir=runner.get("state", {}).get("dir") or PROJECT_DIR_NAME,
            workdir=runner.get("workdir") or ".",
            refresh_hz=int((runner.get("ui") or {}).get("refreshHz", 8)),
            log_tail=int((runner.get("ui") or {}).get("logTail", 400)),
            queue=list(data.get("queue") or []),
            source_path=source_path,
        )
        return cfg

    def to_dict(self) -> dict:
        data: dict[str, Any] = {
            "runner": {
                "agent": {
                    "command": self.agent_command,
                    "args": self.agent_args,
                    "env": self.agent_env,
                },
                "watchdog": self.watchdog.to_dict(),
                "decision": self.decision.to_dict(),
                "state": {"dir": self.state_dir},
                "workdir": self.workdir,
                "ui": {"refreshHz": self.refresh_hz, "logTail": self.log_tail},
            }
        }
        # 队列定义已经搬到 .overnight-runner/queue/<name>/queue.yaml，这里只在
        # 还没迁移时保留（迁移后为空 → 不写出去）
        if self.queue:
            data["queue"] = self.queue
        return data

    def to_yaml(self) -> str:
        header = (
            "# overnight-runner 运行配置\n"
            "# agent / 看门狗 / UI / 决策策略 —— 项目级，全队列共享\n"
            "# 队列里的任务在 .overnight-runner/queue/<name>/queue.yaml\n"
        )
        return header + yaml.dumps(self.to_dict())


def queue_config_path(project_root: Path) -> Path:
    return project_root / QUEUE_CONFIG_NAME


def load_runner_config(project_root: Path) -> RunnerConfig:
    path = queue_config_path(project_root)
    if not path.exists():
        return RunnerConfig(source_path=path)
    data = yaml.loads(path.read_text(encoding="utf-8")) or {}
    return RunnerConfig.from_dict(data, source_path=path)


def save_runner_config(project_root: Path, cfg: RunnerConfig) -> Path:
    path = queue_config_path(project_root)
    atomic_write(path, cfg.to_yaml())
    return path


def default_queue_config(project_root: Path) -> RunnerConfig:
    cfg = RunnerConfig(source_path=queue_config_path(project_root))
    cfg.queue = []
    return cfg


__all__ = [
    "DECISION_MODES",
    "DECISION_MODE_ATTENDED",
    "DECISION_MODE_UNATTENDED",
    "DEFAULT_QUEUE_NAME",
    "DecisionConfig",
    "DecisionRule",
    "ProjectConfig",
    "QueuePaths",
    "RunnerConfig",
    "WatchdogConfig",
    "default_queue_config",
    "load_project_config",
    "load_runner_config",
    "migrate_legacy_queue",
    "queue_config_path",
    "queue_names",
    "queue_paths",
    "save_project_config",
    "save_runner_config",
    "DEFAULT_AGENT_ARGS",
    "DEFAULT_AGENT_COMMAND",
    "DEFAULT_PROJECT_PROMPT",
    "PROJECT_CONFIG_NAME",
    "PROJECT_DIR_NAME",
    "QUEUE_CONFIG_NAME",
    "QUEUE_DIR_NAME",
    "QUEUE_FILE_NAME",
]
