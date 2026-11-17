# 文档体系

本目录是项目的 **单一信息源**。文档分两类：

| 类别 | 目录 | 性质 | 生命周期 |
|---|---|---|---|
| 过程文档 | `features/`、`plans/` | 会随需求演进 | 随需求创建，**定稿后不再修改** |
| 事实文档 | `facts/`、`standards/` | 描述系统当前真实状态 | 随代码同步更新 |

## 目录

| 目录 | 内容 | 谁来写 |
|---|---|---|
| `features/` | 需求规格说明书：背景、字段表、业务规则、权限、验收标准 | 产品 / BA |
| `plans/` | 技术方案：领域模型、DDL、API、时序图、任务拆分、风险 | 架构师 / 负责人 |
| `facts/` | 技术事实：API、库表、领域模型 | 全员，随代码同步 |
| `facts/business/` | 业务事实：流程等 | BA / 开发 |
| `facts/tech-topic/` | 技术专题 / ADR / 实现说明 | 需要时新建 |
| `standards/` | 代码规范（事实）：架构、命名、分层、安全、API、错误、测试 | 架构师 |
| `standards/templates/` | 代码模版 / snippet，供参考复制 | 架构师 |
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

- 需求规格与 Plan **定稿后不改**；同一资源的二次改造新建文件（`YYYYMMDD-{slug}.md`）。
- 事实文档必须与代码一致；改了代码就要改文档。
- 新建需求先复制 `_template.md` 再改，不要从零写。

## 同步检查点

每轮任务结束时必须回答：

- [ ] 本次变更是否影响 `facts/api.yaml`？
- [ ] 本次变更是否影响 `facts/db-schema.md`？
- [ ] 本次变更是否影响 `facts/tech-topic/businessrule.md`？
- [ ] 本次变更是否影响 `facts/tech-topic/data-dict.md`？
