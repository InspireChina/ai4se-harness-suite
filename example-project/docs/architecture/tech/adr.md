# 架构决策（ADR）

跨迭代技术取舍，**每条一句话**。实现细节见 [`../../facts/tech-topic/`](../../facts/tech-topic/)。写法见 [`../../standards/adr.md`](../../standards/adr.md)。

| 编号 | 决策（一句话） | 状态 |
|---|---|---|
| ADR-001 | 后端采用四层 DDD 单体：adapter → application → domain ← infrastructure | 已接受 |
| ADR-002 | 主键使用 UUID 字符串，不用自增整数 | 已接受 |
| ADR-003 | 持久化用 MyBatis-Plus，不用 JPA | 已接受 |
| ADR-004 | 鉴权用 JWT 无状态令牌（HMAC） | 已接受 |
| ADR-005 | 请求内用户上下文用 ThreadLocal `UserContext` | 已接受 |
