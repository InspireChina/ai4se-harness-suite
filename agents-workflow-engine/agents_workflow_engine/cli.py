"""命令行：validate / resolve / render / run。"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .errors import GraphError
from .load import load_overlay
from .load import load_preset
from .load import load_yaml
from .merge import merge
from .prompts import build_prompt
from .version import __version__
from .render_mermaid import render
from .runner import Runner
from .runner import spawn_agent
from .validate import validate
from .yaml_lite import loads


def _graph_from(args: argparse.Namespace) -> dict:
    base = load_yaml(args.graph) if args.graph else load_preset()
    overlay = load_overlay(args.project)
    return merge(base, overlay)


def _print_warnings(warnings: list) -> None:
    for warning in warnings:
        print(warning, file=sys.stderr)


def cmd_validate(args: argparse.Namespace) -> int:
    graph = _graph_from(args)
    errors, warnings = validate(graph)
    _print_warnings(warnings)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("图有效：%s 个节点，%s 个警告" % (len(graph["nodes"]), len(warnings)))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    graph = _graph_from(args)
    errors, warnings = validate(graph)
    _print_warnings(warnings)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(json.dumps(graph, ensure_ascii=False, indent=2))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    graph = _graph_from(args)
    errors, warnings = validate(graph)
    _print_warnings(warnings)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    text = render(graph)
    if args.dry_run or not args.output:
        sys.stdout.write(text)
        return 0
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("已写入 %s" % args.output)
    return 0


def _load_answers(path: str) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = loads(handle.read())
    if not isinstance(data, dict):
        raise GraphError("answers 文件的根必须是映射")
    answers = {}
    for key, value in data.items():
        if isinstance(value, list):
            answers[key] = [str(item) for item in value]
        else:
            answers[key] = [str(value)]
    return answers


MODE_SESSION = "session-subagent"
MODE_SOLO = "session-solo"
MODE_STANDALONE = "standalone"

MODE_TITLES = {
    MODE_SESSION: "会话内 · 开子 agent",
    MODE_SOLO: "会话内 · 只用主会话",
    MODE_STANDALONE: "独立 agent",
}


def _pick_mode(args: argparse.Namespace) -> str:
    """三种执行方式：会话内开子 agent / 会话内只用主会话 / 拉独立 agent。

    默认第一种：能开子 agent 就不拉进程，省一层进程边界。
    """
    chosen = []
    if args.agent:
        chosen.append(("--agent", MODE_STANDALONE))
    if args.manual:
        chosen.append(("--manual", MODE_SESSION))
    if args.solo:
        chosen.append(("--solo", MODE_SOLO))
    if len(chosen) > 1:
        raise GraphError("执行方式只能选一个：%s" % " / ".join(item[0] for item in chosen))
    if chosen:
        return chosen[0][1]

    if not sys.stdin.isatty():
        print("没给 --agent / --manual / --solo，当前也不是交互终端：按「会话内开子 agent」走，输出执行清单。",
              file=sys.stderr)
        return MODE_SESSION

    print("这个会话怎么执行？")
    print("  1) 支持子 agent：我在会话里开子 agent 做（默认）")
    print("  2) 不支持：主会话自己按 skill 做")
    print("  3) 不支持：拉起独立 agent 做（要配合 --agent 给命令）")
    try:
        answer = input("选择 [1/2/3]：").strip()
    except EOFError:
        return MODE_SESSION
    if answer.startswith("3"):
        return MODE_STANDALONE
    if answer.startswith("2"):
        return MODE_SOLO
    return MODE_SESSION


def _manual_result(node: dict) -> str:
    """会话内模式：没人真干活，只给下游一个能继续走的占位结果。"""
    if node.get("kind") == "gate":
        return "满意\n"
    if node.get("batch"):
        return "TASK: 按上一节点的清单，逐个任务执行\n"
    return "（清单模式：不执行，交回当前会话按提示词完成）\n"


def _render_manual(graph: dict, collected: list, mode: str) -> str:
    allow_subagent = mode == MODE_SESSION
    lines = ["# 执行清单 · %s" % graph.get("id", "workflow"), ""]
    lines.append(
        "> 引擎 %s · 执行方式：%s。引擎没拉起任何进程，下面按执行顺序列给**当前会话**。"
        % (__version__, MODE_TITLES[mode])
    )
    if allow_subagent:
        lines.append("> 每条里能开子 agent 就开一个去做，开不了就自己按 skill 干；门禁按「假定通过」往下走。")
    else:
        lines.append("> 每条都由你（主会话）自己按 skill 做完，不开子 agent；门禁按「假定通过」往下走。")
    lines.append("")
    for index, (node, model, task) in enumerate(collected, 1):
        lines.append("## %s. %s" % (index, node.get("title") or node["id"]))
        lines.append("")
        lines.append("```")
        lines.append(build_prompt(node, model, task, manual=True, allow_subagent=allow_subagent))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def cmd_run(args: argparse.Namespace) -> int:
    graph = _graph_from(args)
    errors, warnings = validate(graph)
    _print_warnings(warnings)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    answers = _load_answers(args.answers) if args.answers else {}
    mode = _pick_mode(args)
    if mode == MODE_STANDALONE and not args.agent.strip():
        raise GraphError(
            "独立 agent 得靠 --agent 启动，例如 --agent 'qoder -p'；"
            "不想拉进程就用 --manual（会话内开子 agent）或 --solo（只用主会话）"
        )
    standalone = mode == MODE_STANDALONE
    log = []  # type: list
    collected = []  # type: list

    if standalone:
        def agent(node, model, task):
            return spawn_agent(args.agent, node, model, task, args.project)
    else:
        def agent(node, model, task):
            collected.append((node, model, task))
            return _manual_result(node)

    runner = Runner(graph, answers, agent, args.master_model, log)
    end = runner.run()
    out_dir = os.path.join(args.project, ".agents", "workflow")
    os.makedirs(out_dir, exist_ok=True)
    if not standalone:
        path = os.path.join(out_dir, "prompts.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(_render_manual(graph, collected, mode))
        print("%s：执行清单（%s 条）写在 %s，终点 %s" % (MODE_TITLES[mode], len(collected), path, end))
        return 0
    path = os.path.join(out_dir, "decisions.jsonl")
    with open(path, "a", encoding="utf-8") as handle:
        for item in log:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("到达 %s，记录写在 %s" % (end, path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agents_workflow_engine", description="按项目的工作流图调度子 agent")
    parser.add_argument("--version", action="version", version="agents-workflow-engine %s" % __version__)
    parser.add_argument("--project", default=".", help="目标项目目录，默认当前目录")
    parser.add_argument("--graph", default="", help="图 YAML。缺省用套件预设")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate", help="校验预设叠覆盖之后的图")
    validate_cmd.set_defaults(func=cmd_validate)

    resolve_cmd = sub.add_parser("resolve", help="打印合并后的图")
    resolve_cmd.set_defaults(func=cmd_resolve)

    render_cmd = sub.add_parser("render", help="把图渲成 Mermaid")
    render_cmd.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    render_cmd.add_argument("--output", default="", help="写入的文件。缺省打印到标准输出")
    render_cmd.set_defaults(func=cmd_render)

    run_cmd = sub.add_parser("run", help="主会话按图执行到可上线")
    run_cmd.add_argument("--answers", default="", help="人的答案 YAML")
    run_cmd.add_argument("--agent", default="", help="独立 agent 命令，例如 'qoder -p'；提示词会追加在末尾")
    run_cmd.add_argument("--manual", action="store_true", help="会话内开子 agent：只写提示词清单（默认）")
    run_cmd.add_argument("--solo", action="store_true", help="会话内只用主会话：自己按 skill 做，不开子 agent")
    run_cmd.add_argument("--master-model", default=os.environ.get("MODEL_MASTER", "master"), help="主会话模型，图里两个模型都没配时沿用")
    run_cmd.set_defaults(func=cmd_run)
    return parser


def main(argv: list = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GraphError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
