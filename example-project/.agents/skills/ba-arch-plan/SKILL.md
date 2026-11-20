---
name: ba-arch-plan
description: 起草项目级业务架构意图（产品边界、术语基线、核心领域模型、迭代规划）。当项目准备阶段或新增业务域、需要先把 docs/architecture/business/ 立起来时使用。
---

# BA：项目级业务架构意图（Architecture Plan · business）

在 **项目准备** 或新增业务域时起草 `docs/architecture/business/`：
产品边界、统一语言、核心聚合、迭代规划。技术侧（C4、ADR）由 `tl-arch-plan` 接着做。

## 前置

- `AGENTS.md` 里的业务目标与角色已填（至少不是 TODO）
- 已读 `docs/standards/architecture.md`（写什么、不写什么）
- 有干系人输入：访谈记录、现有系统边界、竞品或政策约束
- `tech/` 可能还不存在 —— 本 skill 不依赖它

## 输出位置

| 路径 | 内容 |
|---|---|
| `docs/architecture/business/product.md` | 一句话定位、用户/端、**本期不做** |
| `docs/architecture/business/glossary.md` | 项目级中英对照术语，唯一权威 |
| `docs/architecture/business/core-domain-model.md` | 核心聚合 + 关键字段（意图侧） |
| `docs/architecture/business/iterations.md` | 里程碑与迭代索引 |
| `docs/architecture/README.md` | 确认业务侧四个链接可点 |

## 怎么做

1. **先定边界**：写 `product.md` 的「一句话」和「本期不做」。边界外的东西后面会被反复塞进来，这一节是第一道闸。
2. **再定语言**：从角色、对象、状态、动作里提炼术语写进 `docs/architecture/business/glossary.md`。只收项目级概念，字段名 / 类名不收。
3. **再定聚合**：只挑核心聚合（3~7 个），每个写职责 + 关键字段。尚未实现的概念标「未实现」，不要删。
4. **最后排迭代**：`iterations.md` 写里程碑意图与索引，指向 `docs/features/` 下真实目录（还没有就留「尚无」）。
5. **给 TL 交接**：在回复末尾输出一张「核心聚合 → 建议容器」表，供 `tl-arch-plan` 画 C4 时对照。

## 硬性约束

- **不画 C4、不写 ADR** —— 那是 `tl-arch-plan`；越界会让两份文档互相抄错
- **不写 as-built** —— 全量模型在 `docs/facts/domain-model.md`，本文只写意图
- **术语表只有一份**：不在 `docs/features/` 下另建 glossary；spec 只能追加条目
- 每条业务规则 / 边界都要标来源（干系人、文档、会议），没有来源的先标「待确认」
- 核心聚合不写行为细节、方法签名、校验 —— 那些属于 feature `plan.md`
- 路径写相对路径，不写某台机器的绝对路径

## 与其它 skill

| Skill | 关系 |
|---|---|
| `tl-arch-plan` | 接手技术侧：C4 上下文/容器 + ADR；容器要能承载本文的核心聚合 |
| `ba-write-spec` | 单 feature 追加术语、引用 `docs/architecture/business/glossary.md`；不重建基线 |
| `ba-arch-sync-back` | 迭代后业务侧漂移对齐（本文是它的基线） |
| `ba-gen-facts` | 产出 `docs/facts/` as-built；本文与 as-built 的差异由 `ba-arch-sync-back` 处理 |

## 自检

- [ ] `product.md` 有「一句话」与「本期不做」，且不是 TODO
- [ ] `docs/architecture/business/glossary.md` 无重复中文键，英文列非空
- [ ] `docs/architecture/business/core-domain-model.md` 核心聚合 3~7 个，每个有关键字段，未实现的已标注
- [ ] `iterations.md` 的迭代索引指向真实目录或明确写「尚无」
- [ ] `docs/architecture/README.md` 的业务侧链接可点
- [ ] 已产出「核心聚合 → 建议容器」交接表，并提示 TL 接着跑 `tl-arch-plan`
