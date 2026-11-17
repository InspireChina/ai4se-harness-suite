"""yaml_lite 与 term 的单元测试（零依赖）。

运行：python tests/test_units.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from overnight_runner import yaml_lite  # noqa: E402
from overnight_runner.agent import extract_session_id, parse_agent_output  # noqa: E402
from overnight_runner.cli import resolve_decision_mode  # noqa: E402
from overnight_runner.config import (  # noqa: E402
    DECISION_MODE_ATTENDED,
    DECISION_MODE_UNATTENDED,
    DecisionConfig,
    DecisionRule,
    ProjectConfig,
    RunnerConfig,
    load_runner_config,
    migrate_legacy_queue,
    queue_names,
    queue_paths,
    save_runner_config,
)
from overnight_runner.decisions import resolve_answer, should_ask  # noqa: E402
from overnight_runner.queue import (  # noqa: E402
    SUCCESS,
    build_task,
    load_queue,
    load_queue_defs,
    save_queue_defs,
    save_state,
)
from overnight_runner.term import dwidth, pad, truncate, wrap  # noqa: E402
from overnight_runner.util import QueueLock  # noqa: E402


# ── yaml_lite ───────────────────────────────────────────────────────
def test_yaml_scalar_types() -> None:
    d = yaml_lite.loads(
        """
i: 42
f: 3.14
t: true
f2: false
n: null
tilde: ~
empty:
s: hello
q: "quoted: value"
sq: 'single'
"""
    )
    assert d["i"] == 42 and isinstance(d["i"], int)
    assert d["f"] == 3.14
    assert d["t"] is True and d["f2"] is False
    assert d["n"] is None and d["tilde"] is None and d["empty"] is None
    assert d["s"] == "hello"
    assert d["q"] == "quoted: value"
    assert d["sq"] == "single"


def test_yaml_nested_and_lists() -> None:
    d = yaml_lite.loads(
        """
runner:
  agent:
    command: opencode
    args: ["run", "--verbose"]
    env: {}
  watchdog:
    maxRetries: 2
queue:
  - id: a
    plan: docs/plans/a.md
    tags: [x, y]
  - id: b
    plan: docs/plans/b.md
"""
    )
    assert d["runner"]["agent"]["command"] == "opencode"
    assert d["runner"]["agent"]["args"] == ["run", "--verbose"]
    assert d["runner"]["agent"]["env"] == {}
    assert d["runner"]["watchdog"]["maxRetries"] == 2
    assert len(d["queue"]) == 2
    assert d["queue"][0]["id"] == "a"
    assert d["queue"][0]["tags"] == ["x", "y"]
    assert d["queue"][1]["plan"] == "docs/plans/b.md"


def test_yaml_sequence_at_same_indent_as_key() -> None:
    """PyYAML 会把序列写在与 key 同缩进的位置，必须能读。"""
    d = yaml_lite.loads(
        """
queue:
- id: a
  plan: p1.md
- id: b
  plan: p2.md
"""
    )
    assert len(d["queue"]) == 2
    assert d["queue"][0]["id"] == "a"
    assert d["queue"][1]["plan"] == "p2.md"


def test_yaml_block_scalar() -> None:
    d = yaml_lite.loads(
        """
default:
  prompt: |
    第一行
    第二行
  other: x
"""
    )
    assert d["default"]["prompt"] == "第一行\n第二行\n"
    assert d["default"]["other"] == "x"


def test_yaml_multi_line_quoted_scalar() -> None:
    """PyYAML 会把带换行的字符串写成跨行引号形式，必须能读。"""
    d = yaml_lite.loads(
        """
prompt: '第一行

第二行'
other: y
"""
    )
    assert d["prompt"] == "第一行\n第二行"
    assert d["other"] == "y"


def test_yaml_comments_ignored() -> None:
    d = yaml_lite.loads(
        """
# 整行注释
a: 1  # 行尾注释
b: "带 # 号的字符串"
"""
    )
    assert d["a"] == 1
    assert d["b"] == "带 # 号的字符串"


def test_yaml_roundtrip() -> None:
    data = {
        "runner": {"agent": {"command": "opencode", "args": ["run"], "env": {}}},
        "queue": [
            {"id": "a", "plan": "docs/plans/a.md", "priority": 10},
            {"id": "b", "plan": "docs/plans/b.md", "prompt": "做点事"},
        ],
        "note": "带: 冒号的字符串",
    }
    text = yaml_lite.dumps(data)
    assert yaml_lite.loads(text) == data


def test_yaml_real_config_files() -> None:
    base = pathlib.Path(__file__).resolve().parent.parent / "config"
    for f in ("overnight-runner.example.yaml", "project.example.yaml"):
        d = yaml_lite.loads((base / f).read_text(encoding="utf-8"))
        assert isinstance(d, dict) and d
        assert yaml_lite.loads(yaml_lite.dumps(d)) == d


# ── term ────────────────────────────────────────────────────────────
def test_term_width_counts_cjk_as_two() -> None:
    assert dwidth("abc") == 3
    assert dwidth("成功") == 4
    assert dwidth("a成b") == 4
    assert dwidth("") == 0


def test_term_width_ignores_ansi() -> None:
    assert dwidth("\x1b[32mabc\x1b[0m") == 3
    assert dwidth("\x1b[97m成功\x1b[0m") == 4


def test_term_truncate() -> None:
    assert truncate("abcdef", 10) == "abcdef"
    out = truncate("abcdef", 4)
    assert dwidth(out) <= 4
    # 截断时会在末尾补 RESET，判定前先去掉
    assert out.replace("\x1b[0m", "").endswith("…")
    assert dwidth(truncate("成功成功", 5)) <= 5


def test_term_pad() -> None:
    assert dwidth(pad("成功", 10)) == 10
    assert dwidth(pad("abc", 10)) == 10
    assert pad("abc", 10).endswith("   ")


def test_term_wrap_keeps_width() -> None:
    lines = wrap("a" * 25, 10)
    assert len(lines) == 3
    assert all(dwidth(x) <= 10 for x in lines)
    lines = wrap("成功成功成功成功", 8)
    assert all(dwidth(x) <= 8 for x in lines)


def _tmp_root() -> pathlib.Path:
    return pathlib.Path(tempfile.mkdtemp(prefix="orn-unit-"))


def _legacy_project(root: pathlib.Path, queue: list[dict] | None = None) -> None:
    """造一个老布局的项目：队列写在项目根的 overnight-runner.yaml。"""
    (root / ".overnight-runner").mkdir(parents=True, exist_ok=True)
    cfg = {
        "runner": {
            "agent": {"command": "opencode", "args": ["run"], "env": {}},
            "watchdog": {"maxRetries": 1, "backoffSec": 0},
        },
        "queue": queue if queue is not None else [
            {"id": "t1", "plan": "docs/plans/p1.md", "priority": 10}
        ],
    }
    (root / "overnight-runner.yaml").write_text(
        yaml_lite.dumps(cfg), encoding="utf-8"
    )


# ── 多队列：路径与迁移 ──────────────────────────────────────────────
def test_queue_paths_resolution() -> None:
    root = _tmp_root()
    p = queue_paths(root, "alice")
    assert p.dir == root / ".overnight-runner" / "queue" / "alice"
    assert p.config.name == "queue.yaml"
    assert p.state.name == "state.json"
    assert p.logs.name == "logs"
    assert p.decisions.name == "decisions.jsonl"
    assert p.lock.name == ".lock"
    # 默认队列名
    assert queue_paths(root).name == "default"


def test_queue_name_rejected() -> None:
    root = _tmp_root()
    for bad in ("", "..", "../evil", "a/b", ".hidden", "名字"):
        try:
            queue_paths(root, bad)
        except ValueError:
            continue
        raise AssertionError(f"队列名 {bad!r} 应该被拒绝")


def test_runner_config_migrated_from_root() -> None:
    root = _tmp_root()
    (root / ".overnight-runner").mkdir(parents=True, exist_ok=True)
    (root / "overnight-runner.yaml").write_text(
        yaml_lite.dumps({"runner": {"agent": {"command": "opencode"}}}),
        encoding="utf-8",
    )
    from overnight_runner.config import (
        load_runner_config,
        migrate_runner_config_into_project_dir,
        queue_config_path,
    )

    note = migrate_runner_config_into_project_dir(root)
    assert note
    assert queue_config_path(root).exists()
    assert not (root / "overnight-runner.yaml").exists()
    # 幂等
    assert migrate_runner_config_into_project_dir(root) == ""
    cfg = load_runner_config(root)
    assert cfg.agent_command == "opencode"


def test_legacy_queue_migrated() -> None:
    root = _tmp_root()
    _legacy_project(root)
    note = migrate_legacy_queue(root)
    assert note, "应该给出迁移说明"
    paths = queue_paths(root, "default")
    assert paths.config.exists(), "队列定义应搬到 queue/default/queue.yaml"
    defs = load_queue_defs(paths)
    assert len(defs) == 1 and defs[0]["id"] == "t1"
    # 配置已迁入 .overnight-runner/，queue: 段被清空
    cfg_path = root / ".overnight-runner" / "overnight-runner.yaml"
    assert cfg_path.exists(), "overnight-runner.yaml 应迁入 .overnight-runner/"
    assert not (root / "overnight-runner.yaml").exists(), "根目录旧配置应被移走"
    data = yaml_lite.loads(cfg_path.read_text(encoding="utf-8"))
    assert not data.get("queue"), "配置的 queue 段应被清空"
    # runner 段还在
    assert data["runner"]["agent"]["command"] == "opencode"


def test_legacy_migration_is_idempotent() -> None:
    root = _tmp_root()
    _legacy_project(root)
    migrate_legacy_queue(root)
    paths = queue_paths(root, "default")
    paths.config.write_text(
        yaml_lite.dumps({"queue": [{"id": "new", "plan": "docs/plans/p2.md"}]}),
        encoding="utf-8",
    )
    migrate_legacy_queue(root)
    migrate_legacy_queue(root)
    defs = load_queue_defs(paths)
    assert len(defs) == 1 and defs[0]["id"] == "new", "重复迁移不能覆盖已有队列"


def test_legacy_state_and_decisions_migrated() -> None:
    root = _tmp_root()
    _legacy_project(root)
    legacy = root / ".overnight-runner"
    (legacy / "state.json").write_text(
        json.dumps(
            {
                "updated_at": "2026-11-06T00:00:00+08:00",
                "tasks": [
                    {"id": "t1", "status": "success", "attempts": 1},
                ],
            }
        ),
        encoding="utf-8",
    )
    (legacy / "decisions.jsonl").write_text(
        json.dumps({"task_id": "t1", "question": "q", "answer": "a"}) + "\n",
        encoding="utf-8",
    )
    migrate_legacy_queue(root)
    paths = queue_paths(root, "default")
    assert paths.state.exists(), "state.json 应搬到队列目录"
    assert not (legacy / "state.json").exists(), "旧文件应被移走而不是复制"
    assert paths.decisions.exists()
    q = load_queue(paths, load_queue_defs(paths))
    assert q.get("t1") is not None and q.get("t1").status == SUCCESS


def test_migration_preserves_comments() -> None:
    """迁移不能把用户写在配置里的注释弄丢。"""
    root = _tmp_root()
    (root / ".overnight-runner").mkdir(parents=True, exist_ok=True)
    (root / "overnight-runner.yaml").write_text(
        "# 头部注释\n"
        "runner:\n"
        "  agent:\n"
        "    command: opencode   # 保留我\n"
        "queue:\n"
        "  - id: t1\n"
        "    plan: docs/plans/p1.md\n"
        "\n"
        "# 末尾的注释也要留\n",
        encoding="utf-8",
    )
    migrate_legacy_queue(root)
    text = (root / ".overnight-runner" / "overnight-runner.yaml").read_text(encoding="utf-8")
    assert "# 头部注释" in text, text
    assert "# 保留我" in text, text
    assert "# 末尾的注释也要留" in text, text
    assert "queue:" not in text, text
    # runner 段还在
    assert yaml_lite.loads(text)["runner"]["agent"]["command"] == "opencode"


def test_strip_queue_section_variants() -> None:
    from overnight_runner.config import strip_queue_section

    # 块序列在中间
    text = "a: 1\nqueue:\n  - id: x\nb: 2\n"
    out = strip_queue_section(text)
    assert "queue" not in out and "a: 1" in out and "b: 2" in out, out
    # 内联写法
    out2 = strip_queue_section("a: 1\nqueue: []\nb: 2\n")
    assert "queue: []" in out2 and "a: 1" in out2, out2
    # 没有 queue 段 —— 原样返回
    out3 = strip_queue_section("a: 1\n# 注释\n")
    assert out3 == "a: 1\n# 注释\n", out3


def test_migration_on_fresh_project() -> None:
    root = _tmp_root()
    assert migrate_legacy_queue(root) == ""
    paths = queue_paths(root, "default")
    assert load_queue_defs(paths) == []


def test_queues_are_isolated() -> None:
    root = _tmp_root()
    a = queue_paths(root, "a")
    b = queue_paths(root, "b")
    for p in (a, b):
        p.dir.mkdir(parents=True, exist_ok=True)
    qa = load_queue(a, load_queue_defs(a))
    qb = load_queue(b, load_queue_defs(b))
    qa.add(build_task(root, "docs/plans/a.md"))
    qb.add(build_task(root, "docs/plans/b.md"))
    save_queue_defs(a, qa)
    save_queue_defs(b, qb)
    assert len(load_queue_defs(a)) == 1
    assert len(load_queue_defs(b)) == 1
    assert load_queue_defs(a)[0]["plan"] == "docs/plans/a.md"
    assert load_queue_defs(b)[0]["plan"] == "docs/plans/b.md"
    assert queue_names(root) == ["a", "b"]
    # 状态也隔离
    save_state(a, qa)
    assert a.state.exists() and not b.state.exists()


# ── 决策 ────────────────────────────────────────────────────────────
def test_should_ask_unattended() -> None:
    assert should_ask(DECISION_MODE_UNATTENDED) is False


def test_should_ask_attended() -> None:
    assert should_ask(DECISION_MODE_ATTENDED) is True


def test_mode_override_from_cli() -> None:
    cfg = RunnerConfig()
    cfg.decision.mode = DECISION_MODE_ATTENDED
    assert resolve_decision_mode(cfg, None, False) == DECISION_MODE_ATTENDED
    assert resolve_decision_mode(cfg, DECISION_MODE_UNATTENDED, False) == (
        DECISION_MODE_UNATTENDED
    )


def test_headless_forces_unattended() -> None:
    cfg = RunnerConfig()
    cfg.decision.mode = DECISION_MODE_ATTENDED
    assert resolve_decision_mode(cfg, None, True) == DECISION_MODE_UNATTENDED
    assert resolve_decision_mode(cfg, DECISION_MODE_ATTENDED, True) == (
        DECISION_MODE_UNATTENDED
    )


def test_decision_config_defaults() -> None:
    cfg = DecisionConfig()
    assert cfg.mode == DECISION_MODE_ATTENDED
    assert cfg.timeout_sec == 600
    assert cfg.resume == "session"
    assert cfg.output_format == "json"
    assert cfg.session_args == ["--session", "{session}"]
    # 从配置文件读也是同一套默认值
    parsed = DecisionConfig.from_dict({})
    assert parsed.mode == DECISION_MODE_ATTENDED and parsed.timeout_sec == 600


def test_session_id_from_json_event() -> None:
    line = json.dumps(
        {
            "type": "text",
            "sessionID": "ses_abc123",
            "part": {"type": "text", "text": "QUESTION: 要改吗？"},
        }
    )
    lines, sid = parse_agent_output(line, "json")
    assert sid == "ses_abc123"
    assert lines == ["QUESTION: 要改吗？"]


def test_session_id_from_text_fallback() -> None:
    pattern = r'"sessionID"\s*:\s*"(ses_[A-Za-z0-9]+)"'
    line = '{"sessionID":"ses_xyz789"}'
    assert extract_session_id(line, pattern) == "ses_xyz789"
    assert extract_session_id("没有 session 的行", pattern) == ""
    assert extract_session_id("x", "") == ""


def test_session_args_placeholder() -> None:
    cfg = DecisionConfig()
    assert cfg.session_command("ses_1") == ["--session", "ses_1"]
    cfg2 = DecisionConfig(session_args=["-s", "{session}", "--x"])
    assert cfg2.session_command("ses_2") == ["-s", "ses_2", "--x"]


def test_resolve_answer_fallback() -> None:
    pcfg = ProjectConfig(on_unknown_decision="跳过并记录")
    answer, rule_id = resolve_answer(pcfg, "完全没听过的问题")
    assert answer == "跳过并记录"
    assert rule_id == ""


def test_resolve_answer_rule() -> None:
    pcfg = ProjectConfig(
        on_unknown_decision="跳过并记录",
        decisions=[
            DecisionRule(id="db", match="数据库迁移", answer="先写回滚脚本")
        ],
    )
    answer, rule_id = resolve_answer(pcfg, "要不要执行数据库迁移脚本？")
    assert answer == "先写回滚脚本"
    assert rule_id == "db"


def test_decision_record_has_new_fields() -> None:
    from overnight_runner.decisions import DecisionEvent

    rec = DecisionEvent(
        task_id="t1",
        question="q",
        answer="a",
        source="human",
        waited_sec=12.34,
        session_id="ses_1",
    ).to_record()
    assert rec["source"] == "human"
    assert rec["waited_sec"] == 12.3
    assert rec["session_id"] == "ses_1"


# ── 队列锁 ──────────────────────────────────────────────────────────
def test_lock_rejects_live_pid() -> None:
    root = _tmp_root()
    lock = QueueLock(root / ".lock")
    ok, err = lock.acquire()
    assert ok, err
    # 另一个锁指向自己（活着的 pid）
    other = QueueLock(root / ".lock")
    ok2, err2 = other.acquire()
    assert not ok2 and "占用" in err2
    lock.release()
    # 释放后能再拿
    ok3, _ = other.acquire()
    assert ok3
    other.release()


def test_lock_cleans_stale() -> None:
    root = _tmp_root()
    path = root / ".lock"
    path.write_text(json.dumps({"pid": 999999999, "heartbeat": 0}), encoding="utf-8")
    lock = QueueLock(path)
    ok, err = lock.acquire()
    assert ok, f"stale 锁应被清理: {err}"
    assert json.loads(path.read_text(encoding="utf-8"))["pid"] == os.getpid()
    lock.release()


# ── 既有缺陷 B2 / B3 ────────────────────────────────────────────────
def test_task_id_has_no_double_date() -> None:
    root = _tmp_root()
    t = build_task(root, "docs/plans/20261106-fix-something.md")
    assert t.id == "20261106-fix-something", t.id
    assert not t.id.startswith("20261106-20261106"), t.id
    # 冲突时加序号
    t2 = build_task(root, "docs/plans/20261106-fix-something.md", existing_ids={t.id})
    assert t2.id == "20261106-fix-something-2"


def test_running_task_duration_does_not_crash() -> None:
    """任务在跑（没有 finished_at）时算耗时不许炸。

    这是个既有缺陷：`duration_sec` 用了 `now()` 但没 import，
    只要队列里有"running"状态的任务，`list` 就会崩。
    """
    root = _tmp_root()
    paths = queue_paths(root, "default")
    paths.dir.mkdir(parents=True, exist_ok=True)
    q = load_queue(paths, [{"id": "t1", "plan": "docs/plans/p1.md"}])
    task = q.get("t1")
    task.started_at = datetime(2026, 11, 6, 10, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    task.finished_at = None
    assert task.duration_sec is not None and task.duration_sec >= 0
    # 状态文件里写了不带时区的时间，也不许炸
    task.started_at = datetime(2026, 11, 6, 10, 0, 0)
    assert task.duration_sec is not None


# ── 按键读取（UTF-8 多字节）──────────────────────────────────────────
def _keys_from_bytes(data: bytes) -> list[str]:
    """把字节喂进管道当按键，按读出来的顺序返回按键序列。"""
    from overnight_runner.keys import PosixKeyReader

    r, w = os.pipe()
    os.write(w, data)
    os.close(w)
    reader = PosixKeyReader()
    out: list[str] = []
    while True:
        key = reader.read_key(r)
        if key == "":
            break
        out.append(key)
    os.close(r)
    return out


def test_key_reader_decodes_chinese() -> None:
    """中文必须原样读出来。

    这是个既有缺陷：老实现一次只读 1 字节再解码，
    一个汉字的 3 个字节被拆成 3 次读、每次都失败 → 中文全变问号。
    """
    keys = _keys_from_bytes("先修 Bug\n".encode("utf-8"))
    assert keys == ["先", "修", " ", "B", "u", "g", "enter"], keys


def test_key_reader_reassembles_split_utf8() -> None:
    """一个汉字被拆到两次读里，也必须还原成完整的字。"""
    import threading
    import time

    from overnight_runner.keys import PosixKeyReader

    r, w = os.pipe()
    raw = "中".encode("utf-8")

    def writer() -> None:
        os.write(w, raw[:1])
        time.sleep(0.3)
        os.write(w, raw[1:])
        os.close(w)

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    reader = PosixKeyReader()
    key = reader.read_key(r)
    t.join(timeout=3)
    os.close(r)
    assert key == "中", repr(key)


def test_key_reader_handles_escape_sequences() -> None:
    keys = _keys_from_bytes(b"\x1b[A\x1b[B\x1b[C\x1b[D")
    assert keys == ["up", "down", "right", "left"], keys


def test_key_reader_single_escape() -> None:
    """单独按 ESC（后面没有序列）要认成 esc。"""
    keys = _keys_from_bytes(b"\x1b")
    assert keys == ["esc"], keys


def test_key_reader_control_keys() -> None:
    keys = _keys_from_bytes(b"\x7f\x03\t")
    assert keys == ["backspace", "ctrl-c", "tab"], keys


def test_deleting_state_does_not_requeue() -> None:
    root = _tmp_root()
    paths = queue_paths(root, "default")
    paths.dir.mkdir(parents=True, exist_ok=True)
    q = load_queue(paths, [{"id": "t1", "plan": "docs/plans/p1.md"}])
    task = q.get("t1")
    task.status = SUCCESS
    save_state(paths, q)
    assert paths.state.exists()
    assert paths.state.with_name(paths.state.name + ".bak").exists()
    # 误删 state.json —— 不该把已成功的任务重新排队
    paths.state.unlink()
    q2 = load_queue(paths, load_queue_defs(paths) or [{"id": "t1", "plan": "docs/plans/p1.md"}])
    assert q2.get("t1").status == SUCCESS, "已成功的任务不该被重新排队"


def _run_all() -> int:
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = []
    for name, fn in tests:
        try:
            fn()
            print(f"  ✔ {name}")
        except Exception as exc:  # noqa: BLE001
            failures.append((name, exc))
            print(f"  ✘ {name}: {exc}")
    print()
    print(f"{len(tests) - len(failures)}/{len(tests)} 通过")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_all())
