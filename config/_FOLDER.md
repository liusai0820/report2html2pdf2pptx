# /config - 配置中心

> **⚠️ 一旦本文件夹有所变化，请更新我。**

环境变量与敏感配置。`.env` 不入版本库，`.env.example` 作为模板。

---

## 文件列表

| 文件           | 地位     | 功能                                      |
| -------------- | -------- | ----------------------------------------- |
| `.env`         | **核心** | 生产环境变量（API Keys 等，**不入 Git**） |
| `.env.example` | 模板     | `.env` 的脱敏模板，供新开发者参考         |

## 关键配置项

| 变量                          | 用途                  |
| ----------------------------- | --------------------- |
| `OPENROUTER_API_KEY`          | LLM API 访问密钥      |
| `VITE_SUPABASE_URL`           | Supabase 项目地址     |
| `SUPABASE_SERVICE_ROLE_KEY`   | Supabase 后端管理密钥 |
| `SMTP_USER` / `SMTP_PASSWORD` | Gmail 邮件发送        |
| `TELEGRAM_BOT_TOKEN`          | Telegram 告警机器人   |
| `COMFYUI_ENABLED`             | 是否启用本地 ComfyUI  |

---

_最后更新: 2025-12-26_
