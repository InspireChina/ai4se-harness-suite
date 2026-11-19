# agents-workflow-engine

一个人用主会话把一条迭代从启动调度到测试通过。图是 YAML。人、graph-master、子 agent 分三道泳道。子 agent 调用 skill，并且可以绑不同模型做对抗验证。

预设的主线：

```
需求规格 → 需求质量门 → 需求决策 ─┬─ 编写 QA 用例（并行侧分支）────────┐
                                  └─ 技术高阶 → 迭代 HLD → 详细规划 → 开发 → 提测
                                                                          │
                                            测试通过 ← 测试决策 ← 编写并运行 E2E ←┘
```

## 用法

在仓库根目录：

```bash
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine validate
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine render --dry-run
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine run \
  --project <目标项目> --answers answers.yaml --agent '你的子 agent 命令'
```

`answers.yaml` 里，人的节点对应一段文字或该决策的选项。同一节点要答多次时写成列表。

- 需求/高阶/plan/构建决策：`满意` 或 `不满意`
- 测试决策：`修订`、`通过`、`打回开发`

子 agent 命令会额外收到 `--skill`、`--node`、`--model`。批量构建还会收到 `--task`。环境变量 `WORKFLOW_TASK` 是同一条任务。门禁要在标准输出单独一行打印 `满意` 或 `不满意`。`dev-plan` 用 `TASK: <id>` 宣布一批任务。

模型用环境变量，不写进仓库：`MODEL_WRITER`、`MODEL_REVIEWER`。两个值相同，或没设，会在 `.agents/workflow/decisions.jsonl` 记下「未做对抗验证」。

## 图的语义

| 字段 | 用在哪 | 含义 |
|---|---|---|
| `kind: milestone` | 主会话节点 | 里程碑，只记一条日志，不调子 agent（预设里的「提测」） |
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

## 项目怎么改图

在目标项目放 `.agents/workflow/overlay.yaml`，可以 `disable` 节点、`replace` skill、改回路的 `maxIterations`。

`disable` 会连同节点相关的边一起删掉。例如禁用 `qa-write-cases` 后，`qa-run-e2e` 的汇入点只剩提测一侧，图仍然可跑。

## 维护

预设在 `presets/iteration-to-test.yaml`。形状说明在 `schema/graph.schema.json`。泳道预览在仓库 `.agents/plan/iteration-to-test.html`。