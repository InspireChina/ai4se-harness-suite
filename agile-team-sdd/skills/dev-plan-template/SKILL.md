---
name: dev-plan-template
description: 在编写任何代码之前在 {{PLANS_DIR}}/ 中创建开发计划。当开始新功能、重构或任何非简单变更时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 开发：制定计划

在实现前在 `{{PLANS_DIR}}/` 中创建计划。

## 模板

使用 `{{PLANS_DIR}}/_template.md` 作为模板，包含以下核心章节：

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
14. 实施后需更新的 design 文档

## 规则

- 计划必须经用户审核确认后方可继续（{{AGENTS_FILE}} §14 第 1 步）
- 包含每个需要变更的文件的路径
- 参考现有模式（assembler、converter、service）以保持一致性
- 考虑文档同步：本次变更是否会影响 `{{DESIGNS_DIR}}/` 中的文件？
- **plan 一旦定稿就不修改**，同一资源的二次改造新建 `YYYYMMDD-{slug}.md`
