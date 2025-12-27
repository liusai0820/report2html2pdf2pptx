# Tailscale 远程访问配置指南

## 🚀 快速开始

### 1. 登录 Tailscale

打开终端执行：

```bash
open "https://tailscale.com/start"
```

或者使用命令行登录：

```bash
sudo tailscale up --accept-routes --accept-dns=false --operator=$USER
```

这会输出一个登录链接，复制到浏览器中完成认证。

### 2. 验证连接状态

```bash
tailscale status
```

应该显示您的设备和 IP 地址。

### 3. 获取您的 Tailscale IP

```bash
tailscale ip -4
```

记下这个 IP 地址（例如：100.x.x.x），这是您在任何地方访问这台 Mac 的内网 IP。

---

## 🔧 远程访问方式

### 方式 1：SSH 访问（推荐）

#### 在 Mac 上启用远程登录：

```bash
sudo systemsetup -setremotelogin on
```

#### 从其他设备连接：

```bash
ssh qibaoba@<tailscale-ip>
# 例如: ssh qibaoba@100.64.1.2
```

### 方式 2：VNC 屏幕共享

#### 在 Mac 上启用屏幕共享：

```bash
sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart \
  -activate -configure -access -on \
  -configure -allowAccessFor -allUsers \
  -configure -restart -agent -privs -all
```

#### 从其他设备连接：

- **从 Mac**：Finder → 前往 → 连接服务器 → `vnc://<tailscale-ip>:5900`
- **从 Windows**：使用 VNC Viewer 连接到 `<tailscale-ip>:5900`
- **从 iPhone/iPad**：安装 VNC Viewer app

### 方式 3：文件传输（Taildrop）

Tailscale 内置文件传输功能：

```bash
# 从其他设备发送文件
tailscale file cp myfile.txt <your-mac-hostname>:

# 在 Mac 上接收文件（文件在 ~/Downloads/Taildrop）
open ~/Downloads/Taildrop
```

---

## 📱 移动端访问

### iOS/Android 安装 Tailscale App

1. 下载 Tailscale app
2. 使用同一账号登录
3. 即可在手机上看到您的 Mac 设备
4. 可以使用 Termius 等 SSH 客户端连接

---

## 🛡️ 安全建议

### 1. 启用 MagicDNS（更易记的域名）

```bash
# 在 Tailscale admin console 启用 MagicDNS
# 然后可以用主机名访问，例如：
ssh qibaoba@mac-studio
```

### 2. 设置 ACL（访问控制列表）

在 Tailscale admin console 中配置，限制哪些设备可以访问哪些端口。

### 3. 启用 Key expiry（密钥过期）

定期轮换设备密钥，增强安全性。

---

## 🔄 保持 Tailscale 始终运行

Tailscale 应该已经配置为开机自动启动（通过系统偏好设置）。

验证：

```bash
ps aux | grep tailscaled
```

如果没有运行，可以手动启动：

```bash
sudo tailscaled install-system-daemon
```

---

## 📊 常用命令

```bash
# 查看连接状态
tailscale status

# 查看 IP 地址
tailscale ip -4

# 查看网络路由
tailscale status --peers

# 临时断开连接
tailscale down

# 重新连接
tailscale up

# 完全登出
tailscale logout
```

---

## 🎯 实际使用场景

### 场景 1：在咖啡厅远程管理服务器

```bash
# 从你的笔记本电脑连接到家里的 Mac Studio
ssh qibaoba@<mac-tailscale-ip>

# 检查 Docker 容器
docker ps

# 查看日志
tail -f ~/VibeCoding/pptx/logs/tunnel_health.log
```

### 场景 2：从手机查看项目状态

使用 Termius 或 Blink Shell：

```bash
ssh qibaoba@<mac-tailscale-ip>
cd ~/VibeCoding/pptx
git status
docker compose ps
```

### 场景 3：访问本地服务

```bash
# 在外网通过 Tailscale 访问本地的服务
# 例如访问 Docker 内的应用
curl http://<mac-tailscale-ip>:5173
curl http://<mac-tailscale-ip>:8005/api/health
```

---

## ⚡ 进阶技巧

### 1. 配置 Exit Node（全局代理）

可以将 Mac 设置为出口节点，从任何地方使用 Mac 的网络：

```bash
sudo tailscale up --advertise-exit-node
```

### 2. 子网路由（访问局域网其他设备）

```bash
sudo tailscale up --advertise-routes=192.168.1.0/24
```

### 3. 配置 Funnel（公开服务到互联网）

如果想临时公开某个服务：

```bash
tailscale funnel 8005
```

---

## 🔍 故障排除

### 问题：无法连接

```bash
# 检查 Tailscale 守护进程
ps aux | grep tailscaled

# 重启 Tailscale
sudo launchctl stop com.tailscale.tailscaled
sudo launchctl start com.tailscale.tailscaled
```

### 问题：连接很慢

```bash
# 检查是否使用了中继（DERP）
tailscale netcheck

# 如果使用了中继，可能需要配置防火墙允许直连
```

---

## 📚 更多资源

- [Tailscale 官方文档](https://tailscale.com/kb/)
- [macOS 快速开始](https://tailscale.com/kb/1016/install-mac)
- [SSH 配置指南](https://tailscale.com/kb/1193/tailscale-ssh/)

---

**提示**：第一次配置完成后，建议记录下您的 Tailscale IP 和主机名，方便以后使用。
