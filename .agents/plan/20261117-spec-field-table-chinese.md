# Spec 字段表：去掉英文列，中文名改名为「字段」

> 日期：2026-11-17
>
> 关联：example-project docs/features 规格约定
>
> **plan 一旦定稿就不修改。**
>
> 状态：**已确认执行**（2026-11-17）

## 1. 目标

把 spec 字段表从「字段名(英文) + 中文名」改为单列「字段」(中文业务名)。

## 2. 约定

- **只改字段表**（§5 完整字段表 + §6 `[ADD]` 表）。
- 业务对象名、状态流转英文码、类型 `string`/`enum`、枚举取值码、§10 引用约束 **不改**。
- 表头：

```
| 字段 | 类型 | 必填 | 描述 | 取值 / 枚举 / 来源 | 创建时必填 | 可修改 |
```

- 行数据：删除原英文「字段名」列，原「中文名」写入「字段」列。

## 3. Phase

1. **example**：`_template/spec.md` + iteration1 九份 `spec.md`
2. **harness**：`harness-installer` 模板 + `ba-write-spec` skill；`--force` 重装到 example
3. **验证**：`./.agents/verify.sh`

## 4. 验证

- 字段表无「字段名 | 中文名」双列
- `ba-write-spec` 约定与模板一致
