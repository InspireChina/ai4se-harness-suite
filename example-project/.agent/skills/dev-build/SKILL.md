---
name: dev-build
description: 遵循四层 DDD 架构实现功能。当为 咨询预约平台 编写后端或前端代码时使用。
---

# 开发：构建实现

按照 `AGENTS.md` 中的架构约定编写代码。

## 后端

- `backend/adapter/rest/` — Controller：仅做协议转换，不含业务逻辑
- `backend/application/service/` — AppService：用例编排，`@Transactional`
- `backend/domain/` — 聚合、值对象、领域服务：业务不变量
- `backend/infrastructure/` — 持久化、安全、配置

层依赖关系：adapter → application → domain ← infrastructure

## 前端

- Vue 3 Composition API + `<script setup>`
- Pinia store 管理认证状态，位于 `frontend/src/stores/auth.ts`
- 视图位于 `frontend/src/views/user/` 或 `frontend/src/views/admin/`
- Axios 拦截器处理 JWT 和 401 跳转

## 验证

```bash
cd backend && mvn test
cd frontend && npm run build
```

## 文档同步

实现完成后检查是否需要更新：
- `docs/designs/api.yaml` — API 变更
- `docs/designs/db-schema.md` — 数据库变更
- `docs/designs/topic/businessrule.md` — 业务规则变更
- `docs/designs/topic/data-dict.md` — 数据字典变更
