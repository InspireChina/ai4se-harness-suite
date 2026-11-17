# 错误码规范

## 全局异常处理

本项目 **没有** 自定义异常类体系。所有异常由
`infrastructure/config/GlobalExceptionHandler`（`@RestControllerAdvice`）统一转换：

| 抛出什么 | HTTP | errorCode | 什么时候用 |
|---|---|---|---|
| `IllegalArgumentException` | 400 | `PARAM_ERROR` | 参数不合法、查不到的资源（异常消息即 `errorMessage`） |
| `IllegalStateException` | 409 | `BUSINESS_CONFLICT` | 业务状态冲突（如同一时段被占用） |
| `MethodArgumentNotValidException` | 400 | `VALIDATION_ERROR` | `@Valid` 字段级校验失败（自动抛出，不手写） |
| 其它 `Exception` | 500 | `SYSTEM_ERROR` | 兜底，消息固定为「系统繁忙」 |

## 写新代码的约定

- 参数不合法 / 资源不存在 → 抛 `IllegalArgumentException`
- 业务状态冲突 → 抛 `IllegalStateException`
- 不要裸抛 `RuntimeException`：会落到 500 兜底，业务语义丢失
- 鉴权失败由 Spring Security 直接返回 401 / 403，不走 `ErrorResponse` 包装

## 响应体格式

`GlobalExceptionHandler.ErrorResponse` 的字段是 `errorCode` / `errorMessage` / `data`
（**不是** `message`）：

```json
{
  "errorCode": "BUSINESS_CONFLICT",
  "errorMessage": "该时段已被占用",
  "data": null
}
```

## 错误码表

全量错误码与"当前实现映射"见 `docs/facts/tech-topic/error-code.md`。

---

## 前端错误处理

### Axios 响应拦截器

```typescript
api.interceptors.response.use(
  res => res,
  error => {
    const { status, data } = error.response || {}

    if (status === 401) {
      // Token 过期或无效 → 清除登录状态，跳转登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (status === 403) {
      // 无权限 → 显示提示
      ElMessage.error('无权访问该资源')
      return Promise.reject(error)
    }

    if (status === 409) {
      // 业务冲突 → 将错误消息透传给调用方显示
      ElMessage.warning(data?.errorMessage || '操作冲突')
      return Promise.reject(error)
    }

    if (status >= 500) {
      ElMessage.error('系统繁忙，请稍后重试')
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)
```

### 业务调用处处理

```typescript
try {
  await appointmentService.cancel(id, reason)
  ElMessage.success('取消成功')
  refreshList()
} catch (err: any) {
  // 409 已在拦截器中处理 toast
  // 400 错误展示具体提示
  if (err.response?.status === 400) {
    ElMessage.warning(err.response.data?.errorMessage || '参数错误')
  }
}
```

### 错误提示原则

| HTTP Status | 用户提示方式 | 说明 |
|-------------|-------------|------|
| 400 | `ElMessage.warning` | 参数错误，具体消息来自后端 |
| 401 | 自动跳转登录页 | Token 失效，静默处理 |
| 403 | `ElMessage.error` | 无权限，阻断操作 |
| 409 | `ElMessage.warning` | 业务冲突，具体消息来自后端 |
| 500 | `ElMessage.error` | 系统繁忙，通用提示 |
