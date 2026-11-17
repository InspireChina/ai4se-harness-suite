# 错误码清单

> as-built（含 ACC）。与 `GlobalExceptionHandler` 及 `docs/standards/error.md` 对齐。

## 当前 Handler 映射

| 抛出 | HTTP | errorCode | 说明 |
|------|------|-----------|------|
| `IllegalArgumentException` | 400 | `PARAM_ERROR` | 参数/资源不合法 |
| `IllegalStateException` | 409 | `BUSINESS_CONFLICT` | 业务状态冲突 |
| `MethodArgumentNotValidException` | 400 | `VALIDATION_ERROR` | `@Valid` 失败 |
| 其它 `Exception` | 500 | `SYSTEM_ERROR` | 兜底（对外「系统繁忙」） |

响应体字段：`errorCode` / `errorMessage` / `data`。

## 鉴权失败（Spring Security 直接返回，不经 GlobalExceptionHandler）

| 场景 | HTTP | errorCode | errorMessage 来源 |
|---|---|---|---|
| 未携带 / 无效 / 过期 token | 401 | `UNAUTHORIZED` | 「未登录或登录已过期」 |
| 账号被禁用 | 401 | `UNAUTHORIZED` | 「账号不可用：<禁用原因>」 |
| 版本不一致（账号被禁用/启用后） | 401 | `UNAUTHORIZED` | 「登录状态已失效，请重新登录」 |
| 已登录但无权限（如非 ADMIN 访问 `/admin/**`） | 403 | `FORBIDDEN` | 「无权访问该资源」 |

实现：`RestAuthenticationEntryPoint`（401）/ `RestAccessDeniedHandler`（403），
响应体沿用与 `GlobalExceptionHandler.ErrorResponse` 相同的字段结构，便于前端统一处理。

## ACC 典型错误文案

| 场景 | HTTP | errorCode | errorMessage |
|---|---|---|---|
| 验证码错误 | 400 | `PARAM_ERROR` | 验证码错误 |
| 验证码已使用 / 过期 / 不存在 | 400 | `PARAM_ERROR` | 验证码已使用，请重新获取 / 验证码已过期，请重新获取 / 验证码不存在或已过期 |
| 验证码连续错误 5 次 | 400 | `PARAM_ERROR` | 验证码连续错误次数过多，已作废 |
| 手机号格式非法 | 400 | `PARAM_ERROR` | 手机号格式不正确 |
| 发码过于频繁 | 409 | `BUSINESS_CONFLICT` | 验证码发送过于频繁，请稍后再试 |
| 账号被禁用时登录 | 409 | `BUSINESS_CONFLICT` | 账号不可用：<禁用原因> |
| 咨询师不存在或不可展示 | 400 | `PARAM_ERROR` | 咨询师不存在或不可展示 |
| 管理员账号或密码错误 | 400 | `PARAM_ERROR` | 账号或密码不正确 |
