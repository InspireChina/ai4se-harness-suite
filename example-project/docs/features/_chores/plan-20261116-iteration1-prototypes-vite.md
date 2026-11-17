# iteration1 原型改为独立 Vite 工程

>日期： 2026-11-16
>
>关联需求：docs/features/iteration1/
>
>**plan一旦定稿就不修改。**

## 1. 背景与目标

- 将 CDN 静态多页原型改为独立 Vite + Vue 3 + Element Plus demo。
- 不并入 `example-project/containers/frontend/`。

## 2. 交付

- `docs/features/iteration1/prototypes/` 成为可 `npm run dev` 的工程（端口 5174）。
- 删除 CDN HTML、`_gen.py`、旧 `assets/`。
- Spec §14 改为路由路径。

## 3. 验收

- [x] `npm install && npm run build` 通过
- [x] 无 `unpkg.com` / `_gen.py` 残留
- [x] README / AGENTS / §14 已同步
