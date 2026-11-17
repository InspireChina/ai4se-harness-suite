# iteration1 需求样例骨架

>日期： 2026-11-16
>
>关联需求：docs/features/iteration1/
>
>设计 design：本轮仅需求骨架，不改 designs/
>
>**plan一旦定稿就不修改。** 同一资源的二次改造新建 `YYYY-MM-DD-{slug}.md`，不修改原计划文件

## 1. 文档说明

### 1.1 背景

- 将 `ai4se-sow-estimate-skill/examples` 中的「咨询师预约平台」PRD 样例迁入 example-project，作为 harness 管理下的标准需求样例。
- 旧 `docs/features/{auth,appointment,admin}.md` 为简化版，与新样例重叠，本轮删除。
- 原型将使用 Element Plus 与前端工程同构；本轮只落需求骨架，原型下一轮。

### 1.2 目标

- 在 `docs/features/iteration1/` 建立 9 份特性 spec 骨架 + 迭代 README。
- 每份 spec 覆盖：背景/目标/范围、功能概述、角色、主流程要点、关键业务对象、REQ 追溯、待补章节标记。
- 同步 `AGENTS.md` 文档树引用。

### 1.3 技术边界

- 不改 backend / frontend 代码。
- 不写完整字段表、业务规则细项、验收 Given-When-Then（标 TODO）。
- 不生成 Element Plus 原型 HTML（目录预留）。

## 2. 特性拆分

| Spec | 源 REQ / 章节 | 说明 |
|---|---|---|
| account.md | §6.1 + REQ-006 | 账号体系与个人中心 |
| consultant-discovery.md | REQ-001、002 | 检索与咨询师主页 |
| booking.md | REQ-003、004、005 | 下单支付、订单、评价 |
| consultant-onboarding.md | REQ-007、008 | 入驻与档案 |
| consultant-schedule.md | REQ-009 | 档期管理 |
| consultant-fulfillment.md | REQ-010、012 | 履约与工作台 |
| settlement.md | REQ-011 | 收入结算 |
| admin-ops.md | REQ-013～017 | 管理端运营治理 |
| platform-capability.md | §6.2～6.6 | 通知/支付/性能/安全/审计 |

## 3. 任务拆分

1. 删除旧 features 三文件。
2. 创建 `iteration1/README.md`（索引 + 里程碑 + 原型约定）。
3. 创建 9 份骨架 spec。
4. 预留 `iteration1/prototypes/` 说明。
5. 同步 `AGENTS.md` 与相关 skill 示例路径。

## 4. 验收

- [x] `docs/features/` 下仅保留 `_template.md` 与 `iteration1/`
- [x] 9 份 spec 均可从 README 索引跳到
- [x] 每份 spec 标注骨架状态与待补章节
- [x] `AGENTS.md` §13 文档树已更新
