---
name: work-in-example
description: 在 example-project 上下文中开发或改约定；结束时若识别到需要改 harness 则询问是否更新。当用户说"在 example 里做"、"只改样例"、"example 上下文"、work-in-example、以案例项目为工作区时使用。
---

# 工作在 example 上下文

默认工作区是 **`example-project/`**：改代码、docs、AGENTS、已安装 skills 的行为验证，都以样例项目为准。

本 skill **不**默认回写 harness。只有当你识别到「样例里的约定已经偏离套件模板 / 安装器」时，在收尾阶段 **询问** 是否更新 harness。

## 什么时候用

- 用户要在样例里实现功能、改文档、调 overnight-runner 配置、验证流程
- 明确「先只动 example，别管 harness」
- 不确定会不会波及 harness，需要结束时再决策

**不要用本 skill**：

- 一开始就确定要改模板/占位符/安装器 → `modify-harness`
- 一开始就确定「example 试约定 → 强制回写套件」→ `modify-example`

## 工作边界

| 可以改 | 默认不要改（除非用户确认更新 harness） |
|---|---|
| `example-project/**` | `agile-team-sdd/`、`harness-installer/`、`tool-chain-installer/`、`overnight-runner/`（套件源） |
| 样例内 `.agents/skills/`（仅作本地验证时可改，须知重装会覆盖） | 根 `AGENTS.md` 里套件级约定（可提建议，不擅自改） |

本仓库自身的 Plan 仍写在 `.agents/plan/`（若改动触及 harness 仓库规范）。  
example 业务 Plan 写在 `example-project/docs/features/.../plan.md` 或 `_chores/`。

## 怎么做

### 1. 锚定上下文

- 路径、命令、自测都以 `example-project/` 为根（如 `apps/backend`、`docs/features/`、`.overnight-runner/`）
- 读 `example-project/AGENTS.md` 与相关 docs，按其规范执行
- 需要安装态 skill 时，以 `example-project/.agents/skills/` 为准

### 2. 执行用户任务

按 example 的开发流程做（Plan 闸门、自测、文档同步等，见 `example-project/AGENTS.md` §14）。

过程中若发现「套件模板明显落后于样例约定」，**先记在清单里，不要中途擅自改 harness**，除非用户当场要求。

### 3. 收尾：识别是否需要更新 harness

任务完成后，用下面信号判断（命中任一条即视为「可能需要更新 harness」）：

| 信号 | 例子 |
|---|---|
| 目录/命名约定变了 | feature 文件夹编码规则、`spec.md`/`plan.md` 布局、`apps/`、`.overnight-runner/` |
| 文档骨架变了 | `docs/` 下新目录、facts/business、`_chores` 语义 |
| 流程/检查清单变了 | `example-project/AGENTS.md` 与模板 `AGENTS.md.template` 明显不一致 |
| 安装默认值会错 | 新默认路径、端口、测试命令，现有 `placeholders.md` / `install.sh` 对不上 |
| skill 行为以样例为准改过 | 只改了 `.agents/skills/` 已安装副本，模板仍是旧的 |

**未命中**：正常收尾（验证、文档同步、提交说明），不必提 harness。

**命中**：在最终回复里 **明确询问**（不要默认执行），例如：

> 本轮在 example 中出现了与 harness 不一致的约定：\<一句话列出信号\>。  
> 是否需要现在更新 harness（按 `modify-example`：回写模板/安装器并重装 example skills）？  
> 回复「是 / 否」即可。

- 用户说 **是** → 切换遵循 `modify-example`（写/补 Plan → 等人确认若尚未覆盖 harness 回写 → 回写 → `PATH_MODE=relative` 重装 → `./.agents/verify.sh`）
- 用户说 **否** → 在收尾注明「已知漂移，暂不回写」，可把差异记进 `.agents/plan/` 或回复中的 follow-up 列表
- 用户说 **稍后 / 另开一轮** → 记下，不在本轮改 harness

## 硬性约束

1. 未经询问确认，**禁止**修改 harness 源模块与根套件文档（维护型 skill 目录除外的只读参考可以读）。
2. 不要把「改了 example 已安装 skill」当成「harness 已更新」。
3. 询问时只给一次清晰二选一，附上为何认为需要更新；不要偷偷 `--force` 重装。
4. 若用户同意更新 harness，遵守根 `AGENTS.md` 的 Plan 闸门与模块边界。

## 反模式

- 在 example 里改完目录约定，静默改掉 `harness-installer` 模板
- 把套件 skill 模板和 example 已安装副本改成两套长期分叉且不告知
- 把任何 docs 措辞差异都升级成「必须更新 harness」（仅约定/结构/安装默认值类信号才问）

## 相关

- 同意回写后：`.agents/skills/modify-example/SKILL.md`
- 直接改套件：`.agents/skills/modify-harness/SKILL.md`
- 验证：`./.agents/verify.sh`
