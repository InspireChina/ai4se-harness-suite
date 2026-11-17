# iteration1 · 咨询师预约平台（需求样例）

> 状态：**v0.1**（字段、规则、验收与原型已完成）  
> 日期：2026-11-16  
> 原型：独立 Vite Demo（Element Plus），见 [`prototypes/`](./prototypes/)（端口 5174）

## 1. 产品概述

线上咨询预约平台，覆盖「找咨询师 → 看档案 → 选时段 → 下单预约 → 履约 → 评价 → 结算」闭环。  
三端：终端用户、咨询师、平台管理员。

本期不覆盖：原生 App / 小程序、音视频通话、跨境结算、发票税务对接。

## 2. 特性索引

| Code | Spec | 覆盖源 REQ / 章节 | 角色 | 状态 |
|---|---|---|---|---|
| ACC | [ACC-account/spec.md](./ACC-account/spec.md) | §6.1 + REQ-006 | 三端 | v0.1 |
| CDC | [CDC-consultant-discovery/spec.md](./CDC-consultant-discovery/spec.md) | REQ-001、002 | 用户 | v0.1 |
| BKG | [BKG-booking/spec.md](./BKG-booking/spec.md) | REQ-003、004、005 | 用户 | v0.1 |
| COB | [COB-consultant-onboarding/spec.md](./COB-consultant-onboarding/spec.md) | REQ-007、008 | 咨询师 | v0.1 |
| CSC | [CSC-consultant-schedule/spec.md](./CSC-consultant-schedule/spec.md) | REQ-009 | 咨询师 | v0.1 |
| CFL | [CFL-consultant-fulfillment/spec.md](./CFL-consultant-fulfillment/spec.md) | REQ-010、012 | 咨询师 | v0.1 |
| SET | [SET-settlement/spec.md](./SET-settlement/spec.md) | REQ-011 | 咨询师 | v0.1 |
| ADM | [ADM-admin-ops/spec.md](./ADM-admin-ops/spec.md) | REQ-013～017 | 管理员 | v0.1 |
| PLT | [PLT-platform-capability/spec.md](./PLT-platform-capability/spec.md) | §6.2～6.6 | 横切 | v0.1 |

## 3. 迭代级 Plan

| Plan | 说明 |
|---|---|
| [plan-20261116-iteration1-feature-skeletons.md](./plan-20261116-iteration1-feature-skeletons.md) | 特性骨架 |
| [plan-20261116-iteration1-prototypes-and-specs.md](./plan-20261116-iteration1-prototypes-and-specs.md) | 原型与规格 |
| [plan-20261116-iteration1-prototypes-vite.md](./plan-20261116-iteration1-prototypes-vite.md) | Vite 原型 |

横切 / 无 feature 归属的方案见 [`../_chores/`](../_chores/)。

## 4. 里程碑（源 PRD）

| 阶段 | 范围 |
|---|---|
| M1 | 账号体系、用户端检索与主页 |
| M2 | 下单支付与咨询师履约 |
| M3 | 管理端审核、分类与治理 |
| M4 | 结算、通知与上线准备 |

## 5. 原型约定

- 独立 Vite 工程：[`prototypes/`](./prototypes/)（`npm run dev` → http://127.0.0.1:5174/）
- 技术：Vue 3 + Vue Router + Element Plus（**不**并入业务 `apps/frontend/`）
- 路由：`/` 入口；`/user/*`、`/consultant/*`、`/admin/*`
- 规格与原型冲突时，以规格中的业务规则与验收标准为准

## 6. v0.1 完成清单

9 份 spec 已完成：

- [x] §5 完整字段表
- [x] §7 可测试业务规则（含规则 ID，覆盖 CREATE / QUERY / UPDATE / DELETE / COMMON）
- [x] §9 状态流转（若有）
