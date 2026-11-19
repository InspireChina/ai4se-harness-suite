# agents-workflow-engine

一个人用主会话把一条迭代从启动调度到可上线。图是 YAML。人、graph-master、子 agent 分三道泳道。子 agent 默认就是**当前会话自己开的**：引擎把逐节点的提示词写成执行清单，它按图一个个做。也可以让引擎拉**独立进程**（`--agent`），提示词进去、stdout 出来。执行者与门禁用两个不同模型，做对抗验证。

> 当前版本 **0.2.0**（`python -m agents_workflow_engine --version`）。版本号唯一事实源是
> `agents_workflow_engine/version.py`，变更记在 [`CHANGELOG.md`](CHANGELOG.md)。
> 跑过的记录 `decisions.jsonl` 第一行会写下引擎版本，事后能对上是哪版跑出来的。

## 图

三行泳道（人 / graph-master / 子 agent）× 五个阶段，从「开始版本」到「可上线」。节点与连线由 `presets/iteration-to-test.yaml` 渲染，**图不手改**。

- **在线交互版**（缩放 / 拖拽 / 适应窗口）：<https://inspirechina.github.io/ai4se-harness-suite/agents-workflow-engine/graph.html>
- **本地打开**：[`graph.html`](graph.html)（双击即可，需联网加载 JointJS CDN）

改完 YAML 后 `render` 只出 Mermaid；`graph.html` 是这张预设的**人读版**，改预设时要顺手把图对齐。

## 预设的主线

```
需求规格 → 需求质量门 → 需求决策 ─┬─ 编写 QA 用例（并行侧分支）────────────┐
                                  └─ 技术高阶 → 迭代 HLD → 详细规划 → 开发 → 提测
                                                                              │
      准备上线 ← 刷新事实文档 ← 人工补测 ← 测试决策 ← 编写并运行 E2E ←────────┘
```

## 用法

在仓库根目录：

```bash
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine validate
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine render --dry-run

# 拉起独立进程干活（提示词会追加到命令末尾）
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine run \
  --project <目标项目> --answers answers.yaml --agent 'qoder -p'

# 不拉进程（默认）：清单交给当前会话，它开子 agent 做
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine run \
  --project <目标项目> --answers answers.yaml --manual

# 不拉进程，只用主会话做（自己按 skill 干，不开子 agent）
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine run \
  --project <目标项目> --answers answers.yaml --solo
```

`answers.yaml` 里，人的节点对应一段文字或该决策的选项。同一节点要答多次时写成列表。

- 需求/高阶/plan/构建决策：`满意` 或 `不满意`
- 测试决策：`修订`、`通过`、`打回开发`

子 agent 收到的是**一段提示词**（不是 `--skill` 参数）：节点、角色、用哪个 skill、skill 文件路径、本批任务、节点说明、以及算做完的判定标准。命令行只多一个 `--model`。

skill 在提示词里写了两份：名字（`用 skill dev-build 完成本节点`）和路径（`.agents/skills/dev-build/SKILL.md`）。对方能直接加载 skill 就用 skill，加载不到就自己读那个文件——不依赖它扫哪个目录。

判定标准也写在提示词里：门禁节点最后单独一行打印 `满意` 或 `不满意`；批量节点（`dev-plan`）用 `TASK: <id>` 宣布一批任务。环境变量 `WORKFLOW_SKILL` / `WORKFLOW_NODE` / `WORKFLOW_MODEL` / `WORKFLOW_TASK` / `WORKFLOW_PROMPT` 同样可用。

命令模板可选占位符：`{prompt}` 和 `{model}`。写 `'qoder -p {prompt} -m {model}'` 就完全自己控制位置。

## 两个模型，配在图里

```yaml
models:
  executor: { model: DeepSeek-V4.1-Flash-1017, env: MODEL_EXECUTOR }   # 所有 action
  gate: { model: GLM-5.3-Flash, env: MODEL_GATE }                     # 所有 gate
```

- 节点里**不用**再写 `model:`：`kind: gate` 取门禁模型，其余取执行者模型（写了具体模型名的节点仍以节点为准，overlay 想单点换时用）
- 环境变量有值时优先，CI 里换模型不用改文件
- 两个模型配成同一个，等于没做对抗验证：`validate` 会给警告，`run` 在日志里记一条 `model-check`

## 三种执行方式

`run` 起来先问一句「这个会话怎么执行？」，三个选项：

| 选项 | 怎么进 | 谁干活 | 产出 |
|---|---|---|---|
| 1 · 会话内开子 agent（默认） | 回车 / `--manual` / 非交互终端 | 当前会话按清单开子 agent；开不了就自己干 | `.agents/workflow/prompts.md` |
| 2 · 会话内只用主会话 | 回答 `2` / `--solo` | 当前会话自己按 skill 做，**不许**开子 agent | 同上 |
| 3 · 独立 agent | 回答 `3` / `--agent '<命令>'` | 每个节点一个独立进程，提示词进去、stdout 出来 | `.agents/workflow/decisions.jsonl` |

前两种都不拉进程，只是提示词里的话术不同：1 写着「能开子 agent 就开一个去做；开不了就自己
按 skill 做完」，2 写着「自己按 skill 做完本节点，不要开子 agent」。`prompts.md` 抬头会记下
是哪种（`执行方式：会话内 · 开子 agent` / `会话内 · 只用主会话`）。

**默认选 1**：能开子 agent 就不拉进程，省一层进程边界 —— 开几个、要不要并行、模型用哪个，
都在同一个会话里掌握。选 3 必须给 `--agent`，否则直接报错退出，不会静默退回清单。
三个入口互斥：`--agent` / `--manual` / `--solo` 同时给两个也报错。

两种清单模式里门禁都按「假定通过」往下走，实际判定不满意时回对应的打回节点。

## 图的语义

| 字段 | 用在哪 | 含义 |
|---|---|---|
| `kind: milestone` | 主会话节点 | 里程碑，只记一条日志，不调独立 agent（预设里的「提测」「人工补测」） |
| `join: true` | 节点 | 等所有向前入边都到过再执行；打回边直接放行 |
| `parallel: true` | 决策的出边 | 与同选项的主出边并行，成为一个独立分支 |
| `batch: true` | 子 agent 节点 | 输出 `TASK:` 清单，交给后续节点逐条消费 |
| `repeatsBatch` | 子 agent 节点 | 逐条消费某个批量节点的任务 |
| `once: true` | 子 agent 节点 | 整个 workflow 只执行一次 |
| `loops[].backEdges` | 回路 | 打回边必须登记，超过 `maxIterations` 就停下等人 |

**并行不是多线程。** 调度器按声明顺序推进各条分支，遇到 `join` 节点时等齐再往下走。日志和人工确认因此是确定的，也能按顺序回放。

预设里两条测试回路：

| 回路 | 打回边 | 上限 | 打回到 |
|---|---|---|---|
| `dev` | 构建不满意、测试决策打回开发 | 3 | 修订输入 → 规划修订 |
| `e2e` | 测试决策修订 | 3 | 重新编写并运行 E2E |

## 安装预设

```bash
./agents-workflow-engine/scripts/install.sh <目标项目> --dry-run
./agents-workflow-engine/scripts/install.sh <目标项目>
```

只写 `.agents/workflow/preset.yaml`。已存在则跳过，`--force` 才覆盖。不碰 `overlay.yaml`。

## 什么时候能装到 poc

`poc-company-a/.agents/workflow/` 里那份引擎比本仓库新：它有 `stepper.py` 和
`start / submit / status / instances` 四个子命令，本仓库还没有。直接覆盖会丢功能。

三条都绿了才装：

- [ ] `stepper.py` 与那四个子命令回到本仓库，或明确决定不引入
- [ ] 本仓库版本 ≥ 项目里那版（看项目的 `.agents/workflow/engine/agents_workflow_engine/version.py`；0.1.x 没有这个文件）
- [ ] 用真 CLI 冒烟过一次：`run --agent '<真命令>'` 至少跑通一个节点

`install.sh` 会读项目里那版的 `version.py` 并与本预设对比，不一致就提示。

**预设和引擎必须成对升级。** 预设里的全局 `models` 旧引擎不认识，只装预设会让
13 个节点失去 `model:` 而静默退回主会话模型 —— 不报错，只是不再做对抗验证。
现在就往 poc 装预设也不安全，得连引擎一起换。

## 项目怎么改图

在目标项目放 `.agents/workflow/overlay.yaml`，可以 `disable` 节点、`replace` skill、改回路的 `maxIterations`。

`disable` 会连同节点相关的边一起删掉。例如禁用 `qa-write-cases` 后，`qa-run-e2e` 的汇入点只剩提测一侧，图仍然可跑。

## 维护

预设在 `presets/iteration-to-test.yaml`。形状说明在 `schema/graph.schema.json`。泳道预览在 [`graph.html`](graph.html)，与预设手工保持同步。

改了引擎行为（入参、提示词协议、日志字段、模型解析、子命令）要 bump
`agents_workflow_engine/version.py` 并在 [`CHANGELOG.md`](CHANGELOG.md) 加一节；
只改文档、注释、标题措辞不用 bump。验证脚本会核对两边版本号是否一致。