# 套件版本号 + 安装清单

## 需求

用户希望「装的是哪一版、几个模块是否一致」能被机器判断，而不是靠人记。
提问原话：*每个模块是不是都搞个版本比较好？这样才能保持一致？*

## 结论：两层，不是每模块一个号

| 层 | 放哪 | 管什么 | 谁跟随 |
|---|---|---|---|
| 套件版本 | 仓库根 `VERSION` + `CHANGELOG.md` | 一次安装的整体快照，回答「这版能不能装到 poc」 | `agile-team-sdd`、`harness-installer`、`tool-chain-installer` 跟随 |
| 模块版本 | 模块自己的代码（已有） | 模块的兼容面：引擎 ↔ 预设格式、runner 运行时 | `agents-workflow-engine` 0.2.0、`overnight-runner` 0.1.0 |

不给每个模块单独编号的理由：四个安装器与套件型模块都从同一个 checkout 安装、
同一次运行装完，没有独立分发与升级通道；再加 6 个号只会多 6 处 bump 和一张兼容矩阵，
反而更容易不一致。模块版本只在「模块被单独复制走、并且有自己的兼容面」时才保留。

## 连接两层：安装清单

每个安装器往目标项目写 **自己那一份**：

```
<目标项目>/.agents/harness/<模块>.json
```

```json
{
  "module": "agile-team-sdd",
  "version": "0.3.0",
  "suite": "0.3.0",
  "installedAt": "2026-11-20T02:11:43Z"
}
```

不采用「所有模块合写一个 `.agents/harness.json`」：那样每个安装器都要读改写同一个文件，
要合并、要防并发，还得维护一份共享的模块清单（违反 §4 清单唯一事实源）。
一个模块一个文件 = 单写者、原子 rename、不需要共享列表，读的时候 `cat .agents/harness/*.json`。

规则：

- `version`：模块自己的版本；没有自带版本号的模块取套件版本
- `suite`：写入时仓库根的 `VERSION`
- 已存在且版本没变 → 不改文件（`installedAt` 保持首次安装时间），保证幂等
- 已存在且版本变了 → 只有 `--force` 才更新；否则 stderr 提示「文件是跳过模式，清单未改」，
  避免出现「文件没升级、清单却升级」
- `--dry-run` 只打印计划

## 改动

| 文件 | 改什么 |
|---|---|
| `VERSION`（新） | `0.3.0` |
| `CHANGELOG.md`（新） | 套件级变更记录，第一节必须与 `VERSION` 相等 |
| `agile-team-sdd/install.sh` | 写 `agile-team-sdd.json` |
| `harness-installer/scripts/init-harness.sh` | 写 `harness-installer.json` |
| `tool-chain-installer/scripts/install-tools.mjs` | 写 `tool-chain-installer.json` |
| `overnight-runner/scripts/install.sh` | 写 `overnight-runner.json`（version 取 `__version__`） |
| `agents-workflow-engine/scripts/install.sh` | 写 `agents-workflow-engine.json`（version 取 `version.py`） |
| `.agents/verify.sh` | 第 13 节：`VERSION` ↔ `CHANGELOG.md`；`example-project/.agents/harness/*.json` ↔ 源码版本 |
| `AGENTS.md` | §6 加「写安装清单」、§10 加两项检查、§12 加版本 bump、§13 树补 `VERSION` / `CHANGELOG.md` |
| `README.md` | 新增「版本与同步」一节 |

## 不做的

- 不引入 `jq` / 第三方库：清单用 `printf` 生成，读用 `sed`
- 不让安装器互相 import 或共享一份 helper 脚本：Bash 侧各写一份 ~25 行，
  符合 §3「安装器之间不互相 import」
- 不给 skill 正文、占位符字典单独编号：它们跟随套件版本
- 不改模块自带的 `version.py` / `__version__` 的取值体系

## 验证

1. `bash -n` / `node --check` 五个安装器
2. 每个安装器对临时目录跑 `--dry-run`（不落盘）与真跑（落盘、内容正确）
3. 幂等：同一版本连跑两次，第二次清单文件 mtime 不变
4. 版本变化 + 不带 `--force`：stderr 提示且清单保持旧值
5. 对 `example-project` 重跑四个安装器（引擎不装进 example），产出清单
6. `./.agents/verify.sh` 全绿