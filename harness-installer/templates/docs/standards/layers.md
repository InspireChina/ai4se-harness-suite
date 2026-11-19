# 分层架构规范

写明 **每层允许做什么、禁止做什么**。分层名称可按技术栈调整，但依赖方向必须保持单向。

## 后端四层

```
adapter → application → domain ← infrastructure
```

### adapter

允许：协议转换（HTTP/gRPC/CLI）、参数基础校验、鉴权信息提取、调用 application 用例。

禁止：业务判断、直接访问数据库、跨用例编排。

### application

允许：用例编排、事务边界、领域对象与 DTO 互转、调用多个 domain 对象协作。

禁止：把业务规则写在 application（规则属于 domain）、直接拼 SQL。

### domain

允许：聚合与实体、值对象、领域服务、仓储 **接口** 定义、业务不变量与状态守卫。

禁止：依赖框架注解与 Web 对象、直接依赖 infrastructure、读写外部系统。

### infrastructure

允许：仓储实现、ORM/Mapper、外部 API 客户端、缓存、消息、配置、安全实现。

禁止：承载业务规则、被 domain 反向依赖。

## 前端分层

```
view → component → composable → service
                                  ↓
                                store
```

- **view**：页面级组件，负责布局与页面组合，不含业务规则
- **component**：通用 UI 组件，收 props、发 events，不直接调 API
- **composable**：可复用逻辑，封装响应式状态与方法
- **service**：API 调用封装，一个资源一个文件
- **store**：跨页面共享的全局状态；页面内状态不要放进 store

## 常见违规

| 违规 | 改法 |
|---|---|
| Controller 里写 if/else 业务分支 | 下沉到 application/domain |
| domain 里 `@Autowired` 仓储实现 | 只依赖仓储接口 |
| Composable 里直接拼 URL 调 axios | 走 service |
| 视图里直接发请求 | 走 composable → service |
| 跨层直接访问另一层的实现类 | 通过接口 + 依赖注入 |

具体包路径与目录见 `{{STANDARDS_DIR}}/architecture.md` 与实际代码。
