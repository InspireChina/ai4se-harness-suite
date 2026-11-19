"""把解析后的图写成 Mermaid。扩展节点不输出。"""

from __future__ import annotations


def _shape(node: dict) -> str:
    title = node.get("title") or node["id"]
    if node.get("batch"):
        title += " · 一批任务"
    if node.get("repeatsBatch"):
        title += " · 按批循环"
    if node.get("join"):
        title += " · 汇入"
    if node.get("kind") == "milestone":
        title += " · 里程碑"
    if node.get("note"):
        title += " / " + "、".join(node["note"])
    node_id = node["id"]
    kind = node.get("kind")
    if kind == "action":
        return "%s(%s)" % (node_id, title)
    if kind == "gate":
        return "%s[[%s]]" % (node_id, title)
    if kind == "decision":
        return "%s{%s}" % (node_id, title)
    if kind == "human_input":
        return "%s[/%s/]" % (node_id, title)
    if kind in ("end", "milestone"):
        return "%s([%s])" % (node_id, title)
    if kind == "entry":
        return "%s{{%s}}" % (node_id, title)
    return "%s[%s]" % (node_id, title)


def render(graph: dict) -> str:
    lines = ["flowchart LR"]
    titles = (("human", "人"), ("master", "graph-master"), ("subagent", "子 agent"))
    for actor, title in titles:
        lines.append("  subgraph %s [%s]" % (actor, title))
        for node in graph.get("nodes") or []:
            if node.get("actor") == actor:
                lines.append("    " + _shape(node))
        lines.append("  end")
    for edge in graph.get("edges") or []:
        arrow = "-.->" if edge.get("back") else "-->"
        label_text = edge.get("when") or ""
        if edge.get("parallel"):
            label_text = (label_text + " · 并行").strip(" ·")
        label = "|%s|" % label_text if label_text else ""
        lines.append("  %s %s%s %s" % (edge["from"], arrow, label, edge["to"]))
    return "\n".join(lines) + "\n"
