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


def cmd_run(args: argparse.Namespace) -> int:
    graph = _graph_from(args)
    errors, warnings = validate(graph)
    _print_warnings(warnings)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    answers = _load_answers(args.answers) if args.answers else {}
    log = []  # type: list

    def agent(node, model, task):
        return spawn_agent(args.agent, node, model, task)

    runner = Runner(graph, answers, agent, args.master_model, log)
    end = runner.run()
    out_dir = os.path.join(args.project, ".agents", "workflow")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "decisions.jsonl")
    with open(path, "a", encoding="utf-8") as handle:
        for item in log:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("到达 %s，记录写在 %s" % (end, path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agents_workflow_engine", description="按项目的工作流图调度子 agent")
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

    run_cmd = sub.add_parser("run", help="主会话按图执行到测试通过")
    run_cmd.add_argument("--answers", default="", help="人的答案 YAML")
    run_cmd.add_argument("--agent", default="", help="子 agent 命令")
    run_cmd.add_argument("--master-model", default=os.environ.get("MODEL_MASTER", "master"), help="主会话模型，子 agent 未配置时沿用")
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


if __name__ == "__main__":
    raise SystemExit(main())
