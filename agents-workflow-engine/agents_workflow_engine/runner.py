"""按图往下走：人答题，子 agent 执行 skill，主会话只调度。"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from . import models
from .errors import GraphError
from .errors import NeedInput
from .prompts import build_prompt
from .validate import node_map
from .version import __schema__
from .version import __version__

Token = Tuple[str, str]


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


def _when_edges(edges: List[dict], node_id: str, answer: str) -> List[dict]:
    return [
        edge for edge in edges
        if edge.get("from") == node_id and edge.get("when") == answer
    ]


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
    return models.resolve(graph, node, master_model)[1]


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
    def __init__(self, graph: dict, answers: Dict[str, List[str]], agent: Callable, master_model: str, log: List[dict], current: str = "", visits: Dict[str, int] = None, loop_counts: Dict[str, int] = None, tasks: List[str] = None, task_index: int = 0, joined: Dict[str, set] = None) -> None:
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
        self.joined = joined or {}

    def run(self) -> str:
        # 一条 token 就是一股独立的执行流；决策的 parallel 分支会各分出一股。
        # 第一行记引擎版本 + 预设格式代次：事后能对上是哪版跑出来的，
        # 也能查「项目里装的是哪版」（预设与引擎必须成对升级）。
        self.log.append({"event": "engine", "version": __version__, "schema": __schema__})
        self._check_models()
        work = [(self.current, "")]
        guard = 0
        while work:
            guard += 1
            if guard > 500:
                raise GraphError("走了 500 步还没到终点，图里可能有死循环")
            current, via = work.pop(0)
            self.current = current
            node = self.nodes[current]
            if node.get("join") and not self._join_ready(current, via):
                continue
            kind = node.get("kind")
            if kind == "end":
                self.log.append({"node": current, "event": "end", "title": node.get("title")})
                return current
            if kind in ("entry", "milestone"):
                if kind == "milestone":
                    self.log.append({"node": current, "event": "milestone", "title": node.get("title")})
                work.insert(0, self._only_token(current))
                continue
            if kind == "human_input":
                text = _take_answer(self.answers, current)
                self.log.append({"node": current, "event": "human_input", "text": text})
                work.insert(0, self._only_token(current))
                continue
            if kind == "decision":
                choice = _take_answer(self.answers, current)
                self.log.append({"node": current, "event": "decision", "choice": choice})
                tokens = self._decision_tokens(current, choice)
                if len(tokens) > 1:
                    self.log.append({"node": current, "event": "fork", "branches": [token[0] for token in tokens]})
                work = tokens + work
                continue
            if kind == "gate":
                result = self._call(node, None)
                verdict = _verdict(result)
                self.log.append({"node": current, "event": "gate", "verdict": verdict, "model": _resolve_model(self.graph, node, self.master_model)})
                matches = _when_edges(self.edges, current, verdict)
                if len(matches) != 1:
                    raise GraphError("门禁 %s 的「%s」有 %s 条出边，必须恰好 1 条" % (current, verdict, len(matches)))
                self._limit_back(matches[0], current)
                work.insert(0, (matches[0]["to"], matches[0]["id"]))
                continue
            if kind == "action":
                nxt = self._run_action(node)
                work.insert(0, nxt if nxt is not None else (current, via))
                continue
            raise GraphError("节点 %s 的 kind 无法执行：%s" % (current, kind))
        raise GraphError("调度队列空了还没到终点。检查图里是否有分支没有汇入")

    def _run_action(self, node: dict) -> Optional[Token]:
        node_id = node["id"]
        if node.get("once") and self.visits.get(node_id):
            return self._only_token(node_id)
        if node.get("repeatsBatch"):
            if self.task_index >= len(self.tasks):
                return self._only_token(node_id)
            task = self.tasks[self.task_index]
            result = self._call(node, task)
            self.visits[node_id] = self.visits.get(node_id, 0) + 1
            self.task_index += 1
            self.log.append({"node": node_id, "event": "batch-step", "task": task, "output": result})
            if self.task_index < len(self.tasks):
                return None
            return self._only_token(node_id)
        result = self._call(node, None)
        self.visits[node_id] = self.visits.get(node_id, 0) + 1
        self.log.append({"node": node_id, "event": "action", "output": result, "model": _resolve_model(self.graph, node, self.master_model)})
        if node.get("batch"):
            self.tasks = _tasks(result)
            self.task_index = 0
            self.log.append({"node": node_id, "event": "batch", "tasks": list(self.tasks)})
        return self._only_token(node_id)

    def _call(self, node: dict, task: Optional[str]) -> str:
        model = _resolve_model(self.graph, node, self.master_model)
        return self.agent(node, model, task)

    def _check_models(self) -> None:
        """两个模型配成同一个，等于没做对抗验证，开场记一笔。"""
        left = models.model_of(self.graph, "executor") or self.master_model
        right = models.model_of(self.graph, "gate") or self.master_model
        if not left or not right or left == right:
            self.log.append({
                "event": "model-check",
                "warning": "未做对抗验证",
                "executorModel": left,
                "gateModel": right,
            })

    def _decision_tokens(self, node_id: str, answer: str) -> List[Token]:
        matches = _when_edges(self.edges, node_id, answer)
        if not matches:
            raise GraphError("节点 %s 没有「%s」这条出边" % (node_id, answer))
        main = [edge for edge in matches if not edge.get("parallel")]
        side = [edge for edge in matches if edge.get("parallel")]
        if len(main) != 1:
            raise GraphError(
                "节点 %s 的「%s」需要恰好一条主出边，现在 %s 条；并行分支请标 parallel: true"
                % (node_id, answer, len(main))
            )
        for edge in matches:
            self._limit_back(edge, node_id)
        # 侧分支先推进，主路径随后；两股都到汇入点时才执行汇入节点。
        return [(edge["to"], edge["id"]) for edge in side] + [(main[0]["to"], main[0]["id"])]

    def _limit_back(self, edge: dict, node_id: str) -> None:
        if not edge.get("back"):
            return
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

    def _join_ready(self, node_id: str, via: str) -> bool:
        if not via:
            return True
        edge = self._edge(via)
        if edge is None or edge.get("back"):
            return True
        forward = set(
            item["id"] for item in self.edges
            if item.get("to") == node_id and not item.get("back")
        )
        seen = self.joined.setdefault(node_id, set())
        seen.add(via)
        if forward <= seen:
            return True
        self.log.append({"node": node_id, "event": "join-wait", "waiting": sorted(forward - seen)})
        return False

    def _edge(self, edge_id: str) -> Optional[dict]:
        for edge in self.edges:
            if edge.get("id") == edge_id:
                return edge
        return None

    def _only_token(self, node_id: str) -> Token:
        chosen = _plain_edges(self.edges, node_id)
        if len(chosen) != 1:
            raise GraphError("节点 %s 有 %s 条向前的边，调度不知道走哪条" % (node_id, len(chosen)))
        return (chosen[0]["to"], chosen[0]["id"])


def _argv(command: str, prompt: str, model: str) -> List[str]:
    """拼子 agent 的命令行。模板里有 {prompt} 就放那里，没有就追在后面。"""
    items = shlex.split(command)
    template = " ".join(items)
    if "{prompt}" in template:
        argv = [item.replace("{prompt}", prompt).replace("{model}", model) for item in items]
        if "{model}" not in template:
            argv.extend(["--model", model])
        return argv
    argv = [item.replace("{model}", model) for item in items]
    if "{model}" not in template:
        argv.extend(["--model", model])
    argv.append(prompt)
    return argv


def spawn_agent(command: str, node: dict, model: str, task: Optional[str], project: str = ".") -> str:
    """拉起一个独立 agent 进程：提示词进去，stdout 出来。"""
    if not command.strip():
        raise GraphError(
            "没有配置独立 agent 命令。run 时加 --agent，例如 --agent 'qoder -p'；"
            "不想拉起进程就用 --manual 输出执行清单"
        )
    prompt = build_prompt(node, model, task)
    env = os.environ.copy()
    env["WORKFLOW_SKILL"] = str(node.get("skill") or "")
    env["WORKFLOW_NODE"] = node["id"]
    env["WORKFLOW_MODEL"] = model
    env["WORKFLOW_TASK"] = task or ""
    env["WORKFLOW_PROMPT"] = prompt
    argv = _argv(command, prompt, model)
    try:
        completed = subprocess.run(
            argv, env=env, text=True, capture_output=True, check=False, cwd=project
        )
    except OSError as exc:
        raise GraphError("启动独立 agent 失败：%s。命令是：%s" % (exc, command)) from exc
    if completed.returncode != 0:
        raise GraphError(
            "独立 agent 退出码 %s，节点 %s。stderr：%s"
            % (completed.returncode, node["id"], completed.stderr.strip()[:400])
        )
    return completed.stdout