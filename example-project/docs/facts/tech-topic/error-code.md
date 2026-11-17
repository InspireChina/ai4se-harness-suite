# 错误码清单

> 框架约定（空壳 as-built）。业务专属错误码待 iteration1 实现后补充。  
> 与 `GlobalExceptionHandler` 及 `docs/standards/error.md` 对齐。

## 当前 Handler 映射

| 抛出 | HTTP | errorCode | 说明 |
|------|------|-----------|------|
| `IllegalArgumentException` | 400 | `PARAM_ERROR` | 参数/资源不合法 |
| `IllegalStateException` | 409 | `BUSINESS_CONFLICT` | 业务状态冲突 |
| `MethodArgumentNotValidException` | 400 | `VALIDATION_ERROR` | `@Valid` 失败 |
| 其它 `Exception` | 500 | `SYSTEM_ERROR` | 兜底（对外「系统繁忙」） |

鉴权失败由 Spring Security 直接返回 **401 / 403**，不走 `ErrorResponse`。

响应体字段：`errorCode` / `errorMessage` / `data`。
