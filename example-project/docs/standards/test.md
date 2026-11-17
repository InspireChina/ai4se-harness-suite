# 测试规范

## 0. 两类用例：开发自测 vs QA 测试

本项目的测试用例分两层，**归属看"谁定义、谁判定"，不是"谁敲的代码"**。

| 维度 | 开发自测（Dev Self-Test） | QA 测试（QA Test） |
|---|---|---|
| **验证什么** | 代码按 **Plan** 的设计工作 | 系统符合 **需求规格** |
| **用例来源** | Plan（技术方案） | 需求规格 `docs/features/` + 业务规则编号 |
| **谁定义** | 开发本人 | QA（与 PO 对齐业务规则） |
| **谁判定** | 开发本人 | **QA** |
| **什么时候写** | 实现过程中，边写边补 | 实现完成后的验收阶段 |
| **用例编号** | 无编号，用命名表达意图 | `TC-xxx`，与文本用例一一对应 |
| **存放位置** | 源码旁（`*Test.java`、`*.test.ts`） | `docs/` 用例库 + `e2e/tests/qa/` |
| **是不是合并闸门** | 否（自测不通过，开发自己不能提交） | **是**（QA 用例不通过，不能验收、不能合并） |
| **失败意味着** | 代码写错了 | 需求没实现 / 理解有偏差 / 规格有歧义 |
| **谁修** | 开发 | 开发（QA 判定并跟单） |

### 关键约定

1. **QA 用例的自动化实现可以由开发代写**，但用例的 **定义权与判定权归 QA**。
2. **开发自测不能替代 QA 测试**。开发自测全绿 ≠ 需求被实现。
3. **QA 用例必须先有文本用例**（`docs/test-cases/e2e-cases/`），再写自动化。反过来做会漏场景。
4. 发现实现中出现 **需求规格之外** 的行为，是缺陷（除非 PO 明确认可）。

---

## 1. 用例归属速查

| 层 | 类型 | 归属 | 位置 | 框架 |
|---|---|---|---|---|
| Adapter | 集成测试 | 开发自测 | `backend/src/test/**/*Test.java` | SpringBootTest + RestAssured |
| Application | 单元测试 | 开发自测 | `backend/src/test/**/*Test.java` | JUnit 5 + Mockito |
| Domain | 单元测试 | 开发自测 | `backend/src/test/**/*Test.java` | JUnit 5 |
| Infrastructure | 集成测试 | 开发自测 | `backend/src/test/**/*Test.java` | SpringBootTest + MariaDB4j |
| View | E2E 验收 | **QA 测试** | `e2e/tests/qa/` | Playwright |
| — | E2E 自测 | 开发自测 | `e2e/tests/dev/` | Playwright |
| Composable / Store / Component | 单元测试 | 开发自测 | `frontend/src/**/*.test.ts` | Vitest |
| — | 手动用例 | **QA 测试** | `docs/test-cases/manual-cases/` | 人工 |
| — | 冒烟用例 | **QA 测试** | `docs/test-cases/smoking-cases/` | 人工 / 自动化 |
| — | 自测场景索引 | 开发自测 | `docs/test-cases/dev-self-cases/` | 可选文本索引 |

---

## 2. 开发自测规范

### 2.1 后端分层测试策略

| 层次 | 测试类型 | 关注点 |
|------|----------|--------|
| Adapter | 集成测试 | 请求/响应/状态码/错误码 |
| Application | 单元测试 | 用例编排/事务边界 |
| Domain | 单元测试 | 业务不变量/状态机 |
| Infrastructure | 集成测试 | 持久化/映射正确性 |

### 2.2 Adapter 层集成测试约定

- 基类：`TestBase` 继承 `@SpringBootTest(webEnvironment = RANDOM_PORT)`
- HTTP 客户端：RestAssured（配置端口 + 日志）
- 数据隔离：`@BeforeEach` 重置所有表
- 认证：使用 `loginAsUser()` / `loginAsAdmin()` 辅助方法获取 Token

### 2.3 命名

- 类名：`{被测Controller}Test`（如 `AuthControllerTest`）
- 方法名：`should_{action}_{expectedResult}`（如 `should_register_and_return_token`）
- 用例名 **不写** `TC-` 编号 —— 编号属于 QA 用例

### 2.4 覆盖要求（每个 Controller 测试）

- 1 个 happy path
- 2 个错误分支
- 涉及聚合写入的，补 1 个业务冲突分支

### 2.5 前端单元测试（Vitest）

- 测试文件与源码同目录，以 `.test.ts` 结尾
- Composable 测试：mock service 层，验证响应式状态
- Store 测试：使用 `setActivePinia(createPinia())` 隔离 store 实例

---

## 3. QA 测试规范

### 3.1 四类 QA 产物

| 产物 | 位置 | 说明 |
|---|---|---|
| 文本验收用例 | `docs/test-cases/e2e-cases/test-cases.md` | QA 用例的 **基线**，先写这里 |
| E2E 自动化 | `e2e/tests/qa/*.spec.ts` | 文本用例的自动化实现，编号一一对应 |
| 手动用例 | `docs/test-cases/manual-cases/manual-test-cases.md` | 自动化难覆盖 / 需人工判断 |
| 冒烟用例 | `docs/test-cases/smoking-cases/smoking-test-cases.md` | 发版前 5 分钟跑完的最小集 |
| 开发自测索引 | `docs/test-cases/dev-self-cases/` | 可选；可执行用例仍在源码旁 / `e2e/tests/dev/` |

### 3.2 编号约定

- QA 用例统一编号 `TC-xxx`（文本用例与自动化用例 **共用** 同一编号）
- 业务规则编号（`R-xxx`）与用例编号（`TC-xxx`）是 **映射关系**，不是同一个编号空间
- 自动化用例的 `test()` 标题里带上 `TC-xxx`，便于双向追溯：

```ts
test('TC-021 预约成功后出现在预约列表中', async ({ page }) => {
  ...
})
```

### 3.3 覆盖要求

- 需求规格 §12 的 **每条** 验收标准 → 至少 1 条 QA 用例
- 每条业务规则（`R-xxx`）→ 至少 1 条 QA 用例
- 至少覆盖：Happy Path / 参数错误 / 权限不足 / 业务冲突 / 边界

### 3.4 可重复执行

- 用例之间 **不能有顺序依赖**
- 每个用例自己准备数据、自己清理数据
- 不依赖真实外部服务的时间点、随机数、当前时间

### 3.5 运行

```bash
cd e2e
npm run test:qa     # 只跑 QA 验收用例（合并闸门）
npm run test:dev    # 只跑开发自测用例
npm test            # 全部
```

---

## 4. 合并闸门

| 闸门 | 要求 | 谁判定 |
|---|---|---|
| 开发自测 | `mvn test` 全绿、`npm run build` 通过、`npm run test:dev` 不阻塞 | 开发 |
| QA 验收 | `npm run test:qa` 全绿 + 文本用例逐条勾选 | QA |

**QA 闸门未过，不能合并。** 开发自测不过，先修再提。

---

## 5. 测试环境

- 测试使用 `application.yml`（test resources），配置 MariaDB4j
- Flyway 在测试中禁用（`spring.flyway.enabled=false`）
- `@ActiveProfiles("test")` 在 TestBase 中设置
- 测试使用 `schema.sql` + `data.sql` 初始化数据
- ResetDbService 在每个 `@BeforeEach` 中 TRUNCATE 全表
- DB 相关用例必须可重复执行，不依赖执行顺序
