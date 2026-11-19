#!/usr/bin/env python3
"""agents-workflow-engine 单元测试。"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents_workflow_engine.errors import GraphError  # noqa: E402
from agents_workflow_engine.load import load_preset  # noqa: E402
from agents_workflow_engine.merge import merge  # noqa: E402
from agents_workflow_engine.render_mermaid import render  # noqa: E402
from agents_workflow_engine.runner import Runner  # noqa: E402
from agents_workflow_engine.validate import validate  # noqa: E402


def happy_answers():
    return {
        "start-version": ["iteration1"],
        "write-spec": ["登录"],
        "requirement-decision": ["满意"],
        "tech-brief": ["账号"],
        "hld-decision": ["满意"],
        "plan-confirm": ["确认"],
        "plan-decision": ["满意"],
        "build-decision": ["满意"],
        "test-decision": ["通过"],
    }


def fake_agent(calls):
    def run(node, model, task):
        calls.append((node["id"], model, task))
        skill = node.get("skill")
        if skill == "dev-plan":
            return "TASK: a\nTASK: b\n"
        if skill in ("ba-requirement-review", "dev-plan-review"):
            return "满意\n"
        return "ok\n"
    return run


class PresetTest(unittest.TestCase):
    def test_preset_valid_and_warns_when_model_unset(self):
        graph = load_preset()
        errors, warnings = validate(graph)
        self.assertEqual(errors, [])
        self.assertTrue(any("未配置对抗模型" in item for item in warnings))

    def test_distinct_models_have_no_same_model_warning(self):
        os.environ["MODEL_WRITER"] = "writer-a"
        os.environ["MODEL_REVIEWER"] = "reviewer-b"
        try:
            errors, warnings = validate(load_preset())
        finally:
            del os.environ["MODEL_WRITER"]
            del os.environ["MODEL_REVIEWER"]
        self.assertEqual(errors, [])
        self.assertFalse(any("未做对抗验证" in item for item in warnings))
        self.assertFalse(any("未配置对抗模型" in item for item in warnings))

    def test_render_shapes(self):
        text = render(load_preset())
        self.assertIn("flowchart LR", text)
        self.assertIn(
            "dev-plan(详细规划 · 一批任务 / 详细设计（API/DB 字段、文件改动）、任务清单、自测用例（DST）)",
            text,
        )
        self.assertIn("qa-write-cases(编写 QA 用例)", text)
        self.assertIn("qa-run-e2e(编写并运行 E2E 测试 · 汇入)", text)
        self.assertIn("test-decision{测试决策}", text)
        self.assertIn("ba-requirement-review[[需求质量门]]", text)
        self.assertIn("start-version[/开始版本/]", text)
        self.assertIn("requirement-decision{需求决策}", text)
        self.assertIn("handoff([提测 · 里程碑])", text)
        self.assertIn("accepted([人工补测 · 里程碑])", text)
        self.assertIn("ba-gen-facts(刷新事实文档)", text)
        self.assertIn("dev-release-plan(准备上线)", text)
        self.assertIn("shipped([可上线])", text)
        self.assertIn("graph-start{{会话启动}}", text)
        self.assertIn("后端 TDD", text)
        self.assertIn("-.->|不满意|", text)
        self.assertIn("-->|满意 · 并行| qa-write-cases", text)

    def test_render_hides_extensions(self):
        graph = load_preset()
        graph["extensions"] = [{
            "id": "future",
            "title": "未来",
            "linked": False,
            "nodes": [{"id": "future-node", "kind": "action", "title": "未来步骤"}],
        }]
        self.assertNotIn("future-node", render(graph))

    def test_disable_prototype_still_reaches_end(self):
        graph = merge(load_preset(), {"disable": ["ba-write-prototype"]})
        errors, _warnings = validate(graph)
        self.assertEqual(errors, [])
        self.assertNotIn("ba-write-prototype", {node["id"] for node in graph["nodes"]})

    def test_disable_qa_cases_keeps_graph_runnable(self):
        graph = merge(load_preset(), {"disable": ["qa-write-cases"]})
        errors, _warnings = validate(graph)
        self.assertEqual(errors, [])
        calls = []
        end = Runner(graph, happy_answers(), fake_agent(calls), "master", []).run()
        self.assertEqual(end, "shipped")
        self.assertNotIn("qa-write-cases", [item[0] for item in calls])

    def test_edge_into_sealed_step_fails(self):
        graph = load_preset()
        graph["edges"].append({"id": "bad", "from": "dev-build", "to": "后端 TDD"})
        errors, _warnings = validate(graph)
        self.assertTrue(any("封死" in item for item in errors))

    def test_edge_into_extension_fails(self):
        graph = load_preset()
        graph["extensions"] = [{
            "id": "future",
            "title": "未来",
            "nodes": [{"id": "future-node", "kind": "action", "title": "未来步骤"}],
        }]
        graph["edges"].append({"id": "bad", "from": "handoff", "to": "future-node"})
        errors, _warnings = validate(graph)
        self.assertTrue(any("扩展" in item for item in errors))

    def test_back_edge_without_loop_fails(self):
        graph = load_preset()
        graph["loops"] = [loop for loop in graph["loops"] if loop["id"] != "spec"]
        errors, _warnings = validate(graph)
        self.assertTrue(any("没有写入任何回路" in item for item in errors))

    def test_parallel_branch_needs_one_main_edge(self):
        graph = load_preset()
        graph["edges"].append({
            "id": "dup",
            "from": "requirement-decision",
            "to": "write-spec",
            "when": "满意",
        })
        errors, _warnings = validate(graph)
        self.assertTrue(any("主出边" in item for item in errors))

    def test_parallel_edge_must_come_from_decision(self):
        graph = load_preset()
        graph["edges"] = [
            dict(edge, parallel=True) if edge["id"] == "e13" else edge
            for edge in graph["edges"]
        ]
        errors, _warnings = validate(graph)
        self.assertTrue(any("parallel" in item for item in errors))

    def test_join_rejects_conditional_input(self):
        graph = load_preset()
        graph["edges"] = [
            dict(edge, when="满意") if edge["id"] == "qa-cases-ready" else edge
            for edge in graph["edges"]
        ]
        errors, _warnings = validate(graph)
        self.assertTrue(any("汇入" in item for item in errors))

    def test_milestone_must_be_master(self):
        graph = load_preset()
        for node in graph["nodes"]:
            if node["id"] == "handoff":
                node["actor"] = "subagent"
        errors, _warnings = validate(graph)
        self.assertTrue(any("里程碑 handoff" in item for item in errors))

    def test_replace_skill(self):
        graph = merge(load_preset(), {"replace": {"ba-write-spec": {"skill": "my-write-spec"}}})
        node = [item for item in graph["nodes"] if item["id"] == "ba-write-spec"][0]
        self.assertEqual(node["skill"], "my-write-spec")


class RunTest(unittest.TestCase):
    def test_happy_path_runs_build_once_per_task(self):
        calls = []
        log = []
        end = Runner(load_preset(), happy_answers(), fake_agent(calls), "master", log).run()
        self.assertEqual(end, "shipped")
        build_calls = [item for item in calls if item[0] == "dev-build"]
        self.assertEqual([item[2] for item in build_calls], ["a", "b"])
        self.assertTrue(any(item.get("event") == "batch" for item in log))

    def test_qa_branch_runs_before_design_and_joins(self):
        calls = []
        log = []
        end = Runner(load_preset(), happy_answers(), fake_agent(calls), "master", log).run()
        self.assertEqual(end, "shipped")
        order = [item[0] for item in calls]
        self.assertLess(order.index("qa-write-cases"), order.index("tl-high-level-design"))
        self.assertEqual(order.count("qa-write-cases"), 1)
        self.assertEqual(order.count("qa-run-e2e"), 1)
        forks = [item for item in log if item.get("event") == "fork"]
        self.assertEqual(forks[0]["branches"], ["qa-write-cases", "tech-brief"])
        waits = [item for item in log if item.get("event") == "join-wait"]
        self.assertEqual(waits[0]["node"], "qa-run-e2e")
        self.assertEqual(waits[0]["waiting"], ["handoff-to-e2e"])

    def test_spec_reject_then_pass(self):
        calls = []
        answers = happy_answers()
        answers["write-spec"] = ["第一稿", "第二稿"]
        answers["requirement-decision"] = ["不满意", "满意"]
        end = Runner(load_preset(), answers, fake_agent(calls), "master", []).run()
        self.assertEqual(end, "shipped")
        self.assertEqual(sum(1 for item in calls if item[0] == "ba-write-spec"), 2)
        self.assertEqual(sum(1 for item in calls if item[0] == "ba-write-prototype"), 1)
        self.assertEqual(sum(1 for item in calls if item[0] == "qa-write-cases"), 1)

    def test_tail_runs_facts_then_release(self):
        calls = []
        log = []
        end = Runner(load_preset(), happy_answers(), fake_agent(calls), "master", log).run()
        self.assertEqual(end, "shipped")
        order = [item[0] for item in calls]
        self.assertLess(order.index("qa-run-e2e"), order.index("ba-gen-facts"))
        self.assertLess(order.index("ba-gen-facts"), order.index("dev-release-plan"))
        self.assertEqual(order[-1], "dev-release-plan")
        milestones = [item["title"] for item in log if item.get("event") == "milestone"]
        self.assertEqual(milestones, ["提测", "人工补测"])

    def test_e2e_revise_then_pass(self):
        answers = happy_answers()
        answers["test-decision"] = ["修订", "通过"]
        calls = []
        end = Runner(load_preset(), answers, fake_agent(calls), "master", []).run()
        self.assertEqual(end, "shipped")
        self.assertEqual(sum(1 for item in calls if item[0] == "qa-run-e2e"), 2)

    def test_e2e_reject_returns_to_dev(self):
        answers = happy_answers()
        answers["plan-confirm"] = ["确认", "再确认"]
        answers["plan-decision"] = ["满意", "满意"]
        answers["build-decision"] = ["满意", "满意"]
        answers["amend-input"] = ["补字段"]
        answers["test-decision"] = ["打回开发", "通过"]
        calls = []
        end = Runner(load_preset(), answers, fake_agent(calls), "master", []).run()
        self.assertEqual(end, "shipped")
        self.assertEqual(sum(1 for item in calls if item[0] == "dev-plan"), 2)
        self.assertEqual(sum(1 for item in calls if item[0] == "dev-plan-amend"), 1)
        self.assertEqual(sum(1 for item in calls if item[0] == "dev-build"), 4)
        self.assertEqual(sum(1 for item in calls if item[0] == "qa-run-e2e"), 2)

    def test_e2e_loop_cap_stops(self):
        answers = happy_answers()
        answers["test-decision"] = ["修订", "修订", "修订", "修订"]
        with self.assertRaises(GraphError) as caught:
            Runner(load_preset(), answers, fake_agent([]), "master", []).run()
        self.assertIn("达到上限", str(caught.exception))

    def test_loop_cap_stops(self):
        answers = happy_answers()
        answers["write-spec"] = ["a", "b", "c", "d"]
        answers["requirement-decision"] = ["不满意", "不满意", "不满意", "不满意"]
        with self.assertRaises(GraphError) as caught:
            Runner(load_preset(), answers, fake_agent([]), "master", []).run()
        self.assertIn("达到上限", str(caught.exception))

    def test_missing_answer_names_the_node(self):
        with self.assertRaises(GraphError) as caught:
            Runner(load_preset(), {}, fake_agent([]), "master", []).run()
        self.assertIn("start-version", str(caught.exception))

    def test_same_model_is_logged(self):
        os.environ["MODEL_WRITER"] = "same"
        os.environ["MODEL_REVIEWER"] = "same"
        log = []
        try:
            Runner(load_preset(), happy_answers(), fake_agent([]), "master", log).run()
        finally:
            del os.environ["MODEL_WRITER"]
            del os.environ["MODEL_REVIEWER"]
        self.assertTrue(any(item.get("warning") == "未做对抗验证" for item in log))

    def test_cli_run_writes_jsonl(self):
        from agents_workflow_engine.cli import main

        with tempfile.TemporaryDirectory() as folder:
            answers = os.path.join(folder, "answers.yaml")
            text = "\n".join("%s: %s" % (key, value[0]) for key, value in happy_answers().items()) + "\n"
            with open(answers, "w", encoding="utf-8") as handle:
                handle.write(text)
            agent = os.path.join(folder, "agent.sh")
            with open(agent, "w", encoding="utf-8") as handle:
                handle.write(
                    "#!/bin/sh\n"
                    "case \"$2\" in\n"
                    "  dev-plan) printf 'TASK: a\\nTASK: b\\n' ;;\n"
                    "  ba-requirement-review|dev-plan-review) printf '满意\\n' ;;\n"
                    "  *) printf 'ok\\n' ;;\n"
                    "esac\n"
                )
            os.chmod(agent, 0o755)
            code = main(["--project", folder, "run", "--answers", answers, "--agent", agent])
            self.assertEqual(code, 0)
            record = os.path.join(folder, ".agents", "workflow", "decisions.jsonl")
            self.assertTrue(os.path.isfile(record))
            with open(record, encoding="utf-8") as handle:
                body = handle.read()
            self.assertIn('"node": "handoff"', body)
            self.assertIn('"node": "accepted"', body)
            self.assertIn('"task": "b"', body)


if __name__ == "__main__":
    unittest.main()