# 实现进度：plan.md

> 关联 plan：./plan.md
> 状态：已完成
> 更新：2026-11-17 全部步骤完成（后端 49 自测 / 前端构建 / QA E2E 10 用例全绿）

## Checklist

### 1. 领域模型、枚举、仓库接口与端口（含 PhoneCrypto / SmsSender / DisplayableConsultantPort）
- [x] 枚举 `AccountRole` / `AccountStatus` / `AgreementType`（实现 `Description`，可注册数据字典）
- [x] 值对象 `PhoneNumber`（规范化 + 格式校验）
- [x] 聚合根 `Account`（角色集合、状态机、tokenVersion、登录校验）
- [x] 实体 `UserProfile` / `FavoriteConsultant` / `AgreementConsent` / `SmsVerificationCode`
- [x] 仓库接口 `AccountRepository` / `UserProfileRepository` / `FavoriteConsultantRepository` /
      `AgreementConsentRepository` / `SmsVerificationCodeRepository`
- [x] 端口 `PhoneCrypto` / `SmsSender` / `DisplayableConsultantPort` / `TokenIssuer`
- [x] 领域服务 `SmsCodeService`（签发、校验、TTL、失败 5 次作废、重发限流）

### 2. Flyway + PO/Mapper/Converter/RepositoryImpl + 测试 schema/data 种子 ADMIN
- [x] Flyway `V20261117__acc_account.sql`（§3 DDL 全量新建）
- [x] 回滚脚本 `db/rollback/V20261117__acc_account_rollback.sql`
- [x] PO：`AccountPO` / `UserProfilePO` / `FavoriteConsultantPO` / `AgreementConsentPO` / `SmsVerificationCodePO`
- [x] Mapper ×5
- [x] Converter ×5（roles_json 序列化、时间转换）
- [x] RepositoryImpl ×5
- [x] 基础设施实现：`AesPhoneCrypto` / `MockSmsSender` / `StubDisplayableConsultantPort`
- [x] 测试 `schema.sql` / `data.sql`（ADMIN 由 `AccountSeedInitializer` 运行时创建，密文与密钥相关）

### 3. Auth / Profile / Favorite / Agreement / Admin 应用服务与 Assembler、事务与幂等
- [x] `AuthAppService`（发码 / 验证码登录注册合一 / 管理员密码登录）
- [x] `ProfileAppService`（me 查询 / 资料更新）
- [x] `FavoriteAppService`（收藏幂等 / 取消幂等）
- [x] `AgreementAppService`（协议同意幂等 + 查询）
- [x] `AdminAccountAppService`（禁用 / 启用，抬 tokenVersion）
- [x] Assembler ×4（Account / Profile / Favorite / Agreement）

### 4. REST API、Security/JWT/UserContext 改造、全局错误语义对齐
- [x] `JwtTokenProvider`：Claims 扩展 `roles`（数组）+ `tokenVersion`
- [x] `JwtAuthenticationFilter`：校验 status=ACTIVE 且 tokenVersion 一致，否则 401
- [x] `UserContext` / `SecurityUtils`：角色集合 + `hasRole`
- [x] `SecurityConfig`：放行 `POST /api/v1/auth/**`；`/api/v1/admin/**` 需 ROLE_ADMIN
- [x] `AuthController` / `MeController` / `AdminAccountController`
- [x] DTO：Command/Request + Response（`adapter/rest/dto/`）

### 5. 前端登录页与个人中心（对齐原型路由）、auth store 与拦截器
- [x] `views/auth/Login.vue`（路由 `/user/login`）
- [x] `views/user/Profile.vue`（路由 `/user/profile`）
- [x] `layouts/UserLayout.vue`
- [x] `services/authService.ts` / `profileService.ts` / `favoriteService.ts` / `agreementService.ts`
- [x] `stores/auth.ts`：token + user + roles
- [x] `router/index.ts`：路由 + 守卫
- [x] `utils/request.ts`：401 跳转、400/403/409 提示

### 6. 开发自测（单元 + API）与 E2E/QA 文本用例挂钩
- [x] 单元测试：`AccountTest`（状态机 / 角色幂等 / tokenVersion）
- [x] 单元测试：`SmsCodeServiceTest`（失败 5 次作废 / 过期）
- [x] 单元测试：`PhoneNumberTest`（规范化 / hash 稳定性）
- [x] API 集成测试：`AuthControllerTest`（AC-001、R-CREATE-002）
- [x] API 集成测试：`MeControllerTest`（AC-002、AC-003、AC-004、PR-001）
- [x] API 集成测试：`AdminAccountControllerTest`（AC-005）
- [x] QA 文本用例写入 `docs/test-cases/e2e-cases/test-cases.md`（TC-001～TC-009）
- [x] E2E 自动化 `e2e/tests/qa/acc-account.spec.ts`（10 passed）

### 7. 同步 `docs/facts/` 与 JWT ADR Claims 说明
- [x] `docs/facts/api.yaml`
- [x] `docs/facts/db-schema.md`
- [x] `docs/facts/domain-model.md`
- [x] `docs/facts/tech-topic/security.md` / `data-dict.md` / `004-jwt-stateless-auth.md` / `error-code.md`
- [x] `AGENTS.md` §8 聚合简述

### 8. 验证与上线准备
- [x] 执行 Flyway 迁移 `V20261117__acc_account.sql`（本地 `consultation` 库按 plan §11.3 重建）
- [x] 回滚脚本就位 `db/rollback/V20261117__acc_account_rollback.sql`
- [x] 冒烟用例（plan §13 六步）全部通过
- [x] `mvn test` 全绿（49 用例）
- [x] `npm run build` 通过
- [x] `npm run test:qa` 全绿（10 用例）

## 备注

- **测试库**：测试环境使用本机 MySQL `consultation_test`（`src/test/resources/application.yml`）。
  AGENTS.md §10 写的是 MariaDB4j + `@ActiveProfiles("test")`，与工程现状不一致 —— **本次未改**（属既有工程问题，已记录）。
- **管理员种子**：ADMIN 账号由 `AccountSeedInitializer` 运行时创建（密文与 `phone.crypto.key` 相关，
  无法固化为 data.sql 静态行），测试用例每个 `@BeforeEach` 清库后重建。
- **前端单元测试**：本次未引入 Vitest（工程尚未配置），前端行为由 E2E（`e2e/tests/qa/`）覆盖。
- **接口层 DTO 位置**：按 plan §11.1，`*Response` 放在 `adapter/rest/dto/`，由 `application/assembler/*`
  组装；因此 application 层存在对 adapter DTO 包的引用（分层细则的一处已知例外）。
