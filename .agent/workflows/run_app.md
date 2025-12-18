---
description: Start the Full Stack AI Presentation Generator (Frontend + Backend)
---

# 本地开发运行

## 快速启动

### 1. 启动后端服务器

```bash
cd /Users/qibaoba/VibeCoding/pptx
python src/server.py
```

后端 API 地址: `http://localhost:8005`

### 2. 启动前端开发服务器

```bash
cd /Users/qibaoba/VibeCoding/pptx/frontend
npm run dev
```

前端地址: `http://localhost:5173`

---

## 部署到生产环境

### 后端部署 (Railway)

1. 在 [Railway](https://railway.app) 创建新项目
2. 连接 GitHub 仓库
3. 在 Railway Dashboard 设置环境变量:
   - `OPENROUTER_API_KEY` - OpenRouter API 密钥
   - `ADOBE_CLIENT_ID` - Adobe PDF Services Client ID
   - `ADOBE_CLIENT_SECRET` - Adobe PDF Services Client Secret
4. Railway 会自动检测 `Dockerfile` 并部署

### 前端部署 (Vercel)

1. 在 [Vercel](https://vercel.com) 导入项目，选择 `frontend` 目录
2. 设置环境变量:
   - `VITE_API_URL` - Railway 后端地址，例如 `https://your-app.railway.app/api`
3. 部署

---

## 环境变量说明

### 后端 (`config/.env`)

```
OPENROUTER_API_KEY=xxx          # 必需 - AI 模型 API
ADOBE_CLIENT_ID=xxx             # 可选 - PDF → PPTX 转换
ADOBE_CLIENT_SECRET=xxx         # 可选 - PDF → PPTX 转换
```

### 前端 (`.env.local`)

```
VITE_API_URL=http://localhost:8005/api  # 后端 API 地址
```

---

## API 端点

| 端点                   | 方法 | 说明                |
| ---------------------- | ---- | ------------------- |
| `/api/health`          | GET  | 健康检查            |
| `/api/scenarios`       | GET  | 获取场景列表        |
| `/api/files`           | GET  | 获取已上传文件      |
| `/api/upload`          | POST | 上传文档            |
| `/api/generate`        | POST | 同步生成 (向后兼容) |
| `/api/generate-stream` | POST | SSE 流式生成 (推荐) |
