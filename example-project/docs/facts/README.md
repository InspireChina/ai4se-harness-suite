# 事实文档（Facts）

描述系统 **当前真实状态** 的文档，随代码同步更新。

> 高阶 **意图**（C4、ADR、术语、领域意图）见 [`../architecture/`](../architecture/)。本目录只写 as-built。

| 位置 | 内容 |
|---|---|
| 本目录根 | `api.yaml`、`db-schema.md`、`domain-model.md`（as-built） |
| [`business/`](./business/) | 业务事实（流程等） |
| [`tech-topic/`](./tech-topic/) | 实现专题（非 ADR；写法见 [`../standards/adr.md`](../standards/adr.md)） |

## 现有文档

- [api.yaml](./api.yaml) — API
- [db-schema.md](./db-schema.md) — 数据库
- [domain-model.md](./domain-model.md) — 领域模型（as-built 全量）；Core 见 [architecture/business/core-domain-model.md](../architecture/business/core-domain-model.md)
- [business/](./business/) — 业务事实
- [tech-topic/](./tech-topic/) — 实现专题（ADR 在 architecture/tech/adr.md）
