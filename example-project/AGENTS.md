# 架构与工程规范（咨询预约单体应用）

本文件定义本代码库的架构边界、分层规则、模块职责与工程规范。目标是让新成员与自动化工具在不了解上下文的情况下，也能按一致方式新增功能、扩展模块并避免破坏依赖关系。

## 1. 仓库拓扑

这是一个全栈工程（Java 17 / Spring Boot 3.2.x / Vue 3 + TypeScript），主要模块如下：

- `containers/backend/`：Spring Boot 后端（四层 DDD 单体）
- `containers/frontend/`：Vue 3 + TypeScript 前端（Vite 构建）

运行时形态：

- Client → Vue 前端 (Vite dev server :5173) → 反向代理 `/api` → Spring Boot 后端 (:8080)
- 后端直连 MySQL，不经过 BFF 层
- JWT 由后端直接签发与校验（HMAC-SHA256）

## 2. 横切关注点：鉴权与用户上下文

当前约定的鉴权与上下文传递：

- 前端登录后获得 JWT token，存储于 Pinia store / localStorage
- Axios 拦截器在请求头添加 `Authorization: Bearer <token>`
- 后端 `JwtAuthenticationFilter` 解析 token，将 `UserContext` 写入 `UserContextHolder`（ThreadLocal）
- 应用层通过 `SecurityUtils` / `UserContextHolder` 获取当前用户上下文

约束：

- 后端自行校验 JWT（不在前端或网关层做）
- 应用层/领域层不得依赖 Web 框架对象（Request/Response），只能依赖 `UserContextHolder` 或方法参数传入的 `userId`
- Admin 端路由使用 `/admin/**` 路径，后端 `SecurityConfig` 限制为 `ROLE_ADMIN`

## 3. 标准分层

业务代码遵循四层结构（包路径 `com.consultation.*`）：

- `adapter`：对外适配层（HTTP Controller），只做协议转换与参数校验（`adapter/rest/`）
- `application`：用例编排层（AppService / Service），组合 domain 行为、调用 repository、管理事务边界
- `domain`：领域模型层（aggregate / vo / DomainService），承载业务不变量与状态机
- `infrastructure`：基础设施层（`infrastructure/persistence/`），提供 repository 实现、MyBatis-Plus mapper、PO 等

依赖方向（强制）：

- adapter → application → domain
- infrastructure → domain（实现 domain 定义的接口）
- domain 不得依赖 infrastructure / adapter / Web 框架

## 4. DTO、Assembler 与 Converter 约定

DTO 约定：

- 写操作入参使用 `*Command` 或 Request DTO（`adapter/rest/dto/`）
- 对外返回使用 `*Response`（`adapter/rest/dto/`）
- domain 与 infrastructure 之间使用 `*Converter` 做 PO ⟷ domain 转换
- application 层使用 `*Assembler` 做 domain ⟷ DTO 转换

映射约定：

- adapter 不直接操作 domain 实体
- 入参先在 Controller 中校验（`@Valid`），以 DTO 传入 application 层
- 使用手动转换（非 MapStruct），遵循现有 Converter/Assembler 命名

## 5. 持久化规则（MyBatis-Plus）

当前技术栈：

- MyBatis-Plus 3.5.5（Spring Boot 3 starter）
- PO（持久化对象）放在 `infrastructure/persistence/po/`
- Mapper 放在 `infrastructure/persistence/mapper/`
- Repository：domain 只定义 repository 接口（聚合根维度），infrastructure 提供实现（`*RepositoryImpl`）
- 主键使用 UUID 字符串（`VARCHAR(64)`），由应用层生成

聚合与一致性：

- 聚合内的子实体由 repository 在同一事务内完成装配与持久化
- 复杂查询优先走 Mapper + DTO，写操作必须通过聚合行为与 repository

## 6. 事务边界

事务边界统一放在 application 层：

- 以一个用例为单位在 AppService 方法上标注 `@Transactional`
- domain 方法不直接开启/提交事务
- `@Transactional` 不在 Controller 或 Repository 层使用

## 7. 错误模型与异常处理

所有异常由 `GlobalExceptionHandler`（`@RestControllerAdvice`）统一转换为 `ErrorResponse`：

| 抛出什么 | HTTP | errorCode | 什么时候用 |
|---|---|---|---|
| `IllegalArgumentException` | 400 | `PARAM_ERROR` | 参数不合法、查不到的资源（异常消息即 `errorMessage`） |
| `IllegalStateException` | 409 | `BUSINESS_CONFLICT` | 业务状态冲突（如同一时段被占用） |
| `MethodArgumentNotValidException` | 400 | `VALIDATION_ERROR` | `@Valid` 字段级校验失败（自动抛出，不手写） |
| 其它 `Exception` | 500 | `SYSTEM_ERROR` | 兜底，消息固定为「系统繁忙」 |

写新代码时的约定：

- 参数不合法 / 资源不存在 → 抛 `IllegalArgumentException`
- 业务状态冲突 → 抛 `IllegalStateException`
- 不要裸抛 `RuntimeException`：会落到 500 兜底，业务语义丢失

鉴权失败由 Spring Security 直接返回 **401 / 403**，**不走** `ErrorResponse` 包装。

对外响应体为 `GlobalExceptionHandler.ErrorResponse`，字段是 `errorMessage`（**不是** `message`）：

```json
{
  "errorCode": "BUSINESS_CONFLICT",
  "errorMessage": "该时段已被占用",
  "data": null
}
```

错误码清单与"当前实现映射"见 `docs/facts/tech-topic/error-code.md`。

## 8. 领域设计：聚合与规则

> **现状**：ACC（账号与个人中心）已落地，聚合见下；其余 feature 以 `docs/features/iteration1/` 为准，
> 按 feature plan 重建后回写本节与 `docs/facts/domain-model.md`（as-built）；Core 见 `docs/architecture/business/core-domain-model.md`。

业务规则引擎（`domain/businessrule/`）— **框架保留、规则未注册**：

- `IBusinessRule` 接口：`getRuleName()` / `getDescription()`
- `BusinessRuleConfig` + `BusinessRuleProvider`；注册入口 `BusinessRuleRegistration`（当前为空）
- 规则 YAML 目录：`resources/business-rules/`（可按 feature 新增）

数据字典（`domain/datadictionary/`）— **框架保留、ACC 已注册**：

- `Description` / `DataDictionaryType` / `DataDictionaryUtil`
- ACC 注册 `AccDataDictionaryType`（账号状态 / 账号角色 / 协议类型）
- 实现 feature 时新增枚举并回写 `docs/facts/tech-topic/data-dict.md`

### 已落地聚合（ACC）

聚合根 **Account**（`domain/aggregate/Account.java`）：角色集合（USER / CONSULTANT / ADMIN）、
状态机（`ACTIVE` ⇄ `DISABLED`）、`tokenVersion`（禁用/启用时 +1，令旧 JWT 立即失效）、
手机号摘要 + 密文。行为：`registerByPhone` / `createAdmin` / `grantConsultantRole`（幂等）/
`disable` / `enable` / `touchLogin` / `assertUsable`。

关联实体：`UserProfile` / `FavoriteConsultant` / `AgreementConsent` / `SmsVerificationCode`。

领域端口（domain 定义、infrastructure 实现，可替换）：
`PhoneCrypto` / `SmsSender` / `DisplayableConsultantPort` / `TokenIssuer` / `PasswordService`。


## 9. 预约状态机

> 旧示例状态机已清除。以 `docs/features/iteration1/BKG-booking`（及相关）spec §9 为准，实现后回写 `docs/facts/tech-topic/state-machine.md`。

## 10. 测试规范

### 两类用例的归属

测试用例分两层，**归属看"谁定义、谁判定"，不是"谁敲的代码"**：

| | 开发自测 | QA 测试 |
|---|---|---|
| 验证什么 | 代码按 Plan 的设计工作 | 系统符合需求规格 |
| 谁定义 / 谁判定 | 开发本人 | **QA** |
| 用例编号 | 无编号，命名表达意图 | `TC-xxx`，与文本用例一一对应 |
| 存放位置 | 源码旁（`*Test.java`、`*.test.ts`） | `docs/` 用例库 + `e2e/tests/qa/` |
| 合并闸门 | 否 | **是** |
| 失败意味着 | 代码写错了 | 需求没实现 / 理解有偏差 / 规格有歧义 |

约定：

- QA 用例的自动化实现可由开发代写，但定义权与判定权归 QA
- 开发自测全绿 ≠ 需求被实现，不能替代 QA 测试
- QA 用例必须先有文本用例（`docs/test-cases/e2e-cases/`），再写自动化

完整规范见 `docs/standards/test.md`。

### 测试技术栈

- JUnit 5 + SpringBootTest + RANDOM_PORT
- RestAssured 做 API 集成测试
- MariaDB4j 启动临时 MySQL 实例（替代 H2），确保 MySQL 方言兼容
- 测试使用 `schema.sql` + `data.sql` 初始化数据
- ResetDbService 在每个 `@BeforeEach` 中 TRUNCATE 全表

### 测试环境配置

- 测试使用 `application.yml`（test resources），配置 MariaDB4j
- Flyway 在测试中禁用（`spring.flyway.enabled=false`）
- `@ActiveProfiles("test")` 在 TestBase 中设置

### 开发自测覆盖要求

- 每个 API **必须** 有对应的集成测试
- 至少覆盖：
  - 1 个 Happy Path
  - 关键失败分支（参数错误 / 权限不足 / 业务冲突）
- DB 相关用例必须可重复执行，不依赖执行顺序
- 前端 Component/Composable 单元测试使用 Vitest（与源码同目录，`*.test.ts`）
- 命名：类名 `{被测Controller}Test`，方法名 `should_{action}_{expectedResult}`（不写 `TC-` 编号）

### QA 测试要求

- 需求规格的每条验收标准、每条业务规则 → 至少 1 条 QA 用例
- 编号统一 `TC-xxx`，文本用例与自动化用例共用同一编号
- 文本用例集中在 `docs/test-cases/`：`e2e-cases/`、`manual-cases/`、`smoking-cases/`（QA）与 `dev-self-cases/`（开发自测索引）；E2E 自动化在 `e2e/tests/qa/`
- 用例可独立重复执行，不依赖执行顺序

### E2E 测试

- Playwright + Chromium，按归属分两层：

| 目录 | 归属 | 说明 |
|---|---|---|
| `e2e/tests/qa/` | **QA 测试** | 验收用例的自动化实现，与 `docs/test-cases/e2e-cases/test-cases.md` 一一对应，合并闸门 |
| `e2e/tests/dev/` | 开发自测 | 开发期快速反馈，不作为验收依据 |

- 运行命令：

```bash
bash e2e-run.sh            # 启动前后端 + 执行全部 E2E
cd e2e && npm run test:qa  # 只跑 QA 验收用例（合并闸门）
cd e2e && npm run test:dev # 只跑开发自测用例
```

## 11. 前端规范

- Vue 3 Composition API + `<script setup>` 语法
- UI 组件库：**Element Plus**（业务前端；需求演示原型为独立 Vite 工程 `docs/features/iteration1/prototypes/`）
- Pinia 管理全局状态（auth store 位于 `src/stores/auth.ts`）
- Vue Router 4 管理路由，布局文件位于 `src/layouts/`
- Axios 统一封装，请求拦截器自动添加 JWT，响应拦截器处理 401 跳转
- 全局 CSS 变量位于 `src/styles/variables.css`
- 视图文件按子系统分组：`src/views/user/`、`src/views/admin/`（咨询师端后续按 `consultant/` 扩展）
- Service 层封装 API 调用（`src/services/xxxService.ts`），每个领域一个文件
- Composable 封装可复用逻辑（`src/composables/useXxx.ts`），如 `useBooking`、`useAuth`
- 页面级组件组合 Composable + UI 组件，视图内不含直接 API 调用

## 12. PR / 变更检查清单

- 分层检查：adapter 不含业务逻辑；domain 不依赖 infrastructure；事务边界在 application
- 错误处理：参数/资源错误抛 `IllegalArgumentException`，业务冲突抛 `IllegalStateException`，避免裸 `RuntimeException`
- API 设计：RESTful 风格，路径统一 `/api/v1/resource`，admin 使用 `/admin/resource`
- 安全：不记录 token / 敏感信息；对外接口做鉴权检查
- 数据字典：新增枚举需要同时更新 `DemoDataDictionaryType` 与 `docs/facts/tech-topic/data-dict.md`
- 业务规则：新增规则需要同时更新 YAML 配置与 `docs/facts/tech-topic/businessrule.md`
- 数据库变更：新增 DDL 需同时更新 Flyway migration 文件、测试 `schema.sql`、以及 `docs/facts/db-schema.md`
- 验证：本地运行 `mvn test` 确认全部通过，`npm run build` 确认前端编译通过

## 13. 文档结构

文档体系位于 `docs/` 目录，所有 AI Agent 及开发人员必须遵守以下路径约定：

```
docs/
├── architecture/           # 高阶意图（项目准备：BA/TL）
│   ├── tech/
│   │   ├── c4-context.md
│   │   ├── c4-container.md
│   │   └── adr.md          # 跨迭代 ADR（一句话表）
│   └── business/
│       ├── glossary.md     # 项目级双语术语表
│       ├── product.md
│       ├── core-domain-model.md # 核心领域模型（核心聚合+关键字段）
│       └── iterations.md
├── features/               # 需求规格 + 技术方案（过程文档）
│   ├── _template/          # spec.md + plan.md（plan 含粗实施步骤）
│   ├── _chores/            # 无关联 feature 的横切 plan
│   └── iteration1/         # 咨询师预约平台样例
│       ├── README.md
│       ├── high-level-design.md
│       ├── ACC-account/spec.md
│       ├── BKG-booking/spec.md
│       ├── CDC-consultant-discovery/spec.md
│       ├── COB-consultant-onboarding/spec.md
│       ├── CSC-consultant-schedule/spec.md
│       ├── CFL-consultant-fulfillment/spec.md
│       ├── SET-settlement/spec.md
│       ├── ADM-admin-ops/spec.md
│       ├── PLT-platform-capability/spec.md
│       └── prototypes/     # 独立 Vite 原型 demo（Element Plus，:5174）
├── facts/                  # 事实文档（as-built）
│   ├── api.yaml            # API 接口定义
│   ├── db-schema.md        # 数据库规格
│   ├── domain-model.md     # 领域模型（as-built）
│   ├── business/           # 业务事实
│   │   └── booking-flow.md # 业务流程
│   └── tech-topic/         # 实现专题（非 ADR）
│       ├── businessrule.md
│       ├── data-dict.md
│       ├── error-code.md
│       ├── security.md
│       └── state-machine.md
├── standards/              # 代码规范（事实文档）
│   ├── architecture.md     # 架构规范
│   ├── naming.md           # 命名规范
│   ├── security.md         # 安全规范
│   ├── api-design.md       # API 设计规范
│   ├── layers.md           # 分层规范
│   ├── db.md               # 数据库规范
│   ├── error.md            # 错误处理规范
│   ├── test.md             # 测试规范
│   ├── business-rule.md    # 业务规则规范
│   ├── data-dictionary.md  # 数据字典规范
│   ├── adr.md              # ADR 写法（正文在 architecture/tech/adr.md）
│   └── templates/          # 代码模版
│       ├── 01-ddd-controller.md
│       ├── 02-ddd-appservice.md
│       ├── 03-ddd-assembler.md
│       ├── 04-ddd-aggregate.md
│       ├── 05-ddd-domain-service.md
│       ├── 06-ddd-repository-interface.md
│       ├── 07-ddd-repository-impl.md
│       ├── 08-ddd-converter.md
│       ├── 09-ddd-po-mapper.md
│       └── 10-global-exception-handler.md
└── test-cases/             # 测试用例文本基线
    ├── e2e-cases/          # QA：E2E 验收用例文本基线（TC-xxx）
    │   └── test-cases.md
    ├── manual-cases/       # QA：手动执行用例（TC-Mxx）
    │   └── manual-test-cases.md
    ├── smoking-cases/      # QA：冒烟用例（TC-Sxx）
    │   └── smoking-test-cases.md
    └── dev-self-cases/     # 开发自测：可选场景索引
        └── README.md
```

> `docs/test-cases/` 下 `e2e-cases/`、`manual-cases/`、`smoking-cases/` 为 **QA 测试** 产物（定义权与判定权归 QA）；
> `dev-self-cases/` 为开发自测可选索引；可执行自测仍在源码旁与 `e2e/tests/dev/`。归属详见 §10 与 `docs/standards/test.md`。

### 同步要求

- 每轮任务完成后，必须检查 `docs/facts/` 中的内容是否因本次变更而需要更新
- 新增/修改 API → 更新 `docs/facts/api.yaml`
- 新增/修改数据表 → 更新 `docs/facts/db-schema.md`
- 新增/修改业务规则 → 更新 `docs/facts/tech-topic/businessrule.md`
- 新增/修改数据字典 → 更新 `docs/facts/tech-topic/data-dict.md`

### 执行检查点

每轮任务提交描述中必须包含：

- [ ] `docs/` 同步检查（已更新 / 不涉及）

## 14. 开发流程（每轮需求的标准执行步骤）

每轮需求开发必须按以下顺序执行，严禁跳过或调换步骤：

1. **迭代高阶设计（HLD）等待确认**：规格齐备后，在 `docs/features/<迭代>/high-level-design.md` 写本迭代技术边界与跨模块契约（skill：`tl-high-level-design`）。**人工确认前不得写 feature Plan**。跨迭代取舍按 `docs/standards/adr.md` 沉淀到 `docs/facts/tech-topic/`。
2. **编写 QA 测试用例**（可与 HLD 并行）：在 `docs/test-cases/e2e-cases/` 下编写本轮需求的 E2E 测试用例（文本格式，编号 `TC-xxx`），由 QA 主导判定。**先写文本用例，再写自动化**。规格确认后即可开始。
3. **Plan 等待确认**：HLD 已确认后，在对应 feature 目录（`docs/features/<迭代>/<CODE>-<slug>/`）写 `plan.md`（或多份 `plan-{slug}.md`）；无关联 feature 的横切方案放 `docs/features/_chores/`。对照 HLD 与规格，等待人工确认后再继续。
4. **编写开发自测（API 测试）**：根据 Plan 在 `containers/backend/src/test/` 中编写 RestAssured 集成测试（API 级别），运行成功但断言失败（TDD 红牌阶段）。
5. **编写实现**：编写单元测试 + 实现代码（后端 application/domain/adapter 层），通过 `mvn compile` 编译。
6. **运行开发自测**：运行 `mvn test` 修复失败的测试及其他错误，直至全部通过；同时补齐 `e2e/tests/qa/` 中本轮需求的自动化实现。
7. **浏览器调试**：使用 Playwright（`./e2e-run.sh`）启动前后端并调试，确认前端视觉效果和交互功能正常。如果报错使用 chrome-devtool-mcp 查看错误。
8. **运行 QA 验收**：`cd e2e && npm run test:qa` 全部通过，并交由 QA 对照 `docs/test-cases/e2e-cases/` 逐条验收。

> 第 4~7 步是 **开发自测**（对开发负责）；第 2、8 步是 **QA 测试**（对需求负责，是合并闸门）。开发自测全绿不等于需求已实现。
