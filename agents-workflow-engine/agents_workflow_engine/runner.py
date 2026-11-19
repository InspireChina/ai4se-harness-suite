"""按图往下走：人答题，子 agent 执行 skill，主会话只调度。"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from .errors import GraphError
from .errors import NeedInput
from .validate import REVIEW_PAIRS
from .validate import node_map


def _plain_edges(edges: List[dict], node_id: str) -> List[dict]:
    outgoing = [
        edge for edge in edges
        if edge.get("from") == node_id and not edge.get("when")
    ]
    drop = set()
    for edge in outgoing:
        others = [item["to"] for item in outgoing if item is not edge]
        for other in others:
            if _can_reach(other, edge["to"], edges):
                drop.add(edge["id"])
    return [edge for edge in outgoing if edge["id"] not in drop]


def _can_reach(start: str, target: str, edges: List[dict]) -> bool:
    seen = set()
    stack = [start]
    while stack:
        current = stack.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        for edge in edges:
            if edge.get("from") != current or edge.get("back") or edge.get("when"):
                continue
            stack.append(edge["to"])
    return False


def _when_edge(edges: List[dict], node_id: str, answer: str) -> dict:
    for edge in edges:
        if edge.get("from") == node_id and edge.get("when") == answer:
            return edge
    raise GraphError("节点 %s 没有「%s」这条出边" % (node_id, answer))


def _loop_for(graph: dict, edge_id: str) -> Optional[dict]:
    for loop in graph.get("loops") or []:
        if edge_id in (loop.get("backEdges") or []):
            return loop
    return None


def _take_answer(answers: Dict[str, List[str]], node_id: str) -> str:
    queue = answers.get(node_id) or []
    if not queue:
        raise NeedInput(
            "节点 %s 需要人的输入。进度已记下。补上 answers 后用同一个 --iteration 再执行 run"
            % node_id
        )
    return str(queue.pop(0))


def _resolve_model(graph: dict, node: dict, master_model: str) -> str:
    key = node.get("model")
    models = graph.get("models") or {}
    if not key or key not in models:
        return master_model
    spec = models[key]
    if isinstance(spec, dict) and spec.get("env"):
        return os.environ.get(str(spec["env"]), "") or master_model
    return str(spec) or master_model


def _verdict(text: str) -> str:
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line in ("满意", "不满意"):
            return line
    if "不满意" in text:
        return "不满意"
    if "满意" in text:
        return "满意"
    raise GraphError("子 agent 没有给出「满意」或「不满意」。输出是：%s" % text.strip()[:200])


def _tasks(text: str) -> List[str]:
    found = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("TASK:"):
            task = line[5:].strip()
            if task:
                found.append(task)
    return found or ["task-1"]


class Runner:
    def __init__(self, graph: dict, answers: Dict[str, List[str]], agent: Callable, master_model: str, log: List[dict], current: str = "", visits: Dict[str, int] = None, loop_counts: Dict[str, int] = None, tasks: List[str] = None, task_index: int = 0) -> None:
        self.graph = graph
        self.answers = answers
        self.agent = agent
        self.master_model = master_model
        self.log = log
        self.nodes = node_map(graph)
        self.edges = graph.get("edges") or []
        self.current = current or graph["entry"]
        self.visits = visits or {}
        self.loop_counts = loop_counts or {}
        self.tasks = list(tasks or [])
        self.task_index = task_index

    def run(self) -> str:
        current = self.current
        guard = 0
        while guard < 500:
            guard += 1
            self.current = current
            node = self.nodes[current]
            kind = node.get("kind")
            if kind == "end":
                self.log.append({"node": current, "event": "end", "title": node.get("title")})
                return current
            if kind == "entry":
                current = self._only(current)
                continue
            if kind == "human_input":
                text = _take_answer(self.answers, current)
                self.log.append({"node": current, "event": "human_input", "text": text})
                current = self._only(current)
                continue
            if kind == "decision":
                choice = _take_answer(self.answers, current)
                self.log.append({"node": current, "event": "decision", "choice": choice})
                current = self._follow_when(current, choice)
                continue
            if kind == "gate":
                self._warn_pair(node)
                result = self._call(node, None)
                verdict = _verdict(result)
                self.log.append({"node": current, "event": "gate", "verdict": verdict, "model": _resolve_model(self.graph, node, self.master_model)})
                current = self._follow_when(current, verdict)
                continue
            if kind == "action":
                current = self._run_action(node)
                continue
            raise GraphError("节点 %s 的 kind 无法执行：%s" % (current, kind))
        raise GraphError("走了 500 步还没到终点，图里可能有死循环")

    def _run_action(self, node: dict) -> str:
        node_id = node["id"]
        if node.get("once") and self.visits.get(node_id):
            return self._only(node_id)
        if node.get("repeatsBatch"):
            if self.task_index >= len(self.tasks):
                return self._only(node_id)
            task = self.tasks[self.task_index]
            result = self._call(node, task)
            self.visits[node_id] = self.visits.get(node_id, 0) + 1
            self.task_index += 1
            self.log.append({"node": node_id, "event": "batch-step", "task": task, "output": result})
            if self.task_index < len(self.tasks):
                return node_id
            return self._only(node_id)
        result = self._call(node, None)
        self.visits[node_id] = self.visits.get(node_id, 0) + 1
        self.log.append({"node": node_id, "event": "action", "output": result, "model": _resolve_model(self.graph, node, self.master_model)})
        if node.get("batch"):
            self.tasks = _tasks(result)
            self.task_index = 0
            self.log.append({"node": node_id, "event": "batch", "tasks": list(self.tasks)})
        return self._only(node_id)

    def _call(self, node: dict, task: Optional[str]) -> str:
        model = _resolve_model(self.graph, node, self.master_model)
        return self.agent(node, model, task)

    def _warn_pair(self, reviewer: dict) -> None:
        for writer_id, reviewer_id in REVIEW_PAIRS:
            if reviewer["id"] != reviewer_id:
                continue
            writer = self.nodes.get(writer_id)
            if not writer:
                return
            left = _resolve_model(self.graph, writer, self.master_model)
            right = _resolve_model(self.graph, reviewer, self.master_model)
            if not left or not right or left == right:
                self.log.append({
                    "node": reviewer["id"],
                    "event": "model-check",
                    "warning": "未做对抗验证",
                    "writer": writer_id,
                    "writerModel": left,
                    "reviewerModel": right,
                })

    def _follow_when(self, node_id: str, answer: str) -> str:
        edge = _when_edge(self.edges, node_id, answer)
        if edge.get("back"):
            loop = _loop_for(self.graph, edge["id"])
            if loop is None:
                raise GraphError("打回边 %s 没有上限" % edge["id"])
            count = self.loop_counts.get(loop["id"], 0) + 1
            self.loop_counts[loop["id"]] = count
            if count > int(loop["maxIterations"]):
                raise GraphError(
                    "回路 %s 已打回 %s 次，达到上限 %s。请人工处理节点 %s 后再继续"
                    % (loop["id"], count - 1, loop["maxIterations"], node_id)
                )
        return edge["to"]

    def _only(self, node_id: str) -> str:
        chosen = _plain_edges(self.edges, node_id)
        if len(chosen) != 1:
            raise GraphError("节点 %s 有 %s 条向前的边，调度不知道走哪条" % (node_id, len(chosen)))
        return chosen[0]["to"]


def spawn_agent(command: str, node: dict, model: str, task: Optional[str]) -> str:
    if not command.strip():
        raise GraphError("没有配置子 agent 命令。run 时加上 --agent，例如 --agent 'opencode run'")
    env = os.environ.copy()
    env["WORKFLOW_SKILL"] = str(node.get("skill") or "")
    env["WORKFLOW_NODE"] = node["id"]
    env["WORKFLOW_MODEL"] = model
    env["WORKFLOW_TASK"] = task or ""
    argv = shlex.split(command) + ["--skill", str(node.get("skill") or ""), "--node", node["id"], "--model", model]
    if task:
        argv.extend(["--task", task])
    try:
        completed = subprocess.run(argv, env=env, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise GraphError("启动子 agent 失败：%s。命令是：%s" % (exc, command)) from exc
    if completed.returncode != 0:
        raise GraphError(
            "子 agent 退出码 %s，节点 %s。stderr：%s" % (completed.returncode, node["id"], completed.stderr.strip()[:400])
        )
    return completed.stdout
