# 技术专题（非 ADR）

实现说明、错误码、安全、数据字典等 **as-built 专题**。

跨迭代 **架构决策（ADR）** 落在 [`../../architecture/tech/adr.md`](../../architecture/tech/adr.md)。

## 已有专题

| 文件 | 专题 |
|---|---|
| `businessrule.md` | 业务规则引擎：规则定义、配置、注册、查询 |
| `data-dict.md` | 数据字典：枚举定义、注册方式、对外查询接口 |
| `error-code.md` | 错误码规范：分段、命名、映射到 HTTP 状态码 |
| `security.md` | 安全设计：认证、鉴权、密码、越权防护 |
| `state-machine.md` | 状态机：状态、流转、守卫方法、非法流转处理 |

## 新增专题

1. 新建 `{topic}.md`
2. 用下面的模板
3. 在上面的表格中登记

```markdown
# {{专题名称}}

## 背景

## 方案

## 取舍

## 影响
```
