# BA 侧架构初始化：新增 ba-arch-plan + 更新泳道图

## 需求

项目准备阶段 `docs/architecture/` 现在只挂了一个 `tl-arch-plan`，业务侧四件套
（product / glossary / core-domain-model / iterations）写在那份 skill 的「与 BA 协作」一行里。
用户提出：BA 也得初始化一部分架构，是不是该有自己的 skill，同时更新角色协作图。

## 结论

新建 **`ba-arch-plan`**（BA 组）负责业务侧意图，`tl-arch-plan` 收窄到技术侧（C4 + ADR）。
guide 的矩阵与 `flow.html` 都把这一格拆成两格。

不把业务侧塞进 `tl-arch-plan` 的理由：skill 前缀就是角色，`ba-*` 与 `tl-*` 的输入、产出、
自检完全不同；合成一个会让 description 变模糊（触发不准），也会让 BA 去调一个 `tl-` 开头的 skill。

## 职责切分

| Skill | 管什么 | 不管什么 |
|---|---|---|
| `ba-arch-plan`（新） | 首次/大幅起草 `business/`：产品边界、术语基线、核心聚合 + 关键字段、迭代规划；给 TL 一份「核心聚合 → 建议容器」的输入 | 不画 C4、不写 ADR、不做 as-built |
| `tl-arch-plan`（收窄） | `tech/`：C4 上下文/容器、ADR；确认容器能承载核心聚合 | 不写 `business/` 正文（只读） |
| `ba-arch-sync-back` | 迭代后业务侧漂移对齐 | 不做首次起草 |
| `ba-write-spec` | 单 feature 追加术语、引用项目术语表 | 不重建术语基线 |

**顺序：BA 先 → TL 后 → 互审 → 进迭代前须齐。**
理由：C4 容器怎么切，依据是核心聚合；先画图再定业务边界必然重画。可并行的只是
「TL 画上下文图」与「BA 细化 glossary」，容器图必须等核心聚合定下来。

## 新 skill 规格

```markdown
---
name: ba-arch-plan-template        # 安装后 ba-arch-plan
description: 起草项目级业务架构意图（产品边界、术语基线、核心领域模型、迭代规划）。
             当项目准备阶段或新增业务域、需要先把 docs/architecture/business/ 立起来时使用。
---
```

正文要点：

- **前置**：`{{AGENTS_FILE}}` 的业务目标已填；读过 `{{STANDARDS_DIR}}/architecture.md`；`tech/` 可能还不存在
- **落点**：`{{ARCHITECTURE_DIR}}/business/{product,glossary,core-domain-model,iterations}.md`，
  以及 `{{ARCHITECTURE_DIR}}/README.md` 的业务索引
- **四件套各写什么**：
  - `product.md`：一句话定位、角色、边界内/外（明确写「不做什么」）
  - `glossary.md`：中英对照，唯一权威；只收项目级术语，不收字段名
  - `core-domain-model.md`：只写核心聚合 + 关键字段；未实现的概念标「未实现」
  - `iterations.md`：迭代目标与里程碑，指向真实迭代目录
- **硬性约束**：不写 C4/ADR；不写 as-built（那是 `{{DOMAIN_MODEL_DOC}}`）；
  术语表只有一份；每条业务规则标来源（干系人 / 文档 / 会议）
- **交接给 TL**：在正文末尾给「核心聚合 → 建议容器」一列，供 `tl-arch-plan` 画 C4 时用
- **与其它 skill**：`ba-arch-sync-back`（漂移对齐）、`ba-write-spec`（单 feature 追加术语）、
  `tl-arch-plan`（技术侧接手）

## 改动

| 文件 | 改什么 |
|---|---|
| `agile-team-sdd/skills/ba-arch-plan-template/SKILL.md`（新） | skill 正文，带 `TEMPLATE-ONLY` 块 |
| `agile-team-sdd/catalog.json` | `ba` 组首位登记（它发生在其它 ba skill 之前） |
| `agile-team-sdd/skills/tl-arch-plan-template/SKILL.md` | description 改「技术侧」；输出表 `business/` 行改成「前置：BA 已产出，本 skill 只读」；自检加「容器能映射核心聚合」；与其它 skill 表加 `ba-arch-plan` |
| `agile-team-sdd/SKILL.md` | skill 表加一行；数据流「项目准备」改为 `ba-arch-plan` → `tl-arch-plan` |
| `agile-team-sdd/README.md` | 目录树与角色表 |
| `harness-installer/templates/docs/architecture/README.md` | `business/` 主责改 `BA（ba-arch-plan）+ TL 审`；维护表加一行 |
| `harness-installer/templates/docs/architecture/business/*.md` | 顶部「维护：」标注加 `ba-arch-plan` |
| `harness-installer/templates/docs/standards/architecture.md` | TODO 回填那句改成两支 skill |
| `example-project/docs/architecture/**` | 与模板同源同步（参考实现要和被管理的样子一致） |
| `team-workflow-guide/index.html` | 矩阵「项目准备」3 行 → 4 行（BA 业务架构 / TL 技术架构）；1.1 表拆两行；1.2 加两步；1.3 出口条件措辞；角色手册 BA 行 |
| `team-workflow-guide/flow.html` | 新增 `ba-arch`（BA 泳道）节点，阶段边界 `3/7/13` → `4/8/14`，连线 `install → ba-arch → arch → direction` |
| `README.md`（根） | 角色表、数据流、高阶设计行、快速开始 |
| `AGENTS.md` | §8 数据流、§13 同步要求 |
| `VERSION` / `CHANGELOG.md` | `0.3.0` → `0.4.0`，新增一节 |
| `example-project/.agents/skills/` | `PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force` |

不新增占位符（复用 `ARCHITECTURE_DIR` / `GLOSSARY_FILE` / `ARCH_DOMAIN_MODEL_DOC` /
`DOMAIN_MODEL_DOC` / `STANDARDS_DIR` / `AGENTS_FILE`），`placeholders.md` 不动。

## 不做的

- 不把 `business/` 与 `tech/` 拆成两道准入闸门（出口条件仍是一条「架构意图可读」）
- 不改 `ba-arch-sync-back` 的职责
- 不给 skill 加子命令或参数
- 不动 `example-project` 的 tech 内容与已有业务文档正文（只改顶部「维护：」标注）

## 验证

1. `catalog.json` 可解析、新 skill 已登记
2. `./.agents/verify.sh` 全绿（第 6 节强制 catalog ↔ 模板 ↔ 已安装 **正文一致**，
   所以 example-project 必须重装；第 8 节查残留占位符 / 绝对路径）
3. `git status example-project` 只多出 `.agents/skills/ba-arch-plan/`
4. `flow.html` 用浏览器确认新列不压线、阶段带边界对齐、无控制台报错
5. Markdown 相对链接（第 9 节）
