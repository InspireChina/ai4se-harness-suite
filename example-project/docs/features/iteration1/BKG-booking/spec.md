# 需求规格说明书：预约下单与订单评价

> 文档类型：需求规格 / Feature Specification  
> 适用目录：`docs/features/iteration1/`  
> 需求类型：NEW  
> 版本：v0.1  
> 作者：BA  
> 日期：2026-11-16  
> 状态：**v0.1** — 字段/规则/验收已补齐；原型已挂接  
> 源追溯：REQ-003、REQ-004、REQ-005

---

## 1. 需求说明

### 1.1 需求名称

预约下单与订单评价

### 1.2 需求类型

NEW

### 1.3 版本信息

| 项目 | 内容 |
|---|---|
| 基线版本 | 无 |
| 目标版本 | v0.1 |

### 1.4 背景

用户选定咨询师与时段后，需要下单支付、管理预约全生命周期，并在完成后评价。

### 1.5 目标

打通「选时段 → 下单 → 支付 → 订单管理 → 评价」用户侧闭环。

### 1.6 范围

本次包含：

- 下单页（主题、描述、联系方式、费用明细、优惠券）
- 微信/支付宝支付；超时关单释档
- 未开始订单取消（填原因）
- 我的预约筛选、详情、时间线、再次预约
- 超时未履约投诉入口
- 完成后 14 天内一次评价（多维评分 + 文字）

本次不包含：

- 咨询师确认/履约（见 consultant-fulfillment.md）
- 退款治理（见 admin-ops.md）
- 支付网关幂等细节（见 platform-capability.md）

---

## 2. 功能说明

术语表见 [项目术语表](../../../architecture/business/glossary.md)。

### 2.1 功能概述

用户创建预约订单并支付；在「我的预约」管理状态与详情；订单完成后提交不可修改的评价。

### 2.2 适用用户

| 用户角色 | 角色说明 | 使用场景 |
|---|---|---|
| USER | 终端用户 | 下单、支付、取消、查看、评价、投诉 |

### 2.3 主要业务对象

| 业务对象 | 说明 |
|---|---|
| BookingOrder | 预约订单 |
| Payment | 支付单 |
| CouponUsage | 优惠券使用 |
| Review | 咨询评价 |
| Complaint | 投诉（用户发起） |

---

## 3. 用户角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可审批 | 说明 |
|---|---:|---:|---:|---:|---:|---|
| USER | 是（本人） | 是 | 有限（取消/评价） | 否 | 否 | 不可改他人订单 |

### 3.1 权限规则

- PR-001：仅本人可查看与操作自己的订单。
- PR-002：已开始订单不可取消。
- PR-003：评价提交后不可修改。
- PR-004：未提及操作一律不允许。

---

## 4. 业务流程

### 4.1 主流程

1. 用户选择咨询师与可约时段，填写下单信息。
2. 系统展示单价、优惠、应付与服务费；校验优惠券。
3. 用户支付（微信/支付宝）；成功生成预约并通知咨询师。
4. 用户在「我的预约」按状态筛选、查看详情/时间线。
5. 订单完成后 14 天内提交评价。

### 4.2 异常流程

| 编号 | 触发条件 | 系统行为 | 结果 |
|---|---|---|---|
| EX-001 | 支付超时 | 关单并释放时段 | 订单关闭 |
| EX-002 | 优惠券不可用 | 提示原因 | 不可提交或需移除券 |
| EX-003 | 取消已开始订单 | 拒绝 | 明确错误 |
| EX-004 | 超 14 天评价 | 拒绝 | 评价入口关闭 |
| EX-005 | 敏感词/长度不合法 | 字段级错误 | 不落库 |

---

## 5. 字段表

### 5.1 BookingOrder

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 订单号 | string | 是 | 唯一标识 | 系统生成 | 否 | 否 |
| 用户 ID | string | 是 | 下单用户 | 当前登录用户 | 是 | 否 |
| 咨询师 | string | 是 | 被预约方 | 用户选择 | 是 | 否 |
| 时段 | string | 是 | 预约时段 | 用户选择 | 是 | 否 |
| 咨询主题 | string(2..80) | 是 | 主题 | 用户输入 | 是 | 否 |
| 问题描述 | string(10..2000) | 是 | 详情 | 用户输入 | 是 | 否 |
| 联系手机号 | string(11) | 是 | 预约联系 | 用户输入/账号带入 | 是 | 否 |
| 状态 | enum | 是 | 订单状态 | pendingPay / pendingConfirm / confirmed / reschedulePending / inProgress / completed / cancelled / refunded | 是 | 系统 |
| 服务单价 | decimal(10,2) | 是 | 下单时价格快照 | 档案线上版 | 否 | 否 |
| 优惠金额 | decimal(10,2) | 是 | 优惠券抵扣 | 系统计算，默认 0 | 否 | 否 |
| 服务费 | decimal(10,2) | 是 | 平台费用展示 | 费率版本计算 | 否 | 否 |
| 应付金额 | decimal(10,2) | 是 | unitPrice-discountAmount | 系统计算 | 否 | 否 |
| 优惠券 ID | string | 否 | 使用的券 | 用户选择 | 否 | 否 |
| 取消原因 | string(2..200) | 条件 | 用户取消时必填 | 用户输入 | 否 | 否 |
| 下单时间 | datetime | 是 | 创建时间 | 系统生成 | 否 | 否 |
| 支付时间 | datetime | 否 | 支付成功时间 | 支付回调 | 否 | 否 |
| 取消时间 | datetime | 否 | 订单关闭时间 | 系统生成 | 否 | 否 |

### 5.2 Payment / CouponUsage

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 支付单 ID | string | 是 | 内部支付标识 | 系统生成 | 否 | 否 |
| 订单 ID | string | 是 | 关联订单 | BookingOrder.id | 是 | 否 |
| 支付渠道 | enum | 是 | 支付方式 | wechat / alipay | 是 | 否 |
| 网关流水号 | string | 否 | 渠道交易号 | 支付网关 | 否 | 否 |
| 支付状态 | enum | 是 | 支付进度 | pending / success / failed / closed / refunded | 是 | 系统 |
| 支付金额 | decimal(10,2) | 是 | 等于订单应付金额 | 系统计算 | 是 | 否 |
| 支付截止时间 | datetime | 是 | 超时自动关闭 | 系统生成 | 否 | 否 |
| 优惠券 ID | string | 是 | 使用券 | Coupon.id | 是 | 否 |
| 抵扣金额 | decimal(10,2) | 是 | 本单实际抵扣 | 系统计算 | 否 | 否 |
| 核销状态 | enum | 是 | 券占用状态 | locked / used / released | 是 | 系统 |

### 5.3 Review / Complaint

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 评价 ID | string | 是 | 评价标识 | 系统生成 | 否 | 否 |
| 评价.订单 ID | string | 是 | 一单一评 | BookingOrder.id | 是 | 否 |
| 总评分 | integer | 是 | 总体星级 | 1..5 | 是 | 否 |
| 专业度评分 | integer | 是 | 维度评分 | 1..5 | 是 | 否 |
| 沟通评分 | integer | 是 | 维度评分 | 1..5 | 是 | 否 |
| 文字评价 | string(0..1000) | 否 | 公开内容 | 用户输入并过敏感词 | 否 | 否 |
| 评价时间 | datetime | 是 | 提交时间 | 系统生成 | 否 | 否 |
| 投诉 ID | string | 是 | 投诉标识 | 系统生成 | 否 | 否 |
| 投诉.订单 ID | string | 是 | 被投诉订单 | BookingOrder.id | 是 | 否 |
| 投诉类型 | enum | 是 | 问题类型 | noShow / service / other | 是 | 否 |
| 投诉说明 | string(10..2000) | 是 | 事实描述 | 用户输入 | 是 | 否 |
| 投诉状态 | enum | 是 | 处理状态 | pending / resolved / rejected | 是 | 系统 |

---

## 6. 字段变更说明

无

---

## 7. 业务规则

1. **R-CREATE-001（原子占档）**：创建订单时须在同一事务中校验时段 open 且有容量并锁定库存；冲突时拒绝下单。
2. **R-CREATE-002（金额快照）**：单价、费率版本、优惠与应付金额在下单时固化；应付金额不得小于 0。
3. **R-CREATE-003（优惠券）**：优惠券须归当前用户、在有效期内、满足门槛且未被使用；下单锁券，支付成功核销，关单释放。
4. **R-CREATE-004（支付单）**：同一订单同一支付尝试只生成一个支付单，渠道限 wechat/alipay，支付金额必须等于订单应付金额。
5. **R-CREATE-005（评价）**：仅订单用户可在 completed 后 14×24 小时内评价一次；各评分为 1–5 整数，内容通过长度和敏感词校验。
6. **R-CREATE-006（投诉）**：订单超过约定开始时间 30 分钟仍未进入 inProgress 时，用户可发起 noShow 投诉。
7. **R-QUERY-001（订单隔离）**：用户只能查询本人订单，支持状态筛选并按 createdAt 倒序分页。
8. **R-QUERY-002（详情快照）**：订单详情展示下单时咨询师、价格和档期快照及完整状态时间线。
9. **R-UPDATE-001（支付回调）**：仅验签成功且金额一致的回调可将支付置 success、订单置 pendingConfirm；重复回调幂等。
10. **R-UPDATE-002（支付超时）**：pendingPay 到 expireAt 未支付时转 cancelled，释放时段和优惠券；迟到成功回调进入人工核对，不恢复订单。
11. **R-UPDATE-003（用户取消）**：pendingConfirm/confirmed 且未到开始时间的订单可由本人取消，必须填写原因并释放时段；inProgress/completed 不可取消。
12. **R-UPDATE-004（再次预约）**：从历史订单再次预约仅预填咨询师与主题，不复用旧时段、价格、优惠或联系方式。
13. **R-DELETE-001（禁止物理删除）**：订单、支付、评价与投诉均不可由业务用户物理删除。
14. **R-COMMON-001（状态守卫）**：所有状态变更须匹配 §9，非法或并发过期请求返回业务冲突。

---

## 8. 业务规则变更说明

无

---

## 9. 状态流转规则

| 当前状态 | 触发动作 | 目标状态 | 允许角色 | 规则编号 |
|---|---|---|---|---|
| （无） | placeOrder | pendingPay | USER | R-STATE-001 |
| pendingPay | paySuccess | pendingConfirm | USER/系统 | R-STATE-002 |
| pendingPay | payTimeout | cancelled | 系统 | R-STATE-003 |
| pendingConfirm / confirmed | cancel | cancelled | USER | R-STATE-004 |
| pendingConfirm | confirm | confirmed | CONSULTANT | R-STATE-005 |
| confirmed | requestReschedule | reschedulePending | CONSULTANT | R-STATE-006 |
| reschedulePending | accept/reject | confirmed | USER | R-STATE-007 |
| confirmed | startConsult | inProgress | CONSULTANT | R-STATE-008 |
| inProgress | complete | completed | 咨询师侧 | 见 fulfillment |
| pendingConfirm | reject | cancelled | CONSULTANT | R-STATE-009 |
| completed | refund | refunded | ADMIN | R-STATE-010 |

---

## 10. 数据约束

### 10.1 唯一性约束

| 字段 | 唯一范围 | 说明 |
|---|---|---|
| review.orderId | 每订单唯一 | 一单一评 |

### 10.2 引用约束

| 当前对象字段 | 引用对象 | 引用字段 | 约束说明 |
|---|---|---|---|
| slotId | AvailableSlot | id | 须可预约且未占用 |
| couponId | Coupon | id | 须可用且未过期 |

### 10.3 数据保留策略

- DATA-001：取消原因、评价内容保留用于审计与展示。
- DATA-002：支付回调以网关为准（见 platform-capability）。

---

## 11. 影响范围

无

---

## 12. 验收标准

- **AC-001**：Given 用户选择了有容量的时段与有效优惠券，When 填写合法信息并下单支付，Then 页面展示单价、优惠、服务费、应付金额，支付成功后订单进入 pendingConfirm 且券被核销。
- **AC-002**：Given 订单处于 pendingPay，When 到达支付截止时间仍未成功，Then 订单转 cancelled、时段与优惠券释放，重复超时任务不产生额外变化。
- **AC-003**：Given 订单尚未开始，When 本人填写原因取消，Then 订单取消并释档；Given 订单已 inProgress，When 尝试取消，Then 系统返回业务冲突。
- **AC-004**：Given 用户有多个状态的订单，When 在“我的预约”按状态筛选并进入详情，Then 仅展示本人匹配订单及按时间排序的完整状态时间线。
- **AC-005**：Given 本人订单完成未满 14 天且未评价，When 提交合法多维评分与文字，Then 评价成功且不可修改；重复、超期或含敏感词提交被拒绝。

---

## 13. 测试场景建议

| 场景编号 | 场景名称 | 前置条件 | 操作 | 预期结果 |
|---|---|---|---|---|
| TC-001 | 正常下单支付 | 有可约时段 | 下单并支付 | pendingConfirm |
| TC-002 | 支付超时 | 待支付 | 超时 | 关单释档 |
| TC-003 | 评价 | 已完成 | 提交评价 | 成功且不可再改 |

---

## 14. 原型引用说明

- 原型工程：`docs/features/iteration1/prototypes/`（`npm run dev` → :5174）
- 路由：`/user/booking`、`/user/my-orders`、`/user/order-detail`

以上原型均使用 Element Plus。

---

## 15. 合并说明

无

---

## 16. AI 实现提示

1. 状态机必须与 consultant-fulfillment / admin-ops 对齐后再实现。
2. 金额按订单快照计算；费率值从平台有效版本读取，不硬编码。
3. 每条 R-* 至少映射一个测试。
