# 高阶架构（Architecture）

项目级 **意图架构**：产品与领域怎么定、系统与容器怎么切、跨迭代决策记在哪。

| 相对目录 | 内容 | 主责 |
|---|---|---|
| [`tech/`](./tech/) | C4 上下文/容器、ADR | TL（`tl-arch-plan`） |
| [`business/`](./business/) | 术语表、产品定义、核心领域模型、迭代规划 | BA + TL |

## 与其它文档的关系

| 目录 | 性质 |
|---|---|
| **本目录** | 高阶意图（项目准备阶段产出） |
| `docs/features/` | 过程：迭代 HLD、feature spec/plan |
| `docs/facts/` | as-built 事实（API、库表、实现专题）；领域模型 as-built 在 `facts/domain-model.md` |
| `docs/standards/` | 怎么写（含 ADR **写法**） |

## 维护

| Skill | 何时 |
|---|---|
| `tl-arch-plan` | 编写/更新本目录（C4、ADR、与迭代边界） |
| `tl-arch-sync-back` | 实现演进后对齐技术 ADR ↔ facts 非 ADR 专题 |
| `ba-arch-sync-back` | 对齐术语/领域/产品 ↔ features 与 `facts/domain-model.md`（as-built） |

## 索引

### 技术

- [C4 系统上下文 / 集成](./tech/c4-context.md)
- [C4 容器](./tech/c4-container.md)
- [ADR 一句话表](./tech/adr.md)

### 业务

- [统一语言术语表](./business/glossary.md)
- [产品定义与高阶概念](./business/product.md)
- [核心领域模型（Core）](./business/core-domain-model.md)
- [迭代规划](./business/iterations.md)
