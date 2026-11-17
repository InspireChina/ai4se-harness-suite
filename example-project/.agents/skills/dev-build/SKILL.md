---
name: dev-build
description: 全栈实现编排：按 Plan 写前后端、维护细化进度，并依次调用自测、界面评审、代码评审；失败则修 bug 回环。当 Plan 已确认、进入实现时使用。
---

# 开发：构建实现（全栈编排）

`dev-build` 是 **全栈实现编排器**，不是「只写代码」。Plan 已确认后方可动手。

按 `AGENTS.md` 架构约定实现，并 **依次执行** 下列依赖 skill（读其已安装正文并照做，不要跳步）：

```
① 实现（本 skill）→ ② dev-self-test → ③ dev-ui-review（有 UI 时）→ ④ dev-code-review
         ↑____________ 失败 / 评审问题：修 bug 后从对应步骤重跑 _____________↓
```

| 阶段 | 调用 | 目的 |
|---|---|---|
| 实现 | 本 skill | 前后端按 Plan + progress 落地 |
| 自测 | `dev-self-test` | 单元/集成/构建/E2E 自测；失败则改实现再测 |
| 界面 | `dev-ui-review` | chrome-devtools-mcp 实机看结构/视觉/交互/控制台/网络 |
| 评审 | `dev-code-review` | 对照 `AGENTS` / standards / facts 自查 diff |
| 调试（按需） | `dev-debug` | 自测或 UI 卡住时用 chrome-mcp 查根因，再回到自测/实现 |

**硬性**：未跑通自测不得宣称 build 完成；有前端改动时不得跳过 `dev-ui-review`；`dev-code-review` 通过前不得进入 `dev-create-mr`。

## 进度文件（硬性）

与正在执行的 plan **同目录**，文件名 = plan 去 `.md` + `-progress.md`：

| plan | progress |
|---|---|
| `plan.md` | `plan-progress.md` |
| `plan-{slug}.md` | `plan-{slug}-progress.md` |

### 开工前

1. 读 plan 的 **「实施步骤（粗）」**（约 5～10 条）
2. 对照修改清单、验证步骤、事实/design 更新，把粗步骤 **细化** 为可勾选细项
3. 在 checklist **末尾追加编排阶段**（若尚无）：

```markdown
### 编排
- [ ] 实现（前后端）
- [ ] dev-self-test
- [ ] dev-ui-review（无 UI 改动可注明跳过）
- [ ] dev-code-review
```

4. 创建或重置对应 `*-progress.md`（总状态：进行中）

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

### 编排
- [ ] 实现（前后端）
- [ ] dev-self-test
- [ ] dev-ui-review
- [ ] dev-code-review

## 备注

- （失败原因 / 阻塞 / 跳过说明）
```

### 执行中

- 每完成一个细项或编排阶段：**立刻**勾选并刷新「更新」时间
- 当前项可标 `← 进行中`；受阻写备注并改总状态
- 全部完成后（含编排四步）：总状态「已完成」

## ① 实现

### 后端

- `containers/backend/adapter/rest/` — Controller：仅做协议转换，不含业务逻辑
- `containers/backend/application/service/` — AppService：用例编排，`@Transactional`
- `containers/backend/domain/` — 聚合、值对象、领域服务：业务不变量
- `containers/backend/infrastructure/` — 持久化、安全、配置

层依赖：adapter → application → domain ← infrastructure

### 前端

- Vue 3 Composition API + `<script setup>`
- Pinia store 管理认证状态，位于 `containers/frontend/src/stores/auth.ts`
- 视图位于 `containers/frontend/src/views/user/` 或 `containers/frontend/src/views/admin/`
- Axios 拦截器处理 JWT 和 401 跳转

实现细项勾完后，进入 ②。

## ② 自测 — 调用 `dev-self-test`

完整按已安装的 `dev-self-test` skill 执行（由快到慢：后端单测 → 集成 → 前端构建/单测 → E2E 自测）。

- 失败：按该 skill 的失败分类改 **实现**（或测试隔离），**禁止**改断言迁就实现、删用例、改 QA 用例
- 环境/浏览器深层问题：可切 `dev-debug`（chrome-devtools-mcp），修好后回到 `dev-self-test`
- 自测绿：勾选 progress「dev-self-test」，进入 ③

快速命令（细节以 `dev-self-test` 为准）：

```bash
cd containers/backend && mvn test
cd containers/frontend && npm run build
```

## ③ 界面评审 — 调用 `dev-ui-review`（有 UI 时）

本次若改了前端页面 / 交互：完整按 `dev-ui-review`（chrome-devtools-mcp：结构 → 视觉 → 控制台/网络 → 交互）。

- 无 UI 改动：在 progress 注明跳过原因并勾选
- 发现问题：修代码 → ② 自测 → 再 ③
- 通过：勾选「dev-ui-review」

## ④ 代码评审 — 调用 `dev-code-review`

完整按 `dev-code-review`（先读 `AGENTS.md` / `docs/standards` / `docs/facts`，再看 diff）。

- 有必须修的问题：改代码 → ②（必要时 ③）→ 再 ④
- 通过：勾选「dev-code-review」

## 文档同步

编排通过后检查是否需要更新：

- `docs/facts/api.yaml` — API 变更
- `docs/facts/db-schema.md` — 数据库变更
- `docs/facts/tech-topic/businessrule.md` — 业务规则变更
- `docs/facts/tech-topic/data-dict.md` — 数据字典变更

事实校准可用 `ba-gen-facts`（不阻塞 build 闭环，但合并前应处理）。

## 自检清单

- [ ] progress 已写，粗步骤已细化，编排四步已勾选（或注明合法跳过）
- [ ] `dev-self-test` 已按 skill 跑通
- [ ] 有 UI 时 `dev-ui-review` 已按 skill 跑通；否则已注明跳过
- [ ] `dev-code-review` 已按 skill 自查通过
- [ ] 代码符合四层依赖；未在 adapter 写业务逻辑
- [ ] 需要的事实文档已同步或已列入后续任务
