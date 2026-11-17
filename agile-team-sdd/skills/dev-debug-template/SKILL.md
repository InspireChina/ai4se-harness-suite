---
name: dev-debug-template
description: 使用 chrome-devtools-mcp 调试前端和后端问题。当浏览器显示错误、UI 异常或网络请求失败时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 开发：调试

## 启动服务栈

```bash
{{E2E_RUNNER}}
```

如需要可仅启动服务而不运行测试。

## chrome-devtools-mcp 工具

MCP 服务器（`{{MCP_CONFIG_FILE}}` 中的 `chrome-devtools`）提供：

- `navigate_page` — 导航到 URL
- `take_screenshot` — 截取页面/元素截图
- `take_snapshot` — 获取无障碍树（带 uid 的文本 DOM 快照）
- `click`、`fill`、`fill_form` — 与元素交互
- `list_console_messages`、`get_console_message` — 读取浏览器控制台
- `list_network_requests`、`get_network_request` — 检查网络请求
- `evaluate_script` — 在页面上下文中运行 JS
- `performance_start_trace` — 记录性能追踪

## 调试流程

1. 导航到问题页面
2. 检查控制台错误（`list_console_messages`）
3. 检查网络失败的请求（`list_network_requests`）
4. 获取 DOM 快照检查状态（`take_snapshot`）
5. 如果是 UI 问题，截图查看（`take_screenshot`）
6. 如果是性能问题，开始追踪（`performance_start_trace`）
