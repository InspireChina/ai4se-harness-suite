---
name: dev-ui-review-template
description: 用 chrome-devtools-mcp 做界面与交互评审。当前端界面需要实机检查视觉、响应式、报错时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# Dev：界面评审

界面评审 **必须实机看**，不能只读代码。工具：chrome-devtools-mcp（配置在 `{{MCP_CONFIG_FILE}}`）。

## 准备

```bash
{{E2E_RUNNER}}
```

- 前端：`http://localhost:{{FRONTEND_PORT}}`
- 后端：`http://localhost:{{BACKEND_PORT}}`

服务没起来就先修服务，不要在报错页面上做评审。

## 评审流程（按顺序，别跳步）

```
1. 导航到页面        → navigate_page
2. 看无障碍树        → take_snapshot        （先确认结构对不对）
3. 截图看视觉        → take_screenshot
4. 看控制台          → list_console_messages
5. 看网络请求        → list_network_requests
6. 换视口再看        → resize / 多视口各截一次
7. 交互走一遍        → click / fill / fill_form
```

**先结构、再视觉、最后交互。** 结构错了，视觉截图再好看也没意义。

## 检查清单

### 结构与语义

- [ ] 标题层级正确（一个 h1）
- [ ] 语义标签用对了（`nav` / `main` / `button` / `label`）
- [ ] 表单控件有关联 `label`
- [ ] 表格有 `th`，行有语义
- [ ] 图片有 `alt`

### 视觉

- [ ] 颜色、间距来自全局 CSS 变量，没有硬编码
- [ ] 长文本不溢出、不撑破布局
- [ ] 中英文混排不出现奇怪的字距
- [ ] 深浅色对比度足够

### 状态覆盖（最容易漏）

每个列表/表单都要有这三种状态：

| 状态 | 表现 |
|---|---|
| 加载中 | 有骨架或 spinner，不是空白 |
| 空数据 | 有引导文案 + 下一步操作 |
| 出错 | 有错误提示 + 可重试 |

- [ ] 三种状态都实机看过

### 交互

- [ ] 按钮点击有反馈（loading / 禁用 / 提交中）
- [ ] 重复点击不会重复提交
- [ ] 401 自动跳登录
- [ ] 403 有明确提示，不是空白页
- [ ] 表单校验错误定位到字段
- [ ] 键盘可达（Tab 顺序、Esc 关闭弹层）

### 响应式

至少看三档：

| 视口 | 宽度 | 关注 |
|---|---|---|
| 移动 | 375px | 单列、导航折叠、按钮可点区域 |
| 平板 | 768px | 两列 / 侧栏收起 |
| 桌面 | 1280px | 布局与最大宽度 |

- [ ] 三档都没有横向滚动条
- [ ] 移动端没有 hover-only 的操作（手点不到）

### 干净度

- [ ] 控制台无 error / warning（`list_console_messages`）
- [ ] 网络请求无意外 4xx/5xx（`list_network_requests`）
- [ ] 没有残留的 `console.log`
- [ ] 没有 404 的静态资源

## 证据

每条问题都要有 **可复现的证据**：

| 级别 | 要求 |
|---|---|
| Blocker | 截图 + 复现步骤 + 控制台/网络报错原文 |
| Major | 截图 + 复现步骤 |
| Minor | 截图 |

问题格式：

```
[Major] 预约列表移动端横向溢出
复现：视口 375px → 访问 /user/appointments
期望：表格转为卡片布局，页面无横向滚动
实际：表格宽度固定 800px，页面出现横向滚动条
证据：<截图路径>
```

## 输出

```
界面评审：<结论>
- 视口：375 / 768 / 1280
- 页面：/xxx、/yyy

Blocker：
- ...

Major：
- ...

已确认正常：
- 三种状态、键盘可达、控制台干净、网络无 4xx/5xx
```
