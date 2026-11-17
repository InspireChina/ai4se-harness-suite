# 事实文档（Facts）

本目录描述系统 **当前的真实状态**，必须与代码保持一致。

## 子目录

| 路径 | 内容 |
|---|---|
| `api.yaml` | OpenAPI 格式的接口定义 |
| `db-schema.md` | 数据库表结构与索引说明 |
| `domain-model.md` | 领域模型：聚合、实体、值对象、关系 |
| `business/` | 业务事实（流程等） |
| `tech-topic/` | 技术专题 / **ADR 正文** / 实现说明（写法见 `docs/standards/adr.md`） |

## 维护规则

- 改了接口 → 更新 `api.yaml`
- 改了表结构 → 更新 `db-schema.md`
- 改了业务规则 → 更新 `tech-topic/businessrule.md`
- 改了数据字典 → 更新 `tech-topic/data-dict.md`
- 新增业务事实 → 在 `business/` 下新建文件
- 新增专题 → 在 `tech-topic/` 下新建文件，并在本表登记
