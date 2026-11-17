# iteration1 · 高阶技术设计（HLD）

> 文档类型：迭代高阶技术方案 / TRD  
> 路径：`docs/features/iteration1/high-level-design.md`  
> 版本：v0.1  
> 作者：TL  
> 日期：2026-11-17  
> 状态：**待确认** — 确认前不得编写 feature `plan.md` 或开始实现

---

## 1. 背景与目标

### 1.1 背景

- 目标需求：本目录下 ACC～PLT 共 9 份 `spec.md` + [`prototypes/`](./prototypes/)。
- 工程现状：业务实现已清空为可编译空壳（见 `_chores/plan-20261117-purge-demo-impl-for-iteration1.md`）。
- 本 HLD 给出 **本迭代技术边界与跨模块契约**，供各 feature Plan 对齐。

### 1.2 目标

- 明确三端（用户 / 咨询师 / 管理）共用的技术底座与模块边界。
- 约定跨 feature 契约（账号、订单、档期、结算、通知等），避免 Plan 各自发明。
- 指出需沉淀为 ADR 的长期取舍（若与既有 ADR 冲突则先改 ADR）。

### 1.3 非目标

- 不展开单 feature 的表结构 / API 细节（写在各自 `plan.md`）。
- 不覆盖原生 App / 小程序、音视频通话、跨境结算、发票税务对接（与迭代 README 一致）。

---

## 2. 本迭代范围

| Code | Feature | 技术关注点（摘要） |
|---|---|---|
| ACC | [账号与个人中心](./ACC-account/spec.md) | 统一账号、角色开通、资料与协议 |
| CDC | [咨询师发现](./CDC-consultant-discovery/spec.md) | 检索、档案展示、收藏入口 |
| BKG | [预约下单](./BKG-booking/spec.md) | 下单、支付、评价与投诉 |
| COB | [咨询师入驻](./COB-consultant-onboarding/spec.md) | 入驻申请与审核 → 角色开通 |
| CSC | [咨询师档期](./CSC-consultant-schedule/spec.md) | 可约时段、占用与释放 |
| CFL | [咨询师履约](./CFL-consultant-fulfillment/spec.md) | 接单、改期、小结、看板 |
| SET | [结算](./SET-settlement/spec.md) | 账单、提现、费率版本 |
| ADM | [管理运营](./ADM-admin-ops/spec.md) | 审核、类目、治理、退款 |
| PLT | [平台能力](./PLT-platform-capability/spec.md) | 通知、回调、审计、限流、隐私请求 |

---

## 3. 技术边界

### 3.1 部署与栈（继承既有 ADR）

| 决策 | 依据 |
|---|---|
| 四层 DDD 单体 | [ADR-001](../../facts/tech-topic/001-4-layer-ddd.md) |
| UUID 字符串主键 | [ADR-002](../../facts/tech-topic/002-uuid-string-pk.md) |
| MyBatis-Plus | [ADR-003](../../facts/tech-topic/003-mybatis-plus-vs-jpa.md) |
| JWT 无状态鉴权 | [ADR-004](../../facts/tech-topic/004-jwt-stateless-auth.md) |
| ThreadLocal 用户上下文 | [ADR-005](../../facts/tech-topic/005-threadlocal-usercontext.md) |

工程布局：`containers/backend`（Spring Boot）+ `containers/frontend`（Vue 3）；本迭代原型仅在 `prototypes/`，**不**并入业务前端直至对应 Plan 确认。

### 3.2 本迭代补充边界

- API：REST + 统一错误体；契约以实现后的 `docs/facts/api.yaml` 为准，Plan 阶段先按 OpenAPI 草案对齐。
- 多角色：同一 Account 可持有 USER / CONSULTANT / ADMIN；咨询师端访问受入驻审核状态约束（见 ACC / COB）。
- 支付 / 退款 / 提现：经支付网关回调；回调幂等键与处理状态由 PLT 约定，业务单状态由 BKG / SET 拥有。
- 通知：站内信必达路径由 PLT 提供；业务模块只发领域事件语义，不直连短信供应商。

---

## 4. 跨模块契约（摘要）

| 契约 | 提供方 | 消费方 | 说明 |
|---|---|---|---|
| Account / 角色 | ACC | 全模块 | 鉴权与权限判断入口 |
| Consultant 可展示档案 | COB + CDC | BKG / 收藏 | 未通过审核不可被检索下单 |
| TimeSlot 占用 | CSC | BKG / CFL | 下单锁定、改期换档、取消释放 |
| BookingOrder 状态机 | BKG | CFL / SET / ADM | 履约与结算只认约定状态 |
| FeeRateVersion | PLT / SET | SET 出账 | 按下单时费率版本计费 |
| 支付/退款回调 | PLT | BKG / SET | 验签 + 幂等后再驱动业务状态 |
| 审计日志 | PLT | ADM | 管理操作可检索导出 |

细则以各 feature spec §5 / §7 / §9 为准；Plan 不得发明与上表冲突的权属。

---

## 5. 开放决策

> 确认 HLD 前应关闭或明确延期。关闭后若属跨迭代取舍，按 [`docs/standards/adr.md`](../../standards/adr.md) 沉淀。

| ID | 问题 | 倾向 | 状态 |
|---|---|---|---|
| OD-001 | 支付网关首期范围（微信 / 支付宝 / 模拟） | 待 TL 拍板 | 开放 |
| OD-002 | 档期时区与夏令时策略 | Asia/Shanghai，存 UTC | 提议 |
| OD-003 | 评价公开可见性与敏感词策略 | 过词后公开 | 提议 |

---

## 6. 确认清单

- [ ] 范围与非目标与迭代 README / 九份 spec 一致
- [ ] 技术边界与既有 ADR 无冲突（或已更新 ADR）
- [ ] 跨模块契约权属清晰，无双头所有
- [ ] 开放决策已关闭或标明延期不影响开工顺序
- [ ] **人工确认**本文件后，方可对各 feature 执行 `dev-plan`

---

## 7. AI 实现提示

1. 先读本 HLD，再读目标 feature 的 `spec.md`，最后写 `plan.md`。
2. 不要在 Plan 中推翻 §3 / §4，除非先修订并重新确认本 HLD。
3. 新增跨迭代技术取舍时，按 `docs/standards/adr.md` 写 ADR 落到 `docs/facts/tech-topic/`。
