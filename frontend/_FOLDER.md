# /frontend - 前端应用

> ⚠️ **一旦我所属的文件夹有所变化，请更新我。**

## 架构 (3 行)

```
React单页应用 ── 用户上传、配置、预览、导出的完整交互界面
       │
       └── 使用Vite构建，Framer Motion动画，与后端通过SSE实时通信
```

## 文件清单

| 文件                    | 地位 | 功能                |
| ----------------------- | ---- | ------------------- |
| `package.json`          | 配置 | 项目依赖与脚本定义  |
| `vite.config.js`        | 配置 | Vite 构建配置       |
| `tailwind.config.js`    | 配置 | Tailwind CSS 配置   |
| `postcss.config.js`     | 配置 | PostCSS 配置        |
| `eslint.config.js`      | 配置 | ESLint 代码检查配置 |
| `index.html`            | 入口 | HTML 模板入口       |
| `vercel.json`           | 部署 | Vercel 部署配置     |
| `Dockerfile`            | 部署 | Docker 容器配置     |
| `README.md`             | 文档 | 前端说明文档        |
| `.env` / `.env.example` | 环境 | 环境变量配置        |

## 子目录

| 目录      | 地位     | 职责                  |
| --------- | -------- | --------------------- |
| `src/`    | **源码** | React 组件、API、样式 |
| `public/` | 静态     | 静态资源文件          |
| `dist/`   | 产物     | 构建输出目录          |

---

_遵循分形规则：修改任何文件后，请更新此文档_
