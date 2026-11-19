# 三种执行方式：会话内开子 agent / 只用主会话 / 独立 agent

## 需求

> 图不用改，如果能支持子 agent，就不用启动独立 agent
>
> 应该是三个选项：
> - 支持-使用子agent
> - 不支持-使用主会话
> - 不支持-使用独立agent

三层：

1. **图不动**：泳道标题继续叫「子 agent」，`graph.html` 一个字不改
2. **问句改成三选一**，不说「真子 agent」也不说「拉不拉进程」，直接说这活由谁干
3. **前两种都是「会话内」**：只写 `prompts.md`，不拉进程；区别只有提示词里的一句话术

## 三个选项

| 选项 | 入口 | 谁干活 | 提示词里的话术 |
|---|---|---|---|
| 1 · 会话内开子 agent（默认） | 回车 / `--manual` / 非交互终端 | 当前会话按清单开子 agent，开不了自己干 | 「能开子 agent 就开一个去做；开不了就自己按 skill 做完」 |
| 2 · 会话内只用主会话 | 回答 `2` / `--solo` | 当前会话自己按 skill 做 | 「你自己（主会话）按 skill 做完本节点，不要开子 agent」 |
| 3 · 独立 agent | 回答 `3` / `--agent '<命令>'` | 每个节点一个独立进程 | —（走 stdout） |

## 改动

| 文件 | 改什么 |
|---|---|
| `prompts.py` | `build_prompt(..., manual, allow_subagent=True)`：`False` 时换成「不要开子 agent」那套话 |
| `cli.py` | `MODE_SESSION / MODE_SOLO / MODE_STANDALONE` 三个常量 + `_pick_mode()`；三行菜单；`--solo`；三个入口互斥；选 3 没给 `--agent` 直接报错 | 
| `tests/test_units.py` | 42 → 46：TTY 选 `2` → 主会话话术；`--solo` 免问直达；`--manual --solo` 互斥；选 `3` 无 `--agent` 报错；`build_prompt` 独奏话术 |
| `README.md` | 「两种模式」→「三种执行方式」表；用法补 `--manual` / `--solo` 两段 |
| `CHANGELOG.md` | 0.2.0（未发布，直接并入）改成三选项描述 |
| `AGENTS.md` | §8 职责、§10 用例数（46）、§12 清单 |

## 版本

**不 bump**：0.2.0 还没发布过（没提交、没装进任何项目），并进 0.2.0 的变更里，
省一个需要人对比的版本号。

## 不做的

- 不改泳道标题、不改 `graph.html`
- 不自动探测 agent 是否支持子 agent：没有可靠手段，问一句最省事
- 不在会话内模式伪造 `decisions.jsonl`：那不是引擎跑出来的
- 独奏模式不校模型：会话换不了模型时退化成单一模型，这事写不进机制

## 验证

- `python3 agents-workflow-engine/tests/test_units.py` → 46/46
- `./.agents/verify.sh` 全绿