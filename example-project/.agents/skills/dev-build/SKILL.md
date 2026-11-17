---
name: dev-build
description: 遵循四层 DDD 架构实现功能，并维护与 plan 同目录的细化进度文件。当为 example-project 编写后端或前端代码时使用。
---

# 开发：构建实现

按照 `AGENTS.md` 中的架构约定编写代码。Plan 已确认后方可动手。

## 进度文件（硬性）

与正在执行的 plan **同目录**，文件名 = plan 去 `.md` + `-progress.md`：

| plan | progress |
|---|---|
| `plan.md` | `plan-progress.md` |
| `plan-{slug}.md` | `plan-{slug}-progress.md` |

### 开工前

1. 读 plan 的 **「实施步骤（粗）」**（约 5～10 条）
2. 对照 §11 修改清单、§13 验证步骤、§15 事实/design 更新，把 **每条粗步骤细化为可勾选细项**（文件/模块/测试级）
3. 创建或重置对应 `*-progress.md`（总状态：进行中）

细项示例（粗步骤「领域与持久化」）：

- 聚合 / 实体
- 仓储接口与实现
- 迁移 / DDL

**不要**把细项回写进 plan（plan 定稿不改）。

### 格式

```markdown
# 实现进度：<plan 文件名>

> 关联 plan：./<plan-file>.md
> 状态：进行中 | 已完成 | 受阻
> 更新：YYYY-MM-DD HH:mm

## Checklist

### 1. <plan 粗步骤标题>
- [x] 细项 A
- [ ] 细项 B ← 进行中

### 2. …
- [ ] …

## 备注

- （失败原因 / 阻塞 / 跳过说明）
```

### 执行中

- 每完成一个细项：**立刻**勾选并刷新「更新」时间
- 当前细项可标 `← 进行中`
- 受阻：总状态改为「受阻」，原因写入备注
- 全部完成后：总状态改为「已完成」

## 后端

- `containers/backend/adapter/rest/` — Controller：仅做协议转换，不含业务逻辑
- `containers/backend/application/service/` — AppService：用例编排，`@Transactional`
- `containers/backend/domain/` — 聚合、值对象、领域服务：业务不变量
- `containers/backend/infrastructure/` — 持久化、安全、配置

层依赖关系：adapter → application → domain ← infrastructure

## 前端

- Vue 3 Composition API + `<script setup>`
- Pinia store 管理认证状态，位于 `containers/frontend/src/stores/auth.ts`
- 视图位于 `containers/frontend/src/views/user/` 或 `containers/frontend/src/views/admin/`
- Axios 拦截器处理 JWT 和 401 跳转

## 验证

```bash
cd containers/backend && mvn test
cd containers/frontend && npm run build
```

## 文档同步

实现完成后检查是否需要更新：

- `docs/facts/api.yaml` — API 变更
- `docs/facts/db-schema.md` — 数据库变更
- `docs/facts/tech-topic/businessrule.md` — 业务规则变更
- `docs/facts/tech-topic/data-dict.md` — 数据字典变更

## 自检清单

- [ ] 已按 plan 文件名写好同目录 `*-progress.md`，粗步骤已细化
- [ ] 执行过程中进度文件持续更新，结束时总状态正确
- [ ] 代码符合四层依赖，未在 adapter 写业务逻辑
- [ ] 相关测试已跑过（或已记入 progress 备注说明为何跳过）
- [ ] 需要的事实文档已同步或已列入后续任务
