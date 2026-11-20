# 高阶架构（Architecture）

项目级 **意图架构**：产品与领域怎么定、系统与容器怎么切、跨迭代决策记在哪。

| 相对目录 | 内容 | 主责 |
|---|---|---|
| [`business/`](./business/) | 术语表、产品定义、核心领域模型、迭代规划 | BA（`ba-arch-plan`）；TL 审 |
| [`tech/`](./tech/) | C4 上下文/容器、ADR | TL（`tl-arch-plan`），以 `business/` 的核心聚合为切分依据 |

顺序：**先业务后技术** —— `business/` 的边界与核心聚合定了，C4 容器才有切分依据；两步都完成后 architecture 才算可读。

## 与其它文档的关系

| 目录 | 性质 |
|---|---|
| **本目录** | 高阶意图（项目准备阶段产出） |
| `docs/features/` | 过程：迭代 HLD、feature spec/plan |
| `docs/facts/` | as-built 事实；领域模型 as-built 在 `facts/domain-model.md` |
| `docs/standards/` | 怎么写（含 ADR **写法**） |

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
