"""冒烟测试：不依赖真实 agent，用假脚本验证队列、决策、看门狗。

运行：
    python -m pytest tests/ -q
或直接：
    python tests/test_smoke.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from overnight_runner import yaml_lite as yaml  # noqa: E402

from overnight_runner.cli import main as cli_main  # noqa: E402
from overnight_runner.config import (  # noqa: E402
    DECISION_MODE_ATTENDED,
    DECISION_MODE_UNATTENDED,
    load_project_config,
    load_runner_config,
    queue_paths,
)
from overnight_runner.controller import RunnerController  # noqa: E402
from overnight_runner.decisions import DecisionLog, match_rule, parse_agent_line  # noqa: E402
from overnight_runner.queue import (  # noqa: E402
    FAILED,
    SUCCESS,
    build_task,
    load_queue,
    load_queue_defs,
    save_queue_defs,
)
from overnight_runner.util import StopFlag  # noqa: E402


# 假 agent 统一前缀：记录第几次调用 + 把参数写进 args 文件（换行压成 ~）
FAKE_PROLOGUE = """
COUNT_FILE="${FAKE_COUNT:-/dev/null}"
ARGS_FILE="${FAKE_ARGS:-/dev/null}"
n=$(cat "$COUNT_FILE" 2>/dev/null || echo 0)
n=$((n+1))
echo "$n" > "$COUNT_FILE" 2>/dev/null || true
printf 'CALL %s: %s\\n' "$n" "$(printf '%s' "$*" | tr '\\n' '~')" >> "$ARGS_FILE" 2>/dev/null || true
"""


def _write_fake_agent(path: Path, body: str) -> str:
    path.write_text(
        f"#!/usr/bin/env bash\n{FAKE_PROLOGUE}{body}\n", encoding="utf-8"
    )
    path.chmod(0o755)
    return str(path)


# 假 agent：第一次调用抛问题，第二次（带 --session）回答"拿到答案"
FAKE_ASK_THEN_ANSWER = """
if [ "$n" -eq 1 ]; then
  echo '{"type":"text","sessionID":"ses_fake0001","part":{"type":"text","text":"QUESTION: 要改吗？"}}'
  exit 0
fi
echo '{"type":"text","sessionID":"ses_fake0001","part":{"type":"text","text":"DONE: 拿到答案继续干"}}'
exit 0
"""


def _setup(
    tmp: Path,
    agent: str,
    queue: list[dict],
    watchdog: dict | None = None,
    decision: dict | None = None,
) -> Path:
    root = tmp / "proj"
    (root / "docs" / "plans").mkdir(parents=True)
    (root / "docs" / "plans" / "p1.md").write_text("# Plan 1\n做点事\n", encoding="utf-8")

    cfg = {
        "runner": {
            "agent": {
                "command": agent,
                "args": [],
                "env": {
                    "FAKE_COUNT": str(tmp / "count"),
                    "FAKE_ARGS": str(tmp / "args"),
                },
            },
            "watchdog": watchdog
            or {"maxRetries": 0, "backoffSec": 1, "idleTimeoutSec": 30, "totalTimeoutSec": 60},
            "decision": decision or {"mode": DECISION_MODE_UNATTENDED},
            "state": {"dir": ".overnight-runner"},
            "workdir": ".",
            "ui": {"refreshHz": 8, "logTail": 100},
        },
    }
    pcfg = {
        "project": {"name": "proj", "agent": {"command": agent, "args": [], "env": {}}},
        "default": {"prompt": "{{DECISIONS}}\n{{PLAN}}", "onUnknownDecision": "跳过并记录"},
        "decisions": [
            {
                "id": "db",
                "question": "是否执行数据库迁移脚本？",
                "match": "数据库迁移",
                "answer": "先写回滚脚本",
                "enabled": True,
            }
        ],
    }
    (root / ".overnight-runner").mkdir()
    (root / ".overnight-runner" / "overnight-runner.yaml").write_text(
        yaml.dumps(cfg), encoding="utf-8"
    )
    (root / ".overnight-runner" / "project.yaml").write_text(
        yaml.dumps(pcfg), encoding="utf-8"
    )

    paths = queue_paths(root, "default")
    paths.dir.mkdir(parents=True, exist_ok=True)
    (paths.config).write_text(yaml.dumps({"queue": queue}), encoding="utf-8")
    return root


def _controller(root: Path) -> tuple[RunnerController, object]:
    cfg = load_runner_config(root)
    pcfg = load_project_config(root)
    paths = queue_paths(root, "default")
    q = load_queue(paths, load_queue_defs(paths))
    ctl = RunnerController(root, cfg, pcfg, q, paths, stop=StopFlag())
    return ctl, q


def _wait_pending(ctl: RunnerController, timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ctl.pending_question() is not None:
            return True
        time.sleep(0.05)
    return False


def _fake_calls(tmp: Path) -> list[str]:
    path = tmp / "args"
    if not path.exists():
        return []
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ── 既有场景 ────────────────────────────────────────────────────────
def test_queue_add_and_append(tmp: Path) -> None:
    root = _setup(tmp, "true", [])
    cfg = load_runner_config(root)
    paths = queue_paths(root, "default")
    q = load_queue(paths, load_queue_defs(paths))

    t1 = build_task(root, "docs/plans/p1.md", existing_ids={t.id for t in q.tasks})
    q.add(t1)
    t2 = build_task(root, "docs/plans/p1.md", existing_ids={t.id for t in q.tasks})
    q.add(t2)
    assert t1.id != t2.id, "同一天同一个 plan 也要能排两次"

    save_queue_defs(paths, q)
    again = load_queue_defs(paths)
    assert len(again) == 2
    assert cfg.agent_command == "true"


def test_successful_task_records_decision(tmp: Path) -> None:
    agent = _write_fake_agent(
        tmp / "ok.sh",
        'echo "DECISION: 是否执行数据库迁移脚本？ → 先写回滚脚本"\necho "DONE: 搞定"',
    )
    root = _setup(tmp, agent, [{"id": "t1", "plan": "docs/plans/p1.md"}])
    ctl, q = _controller(root)
    ctl.run_forever()

    task = q.get("t1")
    assert task is not None
    assert task.status == SUCCESS, f"期望成功，实际 {task.status}: {task.last_error}"
    assert task.summary == "搞定"

    records = DecisionLog(queue_paths(root, "default").decisions).load()
    assert len(records) == 1
    assert records[0]["source"] == "agent"
    assert records[0]["question"] == "是否执行数据库迁移脚本？"


def test_failed_task_retries_then_fails(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "fail.sh", 'echo "boom"\nexit 3')
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        watchdog={"maxRetries": 2, "backoffSec": 0, "idleTimeoutSec": 30, "totalTimeoutSec": 60},
    )
    ctl, q = _controller(root)
    ctl.run_forever()

    task = q.get("t1")
    assert task is not None
    assert task.status == FAILED
    assert task.attempts == 3, f"期望 1 次 + 2 次重试，实际 {task.attempts} 次"


def test_idle_timeout_kills_agent(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "hang.sh", 'echo "开始"\nsleep 30')
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        watchdog={
            "maxRetries": 0,
            "backoffSec": 0,
            "idleTimeoutSec": 1,
            "totalTimeoutSec": 60,
            "killGraceSec": 1,
        },
    )
    ctl, q = _controller(root)
    ctl.run_forever()

    task = q.get("t1")
    assert task is not None
    assert task.status == FAILED
    assert "超时" in task.last_error, task.last_error


def test_question_hits_rule(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "q.sh", 'echo "QUESTION: 是否执行数据库迁移脚本？"\necho "DONE: ok"')
    root = _setup(tmp, agent, [{"id": "t1", "plan": "docs/plans/p1.md"}])
    ctl, q = _controller(root)
    ctl.run_forever()

    records = DecisionLog(queue_paths(root, "default").decisions).load()
    assert len(records) == 1
    assert records[0]["source"] == "rule"
    assert records[0]["rule_id"] == "db"
    assert records[0]["answer"] == "先写回滚脚本"


def test_parse_agent_line(tmp: Path) -> None:
    assert parse_agent_line("DECISION: A → B") == ("decision", ("A", "B"))
    assert parse_agent_line("QUESTION: 要改吗？") == ("question", "要改吗？")
    assert parse_agent_line("DONE: 好了") == ("done", "好了")
    assert parse_agent_line("BLOCKED: 卡住了") == ("blocked", "卡住了")
    assert parse_agent_line("普通输出") == ("", "")


def test_match_rule(tmp: Path) -> None:
    pcfg = load_project_config(_setup(Path(tempfile.mkdtemp()), "true", []))
    assert match_rule(pcfg.decisions, "是否执行数据库迁移脚本？") is not None
    assert match_rule(pcfg.decisions, "要不要重构") is None


# ── 有人值守：人回答 ────────────────────────────────────────────────
def test_attended_human_answer_resumes_session(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "ask.sh", FAKE_ASK_THEN_ANSWER)
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_ATTENDED, "timeoutSec": 30},
    )
    ctl, q = _controller(root)

    worker = threading.Thread(target=ctl.run_forever, daemon=True)
    worker.start()
    assert _wait_pending(ctl), "应该弹出决策窗口"
    ctl.submit_decision("先修 Bug，不要扩大改动范围")
    worker.join(timeout=30)

    task = q.get("t1")
    assert task is not None and task.status == SUCCESS, task.last_error

    calls = _fake_calls(tmp)
    assert len(calls) == 2, f"agent 应被拉起两次（问 + 续跑），实际 {len(calls)} 次"
    assert "--session ses_fake0001" in calls[1], f"续跑应带 --session: {calls[1]}"
    assert "先修 Bug" in calls[1], "续跑的 prompt 里应带上人的答案"

    records = DecisionLog(queue_paths(root, "default").decisions).load()
    humans = [r for r in records if r["source"] == "human"]
    assert len(humans) == 1, records
    assert humans[0]["answer"] == "先修 Bug，不要扩大改动范围"
    assert humans[0]["session_id"] == "ses_fake0001"
    assert humans[0]["waited_sec"] >= 0


# ── 有人值守：超时兜底 ──────────────────────────────────────────────
def test_attended_timeout_falls_back(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "ask.sh", FAKE_ASK_THEN_ANSWER)
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_ATTENDED, "timeoutSec": 1},
    )
    ctl, q = _controller(root)

    worker = threading.Thread(target=ctl.run_forever, daemon=True)
    worker.start()
    assert _wait_pending(ctl), "应该弹出决策窗口"
    worker.join(timeout=30)  # 不回答，等它超时

    task = q.get("t1")
    assert task is not None and task.status == SUCCESS, task.last_error

    calls = _fake_calls(tmp)
    assert len(calls) == 2, f"超时后仍要续跑，实际 {len(calls)} 次"
    assert "--session ses_fake0001" in calls[1]

    records = DecisionLog(queue_paths(root, "default").decisions).load()
    timeouts = [r for r in records if r["source"] == "timeout"]
    assert len(timeouts) == 1, records
    assert timeouts[0]["answer"] == "跳过并记录", "超时应该用兜底策略"


# ── 决策历史注入 ────────────────────────────────────────────────────
def test_decision_history_is_injected(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "ask.sh", FAKE_ASK_THEN_ANSWER)
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_ATTENDED, "timeoutSec": 30},
    )
    ctl, q = _controller(root)

    worker = threading.Thread(target=ctl.run_forever, daemon=True)
    worker.start()
    assert _wait_pending(ctl)
    ctl.submit_decision("按 Plan §11.1 改类型声明")
    worker.join(timeout=30)

    calls = _fake_calls(tmp)
    assert len(calls) == 2
    # 续跑用的是 resume prompt（决策直接带进去）
    assert "按 Plan §11.1 改类型声明" in calls[1]


# ── 无人值守 ────────────────────────────────────────────────────────
def test_unattended_does_not_interrupt(tmp: Path) -> None:
    agent = _write_fake_agent(
        tmp / "q.sh",
        'echo "QUESTION: 是否执行数据库迁移脚本？"\necho "DONE: ok"',
    )
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_UNATTENDED},
    )
    ctl, q = _controller(root)
    ctl.run_forever()

    calls = _fake_calls(tmp)
    assert len(calls) == 1, f"无人值守不该打断 agent，实际调用 {len(calls)} 次"
    records = DecisionLog(queue_paths(root, "default").decisions).load()
    assert any(r["source"] == "rule" for r in records), records


# ── CLI：headless 强制无人值守 ──────────────────────────────────────
def test_cli_headless_forces_unattended(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "q.sh", 'echo "QUESTION: 要改吗？"\necho "DONE: ok"')
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_ATTENDED, "timeoutSec": 600},
    )
    rc = cli_main(
        ["--project", str(root), "--queue", "default", "run", "--headless"]
    )
    assert rc == 0, rc
    calls = _fake_calls(tmp)
    assert len(calls) == 1, "headless 不该等人回答"
    records = DecisionLog(queue_paths(root, "default").decisions).load()
    assert not [r for r in records if r["source"] in ("human", "timeout")], records


def test_cli_mode_override_unattended(tmp: Path) -> None:
    agent = _write_fake_agent(tmp / "q.sh", 'echo "QUESTION: 要改吗？"\necho "DONE: ok"')
    root = _setup(
        tmp,
        agent,
        [{"id": "t1", "plan": "docs/plans/p1.md"}],
        decision={"mode": DECISION_MODE_ATTENDED, "timeoutSec": 600},
    )
    rc = cli_main(
        [
            "--project",
            str(root),
            "--queue",
            "default",
            "run",
            "--headless",
            "--mode",
            DECISION_MODE_UNATTENDED,
        ]
    )
    assert rc == 0, rc
    calls = _fake_calls(tmp)
    assert len(calls) == 1, "--mode unattended 不该打断"


def _run_all() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="orn-test-"))
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        case_dir = tmp / fn.__name__
        case_dir.mkdir(parents=True, exist_ok=True)
        try:
            fn(case_dir)
            print(f"  ✔ {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((fn.__name__, exc))
            print(f"  ✘ {fn.__name__}: {exc}")
    shutil.rmtree(tmp, ignore_errors=True)
    print()
    print(f"{len(tests) - len(failures)}/{len(tests)} 通过")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_all())
