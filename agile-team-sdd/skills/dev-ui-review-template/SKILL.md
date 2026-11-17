---
name: dev-ui-review-template
description: 启动原型与实现环境，按 Plan 界面对照基线做字段/控件与截图对比并落盘；通常由 dev-build 编排，未通过则修到通过。当有前端改动需要实机对照时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# Dev：界面评审（原型对照）

通常由 **`dev-build` 编排调用**（有前端改动时）；也可单独触发。

必须 **实机** 对照，不能只读代码。工具：chrome-devtools-mcp（`{{MCP_CONFIG_FILE}}`）。

## 前置

1. 读 plan 的 **界面对照基线**（字段/控件、原型路由、实现路由）
2. 启动环境：
   - **原型**（若存在）：`{{FEATURES_DIR}}/<迭代>/prototypes/` → `npm run dev`（样例常为 `http://127.0.0.1:5174`）
   - **实现**：`{{E2E_RUNNER}}` 或等价 → 前端 `http://localhost:{{FRONTEND_PORT}}`、后端 `http://localhost:{{BACKEND_PORT}}`
3. 服务没起来先修服务，不要在报错页上评审

**无原型**：在记录中写明「无原型可对」，改为对照 `spec` 字段表 + 实现页截图；**不得**因无原型而直接标通过。

## 对照流程（按基线页面，别跳步）

对基线中的每一页：

```
1. 打开原型对应路由     → navigate + take_screenshot  → 存 artifacts
2. 打开实现对应路由     → navigate + take_snapshot + take_screenshot
3. 字段/控件逐项对比    → 填差异表（缺字段、错控件、文案、校验、必填）
4. 结构 / 控制台 / 网络 → take_snapshot、list_console_messages、list_network_requests
5. 关键态（若基线要求） → 加载 / 空 / 错误
6. 必要视口             → 375 / 768 / 1280（至少桌面 + 移动一档）
```

**先字段控件对齐，再视觉与交互。** 对照不过，视觉好看也算失败。

## 检查清单（在对照之外仍要做）

### 字段与控件（相对基线 / spec）

- [ ] 基线列出的字段均出现，类型/控件一致（输入框、选择器、开关等）
- [ ] 必填、校验提示与 spec/基线一致
- [ ] 主按钮/次按钮文案与位置与原型意图一致（允许设计系统差异，但不可缺操作）

### 结构 / 视觉 / 状态 / 交互 / 响应式 / 干净度

沿用常见项：一页一个 h1、label 关联、加载/空/错三态、点击反馈、无控制台 error、无意外 4xx/5xx、关键视口无横向滚动。细节按页面需要取舍，但 **Blocker/Major 必须有证据**。

## 产物

| 产物 | 路径 |
|---|---|
| 评审记录 | 与 plan 同目录 `{planStem}-ui-review.md` |
| 截图 | `{feature目录}/ui-review-artifacts/`（记录内写相对路径；**不强制**把大图提交 git） |

### 记录模板

```markdown
# UI 评审：<plan 文件名>

> 关联 plan：./<plan-file>.md
> 状态：通过 | 失败
> 更新：YYYY-MM-DD HH:mm
> 原型：http://127.0.0.1:5174 （或：无原型）
> 实现：http://localhost:{{FRONTEND_PORT}}

## 页面对照

### <路由名>

| 字段/控件 | 原型 | 实现 | 结论 |
|---|---|---|---|
| 手机号 | 输入框 | 输入框 | 一致 |
| … | | | 差异：… |

截图：
- 原型：./ui-review-artifacts/proto-xxx.png
- 实现：./ui-review-artifacts/app-xxx.png

## 问题

### Blocker
- …

### Major
- …

### Minor
- …

## 已确认正常

- …
```

问题格式示例：

```
[Major] 登录页缺「同意协议」勾选
复现：实现 /user/login vs 原型 /user/login
期望：与原型一致有协议勾选
实际：无该控件
证据：./ui-review-artifacts/app-login.png
```

## 通过标准

- `{planStem}-ui-review.md` 已写且状态为 **通过**
- **Blocker / Major 清零**（Minor 可记遗留）
- 基线中的页面均有对照行与截图路径（无原型时有 spec 对照说明）

`dev-build` **以该文件为准**：未通过 → 修前端（必要时回 `dev-self-test`）→ 重跑本 skill → 更新记录，直到通过。
