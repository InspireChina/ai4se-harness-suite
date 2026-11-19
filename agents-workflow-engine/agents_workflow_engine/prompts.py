"""把节点渲染成给 agent 的提示词。skill 写在提示词里，不再拼 --skill 参数。"""

from __future__ import annotations

from typing import Optional

from .models import role_of

ROLE_TITLES = {"executor": "执行者", "gate": "门禁"}


def build_prompt(node: dict, model: str, task: Optional[str] = None, manual: bool = False,
                 allow_subagent: bool = True) -> str:
    """拼一段自解释的提示词：谁、做什么、用哪个 skill、算做完的判定标准。

    manual 表示不拉进程、把提示词交回当前会话；allow_subagent=False 时要求
    主会话自己干，不开子 agent。
    """
    kind = node.get("kind")
    role = role_of(node)
    lines = [
        "[graph-master] 节点 %s · %s · 模型 %s（%s）"
        % (node["id"], node.get("title") or node["id"], ROLE_TITLES[role], model or "未配置")
    ]
    if manual:
        lines.append("")
        if allow_subagent:
            lines.append(
                "你（当前会话）现在扮演%s。能开子 agent 就开一个去做；开不了就自己按 skill 做完。"
                % ROLE_TITLES[role]
            )
        else:
            lines.append(
                "你（当前会话里的主会话）现在扮演%s，自己按 skill 做完本节点，不要开子 agent。"
                % ROLE_TITLES[role]
            )
    skill = node.get("skill") or ""
    lines.append("")
    if skill:
        lines.append("用 skill `%s` 完成本节点。" % skill)
        lines.append("skill 文件（相对项目根）：.agents/skills/%s/SKILL.md" % skill)
        lines.append("（能直接加载 skill 就用 skill；加载不到就直接读这个文件）")
    else:
        lines.append("按节点说明完成本节点。")
    if task:
        lines.append("")
        lines.append("本批任务：%s" % task)
    notes = node.get("note") or []
    if notes:
        lines.append("")
        lines.append("节点说明：")
        for note in notes:
            lines.append("- %s" % note)
    lines.append("")
    lines.append("完成标准：")
    step = 1
    lines.append("%s. 只改当前项目内的文件" % step)
    step += 1
    lines.append("%s. 结论写在标准输出，引擎只读 stdout" % step)
    step += 1
    if kind == "gate":
        lines.append("%s. 最后单独一行输出「满意」或「不满意」" % step)
        step += 1
        if manual:
            lines.append("（本次引擎假定通过、继续往下走；实际判定不满意时请回到对应的打回节点）")
    if node.get("batch"):
        lines.append("%s. 每条任务单独一行输出 `TASK: <id>`" % step)
    return "\n".join(lines)