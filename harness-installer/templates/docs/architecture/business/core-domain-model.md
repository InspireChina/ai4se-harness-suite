# 核心领域模型（Core）

> **意图侧**：只维护 **核心聚合 + 关键字段**，不写全量字段/行为/端口。  
> **as-built**（全量）见 `docs/facts/domain-model.md`；漂移时用 `ba-arch-sync-back` 对齐。  
> 维护：`ba-arch-plan` 起草（首次/新增业务域）；`ba-arch-sync-back` 对齐意图与 as-built。

## 核心聚合

| 聚合 | 职责 | 关键字段 |
|---|---|---|
| TODO | TODO | TODO |

## 关系（示意）

```
TODO
```

## 不在本文写的内容

- 全量字段表、方法签名、校验细节 → `facts/domain-model.md` / feature `plan.md`
- 值对象枚举清单、基础设施端口 → as-built 或 ADR / tech-topic
