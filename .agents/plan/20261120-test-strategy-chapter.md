# 指南加一章：测试策略（分层 + 在框架中的落点）

## 目标

把 `.tmp` 第 8–18 行的测试策略落进 `team-workflow-guide/index.html`：**一张表**说清
「九层测试分别由谁做、落在哪个 skill / 命令 / 落盘文件、不过会卡在哪」，
并用一段讲清 **变异测试** 为什么是 AI 测试的必需项、失败后怎么回炉。

现有 `§4 测试分层与归属` 只有「开发自测 vs QA 测试」两栏，讲归属不讲策略。
本章 **升级这一节**（`#testing` 锚点不变），不新增 §8 —— 否则两份测试内容会互相打架。

## 不做什么

- 不改任何 skill 模板（`dev-self-test` 里仍有 `{{E2E_DIR}}/tests/dev/` 通道）。
  与「研发自测不写 E2E」的差异按 **迁移期规则** 写进正文，skill 对齐留作下一轮
- 不改 `example-project` 的测试代码与 `docs/standards/test.md` 的分类表，只加一句指针
- 不引入 lint 工具（example 现在没有 eslint / checkstyle），表里如实写「无专属 skill，项目自定命令」
- 不动 `flow.html`（测试层不落在角色交接的某一列上）

## 改动清单

| 文件 | 改什么 |
|---|---|
| `team-workflow-guide/index.html` | TOC `4. 测试归属` → `4. 测试策略`；`<section id="testing">` 重写为 4.1–4.4 |
| `team-workflow-guide/README.md` | 内容覆盖第 4 条改成「测试策略：九层阶梯 + 框架落点」 |
| `example-project/docs/standards/test.md` | 顶部加一句指针：分层策略看指南 §4，本文件只写本项目实现细节 |
| `CHANGELOG.md` | 0.4.0 段补一条 |

## §4 正文结构

### 4.1 策略阶梯（主表，9 行）

| 层 | 谁做 | 框架落点（skill · 命令 · 落盘） | 不过会怎样 |
|---|---|---|---|
| Lint / 静态检查 | DEV（TL 定命令） | `AGENTS.md` §10 定命令 + CI；**无专属 skill** | 不能提交 |
| Code Review | DEV + AI 互评 | `dev-build` ④ `dev-code-review`（对照 AGENTS / standards / facts） | 不能开 MR |
| 单元测试 | DEV | `dev-self-test`：`mvn test`（Domain/Application）、前端 `vitest` | 不进自测 |
| API 测试 | DEV | `dev-self-test`：RestAssured 打 `localhost`（`*ControllerTest`） | 不进自测 |
| 研发自测 · MCP 浏览器走查 | DEV | `dev-build` ③ `dev-ui-review`：原型对照 + `chrome-devtools` MCP 走查，落盘 `{planStem}-ui-review.md` | 回 ① 改 |
| QA · E2E | QA | `qa-write-cases`（`TC-xxx` 文本用例）→ `qa-run-e2e`（`e2e/tests/qa/` + 规格覆盖核对） | **合并闸门** |
| QA · 变异测试 | QA | 跑在 E2E 之后，检查用例能不能抓住缺陷；工具项目自选（Java 用 PIT / 前端用 Stryker） | 回退重跑自测 |
| QA · 人工补测 | QA | `qa-write-manual-plan`（`docs/test-cases/manual-cases/`） | 不验收 |
| QA · 冒烟 | QA | `qa-write-manual-plan`（`smoking-cases/`，发版前 5 分钟最小集） | 不上线 |

表下一句 **迁移期规则**：现有项目里 `e2e/tests/dev/` 可以留着跑，但不再新增；
新项目研发自测直接走 MCP 走查，E2E 只归 QA —— 两套 E2E 必然漂移。

### 4.2 变异测试：验证「测试有没有牙齿」

- **为什么**：AI 写的 E2E 可能只断言「页面有数字」，实现改坏了照样绿 —— 用例存在 ≠ 能证伪
- **怎么做**：往被测代码里注入小改动（改比较符、删一行校验），跑 E2E；
  用例 **必须变红**，没变红说明这条用例抓不住这个缺陷
- **失败怎么处理**：不修用例了事 —— 回 **研发自测**（`dev-self-test` / `dev-ui-review`）
  重跑，把断言补到能证伪，再回到 E2E
- **判据**：有效变异杀光（或达到项目约定阈值）才算 E2E 可信；不许登记成「已知债务」放行
- **别误用**：环境不稳、数据没隔离会造成假「没杀死」，先排除不稳定再下结论

用一个 `.callout` 呈现「变异测试失败 → 回自测」这条回路，配一行箭头文字。

### 4.3 归属判定（保留现有表）

「开发自测 vs QA 测试」两栏表照搬，加一句：**归属看谁定义、谁判定，不看谁敲的代码**。

### 4.4 编号与追溯

- `R-xxx` / `AC-xxx` → 至少一条 `TC-xxx`（QA 用例）
- 研发自测不编号，用 `DST-xxx`（Plan 的用例表）+ `{planStem}-self-test.md` 落盘

## 验证

1. `./.agents/verify.sh` 全绿（第 9 节相对链接）
2. 浏览器打开 `index.html`：TOC `4. 测试策略` 能跳转且标题不被 sticky 目录条遮住；
   4.1 九行表在窄屏不撑破页面、首列不逐字折行；4.2 callout 正常
3. 表格里每个 skill 名、文件名、命令都能在仓库里对上：
   `dev-build` / `dev-self-test` / `dev-ui-review` / `dev-code-review` /
   `qa-write-cases` / `qa-run-e2e` / `qa-write-manual-plan`、
   `*-self-test.md`、`*-ui-review.md`、`e2e/tests/dev|qa/`、`docs/test-cases/{e2e,manual,smoking}-cases/`

## 已知差异（本轮不做，记在这里）

| 差异 | 现状 | 对齐时改哪 |
|---|---|---|
| 研发自测还写着 dev E2E | `dev-self-test-template` 的「执行顺序」第 5 步与 `npm run test:dev` | 删第 5 步、改成 MCP 走查 |
| 变异测试无 skill 落点 | `qa-run-e2e` 只跑 E2E + 覆盖核对 | `qa-run-e2e` 加「变异测试」小节与失败回炉规则 |
| lint 无闸门 | example 未配 eslint / checkstyle | `AGENTS.md` 模板 §10 + CI 示例 |
