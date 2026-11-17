# 安全设计

> as-built（含 ACC 账号与个人中心）。

## JWT Token

**算法**：HMAC-SHA256（`jjwt`）

**配置**：`jwt.secret` / `jwt.expiration`（毫秒，默认 24h）

**Claims（as-built）**：

| Claim | 说明 |
|---|---|
| `sub` | 账号 ID（`account.id`） |
| `roles` | 角色数组，如 `["USER","CONSULTANT"]` |
| `tokenVersion` | 会话版本，与 `account.token_version` 比对 |
| `iat` / `exp` | 签发 / 过期时间 |

> 旧约定中的 `email` / `role` 单值 Claims 已移除（见 ADR-004 的 Claims 扩展）。

## 处理流程

```
请求 → JwtAuthenticationFilter
        提取 Bearer token → 验签 → 解析 claims
        → 查库取账号：不存在 / 已禁用 / tokenVersion 不一致 → 不放行（401，带原因）
        → 写 UserContextHolder（accountId + roles）+ SecurityContextHolder（authority = ROLE_*）
        finally 清除 ThreadLocal / SecurityContext
```

**会话失效**：管理员禁用 / 启用账号会抬升 `tokenVersion`，旧 JWT 与库内版本不一致 → 立即 401。
账号被禁用时过滤器返回提示「账号不可用：<原因>」。

## 角色与端点

| 端点 | 要求 |
|---|---|
| `GET /api/v1/health` | permitAll |
| `POST /api/v1/auth/**` | permitAll（发码 / 验证码登录 / 管理员登录） |
| `/api/v1/admin/**` | `ROLE_ADMIN`（否则 403） |
| 其它 `/api/**` | authenticated（401） |

角色授权：JWT authority 为 `ROLE_USER` / `ROLE_CONSULTANT` / `ROLE_ADMIN`，
与 Spring Security `hasRole` 对齐；`SecurityUtils.hasRole("CONSULTANT")` 同时接受带/不带 `ROLE_` 前缀。

## 手机号保护

| 项 | 做法 |
|---|---|
| 存储 | `phone_hash`（HMAC-SHA256，带 `phone.crypto.key`）+ `phone_cipher`（AES-256-GCM） |
| 查询 | 唯一索引建在 `phone_hash` 上，不存明文可比对字段 |
| 展示 | 仅本人（`/api/v1/me`）返回明文；管理端等其它视角脱敏为 `138****8000` |
| 密钥 | `phone.crypto.key` 由环境变量注入，生产禁止入仓 |

## 密码

- 仅 ADMIN 账号使用密码登录；BCrypt 存储（`PasswordService` / `PasswordServiceImpl`）。
- ADMIN 账号由平台种子创建（`AccountSeedInitializer`），不开放自助注册或角色提升。

## 短信验证码

- 库内只存 `code_hash`，不存明文。
- TTL 默认 5 分钟；连续错误 5 次即作废；同一手机号 60 秒内不可重发（`BUSINESS_CONFLICT`）。
- 发送通道本期为 `MockSmsSender`（固定码仅本地联调 / E2E 使用，生产留空）。

## 相关类

- `JwtTokenProvider`（实现 `TokenIssuer`）/ `JwtAuthenticationFilter`
- `UserContext` / `UserContextHolder` / `SecurityUtils`
- `RestAuthenticationEntryPoint`（401）/ `RestAccessDeniedHandler`（403）
- `PasswordService` / `PasswordServiceImpl`（BCrypt）
- `AesPhoneCrypto` / `MockSmsSender` / `StubDisplayableConsultantPort`
