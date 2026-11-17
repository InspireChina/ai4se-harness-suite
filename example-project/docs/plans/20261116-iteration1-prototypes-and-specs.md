# iteration1 原型与特性补全

>日期： 2026-11-16
>
>关联需求：docs/features/iteration1/
>
>设计 design：本轮不改 designs/ 业务事实；原型仅 UI 表达
>
>**plan一旦定稿就不修改。**

## 1. 背景与目标

- 上一轮已落 9 份骨架 spec；本轮补全字段表、业务规则、GWT 验收，并落地 Element Plus 静态原型。
- 原型与前端工程同构：Element Plus + Vue 3（CDN 静态页，便于评审；后续 `frontend/` 可装同库）。

## 2. 交付物

1. `docs/features/iteration1/prototypes/` 全套页面（入口 + user + consultant + admin）
2. 9 份 spec：状态由骨架 → v0.1，补齐 §5/§7/§12 并挂接 §14
3. 更新 iteration1 README 待办勾选

## 3. 原型页面清单

| 角色 | 页面 |
|---|---|
| 入口 | index.html |
| 用户 | login, index, search, consultant-detail, booking, my-orders, order-detail, profile |
| 咨询师 | index, application, profile, schedule, orders, settlements |
| 管理 | index, applications, categories, users, orders, reports |

## 4. 验收

- [x] 浏览器直接打开入口可跳转三端各页
- [x] 页面使用 Element Plus 组件（按钮/表单/表格/标签/步骤条等）
- [x] 每份 spec §14 路径可对应到真实 HTML
- [x] 每份 spec 不再标「骨架」，含完整字段表与 GWT 验收
