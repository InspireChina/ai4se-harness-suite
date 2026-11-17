# 术语表

> 项目级统一语言（Ubiquitous Language）。各 feature 的规格、Plan、代码命名应对齐本表。
> 由 `ba-write-spec` 在写/改规格时维护；新增术语追加到本文件，不按 feature 拆分。

| 中文 | 英文 | 说明（可选） |
|---|---|---|
| 咨询师 | consultant / CONSULTANT | 角色 |
| 管理员 | admin / ADMIN | 角色 |
| 终端用户 | end user / USER | 角色 |
| 账号 | Account | 统一账号（手机号、状态、角色集合） |
| 下单 | place order |  |
| 不可约 | unavailable |  |
| 个人中心 | profile center |  |
| 举报 | report |  |
| 举报工单 | ReportCase | 举报工单 |
| 优惠券 | coupon |  |
| 优惠券使用 | CouponUsage | 优惠券使用 |
| 例外不可约 | SlotException | 例外不可约 |
| 入驻 | onboarding |  |
| 入驻申请 | OnboardingApplication | 入驻申请（审核视角） |
| 公开档案 | public profile |  |
| 出账 | billing / issue bill |  |
| 分类 | Category | 分类与标签树 |
| 协议同意 | AgreementConsent | 协议同意记录 |
| 占用 | occupy / lock |  |
| 可预约时段 | AvailableSlot | 可预约时段（只读展示） |
| 周固定可约模板 | WeeklySlotTemplate | 周固定可约模板 |
| 咨询小结 | ConsultSummary | 咨询小结 |
| 咨询师公开档案 | ConsultantPublicProfile | 对外展示的咨询师档案 |
| 咨询师发现 | consultant discovery |  |
| 咨询师工作台 | ConsultantDashboard | 工作台指标快照 |
| 咨询师档案 | ConsultantProfile | 对外档案（含草稿/线上版） |
| 咨询师检索条件 | ConsultantSearchQuery | 检索条件 |
| 回调 | callback |  |
| 备注 | remark | 通用 |
| 审核 | review / approval |  |
| 审计 | audit |  |
| 审计日志 | AuditLog | 操作审计 |
| 履约 | fulfillment |  |
| 幂等 | idempotency |  |
| 投诉 | Complaint | 投诉（用户发起） |
| 拒单 | reject order |  |
| 接单 | accept order |  |
| 提现 | withdrawal |  |
| 提现申请 | WithdrawalRequest | 提现申请 |
| 支付 | payment |  |
| 支付单 | Payment | 支付单 |
| 支付回调 | PaymentCallback | 支付/退款回调记录 |
| 收入概览 | IncomeOverview | 收入概览 |
| 收藏咨询师 | FavoriteConsultant | 用户收藏的咨询师 |
| 改期 | reschedule |  |
| 改期申请 | RescheduleRequest | 改期申请 |
| 服务协议 | service agreement |  |
| 服务费率版本 | FeeRateVersion | 服务费率版本 |
| 标签 | Tag | 分类与标签树 |
| 档期 | schedule |  |
| 档案草稿 | profile draft |  |
| 检索 | search |  |
| 治理 | governance |  |
| 用户账号（治理） | UserAccount | 用户治理对象 |
| 用户资料 | UserProfile | 终端用户资料 |
| 站内信 | inbox message |  |
| 结算 | settlement |  |
| 结算单 | SettlementBill | 月度结算单 |
| 评价 | Review | 咨询评价 |
| 评价摘要 | ReviewSummary | 评价摘要与列表 |
| 资质 | credential |  |
| 资质文件 | CredentialFile | 资质文件 |
| 运营 | operations |  |
| 运营看板指标 | OpsDashboardMetrics | 看板指标 |
| 退款 | refund |  |
| 退款审核 | refund review |  |
| 通知 | Notification | 通知消息 |
| 释放 | release |  |
| 限流 | rate limit |  |
| 限流策略 | RateLimitPolicy | 限流策略 |
| 隐私政策 | privacy policy |  |
| 预约 | booking |  |
| 预约订单 | BookingOrder | 订单治理对象 |
| 验证码 | verification code |  |
| ID | ID | 字段 |
| MIME 类型 | MIME type | 字段 |
| 下单时间 | ordered at | 字段 |
| 下次重试时间 | next retry at | 字段 |
| 专业度评分 | professional rating | 字段 |
| 业务 ID | business ID | 字段 |
| 业务单 ID | business order ID | 字段 |
| 业务类型 | business type | 字段 |
| 个人简介 | bio | 字段 |
| 举报 ID | report ID | 字段 |
| 举报人 ID | reporter ID | 字段 |
| 举报状态 | report status | 字段 |
| 举报类型 | report type | 字段 |
| 举报说明 | report description | 字段 |
| 乐观锁版本 | optimistic lock version | 字段 |
| 事件类型 | event type | 字段 |
| 今日咨询数 | today consultation count | 字段 |
| 今日待办 | today's todos | 字段 |
| 今日收入 | today's income | 字段 |
| 从业年限 | years of practice | 字段 |
| 价格区间 | price range | 字段 |
| 优惠券 ID | coupon ID | 字段 |
| 优惠金额 | discount amount | 字段 |
| 例外 ID | exception ID | 字段 |
| 例外日期 | exception date | 字段 |
| 例外类型 | exception type | 字段 |
| 停用原因 | disabled reason | 字段 |
| 公告列表 | announcements | 字段 |
| 关键词 | keyword | 字段 |
| 内容 | content | 字段 |
| 冻结金额 | frozen amount | 字段 |
| 净收入 | net income | 字段 |
| 出账时间 | issued at | 字段 |
| 分类 ID | category ID | 字段 |
| 分类名 | category name | 字段 |
| 分类状态 | category status | 字段 |
| 分类编码 | category code | 字段 |
| 分类集合 | categories | 字段 |
| 创建人 | created by | 字段 |
| 创建时间 | created at | 字段 |
| 剩余容量 | remaining capacity | 字段 |
| 动作编码 | action code | 字段 |
| 协议版本 | agreement version | 字段 |
| 协议类型 | agreement type | 字段 |
| 单次价格 | session price | 字段 |
| 原因说明 | reason note | 字段 |
| 原时段 ID | original slot ID | 字段 |
| 取消原因 | cancel reason | 字段 |
| 取消时间 | cancelled at | 字段 |
| 变更前后 | before/after snapshot | 字段 |
| 可提现余额 | withdrawable balance | 字段 |
| 可约日期 | available date | 字段 |
| 同意.用户账号 ID | consent account ID | 字段 |
| 同意时间 | accepted at | 字段 |
| 同意记录 ID | consent ID | 字段 |
| 后续建议 | recommendations | 字段 |
| 周期开始 | period start | 字段 |
| 咨询主题 | topic | 字段 |
| 咨询师 ID | consultant ID | 字段 |
| 咨询师数 | consultant count | 字段 |
| 回调单号 | callback ID | 字段 |
| 回调类型 | callback type | 字段 |
| 城市 | city | 字段 |
| 城市编码 | city code | 字段 |
| 处理状态 | process status | 字段 |
| 处理结论 | resolution | 字段 |
| 失效时间 | expire at | 字段 |
| 失败原因 | failure reason | 字段 |
| 失败码 | failure code | 字段 |
| 头像 | avatar | 字段 |
| 头像地址 | avatar URL | 字段 |
| 头像文件 ID | avatar file ID | 字段 |
| 姓名 | full name | 字段 |
| 存储地址 | storage URL | 字段 |
| 安全状态 | security status | 字段 |
| 完成时间 | completed at | 字段 |
| 审核人 | reviewer | 字段 |
| 审核时间 | reviewed at | 字段 |
| 审核状态 | review status | 字段 |
| 审核结果 | review result | 字段 |
| 审核说明 | review note | 字段 |
| 审计日志 ID | audit log ID | 字段 |
| 容量 | capacity | 字段 |
| 对象 ID | target ID | 字段 |
| 对象类型 | target type | 字段 |
| 对象类型/ID | target type/ID | 字段 |
| 小结 ID | summary ID | 字段 |
| 小结.订单 ID | order ID | 字段 |
| 尝试次数 | attempt count | 字段 |
| 展示姓名 | display name | 字段 |
| 已占数量 | occupied count | 字段 |
| 已完成预约数 | completed booking count | 字段 |
| 已读时间 | read at | 字段 |
| 平均评分 | average rating | 字段 |
| 应付金额 | payable amount | 字段 |
| 应结金额 | net payable | 字段 |
| 开始时间 | start at | 字段 |
| 待处理数 | pending count | 字段 |
| 待结算金额 | pending settlement amount | 字段 |
| 总评分 | overall rating | 字段 |
| 成交额 | GMV | 字段 |
| 截止日期 | end date | 字段 |
| 手机号 | phone number | 字段 |
| 手机验证时间 | phone verified at | 字段 |
| 执业身份 | practice identity | 字段 |
| 批量模式 | batch mode | 字段 |
| 投诉 ID | complaint ID | 字段 |
| 投诉.订单 ID | order ID | 字段 |
| 投诉状态 | complaint status | 字段 |
| 投诉类型 | complaint type | 字段 |
| 投诉说明 | complaint description | 字段 |
| 投递状态 | delivery status | 字段 |
| 抵扣金额 | discount amount | 字段 |
| 拒绝原因 | reject reason | 字段 |
| 拒绝说明 | reject note | 字段 |
| 排序 | sort | 字段 |
| 排序值 | sort order | 字段 |
| 接收人 ID | recipient ID | 字段 |
| 接收时间 | received at | 字段 |
| 提交时间 | submitted at | 字段 |
| 提现.完成时间 | withdrawal completed at | 字段 |
| 提现单 ID | withdrawal ID | 字段 |
| 提现状态 | withdrawal status | 字段 |
| 提现金额 | withdrawal amount | 字段 |
| 擅长标签 | expertise tags | 字段 |
| 擅长领域 | expertise area | 字段 |
| 操作人 | operator | 字段 |
| 操作原因 | action reason | 字段 |
| 操作时间 | operated at | 字段 |
| 操作类型 | operation type | 字段 |
| 支付单 ID | payment ID | 字段 |
| 支付截止时间 | pay by | 字段 |
| 支付时间 | paid at | 字段 |
| 支付渠道 | payment channel | 字段 |
| 支付状态 | payment status | 字段 |
| 支付金额 | payment amount | 字段 |
| 收款账户快照 | payout account snapshot | 字段 |
| 收藏 ID | favorite ID | 字段 |
| 收藏.用户账号 ID | favorite account ID | 字段 |
| 收藏时间 | favorited at | 字段 |
| 改期.订单 ID | order ID | 字段 |
| 改期原因 | reschedule reason | 字段 |
| 改期申请 ID | reschedule request ID | 字段 |
| 数据请求类型 | data request type | 字段 |
| 文件 ID | file ID | 字段 |
| 文件大小 | file size | 字段 |
| 文件用途 | file purpose | 字段 |
| 文字评价 | review content | 字段 |
| 新时段 ID | proposed slot ID | 字段 |
| 日志 ID | log ID | 字段 |
| 时段 | time slot | 字段 |
| 时段 ID | slot ID | 字段 |
| 时长 | duration | 字段 |
| 明细 ID | line ID | 字段 |
| 明细.完成时间 | line completed at | 字段 |
| 星期 | weekday | 字段 |
| 星期集合 | weekdays | 字段 |
| 是否已收藏 | is favorited | 字段 |
| 昵称 | nickname | 字段 |
| 更新时间 | updated at | 字段 |
| 最低评分 | min rating | 字段 |
| 最近登录时间 | last login at | 字段 |
| 服务价格 | service price | 字段 |
| 服务分类 | service category | 字段 |
| 服务单价 | unit price | 字段 |
| 服务说明 | service description | 字段 |
| 服务费 | platform fee | 字段 |
| 服务费率 | service fee rate | 字段 |
| 期望定价 | expected price | 字段 |
| 本月收入 | month income | 字段 |
| 本月订单数 | month order count | 字段 |
| 来源 | source | 字段 |
| 来源 IP | source IP | 字段 |
| 标签 ID | tag ID | 字段 |
| 标签名 | tag name | 字段 |
| 标签状态 | tag status | 字段 |
| 标题 | title | 字段 |
| 核销状态 | redemption status | 字段 |
| 档案版本 | profile version | 字段 |
| 沟通评分 | communication rating | 字段 |
| 治理动作 | governance action | 字段 |
| 渠道 | channel | 字段 |
| 渠道流水号 | gateway trade no | 字段 |
| 父分类 ID | parent category ID | 字段 |
| 状态 | status | 字段 |
| 环比 | period-over-period | 字段 |
| 生成时间 | generated at | 字段 |
| 生效时间 | effective at | 字段 |
| 用户 ID | user ID | 字段 |
| 用户展示名 | user display name | 字段 |
| 用户数 | user count | 字段 |
| 用户账号 ID | user account ID | 字段 |
| 申请 ID | application ID | 字段 |
| 申请时间 | applied at | 字段 |
| 申请状态 | request status | 字段 |
| 确认截止时间 | confirm by | 字段 |
| 确认时间 | confirmed at | 字段 |
| 禁用原因 | disabled reason | 字段 |
| 窗口秒数 | window seconds | 字段 |
| 策略键 | policy key | 字段 |
| 线上版本号 | published version | 字段 |
| 结束时间 | end at | 字段 |
| 结果 | result | 字段 |
| 结算单 ID | settlement bill ID | 字段 |
| 统计周期 | stats period | 字段 |
| 网关 | gateway | 字段 |
| 网关流水号 | gateway trade no | 字段 |
| 联系手机号 | contact phone | 字段 |
| 角色集合 | roles | 字段 |
| 订单 ID | order ID | 字段 |
| 订单号 | order number | 字段 |
| 订单总额 | order total | 字段 |
| 订单状态 | order status | 字段 |
| 订单量 | order volume | 字段 |
| 订单金额 | order amount | 字段 |
| 认证标识 | verified badge | 字段 |
| 记录 ID | record ID | 字段 |
| 证件号码 | ID number | 字段 |
| 证据文件 | evidence files | 字段 |
| 评价 ID | review ID | 字段 |
| 评价.订单 ID | order ID | 字段 |
| 评价内容 | review content | 字段 |
| 评价数 | review count | 字段 |
| 评价时间 | reviewed at | 字段 |
| 语言 | locale | 字段 |
| 账单状态 | bill status | 字段 |
| 账号 ID | account ID | 字段 |
| 账期 | billing period | 字段 |
| 费率版本 | fee rate version | 字段 |
| 资料更新时间 | profile updated at | 字段 |
| 起始日期 | start date | 字段 |
| 退款单 ID | refund ID | 字段 |
| 退款原因 | refund reason | 字段 |
| 退款状态 | refund status | 字段 |
| 退款率 | refund rate | 字段 |
| 退款金额 | refund amount | 字段 |
| 通知 ID | notification ID | 字段 |
| 邮箱 | email | 字段 |
| 金额 | amount | 字段 |
| 链路 ID | trace ID | 字段 |
| 链路追踪 ID | trace ID | 字段 |
| 问题描述 | problem description | 字段 |
| 限额 | limit | 字段 |
| 页大小 | page size | 字段 |
| 页码 | page | 字段 |
| 预约开始时间 | slot start at | 字段 |
| 驳回原因 | reject reason | 字段 |
| 驳回原因码 | reject reason code | 字段 |
| 驳回说明 | reject note | 字段 |
| 验签结果 | signature valid | 字段 |
| 默认容量 | default capacity | 字段 |
