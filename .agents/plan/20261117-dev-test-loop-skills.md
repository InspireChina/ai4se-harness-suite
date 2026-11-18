# Plan：dev-plan / self-test / ui-review 与 build 回环强化

> 日期：2026-11-17  
> 状态：**已完成**  
> 方向：modify-harness（改 skill 模板 → 重装 example）

## 目标

1. **`dev-plan`**：必须编写可执行的 **开发自测用例设计**（落到 plan 正文 + 可选索引）
2. **`dev-ui-review`**：启动 **原型**，按字段/控件与实现页对比，**截图对照**，写入测试结果；未通过则 `dev-build` 修到通过
3. **`dev-self-test`**：按 plan 里的自测用例执行并 **落盘记录**；未通过则 `dev-build` 修到通过  
4. **自测必须起真实本地环境**（后端 + DB + 前端按需），对着跑起来的服务测；禁止只靠「未启动服务的纯编译 / 空跑」冒充自测通过

## 落点约定

| 产物 | 路径 | 谁写 |
|---|---|---|
| 自测用例设计 | feature `plan.md` 既有 §8～10（强化为「必须可执行、可勾选」）+ 实施后索引 `{{DEV_SELF_CASES_DIR}}/` | `dev-plan` |
| 自测执行记录 | 同目录 `{planStem}-self-test.md` | `dev-self-test`（build LOOP） |
| UI 对照记录 | 同目录 `{planStem}-ui-review.md`（含截图相对路径） | `dev-ui-review`（build LOOP） |
| 截图 | `{feature}/ui-review-artifacts/`（git 可忽略大图或仅保留关键帧；skill 要求路径写入记录） | `dev-ui-review` |

原型默认：`{{FEATURES_DIR}}/<迭代>/prototypes/`（`npm run dev`，样例端口 5174）。实现前端仍为 `{{FRONTEND_PORT}}`。无原型时：记录「无原型可对」并改为仅对照 `spec` 字段表 + 截图实现页，不得假装通过。

## Skill 变更摘要

### `dev-plan`

- 硬性：§8 单元 / §9 API 集成 / §10 E2E（或前端交互）必须写出 **场景表**（编号 `DST-xxx`，Given-When-Then 或等价 checklist），不能只写标题
- 有 UI：增加「界面对照基线」——列出原型路由 / 关键字段与控件清单，供 `dev-ui-review` 使用
- 同步 `{{PLAN_TEMPLATE}}` 增加 DST 表头与「界面对照基线」小节

### `dev-self-test`

- 执行前读 plan 的 DST 清单与 `*-progress.md`
- **先起真实本地环境**，再跑 DST：
  1. 按项目惯例启动依赖（如 MySQL / 迁移）与后端（`{{BACKEND_PORT}}`）
  2. 有前端 DST / E2E 时启动前端（`{{FRONTEND_PORT}}`）；可用 `{{E2E_RUNNER}}` 一键拉齐
  3. 健康检查通过（如 `/actuator/health` 或项目约定）后再跑用例
  4. 环境起不来 → 记失败并修环境，**不得跳过**改标通过
- 分层仍由快到慢：单测可先跑；**集成 / API / E2E 自测必须打到已启动的本地服务**（RestAssured、Playwright 等指向 `localhost`）
- 按 DST 执行；结果写入 `{planStem}-self-test.md`（含：环境是否就绪、端口、命令、通过/失败、关联 DST）
- 未覆盖的 DST 算失败项，不得标 build 自测通过
- `dev-build`：自测记录未全绿 → 修实现/环境 → 重跑 → 更新记录，直到通过

### `dev-ui-review`

- 准备：启动原型（若存在）+ 实现前后端（`{{E2E_RUNNER}}` 或等价）
- 流程：按 plan「界面对照基线」逐页 —— 原型截图 / 实现截图 / 字段与控件差异表
- 结果写入 `{planStem}-ui-review.md`；Blocker/Major 未清零不得通过
- `dev-build`：UI 记录未通过 → 修前端（必要时回自测）→ 重跑 ui-review，直到通过

### `dev-build`

- progress LOOP 阶段增加显式产物勾选：`*-self-test.md`、`*-ui-review.md`
- 闭环写清：以记录文件为准，不是口头「应该过了」

## 文档同步

- `agile-team-sdd` catalog / SKILL.md / README 表格一句话
- `team-workflow-guide` 迭代中相关表述（若有自测/UI 句）
- 根 `AGENTS.md` 数据流一句（可选）
- example：重装 skills；**不强制**改已定稿 ACC plan（历史）；模板与新 plan 生效

## 非目标

- 不改 overnight-runner 行为
- 不把 DST 混入 QA 的 `TC-xxx` 编号空间
- 不强制把截图二进制提交进 git（skill 写清：至少本地路径 + 关键差异说明；团队可选提交）

## 验证

- `PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force`
- `./.agents/verify.sh`

---

## 已吸收反馈

- 自测必须启动真实本地环境再测（集成/API/E2E 打 localhost）

请确认或指出要改的点（例如：记录文件命名、截图是否入库、无原型时的降级策略、环境启动脚本是否强制 `{{E2E_RUNNER}}`）。确认后按 modify-harness 执行。
