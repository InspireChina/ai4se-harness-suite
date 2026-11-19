"""把项目覆盖叠到预设图上。"""

from __future__ import annotations

import copy
from typing import Optional

from .errors import GraphError


def merge(base: dict, overlay: Optional[dict]) -> dict:
    graph = copy.deepcopy(base)
    if not overlay:
        return graph
    disabled = set(overlay.get("disable") or [])
    unknown = disabled - {node["id"] for node in graph.get("nodes") or []}
    if unknown:
        raise GraphError("覆盖要禁用的节点不存在：%s" % "、".join(sorted(unknown)))
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] not in disabled]
    graph["edges"] = [
        edge for edge in graph.get("edges") or []
        if edge.get("from") not in disabled and edge.get("to") not in disabled
    ]
    by_id = {node["id"]: node for node in graph["nodes"]}
    for node_id, fields in (overlay.get("replace") or {}).items():
        if node_id not in by_id:
            raise GraphError("覆盖要替换的节点不存在：%s" % node_id)
        if not isinstance(fields, dict):
            raise GraphError("节点 %s 的替换内容必须是映射" % node_id)
        by_id[node_id].update(fields)
    loops_by_id = {loop["id"]: loop for loop in graph.get("loops") or []}
    for loop in overlay.get("loops") or []:
        if loop.get("id") not in loops_by_id:
            raise GraphError("覆盖要改的回路不存在：%s" % loop.get("id"))
        loops_by_id[loop["id"]].update(loop)
    edges_by_id = {edge["id"]: edge for edge in graph["edges"]}
    for edge in overlay.get("edges") or []:
        if "id" not in edge:
            raise GraphError("覆盖里的边必须有 id")
        if edge["id"] in edges_by_id:
            edges_by_id[edge["id"]].update(edge)
        else:
            graph["edges"].append(edge)
            edges_by_id[edge["id"]] = edge
    return graph
