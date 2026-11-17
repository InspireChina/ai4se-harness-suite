---
name: dev-plan
description: 在编写任何代码之前为对应 feature 创建开发计划（plan.md），并必须编写可执行的开发自测用例（DST）与有 UI 时的界面对照基线。当开始新功能、重构或任何非简单变更时使用。
---

# 开发：制定计划

在实现前为需求写技术方案，并与规格放在同一 feature 目录。

## 前置

- 本迭代 `docs/features/<迭代>/high-level-design.md` **已人工确认**（由 `tl-high-level-design` 产出）
- 已读对应 feature 的 `spec.md`，并对照 HLD 中的跨模块契约
- HLD 未确认时 **停止**，不要写 `plan.md`

## 输出位置

| 场景 | 路径 |
|---|---|
| 有明确 feature | `docs/features/<迭代>/<CODE>-<slug>/plan.md`（首份）或 `plan-{slug}.md`（后续） |
| 无关联 feature 的横切改造 | `docs/features/_chores/plan-{slug}.md` |

模板：`docs/features/_template/plan.md`。

## 模板核心章节

1. 文档说明（背景、目标）
2. 领域模型（PlantUML）
3. 数据库设计（SQL DDL）
4. API 设计（OpenAPI）
5. 时序图（PlantUML）
6. 专题设计（权限、并发、事务、异常、性能、扩展性）
7. 一致性约束
8. 单元测试设计（**含 DST 场景表**）
9. API 集成测试设计（**含 DST 场景表**）
10. E2E / 前端交互测试设计（**含 DST 场景表**）
11. **界面对照基线**（有 UI 时必填）
12. 修改清单（代码、接口、数据库变更）
13. **实施步骤（粗）** — 5～10 条，供评审；细项留给 `dev-build` 的 progress
14. 验证步骤
15. 风险与回滚
16. 实施后需更新的事实文档

## 开发自测用例（硬性）

Plan **必须**写出可被 `dev-self-test` 执行的自测场景，编号空间 **`DST-xxx`**（勿用 QA 的 `TC-xxx`）。

| 要求 | 说明 |
|---|---|
| 可执行 | 每条 DST 写清：前置 / 步骤或命令入口 / 期望；不能只写章节标题 |
| 可勾选 | 用表格或 checklist；`dev-build` / `dev-self-test` 按表执行 |
| 分层 | §8 单元、§9 API 集成（打真实本地服务）、§10 E2E/前端交互 |
| 索引 | 实现后可把场景登记到 `docs/test-cases/dev-self-cases/`（可选文本索引） |

场景表最低列：`DST` | 层（unit/api/e2e） | 说明 | 期望 | 关联章节/AC

## 界面对照基线（有 UI 时硬性）

供 `dev-ui-review` 使用。写明：

| 项 | 内容 |
|---|---|
| 原型 | 路径（默认 `docs/features/<迭代>/prototypes/`）与启动方式（如 `npm run dev`）、路由列表 |
| 实现页 | 前端路由 / 页面路径 |
| 字段与控件 | 对照 `spec` 字段表：字段名、控件类型、必填/校验、与原型是否一致 |
| 关键态 | 加载 / 空 / 错误 / 成功（至少列出要对照的页面） |

无 UI：在 plan 注明「无界面对照基线」及原因。

## 粗步骤 vs 进度文件

- Plan 里的「实施步骤」必须 **粗**：按阶段/层概括即可
- **不要**在 plan 里写到文件级任务清单
- 实现期由 `dev-build` 在同目录写 `{planStem}-progress.md`；自测/UI 记录见 `dev-self-test` / `dev-ui-review`
- **不回写**已定稿的 plan

## 规则

- 计划必须经用户审核确认后方可继续（AGENTS.md §14 Plan 闸门）
- Plan 不得推翻已确认 HLD 的技术边界与契约权属；若需变更，先修订 HLD 并重新确认
- 包含每个需要变更的文件的路径
- 参考现有模式（assembler、converter、service）以保持一致性
- 考虑文档同步：本次变更是否会影响 `docs/facts/` 中的文件？
- **plan 一旦定稿就不修改**；同一 feature 的二次改造新建 `plan-{slug}.md`
- 自检：已写粗实施步骤；**DST 场景表非空**；有 UI 则界面对照基线非空
