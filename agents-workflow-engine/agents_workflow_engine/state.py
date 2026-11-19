"""一个迭代一条 workflow，进度落在 state.json。"""

from __future__ import annotations

import json
import os
import re

from .errors import GraphError

_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def check_iteration(name: str) -> str:
    if not name or not _NAME.match(name):
        raise GraphError("迭代名不合法：%s。只用字母、数字、点、下划线和连字符" % name)
    return name


def instance_dir(project: str, iteration: str) -> str:
    return os.path.join(project, ".agents", "workflow", "iterations", check_iteration(iteration))


def state_path(project: str, iteration: str) -> str:
    return os.path.join(instance_dir(project, iteration), "state.json")


def decisions_path(project: str, iteration: str) -> str:
    return os.path.join(instance_dir(project, iteration), "decisions.jsonl")


def load_state(project: str, iteration: str) -> dict:
    path = state_path(project, iteration)
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise GraphError("进度文件损坏：%s" % path)
    return data


def save_state(project: str, iteration: str, state: dict) -> str:
    path = state_path(project, iteration)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)
    logged = int(state.get("logged") or 0)
    progress = state.get("progress") or []
    fresh = progress[logged:]
    if fresh:
        with open(decisions_path(project, iteration), "a", encoding="utf-8") as handle:
            for item in fresh:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        state["logged"] = len(progress)
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    return path


def list_states(project: str) -> list:
    root = os.path.join(project, ".agents", "workflow", "iterations")
    if not os.path.isdir(root):
        return []
    found = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name, "state.json")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as handle:
                found.append(json.load(handle))
    return found


def open_instance(project: str, iteration: str, entry: str) -> dict:
    """没有记录就创建。已有记录就返回它，用来接着跑。已到测试通过则拒绝再开一条。"""
    check_iteration(iteration)
    existing = load_state(project, iteration)
    if not existing:
        state = {
            "iteration": iteration,
            "status": "running",
            "current": entry,
            "visits": {},
            "loopCounts": {},
            "tasks": [],
            "taskIndex": 0,
            "progress": [],
            "logged": 0,
        }
        save_state(project, iteration, state)
        return state
    if existing.get("status") == "completed":
        raise GraphError(
            "迭代 %s 已经有一条 workflow，并且已经到测试通过。不能再创建一条。用 status --iteration %s 查看"
            % (iteration, iteration)
        )
    return existing
