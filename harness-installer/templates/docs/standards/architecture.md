# 系统架构规范

> 本文件写 **架构意图与硬约束**（目标状态）；as-built 事实在 `{{FACTS_DIR}}/`。
> 标 `TODO` 的段落必须在项目准备阶段（`tl-arch-plan`）定稿后回填，否则等于没有约定。

## 部署形态

TODO：画/改部署图，写清有几类进程、谁对谁发请求、端口与部署方式（单体 / 前后端分离 / 多服务）。

```
Client ──HTTP──▶ 前端（{{FRONTEND_DIR}} 构建产物）──/api──▶ 后端（{{BACKEND_DIR}}）──▶ 数据存储
```

## 通信方式

| 端 | 目标 | 协议 | 说明 |
|---|---|---|---|
| 浏览器 → 前端 | 静态资源 | HTTP | TODO：开发用 dev server？生产用 Nginx？ |
| 前端 → 后端 | API | HTTP | TODO：代理前缀、端口、超时、鉴权头 |
| 后端 → 数据存储 | 持久化 | TODO | TODO：驱动 / 连接池 / 连接数 |
| 后端 → 外部系统 | 第三方 | TODO | TODO：同步调用还是异步消息 |

## 分层与依赖方向

```
adapter → application → domain ← infrastructure
```

- **adapter**：协议转换与参数基础校验，不含业务逻辑
- **application**：用例编排、事务边界、DTO ↔ domain 转换
- **domain**：业务不变量、聚合与值对象、仓储接口；不依赖框架与存储
- **infrastructure**：实现 domain 定义的接口（持久化、外部调用、安全、配置）

硬约束：

- 依赖方向只能从外到内；`domain` 不得依赖 `infrastructure` / `adapter`
- 跨层调用不得跳过 `application`
- 具体分层与包路径见 `{{STANDARDS_DIR}}/layers.md`

## 前端结构

TODO：按实际目录改写。默认约定：

```
src/
├── views/<subsystem>/     # 页面级组件（按子系统分组）
├── components/            # 通用 UI 组件
├── composables/           # 可复用组合式逻辑
├── services/              # API 调用封装（每个资源一个文件）
├── stores/                # 全局状态
└── types/                 # 类型定义
```

## 技术栈

| 组件 | 技术 | 版本 |
|---|---|---|
| 运行时 | TODO | TODO |
| 后端框架 | TODO | TODO |
| 持久化 | TODO | TODO |
| 前端框架 | TODO | TODO |
| 构建 | TODO | TODO |
| 测试 | TODO | TODO |

## 模块边界

| 模块 | 职责 | 不负责 |
|---|---|---|
| TODO：模块名 | TODO | TODO |

## 跨迭代取舍

不在本文件写长篇决策：按 `{{STANDARDS_DIR}}/adr.md` 的写法，落成一句话进 `{{ADR_FILE}}`。
