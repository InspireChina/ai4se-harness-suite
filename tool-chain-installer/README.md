# tool-chain-installer

把 MCP 工具链写进项目配置，**不依赖开发机的全局状态**。

```
tool-chain-installer/
├── SKILL.md
├── scripts/install-tools.mjs
└── catalog/mcp-catalog.json      # 工具清单（可自行扩展）
```

## 用法

```bash
# 看清单
node tool-chain-installer/scripts/install-tools.mjs --list

# 装浏览器 + 上下文工具
node tool-chain-installer/scripts/install-tools.mjs ../my-project --group browser --group context

# 按名称
node tool-chain-installer/scripts/install-tools.mjs ../my-project --tools chrome-devtools,playwright

# 全部 + 预览
node tool-chain-installer/scripts/install-tools.mjs ../my-project --all --dry-run
```

## 写入位置

| 文件 | 键名 | 适用 |
|---|---|---|
| `.mcp.json` | `mcpServers` | Claude Code / 通用 MCP 客户端 |
| `opencode.jsonc` | `mcp` | opencode 原生格式 |

两个文件默认都写（`--format both`）。已有配置会被 **合并**，其他字段保留。

## 现有工具

| 分组 | 工具 | 用途 |
|---|---|---|
| browser | `chrome-devtools` | 调试：导航 / 截图 / 控制台 / 网络 / 性能 |
| browser | `playwright` | 浏览器自动化 |
| context | `context7` | 拉最新官方文档 |
| context | `sequential-thinking` | 结构化推理 |
| data | `filesystem` | 限定目录文件读写 |
| data | `git` | 仓库历史 / 分支 / diff |
| observability | `sentry` | 线上错误排查（需 `SENTRY_TOKEN`） |

## 扩展

编辑 `catalog/mcp-catalog.json` 加一项即可，脚本自动读取。
