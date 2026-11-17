---
name: dev-build-template
description: 遵循四层 DDD 架构实现功能。当为 {{PROJECT_NAME}} 编写后端或前端代码时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 开发：构建实现

按照 `{{AGENTS_FILE}}` 中的架构约定编写代码。

## 后端

- `{{BACKEND_DIR}}/adapter/rest/` — Controller：仅做协议转换，不含业务逻辑
- `{{BACKEND_DIR}}/application/service/` — AppService：用例编排，`@Transactional`
- `{{BACKEND_DIR}}/domain/` — 聚合、值对象、领域服务：业务不变量
- `{{BACKEND_DIR}}/infrastructure/` — 持久化、安全、配置

层依赖关系：adapter → application → domain ← infrastructure

## 前端

- Vue 3 Composition API + `<script setup>`
- Pinia store 管理认证状态，位于 `{{FRONTEND_DIR}}/src/stores/auth.ts`
- 视图位于 `{{FRONTEND_DIR}}/src/views/user/` 或 `{{FRONTEND_DIR}}/src/views/admin/`
- Axios 拦截器处理 JWT 和 401 跳转

## 验证

```bash
{{TEST_CMD_BACKEND}}
{{TEST_CMD_FRONTEND}}
```

## 文档同步

实现完成后检查是否需要更新：
- `{{DESIGNS_DIR}}/api.yaml` — API 变更
- `{{DESIGNS_DIR}}/db-schema.md` — 数据库变更
- `{{DESIGNS_DIR}}/topic/businessrule.md` — 业务规则变更
- `{{DESIGNS_DIR}}/topic/data-dict.md` — 数据字典变更
