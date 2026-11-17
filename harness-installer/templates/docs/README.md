# 文档体系

本目录是项目的 **单一信息源**。文档分两类：

| 类别 | 目录 | 性质 | 生命周期 |
|---|---|---|---|
| 过程文档 | `features/`（含 spec/plan） | 会随需求演进 | 随需求创建，**定稿后不再修改** |
| 事实文档 | `facts/`、`standards/` | 描述系统当前真实状态 | 随代码同步更新 |

## 目录

| 目录 | 内容 | 谁来写 |
|---|---|---|
| `features/` | JIRA 风格 feature 文件夹：`spec.md` + `plan.md`；迭代目录含 `high-level-design.md` | 产品 / BA / TL / 开发 |
| `features/_chores/` | 无关联 feature 的横切技术方案 | 架构师 / 负责人 |
| `facts/` | 技术事实：API、库表、领域模型 | 全员，随代码同步 |
| `facts/business/` | 业务事实：流程等 | BA / 开发 |
| `facts/tech-topic/` | 技术专题 / ADR 正文 / 实现说明（写法见 `standards/adr.md`） | 需要时新建 |
| `standards/` | 代码规范（事实）：架构、命名、分层、安全、API、错误、测试、ADR 写法 | 架构师 |
| `standards/templates/` | 代码模版 / snippet / ADR 模板 | 架构师 |
| `test-cases/` | 测试用例文本基线（见下） | QA / 开发 |

### `test-cases/` 子目录

| 子目录 | 归属 | 内容 |
|---|---|---|
| `test-cases/e2e-cases/` | **QA 测试** | E2E 验收用例文本基线（`TC-xxx`），合并闸门 |
| `test-cases/manual-cases/` | **QA 测试** | 需人工执行的用例（`TC-Mxx`） |
| `test-cases/smoking-cases/` | **QA 测试** | 上线前快速回归用例（`TC-Sxx`） |
| `test-cases/dev-self-cases/` | **开发自测** | 可选自测场景索引（实现仍在源码旁 / `e2e/tests/dev/`） |

> QA 三目录：定义权与判定权归 QA，是合并闸门。  
> `dev-self-cases/` 对开发负责，不是合并闸门。归属细则见 `standards/test.md`。

## 写作约定

- 需求规格与 Plan **定稿后不改**；同一 feature 的二次改造新建 `plan-{slug}.md`。
- 事实文档必须与代码一致；改了代码就要改文档。
- 新建需求：复制 `features/_template/` 为 `features/<迭代>/<CODE>-<slug>/`，再改 `spec.md` / `plan.md`；新术语写入 `features/glossary.md`。
- 每个迭代应有 `features/<迭代>/high-level-design.md`；**确认前不得写 feature Plan**。

## 同步检查点

每轮任务结束时必须回答：

- [ ] 本次变更是否影响 `facts/api.yaml`？
- [ ] 本次变更是否影响 `facts/db-schema.md`？
- [ ] 本次变更是否影响 `facts/tech-topic/businessrule.md`？
- [ ] 本次变更是否影响 `facts/tech-topic/data-dict.md`？
