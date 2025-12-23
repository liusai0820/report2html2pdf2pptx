# Docker 本地部署 + Cloudflare Tunnel 内网穿透指南

## 前置要求

- Docker 和 Docker Compose 已安装
- Cloudflare 账户（免费版即可）
- 一个域名（可以使用 Cloudflare 托管）

## 第一步：准备环境变量

1. 复制环境变量文件：
```bash
cp config/.env.example config/.env
```

2. 编辑 `config/.env`，填入你的 API 密钥：
```bash
OPENROUTER_API_KEY=your_key_here
ADOBE_CLIENT_ID=your_id_here
ADOBE_CLIENT_SECRET=your_secret_here
```

## 第二步：本地 Docker 部署

### 方式 1：使用 docker-compose（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose down
```

服务启动后：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8005/api
- 健康检查：http://localhost:8005/api/health

### 方式 2：手动 Docker 命令

```bash
# 构建后端镜像
docker build -t ai-presentation-backend .

# 构建前端镜像
docker build -t ai-presentation-frontend ./frontend

# 创建网络
docker network create app-network

# 启动后端
docker run -d \
  --name backend \
  --network app-network \
  -p 8005:8005 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  --env-file config/.env \
  ai-presentation-backend

# 启动前端
docker run -d \
  --name frontend \
  --network app-network \
  -p 5173:5173 \
  -e VITE_API_URL=http://localhost:8005/api \
  ai-presentation-frontend
```

## 第三步：Cloudflare Tunnel 内网穿透

### 安装 Cloudflare Tunnel

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Windows
# 从 https://github.com/cloudflare/cloudflared/releases 下载 exe
```

### 配置 Tunnel

1. 登录 Cloudflare：
```bash
cloudflared tunnel login
```
这会打开浏览器让你选择域名并授权。

2. 创建 Tunnel：
```bash
cloudflared tunnel create my-presentation
```
记下 Tunnel ID。

3. 创建配置文件 `~/.cloudflared/config.yml`：
```yaml
tunnel: my-presentation
credentials-file: /Users/your-username/.cloudflared/my-presentation.json

ingress:
  # 前端路由
  - hostname: app.yourdomain.com
    service: http://localhost:5173
  
  # 后端 API 路由
  - hostname: api.yourdomain.com
    service: http://localhost:8005
  
  # 默认路由（可选）
  - service: http_status:404
```

4. 在 Cloudflare Dashboard 中配置 DNS：
   - 添加 CNAME 记录：`app` → `my-presentation.cfargotunnel.com`
   - 添加 CNAME 记录：`api` → `my-presentation.cfargotunnel.com`

5. 启动 Tunnel：
```bash
cloudflared tunnel run my-presentation
```

### 验证连接

```bash
# 检查 Tunnel 状态
cloudflared tunnel list

# 查看 Tunnel 详情
cloudflared tunnel info my-presentation
```

## 第四步：更新前端配置

编辑 `frontend/.env.local`（或在 docker-compose 中设置）：

```bash
# 本地开发
VITE_API_URL=http://localhost:8005/api

# 通过 Tunnel 访问
VITE_API_URL=https://api.yourdomain.com
```

## 常见问题

### 1. Docker 容器无法访问本地文件

确保挂载路径正确：
```bash
docker-compose up -d
docker exec backend ls -la /app/input
```

### 2. 前端无法连接后端

检查网络连接：
```bash
docker-compose exec frontend curl http://backend:8005/api/health
```

### 3. Cloudflare Tunnel 连接失败

```bash
# 检查日志
cloudflared tunnel run my-presentation --loglevel debug

# 重新认证
cloudflared tunnel login
```

### 4. Chrome/Puppeteer 相关错误

确保 Docker 镜像中的 Chrome 依赖已正确安装：
```bash
docker-compose exec backend google-chrome-stable --version
```

## 生产部署建议

1. **使用环境变量**：不要在 docker-compose 中硬编码敏感信息
2. **启用 HTTPS**：Cloudflare Tunnel 自动处理 SSL/TLS
3. **监控日志**：使用 `docker-compose logs` 或集中日志系统
4. **定期备份**：备份 `output` 目录中的生成文件
5. **资源限制**：在 docker-compose 中添加内存和 CPU 限制

## 停止和清理

```bash
# 停止所有服务
docker-compose down

# 删除所有数据（谨慎！）
docker-compose down -v

# 停止 Tunnel
# 在运行 cloudflared 的终端按 Ctrl+C
```

## 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```
