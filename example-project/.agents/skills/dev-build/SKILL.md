---
name: dev-build
description: 全栈实现 LOOP：按 Plan 写前后端、维护 progress，并依次调用自测与 UI 评审（落盘记录）及代码评审；以记录为准修到通过。当 Plan 已确认、进入实现时使用。
---

# 开发：构建实现（全栈 LOOP）

`dev-build` 是 **全栈实现 LOOP**，不是「只写代码」。Plan 已确认后方可动手。

按 `AGENTS.md` 架构约定实现，并 **依次执行** 下列依赖 skill（读其已安装正文并照做，不要跳步）：

```
① 实现 → ② dev-self-test → ③ dev-ui-review（有 UI 时）→ ④ dev-code-review
    ↑_____ 失败：以 *-self-test.md / *-ui-review.md 为准修 bug 后从对应步重跑 _____↓
```

| 阶段 | 调用 | 目的 | 通过判据 |
|---|---|---|---|
| 实现 | 本 skill | 前后端按 Plan + progress 落地 | progress 实现项勾完 |
| 自测 | `dev-self-test` | **真实本地环境** + 按 DST 执行并落盘 | `{planStem}-self-test.md` 状态=通过 |
| 界面 | `dev-ui-review` | 原型对照、字段/控件与截图、落盘 | `{planStem}-ui-review.md` 状态=通过（或无 UI 已注明跳过） |
| 评审 | `dev-code-review` | 对照 AGENTS / standards / facts | 评审结论通过 |
| 调试（按需） | `dev-debug` | 自测或 UI 卡住时查根因 | 回到自测/UI |

**硬性**：

- 未写出并通过 `*-self-test.md` 不得宣称 build 完成
- 有前端改动时不得跳过 `dev-ui-review`；须有 `*-ui-review.md` 通过（或合法跳过说明）
- **口头「应该过了」无效**，以记录文件为准
- `dev-code-review` 通过前不得进入 `dev-create-mr`

## 进度文件（硬性）

与正在执行的 plan **同目录**，文件名 = plan 去 `.md` + `-progress.md`。

### 开工前

1. 读 plan 的 **「实施步骤（粗）」** 与 **DST / 界面对照基线**
2. 细化 checklist；末尾追加 LOOP 阶段：

```markdown
### LOOP
- [ ] 实现（前后端）
- [ ] dev-self-test → 产物 `{planStem}-self-test.md` 通过
- [ ] dev-ui-review → 产物 `{planStem}-ui-review.md` 通过（无 UI 注明跳过）
- [ ] dev-code-review
```

3. 创建或重置 `*-progress.md`（总状态：进行中）

**不要**把细项回写进 plan。

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

### LOOP
- [ ] 实现（前后端）
- [ ] dev-self-test（./plan-self-test.md）
- [ ] dev-ui-review（./plan-ui-review.md）
- [ ] dev-code-review

## 备注

- （失败原因 / 阻塞 / 跳过说明）
```

### 执行中

- 每完成细项或 LOOP 阶段：立刻勾选并刷新「更新」时间
- 全部完成后（含 LOOP）：总状态「已完成」

## ① 实现

### 后端

- `containers/backend/adapter/rest/` — Controller：仅协议转换
- `containers/backend/application/service/` — AppService：`@Transactional`
- `containers/backend/domain/` — 聚合、值对象、领域服务
- `containers/backend/infrastructure/` — 持久化、安全、配置

层依赖：adapter → application → domain ← infrastructure

### 前端

- Vue 3 Composition API + `<script setup>`
- 按项目约定放置 views / stores；JWT 与 401 处理齐全

实现细项勾完后进入 ②。

## ② 自测 — 调用 `dev-self-test`

完整按已安装的 `dev-self-test` 执行：

- **先起真实本地环境**，再按 plan DST 跑；写出 `{planStem}-self-test.md`
- 失败：改实现或环境 → 重跑 → 更新记录；禁止改断言迁就、删用例、改 QA 用例
- 深层问题可切 `dev-debug`，再回到自测
- 记录状态=通过后，勾选 progress「dev-self-test」，进入 ③

## ③ 界面评审 — 调用 `dev-ui-review`（有 UI 时）

- 启动原型（若有）+ 实现环境；按界面对照基线做字段/控件与截图对比；写出 `{planStem}-ui-review.md`
- 无 UI：progress 注明跳过原因并勾选
- 失败：修前端 →（必要时 ②）→ 再 ③，直到记录通过
- 通过后勾选「dev-ui-review」

## ④ 代码评审 — 调用 `dev-code-review`

- 有必须修的问题：改代码 → ②（必要时 ③）→ 再 ④
- 通过：勾选「dev-code-review」

## 文档同步

LOOP 通过后检查：

- `docs/facts/api.yaml`、`db-schema.md`
- `docs/facts/tech-topic/businessrule.md`、`data-dict.md`
- 可选：`docs/test-cases/dev-self-cases/` 索引

可用 `ba-gen-facts`（不阻塞 build 闭环，合并前应处理）。

## 自检清单

- [ ] progress 已写，LOOP 项已勾选（或合法跳过）
- [ ] `{planStem}-self-test.md` 存在且状态=通过
- [ ] 有 UI 时 `{planStem}-ui-review.md` 存在且状态=通过；否则已注明跳过
- [ ] `dev-code-review` 自查通过
- [ ] 代码符合四层依赖；事实文档已同步或已列入后续
