"""两个模型：执行者管 action，门禁管 gate。配在图里，可被环境变量覆盖。"""

from __future__ import annotations

import os
from typing import Tuple

ROLES = ("executor", "gate")


def role_of(node: dict) -> str:
    """门禁节点用门禁模型，其余用执行者模型。节点写了角色名时以它为准。"""
    key = node.get("model")
    if key in ROLES:
        return str(key)
    return "gate" if node.get("kind") == "gate" else "executor"


def model_of(graph: dict, role: str) -> str:
    """取角色模型：环境变量有值优先，其次图里写的 model。"""
    spec = (graph.get("models") or {}).get(role)
    if isinstance(spec, dict):
        env = spec.get("env")
        if env and os.environ.get(str(env)):
            return str(os.environ[str(env)])
        return str(spec.get("model") or "")
    if isinstance(spec, str):
        return spec
    return ""


def resolve(graph: dict, node: dict, master: str) -> Tuple[str, str]:
    """返回 (角色, 模型)。节点里写了具体模型名时直接用它。"""
    literal = node.get("model")
    role = role_of(node)
    if literal and literal not in ROLES:
        return role, str(literal)
    return role, model_of(graph, role) or master