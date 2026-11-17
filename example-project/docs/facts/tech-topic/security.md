# 安全设计

> 平台骨架 as-built。登录/注册等业务 API 待 ACC 实现。

## JWT Token

**算法**：HMAC-SHA256（`jjwt`）

**配置**：`jwt.secret` / `jwt.expiration`（毫秒）

**Claims（约定）**：`sub`=userId，`email`，`role`（如 `ROLE_USER` / `ROLE_ADMIN`），`iat`，`exp`

## 处理流程

```
请求 → JwtAuthenticationFilter
        提取 Bearer token → 校验 → UserContextHolder + SecurityContextHolder
        finally 清除 ThreadLocal / SecurityContext
```

## 当前放行

- `GET /api/v1/health` — permitAll
- 其它 `/api/**` — authenticated（无签发入口时仅能带有效 token 访问）

## 相关类

- `JwtTokenProvider` / `JwtAuthenticationFilter`
- `UserContext` / `UserContextHolder` / `SecurityUtils`
- `PasswordService` / `PasswordServiceImpl`（BCrypt）
