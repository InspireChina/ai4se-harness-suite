# Plan：工作流引擎接入 QA 用例与 E2E 回路

## 背景

预览图 [graph.html](../../agents-workflow-engine/graph.html) 已经调整到新流程：

1. 需求决策后，`qa-write-cases` 与技术高阶并行；
2. `dev-plan` 节点说明里列出详细设计（API/DB 字段、文件改动）、任务清单、自测用例（DST）；
3. 提测后增加「编写并运行 E2E 测试」和「测试决策」，可选修订重跑、通过、打回开发修订 plan；
   打回开发回到构建决策下面的「修订输入」。

本轮把这个图落进 `agents-workflow-engine` 的预设与调度器。

## 引擎改动

### 新语义

| 语义 | 字段 | 行为 |
|---|---|---|
| 里程碑 | `kind: milestone` | 主会话节点，只记日志，不调子 agent；本次用于「提测」 |
| 并行分支 | 决策出边 `parallel: true` | 同一选项下一条主出边 + 若干侧出边；侧分支独立推进 |
| 汇入 | 节点 `join: true` | 等所有向前入边都到过再执行；打回边直接放行 |

并行不是多线程：调度器按声明顺序推进 token，侧分支先走，主路径随后，在汇入点等齐。

### 预设

- 新增 `qa-write-cases`（需求决策的并行侧分支）与 `qa-run-e2e`（汇入点）。
- `handoff` 由终点改为里程碑，新增终点 `accepted`（人工补测）。
- 新增 `test-decision`，选项 `修订` / `通过` / `打回开发`。
- 新回路 `e2e`（修订重跑，上限 3）；`dev` 回路增加 `e2e-reject` 打回边。
- `dev-plan` 增加 `note`，说明详细设计、任务清单、自测用例。
- 删除原 `extensions` 里的 QA 占位（已接入主线）。

### 校验与渲染

- 决策出边不再限制为满意/不满意，按节点 `options` 校验；门禁仍只认满意/不满意。
- 决策同一选项必须恰好一条主出边；`parallel` 只能出现在决策出边，也不能是打回边。
- 汇入节点的向前入边不能带 `when`，避免等不到；入口/终点不能做汇入点。
- 里程碑必须是 master、恰好一条出边、不带 skill/options。
- Mermaid 渲染：`parallel` 边标「并行」，`join` 节点标「汇入」，里程碑标「里程碑」，节点 `note` 全部显示。

## 验证

```bash
python3 agents-workflow-engine/tests/test_units.py   # 24 个用例
./.agents/verify.sh
```

新增用例覆盖：并行分支先于技术高阶、汇入点等待提测、修订重跑 E2E、
打回开发重跑 dev-plan/dev-build、E2E 回路上限、覆盖禁用 QA 用例后仍可跑通。

## 文档同步

- [x] `agents-workflow-engine/README.md`
- [x] `agents-workflow-engine/schema/graph.schema.json`
- [x] 根 `README.md` 模块职责
- [x] `AGENTS.md` §1 拓扑与 §8 模块职责
- [x] `cli.py --help` 与 `state.py` 文案