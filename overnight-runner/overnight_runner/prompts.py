"""提示词组装：把项目默认提示词 + 默认决策 + plan 内容拼成给 agent 的一次性提示。"""

from __future__ import annotations

from pathlib import Path

from .config import ProjectConfig

PLAN_PLACEHOLDER = "{{PLAN}}"
DECISIONS_PLACEHOLDER = "{{DECISIONS}}"


def read_plan(project_root: Path, plan_rel: str) -> tuple[str, str]:
    """读 plan 文件，返回 (内容, 错误信息)。"""
    path = project_root / plan_rel
    if not path.exists():
        return "", f"plan 文件不存在: {plan_rel}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return "", f"plan 文件读取失败: {plan_rel} ({exc})"
    if not text.strip():
        return "", f"plan 文件为空: {plan_rel}"
    return text, ""


def build_prompt(
    project_root: Path,
    project_cfg: ProjectConfig,
    plan_rel: str,
    task_prompt: str = "",
) -> tuple[str, str]:
    """返回 (最终提示词, 错误信息)。"""
    plan_text, err = read_plan(project_root, plan_rel)
    if err:
        return "", err

    decisions = project_cfg.decision_text() or "（无预设决策，遇到需决策的问题请选择最安全、可回滚的方案）"

    template = project_cfg.default_prompt or ""
    if PLAN_PLACEHOLDER in template:
        prompt = template.replace(PLAN_PLACEHOLDER, plan_text)
    else:
        prompt = f"{template}\n\n{plan_text}"

    if DECISIONS_PLACEHOLDER in prompt:
        prompt = prompt.replace(DECISIONS_PLACEHOLDER, decisions)
    elif decisions:
        prompt = f"{prompt}\n\n默认决策：\n{decisions}"

    prompt += f"\n\n---\n本次任务：{plan_rel}\n"

    if task_prompt:
        prompt += f"补充要求：\n{task_prompt}\n"

    return prompt, ""


def build_resume_prompt(question: str, answer: str, plan_rel: str) -> str:
    """续跑时的提示词：把人的决策送回给同一个 session 的 agent。"""
    return (
        f"针对你刚才提出的问题：{question}\n\n"
        f"决策如下：{answer}\n\n"
        f"请基于这个决策继续完成原任务（计划：{plan_rel}）。"
        "不要重复已经完成的步骤，只做剩下的部分。"
    )
