---
name: modify-example
description: 先改 example-project 样例，再把约定回写刷新 harness 模板与安装器。当用户说"改样例"、"改 example-project"、"样例目录结构调整"、"以 example 为准刷新 harness"、modify-example 时使用。
---

# 改样例 → 刷新 harness

**方向**：`example-project/` 是事实源 → 约定成熟后再回写 harness 交付物。

适用于：目录布局、docs 约定、AGENTS 规范、overnight-runner 安装形态等，**先在样例里跑通**，再推广到安装器 / skill 模板。

## 什么时候用

- 要调整案例项目结构或文档体系，并希望新项目安装后长成一样
- 用户明确说「先改 example，再刷 harness」
- 不确定最终约定时，用 example 当沙盒试错

**不要用本 skill**：只改 harness 模板、占位符、安装脚本（用 `modify-harness`）。

## 硬性约束

1. **Plan 闸门**：在 `.agents/plan/YYYYMMDD-{slug}.md` 写方案，**等人确认**后再动手。
2. **模块边界**：四个安装器/套件模块互不 import；只通过文件系统与清单通信。
3. **不写死绝对路径**进会分发的产物；模板用 `{{PLACEHOLDER}}`，并登记 `agile-team-sdd/placeholders.md`。
4. **不碰** example 业务代码之外的无关重构；安装器默认不覆盖，刷新用显式 `--force`。
5. 改完跑 `./.agents/verify.sh`（动 overnight-runner 行为则全量，含冒烟）。

## 怎么做

### 1. 确认范围

分清本轮只动 example 的哪一块，以及回写会落到哪些 harness 模块：

| example 改动 | 通常要回写 |
|---|---|
| `containers/`、根布局、脚本路径 | `harness-installer` 探测默认值、`agile-team-sdd` 占位符默认值、文档树 |
| `docs/features` 约定（编码文件夹、spec/plan、`_chores`） | `harness-installer/templates/docs/`、`ba-write-spec` / `dev-plan`、catalog、`placeholders.md` |
| `docs/facts` 等事实目录 | 模板骨架、相关 skill、`team-workflow-guide` |
| `.overnight-runner/` 布局 | `overnight-runner/scripts/install.sh` + README/SKILL |
| `AGENTS.md` 流程/检查清单 | `harness-installer/templates/AGENTS.md.template` |

### 2. Plan → 等人确认

写清：目标结构、迁移映射、旧路径怎么处理、Phase 划分（example 先 / harness 后）、验证命令。

### 3. 只改 `example-project/`

- 搬家优先 `git mv` 保历史
- 同步活文档：`example-project/AGENTS.md`、`docs/README.md`、索引 README、队列里的 plan 路径
- 历史已定稿 plan：**可不改语义**；为保链接可批量替换路径字符串
- 此阶段 **不要** 先改模板「假装同步」——以 example 落地结果为准

### 4. 回写 harness（刷新）

按映射改对应模块，常见清单：

- [ ] `agile-team-sdd/placeholders.md` + `install.sh` 默认值 / PAIRS
- [ ] `agile-team-sdd/skills/*-template/SKILL.md` + `catalog.json` + `SKILL.md` / `README.md` 表格
- [ ] `harness-installer/templates/**` + `scripts/init-harness.sh`
- [ ] `overnight-runner/scripts/install.sh` + 文档（若涉及）
- [ ] 根 `AGENTS.md` / `README.md` / `team-workflow-guide/index.html`（若流程或路径变了）

### 5. 把刷新结果装回 example

```bash
PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force
# 若动了 overnight-runner 安装布局：
./overnight-runner/scripts/install.sh example-project --force
```

确认 `example-project/.agents/skills/` 无残留 `{{...}}`、路径与新约定一致。

### 6. 验证与自检

```bash
./.agents/verify.sh
```

- [ ] example 新结构可导航，无大面积死链
- [ ] 占位符已登记；模板无未替换 `{{...}}`
- [ ] catalog ↔ 模板 ↔ 已安装三方一致
- [ ] 文档同步检查（§13）已做
- [ ] 提交说明含：改了什么 / 为什么 / 怎么验证 / 文档同步

## 反模式

- 只改 example 不回写 harness，导致「样例是一套、安装又是一套」
- 未确认 Plan 就大面积搬家
- 用绝对路径写进 skill 模板
- 回写时漏掉 `placeholders.md` / `catalog.json` / 工作流指南中的一处

## 相关

- 反向流程：`.agents/skills/modify-harness/SKILL.md`
- 规范：根目录 `AGENTS.md`
- 验证：`./.agents/verify.sh`
