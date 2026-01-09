# Docker + Cloudflare Tunnel 部署检查清单

## ✅ 本地 Docker 部署检查

### 前置条件
- [ ] Docker 已安装 (`docker --version`)
- [ ] Docker Compose 已安装 (`docker-compose --version`)
- [ ] 有足够的磁盘空间（至少 5GB）
- [ ] 端口 5173 和 8005 未被占用

### 环境配置
- [ ] 复制了 `config/.env.example` 到 `config/.env`
- [ ] 填入了 `OPENROUTER_API_KEY`
- [ ] 填入了 `ADOBE_CLIENT_ID` 和 `ADOBE_CLIENT_SECRET`（可选）
- [ ] 检查了 `config/.env` 中的其他配置

### Docker 镜像构建
- [ ] 后端 Dockerfile 正确（已验证）
- [ ] 前端 Dockerfile 已创建
- [ ] `.dockerignore` 已创建
- [ ] `docker-compose.yml` 已创建

### 启动和验证
```bash
# 1. 启动服务
./docker-start.sh start

# 2. 检查服务状态
docker-compose ps

# 3. 验证后端健康
curl http://localhost:8005/api/health

# 4. 访问前端
# 打开浏览器访问 http://localhost:5173
```

### 常见问题排查
- [ ] 检查后端日志：`docker-compose logs backend`
- [ ] 检查前端日志：`docker-compose logs frontend`
- [ ] 验证网络连接：`docker-compose exec frontend curl http://backend:8005/api/health`
- [ ] 检查文件挂载：`docker-compose exec backend ls -la /app/input`

---

## ✅ Cloudflare Tunnel 内网穿透检查

### 前置条件
- [ ] 有 Cloudflare 账户（免费版即可）
- [ ] 有一个域名并在 Cloudflare 托管
- [ ] 已安装 cloudflared CLI

### 安装 cloudflared
```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# 验证安装
cloudflared --version
```

### 创建和配置 Tunnel
- [ ] 登录 Cloudflare：`cloudflared tunnel login`
- [ ] 创建 Tunnel：`cloudflared tunnel create my-presentation`
- [ ] 记下 Tunnel ID
- [ ] 创建配置文件 `~/.cloudflared/config.yml`
- [ ] 配置前端路由：`app.yourdomain.com` → `http://localhost:5173`
- [ ] 配置后端路由：`api.yourdomain.com` → `http://localhost:8005`

### DNS 配置
在 Cloudflare Dashboard 中：
- [ ] 添加 CNAME 记录：`app` → `my-presentation.cfargotunnel.com`
- [ ] 添加 CNAME 记录：`api` → `my-presentation.cfargotunnel.com`
- [ ] 等待 DNS 生效（通常 5-10 分钟）

### 启动 Tunnel
```bash
# 启动 Tunnel
cloudflared tunnel run my-presentation

# 在另一个终端验证
curl https://api.yourdomain.com/api/health
```

### 验证连接
- [ ] 前端可访问：`https://app.yourdomain.com`
- [ ] 后端 API 可访问：`https://api.yourdomain.com/api/health`
- [ ] 前端可连接后端（检查浏览器控制台）

---

## ✅ 生产部署建议

### 安全性
- [ ] 不要在 docker-compose 中硬编码敏感信息
- [ ] 使用 `.env` 文件管理环境变量
- [ ] 定期更新 Docker 镜像
- [ ] 启用 Cloudflare 的 DDoS 防护

### 性能
- [ ] 在 docker-compose 中设置内存限制
- [ ] 配置 CPU 限制
- [ ] 启用 Cloudflare 的缓存
- [ ] 监控容器资源使用

### 监控和日志
- [ ] 设置日志收集（ELK、Datadog 等）
- [ ] 配置告警规则
- [ ] 定期检查 Tunnel 连接状态
- [ ] 监控 API 响应时间

### 备份和恢复
- [ ] 定期备份 `output` 目录
- [ ] 备份 `config/.env` 文件
- [ ] 记录 Tunnel 配置
- [ ] 测试恢复流程

---

## 🚀 快速启动命令

```bash
# 1. 启动所有服务
./docker-start.sh start

# 2. 查看日志
./docker-start.sh logs

# 3. 启动 Tunnel（在另一个终端）
cloudflared tunnel run my-presentation

# 4. 访问应用
# 本地：http://localhost:5173
# 远程：https://app.yourdomain.com

# 5. 停止服务
./docker-start.sh stop
```

---

## 📝 故障排查

### Docker 相关
```bash
# 查看所有容器
docker ps -a

# 查看容器日志
docker logs <container-id>

# 进入容器
docker exec -it <container-id> /bin/bash

# 重启容器
docker-compose restart
```

### Tunnel 相关
```bash
# 查看 Tunnel 列表
cloudflared tunnel list

# 查看 Tunnel 详情
cloudflared tunnel info my-presentation

# 调试模式运行
cloudflared tunnel run my-presentation --loglevel debug

# 检查 DNS 解析
nslookup app.yourdomain.com
```

### 网络相关
```bash
# 测试后端连接
curl http://localhost:8005/api/health

# 测试 Tunnel 连接
curl https://api.yourdomain.com/api/health

# 查看容器网络
docker network inspect app-network
```

---

## 📞 获取帮助

- Docker 文档：https://docs.docker.com/
- Docker Compose 文档：https://docs.docker.com/compose/
- Cloudflare Tunnel 文档：https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- 项目 GitHub Issues：[你的项目地址]
