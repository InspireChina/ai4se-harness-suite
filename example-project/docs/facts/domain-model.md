# 领域模型

> 当前已实现 ACC（账号与个人中心）。  
> 其余 feature 按 `docs/features/iteration1/`（COB～PLT）继续落地后回写本文档。

## 聚合根

### Account（账号）

统一账号：终端用户 / 咨询师 / 管理员共用一套账号体系。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String | UUID 字符串主键 |
| phoneHash | String | 手机号摘要，唯一登录标识 |
| phoneCipher | String | 手机号密文，仅本人可解密展示 |
| roles | Set\<AccountRole\> | 角色集合：`USER` / `CONSULTANT` / `ADMIN` |
| status | AccountStatus | `ACTIVE` / `DISABLED` |
| phoneVerifiedAt / lastLoginAt | Instant | 验证时间 / 最近登录时间 |
| disabledReason | String | 禁用原因 |
| tokenVersion | int | 会话版本；禁用/启用时 +1，令旧 JWT 立即失效 |
| passwordHash | String | 仅 ADMIN 使用（BCrypt） |

行为：

| 方法 | 说明 |
|---|---|
| `registerByPhone(...)` | 手机号注册，默认授予 `USER` 角色 |
| `createAdmin(...)` | 平台分配管理员（R-COMMON-001，不开放自助注册） |
| `grantConsultantRole()` | 幂等授予 `CONSULTANT`（供 COB 审核通过后调用） |
| `disable(reason)` / `enable()` | 状态流转 + 抬升 `tokenVersion`；重复调用幂等 |
| `touchLogin(now)` | 记录最近登录时间 |
| `assertUsable()` | 账号禁用时抛 `IllegalStateException`（提示不可用原因） |

状态机：

```
ACTIVE --disable(reason)--> DISABLED   （tokenVersion +1）
DISABLED --enable()------> ACTIVE      （tokenVersion +1）
```

### UserProfile（用户资料）

`accountId` / `nickname` / `avatarUrl` / `email` / `cityCode` / `locale` / `updatedAt`。
昵称 2~30 字符、邮箱格式与长度、城市编码长度在领域层校验。

### FavoriteConsultant（收藏咨询师）

`id` / `accountId` / `consultantId` / `createdAt`；(accountId, consultantId) 唯一。

### AgreementConsent（协议同意记录）

`id` / `accountId` / `agreementType` / `agreementVersion` / `consentedAt` / `sourceIp`；
不可变、不可物理删除；(accountId, type, version) 唯一。

### SmsVerificationCode（短信验证码）

`id` / `phoneHash` / `codeHash` / `expiresAt` / `failCount` / `usedAt` / `createdAt`；
连续失败 5 次作废。

## 领域服务与端口

| 组件 | 层 | 说明 |
|---|---|---|
| `SmsCodeService` | domain/service | 验证码签发 / 校验 / TTL / 失败次数作废 / 重发限流（纯 Java，由 `DomainServiceConfig` 注册） |
| `PhoneCrypto` | domain/service | 手机号摘要与加解密端口（实现 `AesPhoneCrypto`：HMAC-SHA256 摘要 + AES-256-GCM 密文） |
| `SmsSender` | domain/service | 短信发送端口（实现 `MockSmsSender`，真通道归 PLT） |
| `DisplayableConsultantPort` | domain/service | 咨询师「可展示」判定端口（实现 `StubDisplayableConsultantPort`，CDC/COB 落地后替换） |
| `TokenIssuer` | domain/service | 令牌签发端口（实现 `JwtTokenProvider`） |
| `PasswordService` | domain/service | 密码编码端口（实现 `PasswordServiceImpl`，BCrypt） |

## 值对象与枚举（domain/vo）

| 类型 | 取值 | 说明 |
|---|---|---|
| `AccountRole` | USER / CONSULTANT / ADMIN | 角色，JWT authority = `ROLE_<name>` |
| `AccountStatus` | ACTIVE / DISABLED | 账号状态 |
| `AgreementType` | SERVICE(`service`) / PRIVACY(`privacy`) | 协议类型，对外用小写码 |
| `PhoneNumber` | — | 手机号规范化（去空格/横线）与格式校验 |

## 平台骨架（非业务聚合）

| 组件 | 说明 |
|------|------|
| JWT / UserContext | 无状态鉴权：Claims `sub` / `roles` / `tokenVersion`；过滤器校验账号状态与版本 |
| IBusinessRule / BusinessRuleConfig | 业务规则框架空注册 |
| DataDictionary* | 数据字典框架类型，已注册 `AccDataDictionaryType`（账号状态 / 角色 / 协议类型） |
| PasswordService | 密码编码接口（BCrypt 实现） |
