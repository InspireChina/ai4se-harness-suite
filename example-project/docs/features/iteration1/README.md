# iteration1 · 咨询师预约平台（需求样例）

> 状态：**v0.1**（字段、规则、验收与原型已完成）  
> 日期：2026-11-16  
> 原型：独立 Vite Demo（Element Plus），见 [`prototypes/`](./prototypes/)（端口 5174）

## 1. 产品概述

线上咨询预约平台，覆盖「找咨询师 → 看档案 → 选时段 → 下单预约 → 履约 → 评价 → 结算」闭环。  
三端：终端用户、咨询师、平台管理员。

本期不覆盖：原生 App / 小程序、音视频通话、跨境结算、发票税务对接。

## 2. 特性索引

| Spec | 覆盖源 REQ / 章节 | 角色 | 状态 |
|---|---|---|---|
| [account.md](./account.md) | §6.1 + REQ-006 | 三端 | v0.1 |
| [consultant-discovery.md](./consultant-discovery.md) | REQ-001、002 | 用户 | v0.1 |
| [booking.md](./booking.md) | REQ-003、004、005 | 用户 | v0.1 |
| [consultant-onboarding.md](./consultant-onboarding.md) | REQ-007、008 | 咨询师 | v0.1 |
| [consultant-schedule.md](./consultant-schedule.md) | REQ-009 | 咨询师 | v0.1 |
| [consultant-fulfillment.md](./consultant-fulfillment.md) | REQ-010、012 | 咨询师 | v0.1 |
| [settlement.md](./settlement.md) | REQ-011 | 咨询师 | v0.1 |
| [admin-ops.md](./admin-ops.md) | REQ-013～017 | 管理员 | v0.1 |
| [platform-capability.md](./platform-capability.md) | §6.2～6.6 | 横切 | v0.1 |

## 3. 里程碑（源 PRD）

| 阶段 | 范围 |
|---|---|
| M1 | 账号体系、用户端检索与主页 |
| M2 | 下单支付与咨询师履约 |
| M3 | 管理端审核、分类与治理 |
| M4 | 结算、通知与上线准备 |

## 4. 原型约定

- 独立 Vite 工程：[`prototypes/`](./prototypes/)（`npm run dev` → http://127.0.0.1:5174/）
- 技术：Vue 3 + Vue Router + Element Plus（**不**并入业务 `apps/frontend/`）
- 路由：`/` 入口；`/user/*`、`/consultant/*`、`/admin/*`
- 规格与原型冲突时，以规格中的业务规则与验收标准为准

## 5. v0.1 完成清单

9 份 spec 已完成：

- [x] §5 完整字段表
- [x] §7 可测试业务规则（含规则 ID，覆盖 CREATE / QUERY / UPDATE / DELETE / COMMON）
- [x] §9 状态流转（若有）
- [x] §12 Given-When-Then 验收标准
- [x] §14 挂接独立 Vite 原型路由
