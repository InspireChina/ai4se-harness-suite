# iteration1 原型（独立 Vite Demo）

Vue 3 + Vue Router + Element Plus，与业务 `apps/frontend/` **并列独立**，仅作需求演示。

## 启动

```bash
cd docs/features/iteration1/prototypes
npm install
npm run dev
# http://127.0.0.1:5174/
```

构建：`npm run build`（产物在 `dist/`，已 gitignore）。

## 路由

| 路径 | 说明 |
|---|---|
| `/` | 三端入口 |
| `/user/*` | 终端用户端 |
| `/consultant/*` | 咨询师端 |
| `/admin/*` | 管理端 |

## 目录

```
src/
├── main.ts / App.vue
├── router/index.ts
├── layouts/          # UserLayout / SideLayout
├── views/            # Home + user / consultant / admin
└── styles/app.css
```

样式与交互以本工程为准；业务规则以对应 spec 为准。
