# 核心领域模型（Core）

> **意图侧**：只维护 **核心聚合 + 关键字段**（统一语言与边界），不写全量字段/行为/端口实现。  
> **as-built**（全量）见 [`../../facts/domain-model.md`](../../facts/domain-model.md)；漂移时用 `ba-arch-sync-back` 对齐。  
> 维护：`ba-arch-plan` 起草（首次/新增业务域）；`ba-arch-sync-back` 对齐意图与 as-built。

## 核心聚合

| 聚合 | 职责 | 关键字段 |
|---|---|---|
| **Account** | 统一账号（用户 / 咨询师 / 管理员） | `id` · `phone`（摘要/密文） · `roles` · `status` · `tokenVersion` |
| **UserProfile** | 终端用户资料 | `accountId` · `nickname` · `avatarUrl` |
| **ConsultantProfile** | 咨询师对外档案（含草稿/线上） | `accountId` · `displayName` · `status` · 分类/标签 |
| **AvailableSlot** | 可约时段 | `consultantId` · `start` · `end` · `status` |
| **BookingOrder** | 预约单 | `userId` · `consultantId` · `slotId` · `status` · `amount` |
| **OnboardingApplication** | 入驻申请 | `accountId` · `status` · 资质材料引用 |
| **SettlementBill** | 结算出账 | `consultantId` · `period` · `amount` · `status` |

## 关系（示意）

```
Account ──1:1── UserProfile
Account ──1:1── ConsultantProfile
ConsultantProfile ──1:N── AvailableSlot
Account(User) + AvailableSlot ──▶ BookingOrder
Account(Consultant) ──1:N── OnboardingApplication
Account(Consultant) ──1:N── SettlementBill
```

## 不在本文写的内容

- 全量字段表、方法签名、校验细节 → `facts/domain-model.md` / feature `plan.md`
- 值对象枚举清单、基础设施端口 → as-built 或 ADR / tech-topic
