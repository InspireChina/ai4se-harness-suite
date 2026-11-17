---
name: tool-chain-installer
description: 安装 MCP 工具链（chrome-devtools / playwright / context7 / sequential-thinking / filesystem / git / sentry 等）到指定项目。当用户说"装 MCP"、"安装工具链"、"配置 chrome-devtools"、"把 playwright 装上"、"tool chain 安装"时使用。
---

# 工具链安装器

把 MCP 工具链写进项目配置，**不依赖开发机的全局状态** —— 换一台机器 clone 下来就能跑。

## 可用工具

| 分组 | 工具 | 用途 | 谁用 |
|---|---|---|---|
| `browser` | `chrome-devtools` | 页面导航、截图、无障碍树、控制台、网络、性能追踪 | `dev-debug` |
| `browser` | `playwright` | 跨浏览器自动化、截图、表单填写 | `dev-debug`、QA |
| `context` | `context7` | 拉取框架/库的最新官方文档 | `dev-build` |
| `context` | `sequential-thinking` | 结构化推理，拆解复杂任务 | `dev-plan` |
| `data` | `filesystem` | 限定目录范围内的文件读写 | 通用 |
| `data` | `git` | 查询仓库历史、分支、diff | 通用 |
| `observability` | `sentry` | 线上错误排查（需 `SENTRY_TOKEN`） | `dev-debug` |

完整清单以 [`catalog/mcp-catalog.json`](catalog/mcp-catalog.json) 为准，脚本会读取它。

## 执行

```bash
# 查看全部可用工具
node tool-chain-installer/scripts/install-tools.mjs --list

# 按分组安装
node tool-chain-installer/scripts/install-tools.mjs <目标项目目录> --group browser --group context

# 按名称安装
node tool-chain-installer/scripts/install-tools.mjs <目标项目目录> --tools chrome-devtools,playwright

# 全部安装
node tool-chain-installer/scripts/install-tools.mjs <目标项目目录> --all

# 先预览
node tool-chain-installer/scripts/install-tools.mjs <目标项目目录> --all --dry-run
```

| 参数 | 说明 |
|---|---|
| `--tools <a,b>` | 按名称安装 |
| `--group <name>` | 按分组安装，可重复 |
| `--all` | 安装全部 |
| `--dry-run` | 只打印将要发生的改动 |
| `--format <fmt>` | `both`(默认) \| `mcp-json` \| `opencode` |

## 写入哪些文件

| 文件 | 写入位置 | 用途 |
|---|---|---|
| `.mcp.json` | `mcpServers.<name>.{command,args,env}` | Claude Code / 通用 MCP 客户端 |
| `opencode.jsonc` | `mcp.<name>.{type,command,enabled,environment}` | opencode 原生格式 |

脚本会 **合并** 进已有配置，不会覆盖 `skills` 等其他字段；同名工具以本次配置为准。

## 密钥处理

需要密钥的工具（如 `sentry`）在配置里写占位引用，**不要把真值写进仓库**：

```json
{ "env": { "SENTRY_TOKEN": "{env:SENTRY_TOKEN}" } }
```

开发者自行 `export SENTRY_TOKEN=xxx`。opencode 配置里用 `{env:VAR}`，MCP 的 `env` 字段里同样用 `{env:VAR}`。

## 加一个新工具

编辑 `catalog/mcp-catalog.json`，在对应分组里加一项：

```json
{
  "name": "my-tool",
  "description": "一句话说明",
  "package": "my-mcp@1.2.3",
  "command": "npx",
  "args": ["-y", "my-mcp@1.2.3"],
  "env": {},
  "usedBy": ["dev-build"]
}
```

`package` 只是给人看的说明，真正生效的是 `command` + `args`。

## 注意

- MCP 配置在 opencode **启动时加载，不热更新** —— 装完必须重启 opencode。
- `npx -y <pkg>@latest` 每次启动都会检查 registry，离线环境会失败；内网请改用固定版本 + 本地安装。
- 装完在项目里记一笔：`docs/standards/toolchain.md`，方便交接。

## 相关

- `agile-team-sdd/` — `dev-debug` 依赖本目录装的 `chrome-devtools`
- `harness-installer/` — 装 MCP 之前应先铺好 `AGENTS.md` 与 `docs/`
