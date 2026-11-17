# 业务规则规范

## 定义方式

业务规则通过 `IBusinessRule` 接口定义：

```java
public interface IBusinessRule {
    String getRuleName();       // 唯一规则名
    String getDescription();    // 描述
}
```

## 配置存储

- 规则配置存储在 `resources/business-rules/*.yml` 中
- 命名：`{domain}.yml`（如 `appointment.yml`、`auth.yml`）
- 格式：

```yaml
appointment:
  conflict:
    detection: "同一咨询师同一时段不可重复预约"
  slot:
    minMinutes: 30
    maxMinutes: 120
    intervalMinutes: 60
```

- 加载方式：`application.yml` 通过 `spring.config.import` 显式导入这些 YAML，
  导入后的顶层键（`appointment` / `auth`）作为根级属性绑定到 `BusinessRuleConfig`。
  漏掉 `spring.config.import` 时 YAML 不会进入 Environment，接口将**静默少返回 `config` 字段**。

## 查询

- `BusinessRuleProvider` 在启动时加载所有 YAML 规则
- 通过 `GET /api/v1/business-rules` 公开查询

## 配置类型绑定

顶层键绑定到 `domain/businessrule/BusinessRuleConfig`：

| 顶层键 | Java 类型 | 说明 |
|--------|-----------|------|
| `appointment` | `Map<String, Object>` | 目前全是标量子结构，绑 Map 安全 |
| `auth` | `AuthConfig`（有类型嵌套类） | `password` / `token` / `publicEndpoints` 均为强类型 |

**约束：往 YAML 里加列表前，必须先给对应的配置类加类型。**

Spring Boot 的 binder 拿到 YAML 里的 **序列** 而目标类型是 `Map<String, Object>` 时，
无法判断该绑成数组还是 Map，会退化成 **以 0/1/2… 为键的 Map**，
最终序列化出 `{"0": "...", "1": "..."}` 这种错误结构（而不是 JSON 数组）。

只有 **列表** 这一种形状会被绑坏 —— 纯标量子结构绑 Map 没问题。
`auth.publicEndpoints` 就是踩过这个坑的地方，现在由 `AuthConfig.publicEndpoints`
（`List<String>`）承接。

同时约定：

- YAML 与 Java 类必须 **同时改**，键结构一一对应
- 类里的字段默认值写死当前 YAML 的值，避免 YAML 加载失败时接口返回"空壳"配置

## 同步

新增或修改业务规则后，同步更新 `docs/designs/topic/businessrule.md`。
