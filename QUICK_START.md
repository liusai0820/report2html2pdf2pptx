# 🚀 Docker + Cloudflare Tunnel 快速开始指南

## 5 分钟快速部署

### 1️⃣ 验证环境

```bash
# 验证 Docker 和配置
./verify-docker-setup.sh
```

### 2️⃣ 配置 API 密钥

```bash
# 复制环境变量模板
cp config/.env.example config/.env

# 编辑并填入你的 API 密钥
# 必需：OPENROUTER_API_KEY
# 可选：ADOBE_CLIENT_ID, ADOBE_CLIENT_SECRET
nano config/.env
```

### 3️⃣ 启动本地服务

```bash
# 启动所有服务（后端 + 前端）
./docker-start.sh start

# 查看日志
./docker-start.sh logs
```

### 4️⃣ 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8005/api
- **健康检查**: http://localhost:8005/api/health

---

## 🌐 Cloudflare Tunnel 内网穿透（可选）

### 前置条件
- Cloudflare 账户（免费版即可）
- 一个域名在 Cloudflare 托管

### 安装 cloudflared

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# 验证
cloudflared --version
```

### 创建 Tunnel

```bash
# 1. 登录 Cloudflare（会打开浏览器）
cloudflared tunnel login

# 2. 创建 Tunnel
cloudflared tunnel create my-presentation

# 3. 记下 Tunnel ID
```

### 配置 DNS

在 Cloudflare Dashboard 中添加 CNAME 记录：
- `app.yourdomain.com` → `my-presentation.cfargotunnel.com`
- `api.yourdomain.com` → `my-presentation.cfargotunnel.com`

### 配置 Tunnel

编辑 `~/.cloudflared/config.yml`：

```yaml
tunnel: my-presentation
credentials-file: /Users/your-username/.cloudflared/my-presentation.json

ingress:
  - hostname: app.yourdomain.com
    service: http://localhost:5173
  - hostname: api.yourdomain.com
    service: http://localhost:8005
  - service: http_status:404
```

### 启动 Tunnel

```bash
# 在新的终端窗口运行
cloudflared tunnel run my-presentation
```

### 验证连接

```bash
# 测试前端
curl https://app.yourdomain.com

# 测试后端
curl https://api.yourdomain.com/api/health
```

---

## 📋 常用命令

```bash
# 启动服务
./docker-start.sh start

# 停止服务
./docker-start.sh stop

# 查看日志
./docker-start.sh logs

# 重新构建镜像
./docker-start.sh rebuild

# 查看服务状态
./docker-start.sh status

# 进入后端容器
docker compose exec backend bash

# 进入前端容器
docker compose exec frontend sh

# 查看后端日志
docker compose logs backend -f

# 查看前端日志
docker compose logs frontend -f
```

---

## 🔧 故障排查

### 后端无法启动

```bash
# 查看详细日志
docker compose logs backend

# 检查端口是否被占用
lsof -i :8005

# 检查环境变量
docker compose exec backend env | grep OPENROUTER
```

### 前端无法连接后端

```bash
# 测试容器间连接
docker compose exec frontend curl http://backend:8005/api/health

# 检查前端环境变量
docker compose exec frontend env | grep VITE_API_URL
```

### Tunnel 连接失败

```bash
# 调试模式运行
cloudflared tunnel run my-presentation --loglevel debug

# 检查 DNS 解析
nslookup app.yourdomain.com

# 重新认证
cloudflared tunnel login
```

---

## 📚 详细文档

- **完整部署指南**: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)
- **部署检查清单**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **项目结构**: [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

---

## 💡 提示

1. **本地开发**: 使用 `http://localhost:8005/api` 作为后端地址
2. **远程访问**: 使用 `https://api.yourdomain.com` 作为后端地址
3. **日志查看**: 使用 `docker compose logs -f` 实时查看所有日志
4. **数据持久化**: `input` 和 `output` 目录已挂载到容器，本地修改会同步

---

## 🆘 需要帮助？

- 查看 [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) 获取详细说明
- 查看 [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) 进行完整检查
- 运行 `./verify-docker-setup.sh` 验证配置

---

## 🎉 下一步

1. ✅ 验证环境：`./verify-docker-setup.sh`
2. ✅ 配置 API 密钥：编辑 `config/.env`
3. ✅ 启动服务：`./docker-start.sh start`
4. ✅ 访问应用：http://localhost:5173
5. ✅ （可选）设置 Tunnel：按照上面的步骤配置

祝你使用愉快！🚀
