# 领域模型

> 当前为工程空壳：**无业务聚合**。  
> 目标需求：`docs/features/iteration1/`（ACC～PLT）。按 feature plan 落地后回写本文档。

## 平台骨架（非业务聚合）

| 组件 | 说明 |
|------|------|
| JWT / UserContext | 无状态鉴权骨架，待 ACC 接入登录签发 |
| IBusinessRule / BusinessRuleConfig | 业务规则框架空注册 |
| DataDictionary* | 数据字典框架类型，暂无注册枚举 |
| PasswordService | 密码编码接口（BCrypt 实现） |
