# agents-workflow-engine

一个人用主会话把一条迭代从启动调度到提测。图是 YAML。人、graph-master、子 agent 分三道泳道。子 agent 调用 skill，并且可以绑不同模型做对抗验证。

## 用法

在仓库根目录：

```bash
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine validate
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine render --dry-run
PYTHONPATH=agents-workflow-engine python -m agents_workflow_engine run \
  --project <目标项目> --answers answers.yaml --agent '你的子 agent 命令'
```

`answers.yaml` 里，人的节点对应一段文字或「满意 / 不满意」。同一节点要答多次时写成列表。

子 agent 命令会额外收到 `--skill`、`--node`、`--model`。批量构建还会收到 `--task`。环境变量 `WORKFLOW_TASK` 是同一条任务。门禁要在标准输出单独一行打印 `满意` 或 `不满意`。`dev-plan` 用 `TASK: <id>` 宣布一批任务。

模型用环境变量，不写进仓库：`MODEL_WRITER`、`MODEL_REVIEWER`。两个值相同，或没设，会在 `.agents/workflow/decisions.jsonl` 记下「未做对抗验证」。

## 安装预设

```bash
./agents-workflow-engine/scripts/install.sh <目标项目> --dry-run
./agents-workflow-engine/scripts/install.sh <目标项目>
```

只写 `.agents/workflow/preset.yaml`。已存在则跳过，`--force` 才覆盖。不碰 `overlay.yaml`。

## 项目怎么改图

在目标项目放 `.agents/workflow/overlay.yaml`，可以 `disable` 节点、`replace` skill、改回路的 `maxIterations`。

## 维护

预设在 `presets/iteration-to-test.yaml`。形状说明在 `schema/graph.schema.json`。泳道预览在仓库 `.agents/plan/iteration-to-test.html`。
