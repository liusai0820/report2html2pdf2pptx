# 🐳 Docker 部署完整指南

你的应用已经完全 Docker 化，可以轻松在本地部署并通过 Cloudflare Tunnel 进行内网穿透。

## 📋 目录

1. [快速开始](#快速开始)
2. [完整部署](#完整部署)
3. [Cloudflare Tunnel](#cloudflare-tunnel)
4. [故障排查](#故障排查)
5. [文件说明](#文件说明)

---

## 🚀 快速开始

### 1. 验证环境（1 分钟）

```bash
./verify-docker-setup.sh
```

这会检查：
- Docker 和 Docker Compose 是否已安装
- 所有配置文件是否完整
- 端口是否可用
- 磁盘空间是否充足

### 2. 配置 API 密钥（2 分钟）

```bash
# 复制环境变量模板
cp config/.env.example config/.env

# 编辑并填入你的 API 密钥
nano config/.env
```

**必需的密钥：**
- `OPENROUTER_API_KEY` - 从 https://openrouter.ai 获取

**可选的密钥：**
- `ADOBE_CLIENT_ID` 和 `ADOBE_CLIENT_SECRET` - 用于 PPTX 生成

### 3. 启动服务（2 分钟）

```bash
# 启动所有服务
./docker-start.sh start

# 等待 3-5 秒，然后访问
```

### 4. 访问应用（1 分钟）

打开浏览器访问：
- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8005/api
- **健康检查**: http://localhost:8005/api/health

---

## 📚 完整部署

### 详细步骤

详见 [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)，包括：
- 详细的环境配置
- 手动 Docker 命令
- 生产部署建议
- 常见问题解决

### 部署检查清单

详见 [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)，包括：
- 本地 Docker 部署检查
- Cloudflare Tunnel 配置检查
- 生产部署建议
- 故障排查指南

---

## 🌐 Cloudflare Tunnel

### 什么是 Cloudflare Tunnel？

Cloudflare Tunnel 允许你在没有公网 IP 的情况下，通过 Cloudflare 的全球网络将本地应用暴露到互联网。

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

| 名称 | 类型 | 内容 |
|------|------|------|
| app | CNAME | my-presentation.cfargotunnel.com |
| api | CNAME | my-presentation.cfargotunnel.com |

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

## 🔧 常用命令

### 启动和停止

```bash
# 启动所有服务
./docker-start.sh start

# 停止所有服务
./docker-start.sh stop

# 查看服务状态
./docker-start.sh status
```

### 日志和调试

```bash
# 查看实时日志
./docker-start.sh logs

# 查看后端日志
docker compose logs backend -f

# 查看前端日志
docker compose logs frontend -f

# 进入后端容器
docker compose exec backend bash

# 进入前端容器
docker compose exec frontend sh
```

### 重新构建

```bash
# 重新构建镜像（修改代码后）
./docker-start.sh rebuild

# 完全清理并重新构建
docker compose down -v
./docker-start.sh rebuild
./docker-start.sh start
```

---

## 🐛 故障排查

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

# 检查浏览器控制台是否有错误
# 打开 http://localhost:5173，按 F12 查看控制台
```

### Tunnel 连接失败

```bash
# 调试模式运行
cloudflared tunnel run my-presentation --loglevel debug

# 检查 DNS 解析
nslookup app.yourdomain.com

# 重新认证
cloudflared tunnel login

# 查看 Tunnel 状态
cloudflared tunnel list
```

### Chrome/Puppeteer 错误

```bash
# 检查 Chrome 是否正确安装
docker compose exec backend google-chrome-stable --version

# 查看详细错误
docker compose logs backend | grep -i chrome
```

---

## 📁 文件说明

### 新增文件

| 文件 | 说明 |
|------|------|
| `docker-compose.yml` | Docker Compose 配置，定义后端和前端服务 |
| `.dockerignore` | Docker 构建忽略文件，优化镜像大小 |
| `docker-start.sh` | 启动脚本，简化常用命令 |
| `verify-docker-setup.sh` | 验证脚本，检查部署配置 |
| `cloudflare-tunnel-config.yml` | Tunnel 配置示例 |
| `frontend/Dockerfile` | 前端 Docker 镜像配置 |
| `QUICK_START.md` | 5 分钟快速开始指南 |
| `DOCKER_DEPLOYMENT.md` | 完整部署指南 |
| `DEPLOYMENT_CHECKLIST.md` | 部署检查清单 |
| `DOCKER_SETUP_SUMMARY.md` | 配置完成总结 |
| `DOCKER_README.md` | 本文件 |

### 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `Dockerfile` | 修复了启动命令和文件复制 |

---

## 🎯 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   Cloudflare Tunnel                      │
│  (可选，用于内网穿透)                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐          ┌────▼────┐
   │ Frontend │          │ Backend  │
   │ (React)  │          │ (FastAPI)│
   │ :5173    │          │ :8005    │
   └──────────┘          └──────────┘
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Docker Network     │
        │  (app-network)      │
        └─────────────────────┘
```

---

## 💾 数据持久化

以下目录已挂载到容器，本地修改会同步：

- `input/` - 输入文件目录
- `output/` - 生成的演示文稿目录
- `config/` - 配置文件目录

---

## 🔐 安全建议

1. **不要提交 `.env` 文件** - 已在 `.gitignore` 中
2. **使用强密码** - 保护你的 API 密钥
3. **定期更新** - 更新 Docker 镜像和依赖
4. **启用 HTTPS** - Cloudflare Tunnel 自动处理
5. **监控日志** - 定期检查错误日志

---

## 📞 获取帮助

1. **查看文档**
   - [QUICK_START.md](./QUICK_START.md) - 快速开始
   - [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - 完整指南
   - [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - 检查清单

2. **运行验证**
   ```bash
   ./verify-docker-setup.sh
   ```

3. **查看日志**
   ```bash
   ./docker-start.sh logs
   ```

4. **查看官方文档**
   - Docker: https://docs.docker.com/
   - Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/

---

## 🎉 完成！

你现在已经拥有：
- ✅ 完全 Docker 化的应用
- ✅ 本地开发环境
- ✅ 内网穿透解决方案
- ✅ 完整的部署文档

祝你使用愉快！🚀

---

**最后更新**: 2025-12-22
**版本**: 1.0
