# ADR-004: 采用 JWT HMAC-SHA256 无状态鉴权

- **状态**: 已接受（2026-11-17 扩展 Claims，方案本身不变）
- **日期**: 2026-06-19
- **扩展记录**: 2026-11-17 · ACC（账号与个人中心）落地，Claims 扩展为多角色 + 会话版本

## 上下文

前后端分离架构需要鉴权方案。需要决定使用 Session/Cookie 还是 Token（JWT）。

## 决策

后端自行签发与校验 JWT（HMAC-SHA256，24h 过期），无状态鉴权。

JWT Payload（as-built）：

- `sub`: 账号 ID（`account.id`）
- `roles`: 角色数组，如 `["USER","CONSULTANT","ADMIN"]`（authority = `ROLE_<name>`）
- `tokenVersion`: 会话版本，与 `account.token_version` 比对
- `iat` / `exp`: 签发 / 过期时间

### Claims 扩展（2026-11-17）

原约定的 `email` 与单值 `role` Claims 移除，改为：

| 变更 | 原因 |
|---|---|
| `role` → `roles` 数组 | 同一账号可同时持有 USER / CONSULTANT / ADMIN 三种角色（HLD §3.2） |
| 新增 `tokenVersion` | 管理员禁用账号时抬升库内版本，令既有 JWT 立即失效（R-UPDATE-003 / AC-005） |

`JwtAuthenticationFilter` 在验签后需查库比对账号状态与 `tokenVersion`：
账号不存在 / 已禁用 / 版本不一致 → 不放行，返回 401 并带明确原因。

## 备选方案

| 方案 | 理由 | 否决原因 |
|------|------|----------|
| Session + Cookie | Spring Security 默认方案 | 需 Redis 存储 session、跨域配置复杂、不适合前后端分离 |
| OAuth2 / OIDC | 标准协议 | 增加 IDP 依赖，小型项目不需要 |
| JWT HMAC-SHA256 | 无状态、无额外存储 | 无法主动使 token 失效（本次以 `tokenVersion` 补齐） |
| JWT + 撤销名单（黑名单） | 精确吊销 | 需持久化与额外查询，收益有限；`tokenVersion` 已满足账号级失效 |

## 后果

**正面**：
- 无状态、无需 Redis
- 前后端分离友好（`Authorization: Bearer <token>`）
- 后端自行签发，无外部依赖
- 账号级会话失效无需维护令牌黑名单

**负面**：
- 每个已认证请求需查库一次（比对状态与版本），有额外开销
- Token 仍无法按请求粒度吊销（24h 内有效，账号级失效除外）
- 密钥保存在配置中，泄漏风险需注意
- 载荷明文字段不宜存放敏感信息（手机号不入载荷，只放账号 ID）
