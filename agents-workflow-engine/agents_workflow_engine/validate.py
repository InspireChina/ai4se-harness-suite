"""校验解析后的图。错误阻断，模型未拉开只警告。"""

from __future__ import annotations

import os
from typing import Any

WORK_KINDS = ("action", "gate", "decision", "human_input")
ACTORS = ("human", "master", "subagent")
REVIEW_PAIRS = (
    ("ba-write-spec", "ba-requirement-review"),
    ("dev-plan", "dev-plan-review"),
)


def node_map(graph: dict) -> dict:
    return {node["id"]: node for node in graph.get("nodes") or []}


def extension_ids(graph: dict) -> set:
    found = set()
    for ext in graph.get("extensions") or []:
        for node in ext.get("nodes") or []:
            if "id" in node:
                found.add(node["id"])
    return found


def _model_value(graph: dict, node: dict) -> str:
    key = node.get("model")
    models = graph.get("models") or {}
    if not key or key not in models:
        return ""
    spec = models[key]
    if isinstance(spec, dict) and spec.get("env"):
        return os.environ.get(str(spec["env"]), "")
    return str(spec)


def validate(graph: dict) -> tuple:
    """返回 (errors, warnings)。errors 非空时图不能跑。"""
    errors = []
    warnings = []
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    ids = [node.get("id") for node in nodes]
    if len(ids) != len(set(ids)):
        errors.append("节点 id 有重复")
    by_id = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            errors.append("有节点缺少 id")
            continue
        by_id[node_id] = node
        kind = node.get("kind")
        actor = node.get("actor")
        if kind not in WORK_KINDS and kind not in ("entry", "end"):
            errors.append("节点 %s 的 kind 不合法：%s" % (node_id, kind))
        if actor not in ACTORS:
            errors.append("节点 %s 的 actor 必须是 human、master 或 subagent" % node_id)
        if node.get("skill") and actor != "subagent":
            errors.append("节点 %s 调用了 skill，actor 必须是 subagent" % node_id)
        if kind == "end" and _outgoing(edges, node_id):
            errors.append("终点 %s 不能有出边" % node_id)
        if kind == "human_input" and len(_outgoing(edges, node_id)) > 1:
            errors.append("人类输入 %s 只能有一条出边" % node_id)
        if kind == "decision":
            options = set(node.get("options") or [])
            for edge in _outgoing(edges, node_id):
                if edge.get("when") not in options:
                    errors.append("决策 %s 的出边 %s 不在选项里" % (node_id, edge.get("id")))
        if kind == "gate":
            for edge in _outgoing(edges, node_id):
                if edge.get("when") not in ("满意", "不满意"):
                    errors.append("门禁 %s 的出边 %s 只能是满意或不满意" % (node_id, edge.get("id")))

    entries = [node["id"] for node in nodes if node.get("kind") == "entry"]
    ends = [node["id"] for node in nodes if node.get("kind") == "end"]
    if entries != [graph.get("entry")]:
        errors.append("入口必须恰好是 entry 节点 %s" % graph.get("entry"))
    if len(ends) != 1:
        errors.append("必须恰好有一个终点")

    ext = extension_ids(graph)
    notes = set()
    for node in nodes:
        if node.get("sealed"):
            for item in node.get("note") or []:
                notes.add(item)
    known = set(by_id) | ext | notes
    loops = graph.get("loops") or []
    back_to_loop = {}
    for loop in loops:
        if "maxIterations" not in loop:
            errors.append("回路 %s 缺少 maxIterations" % loop.get("id"))
        for edge_id in loop.get("backEdges") or []:
            back_to_loop[edge_id] = loop

    for edge in edges:
        edge_id = edge.get("id")
        src = edge.get("from")
        dst = edge.get("to")
        if src not in by_id:
            errors.append("边 %s 的起点不存在：%s" % (edge_id, src))
        if dst in notes:
            errors.append("边 %s 指向了封死节点内部的步骤 %s，不能加边" % (edge_id, dst))
        elif dst in ext:
            errors.append("边 %s 指向了未接入的扩展节点 %s" % (edge_id, dst))
        elif dst not in by_id:
            errors.append("边 %s 的终点不存在：%s" % (edge_id, dst))
        if edge.get("back") and edge.get("when") and edge_id not in back_to_loop:
            errors.append("打回边 %s 没有写入任何回路的上限" % edge_id)
        if src in by_id and by_id[src].get("kind") in ("decision", "gate"):
            if edge.get("when") not in ("满意", "不满意"):
                errors.append("边 %s 从门禁或决策出发，when 只能是满意或不满意" % edge_id)

    batches = {node["id"] for node in nodes if node.get("batch")}
    consumed = {node.get("repeatsBatch") for node in nodes if node.get("repeatsBatch")}
    missing = batches - consumed
    if missing:
        errors.append("批量节点没有被消费：%s" % "、".join(sorted(missing)))
    for node in nodes:
        target = node.get("repeatsBatch")
        if target and target not in by_id:
            errors.append("节点 %s 要循环的批量节点不存在：%s" % (node["id"], target))

    if graph.get("entry") in by_id and not errors:
        reached = _reachable(graph["entry"], edges)
        stranded = [node_id for node_id in by_id if node_id not in reached]
        if stranded:
            errors.append("这些节点从入口走不到：%s。覆盖可能把图切断了" % "、".join(stranded))

    for writer_id, reviewer_id in REVIEW_PAIRS:
        writer = by_id.get(writer_id)
        reviewer = by_id.get(reviewer_id)
        if not writer or not reviewer:
            continue
        left = _model_value(graph, writer)
        right = _model_value(graph, reviewer)
        if not left or not right:
            warnings.append("未配置对抗模型：%s 与 %s 将沿用主会话模型" % (writer_id, reviewer_id))
        elif left == right:
            warnings.append("未做对抗验证：%s 与 %s 使用了同一个模型" % (writer_id, reviewer_id))
    return errors, warnings


def _outgoing(edges: list, node_id: str) -> list:
    return [edge for edge in edges if edge.get("from") == node_id]


def _reachable(entry: str, edges: list) -> set:
    seen = set()
    stack = [entry]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for edge in edges:
            if edge.get("from") == current:
                stack.append(edge.get("to"))
    return seen


def _model_value(graph: dict, node: dict) -> str:
    key = node.get("model")
    models = graph.get("models") or {}
    if not key or key not in models:
        return ""
    spec: Any = models[key]
    if isinstance(spec, dict) and spec.get("env"):
        return os.environ.get(str(spec["env"]), "")
    return str(spec)
