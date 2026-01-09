# Render 部署指南

## 概述

本指南帮助你将 SlideCraft AI 部署到 [Render](https://render.com)。

## 架构

```
┌─────────────────────────────────────────────┐
│              Render 平台                     │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │   前端 (静态)    │  │  后端 (Docker)  │  │
│  │   React/Vite    │→ │  FastAPI        │  │
│  │   免费          │  │  $7/月起        │  │
│  └─────────────────┘  └────────┬────────┘  │
│                                │            │
└────────────────────────────────┼────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │    Supabase     │ │  Cloudflare R2  │ │   OpenRouter    │
    │   (用户/数据库)  │ │  (文件存储)      │ │   (AI API)      │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Cloudflare R2 存储设置 ⭐

R2 用于存储生成的 HTML/PDF/PPTX 文件，替代 Render 的临时文件系统。

### 1. 创建 R2 Bucket

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 侧边栏选择 **R2 Object Storage**
3. 点击 **Create bucket**
4. 输入名称：`slidecraft`（或自定义）
5. 选择 **Automatic** 位置（或选择靠近用户的区域）

### 2. 启用公开访问

1. 进入刚创建的 bucket
2. 点击 **Settings** 标签
3. 找到 **Public Access**
4. 点击 **Allow Access**（允许公开读取）

### 3. 创建 API Token

1. 回到 R2 Overview 页面
2. 点击 **Manage R2 API Tokens**
3. 点击 **Create API token**
4. 配置：
   - **Token name**: `slidecraft-render`
   - **Permissions**: Object Read & Write
   - **Specify bucket(s)**: 选择 `slidecraft`
5. 点击 **Create API Token**
6. **立即复制并保存**：
   - Access Key ID
   - Secret Access Key
   - Account ID (在页面右上角可以找到)

### 4. (可选) 配置自定义域名

1. 进入 bucket **Settings**
2. 找到 **Custom Domains**
3. 点击 **Connect Domain**
4. 输入子域名如 `cdn.yourdomain.com`
5. Cloudflare 会自动配置 DNS 和 SSL

### 5. 配置 CORS（重要！）

为了让前端能够加载 R2 上的 HTML 文件，需要配置 CORS：

1. 使用 Wrangler CLI：

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 设置 CORS
wrangler r2 bucket cors put slidecraft --rules '[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 86400
  }
]'
```

2. 或者在 Cloudflare Dashboard 中配置（需要使用 API）

### R2 免费额度

| 项目         | 免费额度 | 超出价格     |
| ------------ | -------- | ------------ |
| 存储         | 10 GB    | $0.015/GB/月 |
| Class A (写) | 1M 请求  | $4.50/M      |
| Class B (读) | 10M 请求 | $0.36/M      |
| 出站流量     | 无限     | 免费         |

**预估**：一般使用场景下，完全在免费额度内。

## 成本估算

| 服务 | Plan          | 价格     | 说明                  |
| ---- | ------------- | -------- | --------------------- |
| 前端 | Static (Free) | $0/月    | 静态文件托管          |
| 后端 | Starter       | $7/月    | 512MB RAM, 0.5 CPU    |
| 后端 | Standard      | $25/月   | 2GB RAM, 1 CPU (推荐) |
| 磁盘 | 1GB           | $0.25/月 | 持久存储              |

**最低成本**: ~$7.25/月 (Starter)
**推荐配置**: ~$25.25/月 (Standard)

## 部署步骤

### 方式一：Blueprint 自动部署（推荐）

1. **连接 GitHub**

   - 登录 [Render Dashboard](https://dashboard.render.com)
   - 点击 "New" → "Blueprint"
   - 选择你的 GitHub 仓库

2. **选择 Blueprint 文件**

   - Render 会自动检测 `render.yaml`
   - 点击 "Apply" 开始部署

3. **配置环境变量**
   - 部署后进入 "Environment" 标签
   - 填入 `.env.render.example` 中的敏感信息

### 方式二：手动部署

#### 部署后端

1. 点击 "New" → "Web Service"
2. 选择 "Docker" 运行时
3. 配置：
   - **Name**: `slidecraft-backend`
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Region**: Singapore (离中国近)
   - **Plan**: Starter ($7) 或 Standard ($25)
4. 添加环境变量（见下方列表）
5. 添加持久磁盘：
   - **Mount Path**: `/app/output`
   - **Size**: 1 GB

#### 部署前端

1. 点击 "New" → "Static Site"
2. 配置：
   - **Name**: `slidecraft-frontend`
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Publish Directory**: `frontend/dist`
3. 添加环境变量：
   - `VITE_API_URL`: 后端服务 URL (如 `https://slidecraft-backend.onrender.com`)
   - `VITE_SUPABASE_URL`: Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Supabase 匿名密钥

## 环境变量配置

### 必需变量

| 变量名                      | 说明                  | 示例                      |
| --------------------------- | --------------------- | ------------------------- |
| `OPENROUTER_API_KEY`        | OpenRouter API 密钥   | `sk-or-v1-xxx`            |
| `VITE_SUPABASE_URL`         | Supabase 项目 URL     | `https://xxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY`    | Supabase 匿名密钥     | `eyJhxxx`                 |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase 服务密钥     | `eyJhxxx`                 |
| `R2_ACCOUNT_ID`             | Cloudflare Account ID | `abc123...`               |
| `R2_ACCESS_KEY_ID`          | R2 Access Key         | `xxx`                     |
| `R2_SECRET_ACCESS_KEY`      | R2 Secret Key         | `xxx`                     |

### 可选变量

| 变量名                    | 说明              | 默认值       |
| ------------------------- | ----------------- | ------------ |
| `R2_BUCKET_NAME`          | R2 Bucket 名称    | `slidecraft` |
| `R2_PUBLIC_URL`           | R2 自定义域名     | 自动生成     |
| `COMFYUI_ENABLED`         | ComfyUI 开关      | `false`      |
| `DISABLE_PPTX`            | 禁用 PPTX 转换    | `true`       |
| `MAX_CONCURRENT_REQUESTS` | 最大并发数        | `2`          |
| `UVICORN_WORKERS`         | Uvicorn worker 数 | `1`          |

完整列表见 `.env.render.example`

## 限制说明

### Render Starter Plan 限制

1. **内存限制 (512MB)**

   - 已优化 Dockerfile 减少内存使用
   - 建议升级 Standard Plan (2GB) 以获得更好性能

2. **无 GPU**

   - ComfyUI 已禁用
   - AI 图片生成功能不可用

3. **冷启动**

   - 免费和 Starter Plan 有冷启动时间
   - 首次请求可能需要 30-60 秒

4. **文件存储**
   - 使用 Cloudflare R2 云存储
   - 免费 10GB，无需担心磁盘限制
   - 文件通过 CDN 全球加速

## 故障排查

### 常见问题

1. **PDF 生成失败**

   ```
   解决：检查 Chromium 是否正常安装
   日志：查看 Render Dashboard > Logs
   ```

2. **内存超限 (OOM)**

   ```
   解决：升级到 Standard Plan，或减少 MAX_CONCURRENT_PDF_TASKS
   ```

3. **超时错误**
   ```
   解决：增加 TIMEOUT_SECONDS，或优化请求处理
   ```

### 查看日志

```bash
# Render Dashboard > 你的服务 > Logs
# 或使用 Render CLI
render logs --service slidecraft-backend
```

## 与原 Docker 部署对比

| 项目     | Docker (本地)        | Render       |
| -------- | -------------------- | ------------ |
| 成本     | 电费 + 硬件          | $7-25/月     |
| 维护     | 需自行管理           | 托管服务     |
| 扩展     | 受本地资源限制       | 可随时升级   |
| ComfyUI  | ✅ 支持              | ❌ 不支持    |
| 冷启动   | 无                   | 有 (Starter) |
| 全球访问 | 需 Cloudflare Tunnel | 内置 CDN     |

## 回滚到 Docker

如果 Render 不满足需求，可以随时切回 Docker 部署：

```bash
# 回到项目目录
cd /Users/qibaoba/VibeCoding/pptx

# 启动 Docker
docker-compose up -d

# 恢复 Cloudflare Tunnel
# ...
```
