#!/usr/bin/env python3
"""agents-workflow-engine 单元测试。"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents_workflow_engine.errors import GraphError  # noqa: E402
from agents_workflow_engine.load import load_preset  # noqa: E402
from agents_workflow_engine.merge import merge  # noqa: E402
from agents_workflow_engine.models import model_of  # noqa: E402
from agents_workflow_engine.models import resolve  # noqa: E402
from agents_workflow_engine.models import role_of  # noqa: E402
from agents_workflow_engine.prompts import build_prompt  # noqa: E402
from agents_workflow_engine.render_mermaid import render  # noqa: E402
from agents_workflow_engine.runner import Runner  # noqa: E402
from agents_workflow_engine.runner import spawn_agent  # noqa: E402
from agents_workflow_engine.validate import validate  # noqa: E402
from agents_workflow_engine.version import __schema__  # noqa: E402
from agents_workflow_engine.version import __version__  # noqa: E402


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


def write_answers(folder):
    """把 happy_answers 写成 answers.yaml，返回路径。"""
    path = os.path.join(folder, "answers.yaml")
    text = "\n".join("%s: %s" % (key, value[0]) for key, value in happy_answers().items()) + "\n"
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


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
    def test_preset_ships_two_distinct_models(self):
        graph = load_preset()
        errors, warnings = validate(graph)
        self.assertEqual(errors, [])
        self.assertEqual(model_of(graph, "executor"), "DeepSeek-V4.1-Flash-1017")
        self.assertEqual(model_of(graph, "gate"), "GLM-5.3-Flash")
        self.assertFalse(any("未配置对抗模型" in item for item in warnings))
        self.assertFalse(any("未做对抗验证" in item for item in warnings))

    def test_env_override_can_make_models_equal(self):
        os.environ["MODEL_GATE"] = "DeepSeek-V4.1-Flash-1017"
        try:
            errors, warnings = validate(load_preset())
        finally:
            del os.environ["MODEL_GATE"]
        self.assertEqual(errors, [])
        self.assertTrue(any("未做对抗验证" in item for item in warnings))

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
        os.environ["MODEL_GATE"] = "DeepSeek-V4.1-Flash-1017"
        log = []
        try:
            Runner(load_preset(), happy_answers(), fake_agent([]), "master", log).run()
        finally:
            del os.environ["MODEL_GATE"]
        self.assertTrue(any(item.get("warning") == "未做对抗验证" for item in log))

    def test_cli_run_writes_jsonl(self):
        from agents_workflow_engine.cli import main

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            agent = os.path.join(folder, "agent.sh")
            with open(agent, "w", encoding="utf-8") as handle:
                handle.write(
                    "#!/bin/sh\n"
                    "case \"$WORKFLOW_SKILL\" in\n"
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

    def test_cli_manual_writes_prompts_not_decisions(self):
        from agents_workflow_engine.cli import main

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            code = main(["--project", folder, "run", "--answers", answers, "--manual"])
            self.assertEqual(code, 0)
            prompts = os.path.join(folder, ".agents", "workflow", "prompts.md")
            self.assertTrue(os.path.isfile(prompts))
            with open(prompts, encoding="utf-8") as handle:
                body = handle.read()
            self.assertIn("skill `dev-build`", body)
            self.assertIn("引擎 %s" % __version__, body)
            self.assertIn("能开子 agent 就开", body)
            self.assertIn("假定通过", body)
            self.assertIn("执行者（DeepSeek-V4.1-Flash-1017）", body)
            self.assertIn("门禁（GLM-5.3-Flash）", body)
            self.assertFalse(os.path.exists(os.path.join(folder, ".agents", "workflow", "decisions.jsonl")))

    def test_cli_without_agent_and_not_tty_falls_back_to_manual(self):
        from agents_workflow_engine.cli import main

        class NotATTY(object):
            def isatty(self):
                return False

            def readline(self):
                raise AssertionError("非 TTY 不应该等输入")

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            saved, sys.stdin = sys.stdin, NotATTY()
            try:
                code = main(["--project", folder, "run", "--answers", answers])
            finally:
                sys.stdin = saved
            self.assertEqual(code, 0)
            self.assertTrue(os.path.isfile(os.path.join(folder, ".agents", "workflow", "prompts.md")))

    def test_cli_tty_default_keeps_work_in_session(self):
        """支持子 agent（回车）→ 不拉进程，只出清单。"""
        import builtins

        from agents_workflow_engine.cli import main

        class TTY(object):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            saved_stdin, saved_input = sys.stdin, builtins.input
            sys.stdin, builtins.input = TTY(), (lambda prompt="": "")
            try:
                code = main(["--project", folder, "run", "--answers", answers])
            finally:
                sys.stdin, builtins.input = saved_stdin, saved_input
            self.assertEqual(code, 0)
            work = os.path.join(folder, ".agents", "workflow")
            self.assertTrue(os.path.isfile(os.path.join(work, "prompts.md")))
            self.assertFalse(os.path.exists(os.path.join(work, "decisions.jsonl")))

    def test_cli_tty_without_subagent_needs_agent_command(self):
        """选 3（独立 agent）又没给 --agent → 报错，而不是静默走清单。"""
        import builtins

        from agents_workflow_engine.cli import main

        class TTY(object):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            saved_stdin, saved_input = sys.stdin, builtins.input
            sys.stdin, builtins.input = TTY(), (lambda prompt="": "3")
            try:
                code = main(["--project", folder, "run", "--answers", answers])
            finally:
                sys.stdin, builtins.input = saved_stdin, saved_input
            self.assertEqual(code, 1)
            work = os.path.join(folder, ".agents", "workflow")
            self.assertFalse(os.path.exists(os.path.join(work, "prompts.md")))

    def test_cli_tty_pick_solo(self):
        """选 2（不支持、用主会话）→ 清单里要求主会话自己干。"""
        import builtins

        from agents_workflow_engine.cli import main

        class TTY(object):
            def isatty(self):
                return True

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            saved_stdin, saved_input = sys.stdin, builtins.input
            sys.stdin, builtins.input = TTY(), (lambda prompt="": "2")
            try:
                code = main(["--project", folder, "run", "--answers", answers])
            finally:
                sys.stdin, builtins.input = saved_stdin, saved_input
            self.assertEqual(code, 0)
            with open(os.path.join(folder, ".agents", "workflow", "prompts.md"), encoding="utf-8") as handle:
                body = handle.read()
            self.assertIn("会话内 · 只用主会话", body)
            self.assertIn("不要开子 agent", body)
            self.assertNotIn("能开子 agent 就开", body)

    def test_cli_solo_flag_skips_the_question(self):
        from agents_workflow_engine.cli import main

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            code = main(["--project", folder, "run", "--answers", answers, "--solo"])
            self.assertEqual(code, 0)
            with open(os.path.join(folder, ".agents", "workflow", "prompts.md"), encoding="utf-8") as handle:
                body = handle.read()
            self.assertIn("不要开子 agent", body)

    def test_cli_rejects_two_mode_flags(self):
        from agents_workflow_engine.cli import main

        with tempfile.TemporaryDirectory() as folder:
            answers = write_answers(folder)
            code = main(["--project", folder, "run", "--answers", answers, "--manual", "--solo"])
            self.assertEqual(code, 1)
            self.assertFalse(os.path.exists(os.path.join(folder, ".agents", "workflow", "prompts.md")))


class ModelTest(unittest.TestCase):
    def test_role_follows_kind(self):
        self.assertEqual(role_of({"id": "g", "kind": "gate"}), "gate")
        self.assertEqual(role_of({"id": "a", "kind": "action"}), "executor")

    def test_node_level_literal_model_wins(self):
        graph = load_preset()
        node = {"id": "dev-build", "kind": "action", "model": "my-own-model"}
        role, model = resolve(graph, node, "master")
        self.assertEqual(role, "executor")
        self.assertEqual(model, "my-own-model")

    def test_missing_role_falls_back_to_master(self):
        graph = {"models": {}, "nodes": []}
        role, model = resolve(graph, {"id": "x", "kind": "gate"}, "master")
        self.assertEqual((role, model), ("gate", "master"))


class PromptTest(unittest.TestCase):
    def test_action_prompt_mentions_skill_file(self):
        text = build_prompt({"id": "dev-build", "kind": "action", "skill": "dev-build", "title": "构建与自测", "note": ["后端 TDD"]}, "M")
        self.assertIn("skill `dev-build`", text)
        self.assertIn(".agents/skills/dev-build/SKILL.md", text)
        self.assertIn("- 后端 TDD", text)
        self.assertIn("执行者（M）", text)

    def test_gate_prompt_asks_for_verdict(self):
        text = build_prompt({"id": "dev-plan-review", "kind": "gate", "skill": "dev-plan-review", "title": "plan 质量门"}, "M")
        self.assertIn("门禁（M）", text)
        self.assertIn("满意", text)
        self.assertIn("不满意", text)

    def test_batch_prompt_commands_task_lines(self):
        text = build_prompt({"id": "dev-plan", "kind": "action", "skill": "dev-plan", "batch": True}, "M")
        self.assertIn("TASK: <id>", text)

    def test_prompt_without_skill_still_builds(self):
        text = build_prompt({"id": "m", "kind": "milestone", "title": "提测"}, "M")
        self.assertNotIn("skill `", text)
        self.assertIn("提测", text)

    def test_manual_prompt_offers_subagent(self):
        text = build_prompt({"id": "dev-build", "kind": "action", "skill": "dev-build"}, "M", manual=True)
        self.assertIn("能开子 agent 就开", text)

    def test_solo_prompt_forbids_subagent(self):
        text = build_prompt({"id": "dev-build", "kind": "action", "skill": "dev-build"}, "M",
                            manual=True, allow_subagent=False)
        self.assertIn("不要开子 agent", text)
        self.assertNotIn("能开子 agent 就开", text)


class SpawnTest(unittest.TestCase):
    def test_spawn_passes_prompt_and_runs_in_project(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = os.path.join(folder, "agent.sh")
            dump = os.path.join(folder, "argv.txt")
            script = (
                "#!/bin/sh\n"
                "printf '%s\\n' \"$PWD\" \"$@\" > '" + dump + "'\n"
                "printf 'ok\\n'\n"
            )
            with open(agent, "w", encoding="utf-8") as handle:
                handle.write(script)
            os.chmod(agent, 0o755)
            node = {"id": "dev-build", "kind": "action", "skill": "dev-build", "title": "构建与自测"}
            out = spawn_agent(agent, node, "M", None, folder)
            self.assertIn("ok", out)
            with open(dump, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
            self.assertEqual(os.path.realpath(lines[0]), os.path.realpath(folder))
            self.assertNotIn("--skill", lines)
            self.assertTrue(any("skill `dev-build`" in line for line in lines))
            self.assertIn("--model", lines)
            self.assertIn("M", lines)

    def test_spawn_placeholders_are_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = os.path.join(folder, "agent.sh")
            dump = os.path.join(folder, "argv.txt")
            script = (
                "#!/bin/sh\n"
                "printf '%s\\n' \"$@\" > '" + dump + "'\n"
                "printf 'ok\\n'\n"
            )
            with open(agent, "w", encoding="utf-8") as handle:
                handle.write(script)
            os.chmod(agent, 0o755)
            node = {"id": "dev-plan-review", "kind": "gate", "skill": "dev-plan-review"}
            spawn_agent(agent + " -p {prompt} --model {model}", node, "GLM", None, folder)
            with open(dump, encoding="utf-8") as handle:
                body = handle.read()
            lines = body.splitlines()
            self.assertEqual(lines[0], "-p")
            self.assertIn("GLM", lines)
            self.assertNotIn("{prompt}", body)
            self.assertTrue(any("门禁（GLM）" in line for line in lines))

    def test_spawn_failure_raises(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = os.path.join(folder, "agent.sh")
            with open(agent, "w", encoding="utf-8") as handle:
                handle.write("#!/bin/sh\nexit 3\n")
            os.chmod(agent, 0o755)
            with self.assertRaises(GraphError) as caught:
                spawn_agent(agent, {"id": "x", "kind": "action"}, "M", None, folder)
            self.assertIn("退出码 3", str(caught.exception))


class VersionTest(unittest.TestCase):
    def test_run_logs_engine_version_first(self):
        log = []
        Runner(load_preset(), happy_answers(), fake_agent([]), "master", log).run()
        first = log[0]
        self.assertEqual(first.get("event"), "engine")
        self.assertEqual(first.get("version"), __version__)
        self.assertEqual(first.get("schema"), __schema__)

    def test_version_flag_prints_version(self):
        from agents_workflow_engine.cli import main

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit) as caught:
                main(["--version"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn(__version__, buf.getvalue())


if __name__ == "__main__":
    unittest.main()