# 需求规格说明书：预约履约与工作台

> 文档类型：需求规格 / Feature Specification  
> 适用目录：`docs/features/iteration1/`  
> 需求类型：NEW  
> 版本：v0.1  
> 作者：BA  
> 日期：2026-11-16  
> 状态：**v0.1** — 字段/规则/验收已补齐；原型已挂接  
> 源追溯：REQ-010、REQ-012

---

## 1. 需求说明

### 1.1 需求名称

预约履约与工作台

### 1.2 需求类型

NEW

### 1.3 版本信息

| 项目 | 内容 |
|---|---|
| 基线版本 | 无 |
| 目标版本 | v0.1 |

### 1.4 背景

咨询师需要确认/拒绝预约、履约并提交小结，并有工作台聚合今日待办与指标。

### 1.5 目标

打通咨询师侧「接单 → 履约 → 小结」；工作台提供概览与快捷入口。

### 1.6 范围

本次包含：

- 预约订单列表筛选（待确认/已确认/进行中/已完成/已取消）
- 确认或拒绝（拒绝必选原因+说明）
- 到点开始咨询 → 进行中；提交咨询小结（对用户可见）
- 查看沟通记录与历史订单
- 申请改期（需用户确认后生效）
- 工作台：今日咨询数、本月订单、平均评分、待处理数；今日待办列表；公告；快捷入口

本次不包含：

- 用户侧下单与评价（booking.md）
- 结算提现（settlement.md）
- 音视频通话能力

---

## 2. 功能说明

### 2.1 功能概述

咨询师处理预约全流程并在工作台查看待办与核心指标。

### 2.2 适用用户

| 用户角色 | 角色说明 | 使用场景 |
|---|---|---|
| CONSULTANT | 已入驻咨询师 | 接单、履约、看工作台 |

### 2.3 主要业务对象

| 业务对象 | 说明 |
|---|---|
| BookingOrder | 与用户侧同一订单 |
| ConsultSummary | 咨询小结 |
| RescheduleRequest | 改期申请 |
| ConsultantDashboard | 工作台指标快照 |

---

## 3. 用户角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可审批 | 说明 |
|---|---:|---:|---:|---:|---:|---|
| CONSULTANT | 是（本人订单） | 是（小结/改期） | 是（确认/拒绝/开始） | 否 | 否 | 不可看他人订单 |
| USER | 是（本人） | 否 | 是（确认改期） | 否 | 否 | 改期确认 |

### 3.1 权限规则

- PR-001：仅处理指派给本人的订单。
- PR-002：拒绝必须选择原因并填写说明。
- PR-003：改期须用户确认后生效。
- PR-004：未提及操作一律不允许。

---

## 4. 业务流程

### 4.1 主流程

1. 咨询师在工作台或订单列表看到待确认订单。
2. 确认或拒绝；确认后在约定时间开始咨询。
3. 进行中提交小结；订单完成。
4. 如需改期，发起申请等待用户确认。

### 4.2 异常流程

| 编号 | 触发条件 | 系统行为 | 结果 |
|---|---|---|---|
| EX-001 | 拒绝未填原因 | 拒绝操作 | 字段错误 |
| EX-002 | 非待确认状态确认 | 拒绝 | 状态冲突 |
| EX-003 | 改期用户拒绝/超时 | 保持原档期 | 申请关闭 |

---

## 5. 字段表

### 5.1 BookingOrder 履约视图

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 订单 ID | string | 是 | 预约标识 | BookingOrder.id | 否 | 否 |
| 咨询师 ID | string | 是 | 履约人 | BookingOrder | 否 | 否 |
| 用户展示名 | string | 是 | 订单用户 | 资料快照 | 否 | 否 |
| 咨询主题 | string | 是 | 订单主题 | BookingOrder | 否 | 否 |
| 预约开始时间 | datetime | 是 | 当前生效时段 | TimeSlot | 否 | 否 |
| 订单状态 | enum | 是 | 履约状态 | pendingConfirm / confirmed / reschedulePending / inProgress / completed / cancelled | 否 | 系统 |
| 拒绝原因 | enum | 条件 | 拒单原因 | unavailable / scopeMismatch / conflict / other | 拒绝时 | 否 |
| 拒绝说明 | string(2..500) | 条件 | 补充说明 | 咨询师输入 | 拒绝时 | 否 |
| 确认时间 | datetime | 否 | 接单时间 | 系统生成 | 否 | 否 |
| 开始时间 | datetime | 否 | 实际开始时间 | 系统生成 | 否 | 否 |
| 完成时间 | datetime | 否 | 实际完成时间 | 系统生成 | 否 | 否 |

### 5.2 ConsultSummary / RescheduleRequest

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 小结 ID | string | 是 | 小结标识 | 系统生成 | 否 | 否 |
| 小结.订单 ID | string | 是 | 一单一份小结 | BookingOrder.id | 是 | 否 |
| 咨询小结 | string(20..3000) | 是 | 对用户可见 | 咨询师输入 | 是 | 否 |
| 后续建议 | string(0..2000) | 否 | 可选建议 | 咨询师输入 | 否 | 否 |
| 提交时间 | datetime | 是 | 完成凭据 | 系统生成 | 否 | 否 |
| 改期申请 ID | string | 是 | 申请标识 | 系统生成 | 否 | 否 |
| 改期.订单 ID | string | 是 | 关联订单 | BookingOrder.id | 是 | 否 |
| 原时段 ID | string | 是 | 原预约档期 | TimeSlot.id | 是 | 否 |
| 新时段 ID | string | 是 | 候选档期 | TimeSlot.id | 是 | 否 |
| 改期原因 | string(2..500) | 是 | 用户可见 | 咨询师输入 | 是 | 否 |
| 申请状态 | enum | 是 | 用户处理状态 | pending / accepted / rejected / expired | 是 | 系统 |
| 确认截止时间 | datetime | 是 | 最晚为原时段前 2 小时 | 系统生成 | 否 | 否 |

### 5.3 ConsultantDashboard

| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
|---|---|---:|---|---|---:|---:|
| 今日咨询数 | integer | 是 | 今日有效订单 | 系统聚合 | 否 | 否 |
| 本月订单数 | integer | 是 | 本月有效订单 | 系统聚合 | 否 | 否 |
| 平均评分 | decimal(2,1) | 是 | 已发布评价均值 | 0.0..5.0 | 否 | 否 |
| 待处理数 | integer | 是 | 待确认+待履约 | 系统聚合 | 否 | 否 |
| 今日待办 | array | 是 | 按开始时间排序 | 系统聚合 | 否 | 否 |
| 公告列表 | array | 是 | 有效平台公告 | 管理端发布 | 否 | 否 |
| 生成时间 | datetime | 是 | 指标口径时间 | 系统生成 | 否 | 否 |

---

## 6. 字段变更说明

无

---

## 7. 业务规则

1. **R-CREATE-001（小结唯一）**：每个订单最多一份小结，仅订单咨询师可在 inProgress 状态提交。
2. **R-CREATE-002（改期申请）**：仅 confirmed 且未开始订单可发起一份 pending 改期，新时段须属于本人、open 且早于原时段开始。
3. **R-QUERY-001（订单隔离）**：咨询师只能查询指派给本人的订单，支持状态筛选并按预约时间升序。
4. **R-QUERY-002（沟通与历史）**：仅订单双方可查看该订单沟通记录和关联历史，不得展示另一方无关订单。
5. **R-QUERY-003（工作台口径）**：今日按 Asia/Shanghai 自然日、本月按自然月；取消/退款订单不计入有效订单数。
6. **R-UPDATE-001（确认）**：仅 pendingConfirm 可确认，确认后进入 confirmed 并通知用户。
7. **R-UPDATE-002（拒绝）**：仅 pendingConfirm 可拒绝，原因码和说明必填；拒绝后订单取消、释放时段并通知用户。
8. **R-UPDATE-003（开始窗口）**：仅 confirmed 订单可在预约开始前 15 分钟至结束后 30 分钟内开始，成功后进入 inProgress。
9. **R-UPDATE-004（完成）**：提交合法小结与完成动作必须同一事务，订单进入 completed 后小结不可修改。
10. **R-UPDATE-005（改期确认）**：用户 accepted 时原子占用新时段并释放旧时段；新时段已不可用则确认失败且保留原时段。
11. **R-UPDATE-006（改期拒绝/过期）**：用户拒绝或超过 expireAt 时申请关闭，订单回到 confirmed，原时段不变。
12. **R-DELETE-001（禁止删除）**：履约记录、小结和改期申请不可物理删除。
13. **R-COMMON-001（状态幂等）**：重复确认、开始、完成请求在目标状态一致时返回当前结果，不重复通知或计数。

---

## 8. 业务规则变更说明

无

---

## 9. 状态流转规则

| 当前状态 | 触发动作 | 目标状态 | 允许角色 | 规则编号 |
|---|---|---|---|---|
| pendingConfirm | confirm | confirmed | CONSULTANT | R-STATE-001 |
| pendingConfirm | reject | cancelled | CONSULTANT | R-STATE-002 |
| confirmed | start | inProgress | CONSULTANT | R-STATE-003 |
| inProgress | submitSummary | completed | CONSULTANT | R-STATE-004 |
| confirmed | requestReschedule | reschedulePending | CONSULTANT | R-STATE-005 |
| reschedulePending | userAccept | confirmed | USER | R-STATE-006 |
| reschedulePending | userReject / expire | confirmed | USER/系统 | R-STATE-007 |

---

## 10. 数据约束

### 10.1 唯一性约束

无新增

### 10.2 引用约束

| 当前对象字段 | 引用对象 | 引用字段 | 约束说明 |
|---|---|---|---|
| proposedSlotId | TimeSlot | id | 须 open 且属本人 |

### 10.3 数据保留策略

- DATA-001：小结对用户可见且保留。
- DATA-002：拒绝原因可审计。

---

## 11. 影响范围

无

---

## 12. 验收标准

- **AC-001**：Given 咨询师有待确认订单，When 按状态筛选并确认或填写原因拒绝，Then 订单分别进入 confirmed 或 cancelled，用户收到通知且拒绝订单释放时段。
- **AC-002**：Given confirmed 订单进入可开始窗口，When 咨询师开始并提交合法小结，Then 订单依次进入 inProgress、completed，用户可查看小结且不可被修改。
- **AC-003**：Given confirmed 订单尚未开始且有可用新时段，When 咨询师发起改期，Then 用户确认前原时段保持；用户接受后原子换档，拒绝或超时则保留原档。
- **AC-004**：Given 咨询师有订单、评价和有效公告，When 打开工作台，Then 展示口径一致的今日咨询数、本月订单、平均评分、待处理数、按时间排序待办、公告及可用快捷入口。

---

## 13. 测试场景建议

| 场景编号 | 场景名称 | 前置条件 | 操作 | 预期结果 |
|---|---|---|---|---|
| TC-001 | 确认订单 | pendingConfirm | 确认 | confirmed |
| TC-002 | 拒绝无原因 | pendingConfirm | 拒绝不填原因 | 失败 |
| TC-003 | 提交小结 | inProgress | 提交小结 | completed |

---

## 14. 原型引用说明

- 原型工程：`docs/features/iteration1/prototypes/`（`npm run dev` → :5174）
- 路由：`/consultant`（工作台）、`/consultant/orders`

---

## 15. 合并说明

无

---

## 16. AI 实现提示

1. 先与 booking 对齐状态机再写代码。
2. 工作台指标可为只读聚合，勿在本模块发明结算字段。
