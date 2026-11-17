"""命令行入口。

子命令：
  init      初始化配置文件（队列 + 项目配置）
  add       往队列里追加 plan
  list      列出队列
  status    查看运行状态
  decisions 查看决策记录
  queues    列出所有队列
  run       启动（默认分屏面板；--headless 无界面）

所有子命令都支持全局参数 `--queue <name>`（默认 `default`）。
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

from . import __version__
from .config import (
    DECISION_MODE_ATTENDED,
    DECISION_MODE_UNATTENDED,
    DECISION_MODES,
    DEFAULT_AGENT_ARGS,
    DEFAULT_AGENT_COMMAND,
    DEFAULT_PROJECT_PROMPT,
    DEFAULT_QUEUE_NAME,
    ProjectConfig,
    QueuePaths,
    load_project_config,
    load_runner_config,
    migrate_legacy_queue,
    queue_config_path,
    queue_names,
    queue_paths,
    save_project_config,
    save_runner_config,
)
from .controller import RunnerController
from .decisions import DecisionLog
from .queue import (
    PENDING,
    Queue,
    build_task,
    load_queue,
    load_queue_defs,
    save_queue_defs,
    save_state,
)
from .util import QueueLock, StopFlag, fmt_duration, fmt_ts, now


def _project_root(args) -> Path:
    return Path(args.project).expanduser().resolve()


def _queue_paths(args) -> QueuePaths:
    """解析本次命令要操作的队列（顺带做老布局迁移）。"""
    root = _project_root(args)
    note = migrate_legacy_queue(root)
    if note:
        print(f"已迁移旧队列布局 → .overnight-runner/queue/{DEFAULT_QUEUE_NAME}/（{note}）")
    name = getattr(args, "queue", DEFAULT_QUEUE_NAME) or DEFAULT_QUEUE_NAME
    try:
        return queue_paths(root, name)
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(2)


def resolve_decision_mode(
    cfg, mode_override: str | None = None, headless: bool = False
) -> str:
    """决定本次运行用哪个决策模式。

    优先级：headless（强制无人值守）> 命令行 --mode > 配置文件。
    """
    if headless:
        return DECISION_MODE_UNATTENDED
    if mode_override:
        return mode_override
    return cfg.decision.mode


# ── init ────────────────────────────────────────────────────────────
def cmd_init(args) -> int:
    root = _project_root(args)
    root.mkdir(parents=True, exist_ok=True)
    paths = _queue_paths(args)

    qpath = queue_config_path(root)
    if not qpath.exists():
        cfg = load_runner_config(root)
        cfg.agent_command = args.agent or cfg.agent_command
        cfg.agent_args = list(args.agent_args) if args.agent_args else cfg.agent_args
        save_runner_config(root, cfg)
        print(f"已创建运行配置: {qpath}")
    else:
        print(f"运行配置已存在，保持不变: {qpath}")

    if not paths.config.exists():
        paths.dir.mkdir(parents=True, exist_ok=True)
        save_queue_defs(paths, Queue())
        print(f"已创建队列: {paths.name} → {paths.config}")
    else:
        print(f"队列已存在，保持不变: {paths.config}")

    ppath = root / ".overnight-runner" / "project.yaml"
    if not ppath.exists():
        pcfg = ProjectConfig(name=root.name)
        pcfg.agent_command = args.agent or DEFAULT_AGENT_COMMAND
        pcfg.agent_args = list(args.agent_args) if args.agent_args else list(DEFAULT_AGENT_ARGS)
        pcfg.default_prompt = DEFAULT_PROJECT_PROMPT
        save_project_config(root, pcfg)
        print(f"已创建项目配置: {ppath}")
    else:
        print(f"项目配置已存在，保持不变: {ppath}")

    print()
    print("下一步：")
    print(f"  1) 编辑 {paths.config} 填入 queue（plan 用相对项目根的路径）")
    print(f"  2) 编辑 {ppath} 配默认提示词与默认决策")
    print(f"  3) 运行: overnight-runner --queue {paths.name} run")
    return 0


# ── add ─────────────────────────────────────────────────────────────
def cmd_add(args) -> int:
    root = _project_root(args)
    paths = _queue_paths(args)
    cfg = load_runner_config(root)
    queue = load_queue(paths, load_queue_defs(paths))

    try:
        task = build_task(
            root,
            args.plan,
            prompt=args.prompt or "",
            role=args.role or "",
            priority=args.priority,
            existing_ids={t.id for t in queue.tasks},
        )
        queue.add(task)
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    save_queue_defs(paths, queue)
    print(f"已加入队列 [{paths.name}]: {task.id} → {task.plan}")
    return 0


# ── list ────────────────────────────────────────────────────────────
def cmd_list(args) -> int:
    root = _project_root(args)
    paths = _queue_paths(args)
    queue = load_queue(paths, load_queue_defs(paths))

    print(f"队列: {paths.name}")
    if not len(queue):
        print("队列为空。用 `overnight-runner add <plan>` 追加。")
        return 0

    print(f"{'ID':<32} {'状态':<8} {'次':<3} {'耗时':<8} PLAN")
    print("-" * 100)
    for t in queue.tasks:
        print(
            f"{t.id:<32} {t.status:<8} {t.attempts:<3} "
            f"{fmt_duration(t.duration_sec):<8} {t.plan}"
        )
    return 0


# ── status ──────────────────────────────────────────────────────────
def cmd_status(args) -> int:
    root = _project_root(args)
    paths = _queue_paths(args)
    cfg = load_runner_config(root)
    queue = load_queue(paths, load_queue_defs(paths))
    stats = queue.stats()

    print(f"项目: {root}")
    print(f"队列: {paths.name}")
    print(f"agent: {cfg.agent_command} {' '.join(cfg.agent_args)}")
    print(f"决策: {cfg.decision.mode}（{DECISION_MODE_ATTENDED}=有人值守 / "
          f"{DECISION_MODE_UNATTENDED}=无人值守）· 等待 {cfg.decision.timeout_sec}s")
    print(f"看门狗: 重试 {cfg.watchdog.max_retries} 次 · 退避 {cfg.watchdog.backoff_sec}s · "
          f"空闲超时 {cfg.watchdog.idle_timeout_sec}s · 总超时 {cfg.watchdog.total_timeout_sec}s")
    print()
    for k in ("pending", "running", "retrying", "success", "failed", "blocked", "stopped"):
        if stats.get(k):
            print(f"  {k:<10} {stats[k]}")
    print()
    for t in queue.tasks:
        if t.status in ("failed", "blocked"):
            print(f"  ✘ {t.id}: {t.last_error}")
    return 0


# ── decisions ───────────────────────────────────────────────────────
def cmd_decisions(args) -> int:
    paths = _queue_paths(args)
    log = DecisionLog(paths.decisions)
    records = log.load()

    if not records:
        print(f"队列 [{paths.name}] 还没有决策记录。")
        return 0

    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0

    print(f"队列: {paths.name}")
    print(f"{'时间':<20} {'任务':<28} {'来源':<9} 问题 → 答案")
    print("-" * 110)
    for r in records:
        print(
            f"{str(r.get('at',''))[:19]:<20} {str(r.get('task_id',''))[:27]:<28} "
            f"{str(r.get('source','')):<9} {r.get('question','')} → {r.get('answer','')}"
        )
    return 0


# ── queues ──────────────────────────────────────────────────────────
def cmd_queues(args) -> int:
    root = _project_root(args)
    note = migrate_legacy_queue(root)
    if note:
        print(f"已迁移旧队列布局 → .overnight-runner/queue/{DEFAULT_QUEUE_NAME}/（{note}）")
    names = queue_names(root)
    if not names:
        print("还没有任何队列。用 `overnight-runner init` 建一条。")
        return 0

    print(f"{'队列':<16} {'任务':<6} {'待跑':<6} {'运行':<6} {'成功':<6} {'失败':<6} 最后活动")
    print("-" * 78)
    for name in names:
        paths = queue_paths(root, name)
        queue = load_queue(paths, load_queue_defs(paths))
        stats = queue.stats()
        last = _last_activity(queue)
        print(
            f"{name:<16} {len(queue):<6} {stats.get(PENDING, 0):<6} "
            f"{stats.get('running', 0):<6} {stats.get('success', 0):<6} "
            f"{stats.get('failed', 0):<6} {last}"
        )
    return 0


def _last_activity(queue: Queue) -> str:
    times = [t.finished_at or t.started_at for t in queue.tasks]
    times = [t for t in times if t is not None]
    if not times:
        return "-"
    return fmt_ts(max(times))


# ── run ─────────────────────────────────────────────────────────────
def cmd_run(args) -> int:
    root = _project_root(args)
    paths = _queue_paths(args)
    cfg = load_runner_config(root)
    project_cfg = load_project_config(root)
    queue = load_queue(paths, load_queue_defs(paths))

    # 决策模式：命令行优先；headless 强制无人值守（没人看面板，不能卡在等决策上）
    cfg.decision.mode = resolve_decision_mode(
        cfg, getattr(args, "mode", None), args.headless
    )

    if getattr(args, "retry_failed", False):
        reset = 0
        for t in queue.tasks:
            if t.status in ("failed", "blocked", "stopped"):
                t.status = PENDING
                t.attempts = 0
                t.last_error = ""
                t.exit_code = None
                t.finished_at = None
                t.summary = ""
                reset += 1
        if reset:
            save_state(paths, queue)
            print(f"已重置 {reset} 个失败/阻塞任务。")

    lock = QueueLock(paths.lock)
    ok, err = lock.acquire()
    if not ok:
        print(f"错误: {err}（同一条队列不能同时跑两个 runner）", file=sys.stderr)
        return 2

    stop = StopFlag()
    controller = RunnerController(root, cfg, project_cfg, queue, paths, stop=stop)

    try:
        if args.headless:
            return _run_headless(controller, queue, paths, stop, args)

        try:
            from .ui import RunnerUI
        except ImportError as exc:  # pragma: no cover - 只在环境被破坏时触发
            print(f"无法启动面板: {exc}", file=sys.stderr)
            print("也可以用 --headless 无界面运行。", file=sys.stderr)
            return 2

        ui = RunnerUI(controller, queue, cfg, root, paths)

        worker = threading.Thread(target=controller.run_forever, name="runner", daemon=True)
        worker.start()
        heartbeat = threading.Thread(target=_heartbeat, args=(lock, stop), daemon=True)
        heartbeat.start()

        try:
            ui.run()
        finally:
            stop.set()
            worker.join(timeout=10)
    finally:
        lock.release()

    save_state(paths, queue)
    return 0


def _heartbeat(lock: QueueLock, stop: StopFlag) -> None:
    """定期更新锁的心跳（长跑时用来识别 stale 锁）。"""
    while not stop.is_set():
        lock.touch()
        stop.wait(timeout=15)


def _run_headless(controller, queue, paths, stop, args) -> int:
    """无界面模式：直接跑，输出到 stdout。适合 CI / 脚本。"""
    def on_event(kind: str, task) -> None:
        if task is not None:
            print(f"[{fmt_ts(now())}] {kind:<16} {task.id}  {task.plan}")
        else:
            print(f"[{fmt_ts(now())}] {kind}")

    def on_log(line: str) -> None:
        if args.verbose:
            print(f"    {line}")

    controller.on_event = on_event
    controller.on_log = on_log

    controller.run_forever()
    save_state(paths, queue)

    stats = queue.stats()
    failed = [t for t in queue.tasks if t.status in ("failed", "blocked")]
    print()
    print(controller.snapshot())
    if failed:
        print()
        print("失败任务：")
        for t in failed:
            print(f"  ✘ {t.id}: {t.last_error}")
    return 1 if failed else 0


# ── 参数解析 ────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="overnight-runner",
        description="把一串 plan 交给 coding agent 无人值守地跑",
    )
    p.add_argument("--version", action="version", version=f"overnight-runner {__version__}")
    p.add_argument("--project", default=".", help="项目根目录（默认当前目录）")
    p.add_argument(
        "--queue",
        default=DEFAULT_QUEUE_NAME,
        help=f"队列名（默认 {DEFAULT_QUEUE_NAME}）",
    )
    sub = p.add_subparsers(dest="command")

    s = sub.add_parser("init", help="初始化配置文件")
    s.add_argument("--agent", help="coding agent 命令，如 opencode / claude / codex")
    s.add_argument("--agent-args", nargs="*", help="agent 参数，默认 run")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("add", help="往队列追加 plan")
    s.add_argument("plan", help="plan 文件路径（相对项目根或绝对路径）")
    s.add_argument("--prompt", default="", help="补充要求")
    s.add_argument("--role", default="", help="角色标签 BA / DEV / QA")
    s.add_argument("--priority", type=int, default=100, help="优先级，数字小的先跑")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("list", help="列出队列")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("status", help="查看运行状态")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("decisions", help="查看决策记录")
    s.add_argument("--json", action="store_true", help="输出 JSON")
    s.set_defaults(func=cmd_decisions)

    s = sub.add_parser("queues", help="列出所有队列")
    s.set_defaults(func=cmd_queues)

    s = sub.add_parser("run", help="启动（默认分屏面板；--headless 无界面）")
    s.add_argument("--headless", action="store_true", help="无界面模式")
    s.add_argument("--verbose", action="store_true", help="headless 模式下打印 agent 输出")
    s.add_argument(
        "--retry-failed",
        action="store_true",
        help="把失败/阻塞的任务重置为待跑",
    )
    s.add_argument(
        "--mode",
        choices=list(DECISION_MODES),
        default=None,
        help=(
            f"决策模式：{DECISION_MODE_ATTENDED}=有人值守（弹窗问人，"
            f"超时自动决策）/ {DECISION_MODE_UNATTENDED}=无人值守（直接决策）"
        ),
    )
    s.set_defaults(func=cmd_run)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
