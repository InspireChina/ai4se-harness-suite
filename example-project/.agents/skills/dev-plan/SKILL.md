---
name: dev-plan
description: 在编写任何代码之前为对应 feature 创建开发计划（plan.md）。当开始新功能、重构或任何非简单变更时使用。
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
8. 单元测试设计
9. API 集成测试设计
10. E2E 测试设计
11. 修改清单（代码、接口、数据库变更）
12. 验证步骤
13. 风险与回滚
14. 实施后需更新的事实文档

## 规则

- 计划必须经用户审核确认后方可继续（AGENTS.md §14 Plan 闸门）
- Plan 不得推翻已确认 HLD 的技术边界与契约权属；若需变更，先修订 HLD 并重新确认
- 包含每个需要变更的文件的路径
- 参考现有模式（assembler、converter、service）以保持一致性
- 考虑文档同步：本次变更是否会影响 `docs/facts/` 中的文件？
- **plan 一旦定稿就不修改**；同一 feature 的二次改造新建 `plan-{slug}.md`
