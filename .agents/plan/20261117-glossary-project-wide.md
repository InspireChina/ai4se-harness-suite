# Plan：术语表改为项目级一份

> 日期：2026-11-17  
> 状态：已完成

## 约定

- 落点：`docs/features/glossary.md`（项目级统一语言）
- 删除各 feature / `_template` 下的 `glossary.md`
- `spec.md` 引用项目级术语表；`ba-write-spec` 维护该文件（增补术语），不再产出 per-feature glossary

## 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force`  
`./.agents/verify.sh`
