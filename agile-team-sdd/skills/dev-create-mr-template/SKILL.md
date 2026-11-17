---
name: dev-create-mr-template
description: 创建 Merge Request / Pull Request。当分支开发完成、自测通过、准备提交评审时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# Dev：创建 Merge Request

## 提交前闸门（不满足就别提）

```
[ ] 自测全绿          —— dev-self-test
[ ] 代码评审自查通过   —— dev-code-review
[ ] 事实文档已同步     —— ba-gen-facts（API / 库表 / 规则 / 字典）
[ ] diff 里没有无关文件
[ ] 没有调试代码、console.log、TODO 残留
[ ] 没有硬编码密钥
```

**任一不满足，先修。** 提一个明知过不了的 MR 只会浪费评审时间。

## 识别平台

```bash
git remote -v
```

| remote 形态 | 平台 | 工具 |
|---|---|---|
| `github.com` | GitHub | `gh pr create` |
| `gitlab` | GitLab | `glab mr create` |
| 其他 / 无 | 通用 | 推分支 + 输出手动创建链接 |

工具缺失时：装 CLI（`gh auth login` / `glab auth login`），或退化成 **推分支 + 给出创建链接**。

## 分支

```bash
git checkout -b feature/<简述-slug>
```

| 类型 | 前缀 | 例 |
|---|---|---|
| 功能 | `feature/` | `feature/appointment-cancel` |
| 缺陷 | `fix/` | `fix/token-refresh-loop` |
| 重构 | `refactor/` | `refactor/appointment-aggregate` |
| 文档 | `docs/` | `docs/testing-standard` |
| 发布 | `release/` | `release/v1.2.0` |

从 `{{TARGET_BRANCH}}` 切出。**不要**把无关改动混进来。

## 提交信息

Conventional Commits：

```
<type>(<scope>): <描述>

<正文：为什么这么改，不是改了什么>

<脚注：关联需求/规则/用例>
```

| type | 用于 |
|---|---|
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `refactor` | 不改行为的重构 |
| `docs` | 文档 |
| `test` | 测试 |
| `chore` | 构建/依赖/杂项 |
| `perf` | 性能 |

脚注要挂上可追溯的锚点：

```
Refs: R-CANCEL-003
Refs: AC-007
Refs: TC-013
```

## 创建

```bash
# GitHub
gh pr create --base {{TARGET_BRANCH}} --title "feat(appointment): 支持取消预约" --body-file /tmp/mr-body.md

# GitLab
glab mr create --target-branch {{TARGET_BRANCH}} --title "feat(appointment): 支持取消预约" --description "$(cat /tmp/mr-body.md)"
```

## MR 描述模板

```markdown
## 变更内容

- 新增：取消预约用例（`Appointment.canCancel()` 守卫）
- 修改：预约列表增加"取消"按钮
- 影响：仅前端 + application 层，domain 无破坏性变更

## 关联

- 需求：`{{FEATURES_DIR}}/appointment.md`
- 规则：R-CANCEL-003
- 用例：TC-013

## 自测结果

- 后端单元：N/N 通过
- 后端集成：N/N 通过
- 前端构建：通过
- 前端单元：N/N 通过
- E2E 自测：N/N 通过

## 事实文档同步

- [x] `{{API_SPEC}}` —— 新增 DELETE /api/v1/appointments/{id}
- [x] `{{DB_SCHEMA_DOC}}` —— 不涉及
- [ ] `{{BUSINESS_RULES_DOC}}` —— 不涉及
- [ ] `{{DATA_DICT_DOC}}` —— 不涉及

## 风险与回滚

- 风险：低。改动集中在新增路径，旧路径未改。
- 回滚：revert 本 MR 即可，无数据迁移。

## 截图 / 演示

<有 UI 变化时附截图>
```

## 拆分原则

一个 MR 做 **一件事**。

| 该拆 | 不该拆 |
|---|---|
| 功能 + 顺带重构 | 功能 + 格式化全文件 |
| 后端 + 无关的前端改动 | 功能 + 修 bug + 加日志 |
| 数据库迁移 + 大量业务改动 | 多个独立功能 |

实在要一起提，在描述里 **分节说明** 每部分为什么不能拆。

## 输出

把 MR 链接作为最终产出返回，并在描述里附上自测结果与文档同步勾选。
