# 开发自测用例索引（可选）

> **归属：开发自测。** 本目录用于记录本迭开发自测场景清单（可选文本索引）。
>
> - 真正的可执行用例放在源码旁（`*Test.java`、`*.test.ts`）与 `e2e/tests/dev/`
> - **不写 `TC-` 编号**（`TC-` 是 QA 用例编号空间）
> - 自测全绿 ≠ 需求已验收

## 本迭索引

### ACC · 账号与个人中心

| 场景 | 位置 | 备注 |
|---|---|---|
| 账号状态机、角色幂等授予、tokenVersion | `containers/backend/src/test/java/com/consultation/domain/aggregate/AccountTest.java` | 禁用/启用幂等、禁用拒绝登录 |
| 验证码签发 / 校验 / 失败 5 次作废 / 过期 / 重发限流 | `containers/backend/src/test/java/com/consultation/domain/service/SmsCodeServiceTest.java` | 领域服务（纯 Java） |
| 手机号规范化与格式校验 | `containers/backend/src/test/java/com/consultation/domain/vo/PhoneNumberTest.java` | 值对象 |
| 发码、验证码登录注册、管理员登录 | `containers/backend/src/test/java/com/consultation/adapter/rest/AuthControllerTest.java` | AC-001、R-CREATE-001/002 |
| 本人资料、收藏幂等、协议同意 | `containers/backend/src/test/java/com/consultation/adapter/rest/MeControllerTest.java` | AC-002/003/004、PR-001 |
| 管理员禁用 / 启用、会话失效、越权拦截 | `containers/backend/src/test/java/com/consultation/adapter/rest/AdminAccountControllerTest.java` | AC-005、PR-003 |
