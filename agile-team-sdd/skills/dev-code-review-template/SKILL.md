---
name: dev-code-review-template
description: 按项目规范做代码评审。当提交前自查、或评审别人的 PR/MR 时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# Dev：代码评审

评审的标准来自项目自己的规范，不来自评审者的口味。

## 先读规范，再看代码

```
1. {{AGENTS_FILE}}          —— 架构边界、分层规则、工程规范
2. {{STANDARDS_DIR}}/       —— 命名、分层、API、数据库、错误、安全、测试规范
3. {{DESIGNS_DIR}}/         —— 系统现状（对照实现是否与设计一致）
4. 再看 diff
```

**不要跳过第 1~3 步。** 没读规范就评审，只能评审代码风格。

## 评审前确认范围

```bash
git diff {{TARGET_BRANCH}}...HEAD          # 本次改动全貌
git diff {{TARGET_BRANCH}}...HEAD --stat   # 改动文件清单
```

先看清单 —— **改了不该改的文件** 是最常见的问题：

- 顺手重构了无关模块 → 要求拆开
- 改了格式化整个文件 → 要求还原无关行
- 改了测试期望值来迁就实现 → 要求改实现

## 检查清单

### 分层（`{{AGENTS_FILE}}` §3）

- [ ] `adapter` 层只有协议转换与参数校验，没有业务逻辑
- [ ] `application` 层用例编排完整，事务边界在这里
- [ ] `domain` 层没有依赖 infrastructure / adapter / Web 框架
- [ ] `infrastructure` 实现 domain 定义的接口，没有反向依赖

### 依赖与持久化

- [ ] 写操作走聚合行为 + repository，没有直接操作 PO
- [ ] 主键策略与项目一致
- [ ] 没有在 Controller / Repository 上写 `@Transactional`

### 错误处理

- [ ] 业务错误用 `BusinessException`，不是裸 `RuntimeException`
- [ ] 参数错误能被统一异常处理转成 400
- [ ] 权限不足返回 401/403，不是 500
- [ ] 没有把异常堆栈或敏感信息返回给前端

### 安全

- [ ] 没有硬编码密钥、密码、token
- [ ] 日志没有打印 token / 密码 / 身份证
- [ ] 对外接口都做了鉴权检查
- [ ] SQL 用参数绑定，没有字符串拼接

### 命名与风格

- [ ] 类名、方法名、字段名符合 `{{STANDARDS_DIR}}/naming.md`
- [ ] REST 路径符合 `{{STANDARDS_DIR}}/api-design.md`（`/api/v1/resource`，admin 用 `/admin/xxx`）
- [ ] 没有无用 import、没有 `TODO` 残留、没有调试 `console.log`
- [ ] 复用了现有的 assembler / converter / repository 模式，没有自创一套

### 测试

- [ ] 新增/修改的 API 有对应集成测试
- [ ] 至少覆盖 Happy Path + 关键失败分支
- [ ] 测试之间无顺序依赖，可重复执行
- [ ] 没有为了让测试变绿而弱化断言

### 文档

- [ ] API 变更 → `{{API_SPEC}}` 已更新
- [ ] 表结构变更 → `{{DB_SCHEMA_DOC}}` 已更新
- [ ] 业务规则变更 → `{{BUSINESS_RULES_DOC}}` 已更新
- [ ] 枚举变更 → `{{DATA_DICT_DOC}}` 已更新
- [ ] 迁移脚本 + 测试 `schema.sql` 同步

## 严重级别

| 级别 | 含义 | 处理 |
|---|---|---|
| **Blocker** | 安全漏洞、数据损坏、违反分层、需求没实现 | 必须改，不合并 |
| **Major** | 边界没覆盖、错误处理不对、文档没同步 | 必须改 |
| **Minor** | 命名不一致、重复代码、注释缺失 | 建议改 |
| **Nit** | 纯风格偏好 | 作者自行决定 |

**不要用 Minor / Nit 掩盖 Major。** 评审意见要指向 **规则**，不是"我觉得"。

## 评审意见写法

```
[Blocker] {{BACKEND_DIR}}/.../AppointmentService.java:42
事务边界放错了：@Transactional 标在 repository 实现上，违反 {{AGENTS_FILE}} §6。
应移到 AppService 的用例方法上。
```

每条意见包含：**位置 + 违反了哪条规则 + 应该怎么改**。

## 评审结论

- ✅ **通过** —— 无 Blocker / Major
- 🔄 **需修改** —— 有 Blocker / Major，列出清单
- ❓ **有疑问** —— 需要作者解释才能判断（写清楚问什么）

对事不对人。评审的是 **代码**，不是作者。
