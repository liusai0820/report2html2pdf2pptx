# /src - 后端核心

> **⚠️ 一旦本文件夹有所变化，请更新我。**

Python 后端引擎。处理 API 请求、AI 编排、文档解析、输出渲染、用户管理、Telegram 通知。

---

## 子目录

| 目录       | 地位           | 功能                                |
| ---------- | -------------- | ----------------------------------- |
| `v2/`      | **当前主引擎** | AI 设计器、设计系统、图像生成       |
| `core/`    | 兼容层         | 旧版组件，server.py 仍有依赖        |
| `prompts/` | 兼容层         | 旧版 Prompt 系统                    |
| `themes/`  | 主题系统       | CSS 生成器、主题管理器              |

## 文件列表

| 文件                 | 地位     | 功能                                 |
| -------------------- | -------- | ------------------------------------ |
| `server.py`          | **入口** | FastAPI 主服务，API、Admin、Telegram 通知 |
| `config.py`          | 配置中心 | 加载环境变量，提供全局配置           |
| `db.py`              | 数据库   | Supabase 交互（用户配额、职业信息）  |
| `mailer.py`          | 邮件服务 | SMTP 发信、Gmail 草稿保存            |
| `comfyui.py`         | 图像生成 | 与本地 ComfyUI 通信                  |
| `v2_adapter.py`      | 适配器   | 连接 v1 API 与 v2 引擎               |
| `document_parser.py` | 文档解析 | 支持 PDF/DOCX/MD/TXT                 |
| `workflow_api.json`  | 资源     | ComfyUI 工作流模板                   |

## 本次更新 (2026-01-04)

- 新增 Admin API: `/api/admin/users`, `/api/admin/upgrade`, `/api/admin/generations`
- 新增用户职业信息收集 (occupation 字段)
- Telegram 通知增强: 新用户注册带职业、生成完成发 HTML
- 活跃用户定义: 7日内有生成记录

---

_最后更新: 2026-01-04_
