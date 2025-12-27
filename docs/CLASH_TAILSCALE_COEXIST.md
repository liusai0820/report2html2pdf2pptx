# Clash Verge + Tailscale 共存配置

## 🔧 配置 Clash 绕过 Tailscale

### 方法 1：在 Clash 配置中添加规则

打开 Clash Verge：

1. 点击 "配置" 或 "Profiles"
2. 编辑当前使用的配置文件
3. 在 `rules` 部分的**最前面**添加：

```yaml
rules:
  # ===== Tailscale 直连规则（必须放在最前面）=====
  - IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
  - IP-CIDR,fd7a:115c:a1e0::/48,DIRECT,no-resolve

  # ===== 本地网络直连 =====
  - IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
  - IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve

  # ... 其他规则 ...
```

### 方法 2：使用 TUN 配置中的 bypass

如果 Clash 配置有 `tun` 部分，添加：

```yaml
tun:
  enable: true
  stack: system
  dns-hijack:
    - any:53
  auto-route: true
  auto-detect-interface: true

  # 重点：绕过 Tailscale 网段
  inet4-route-exclude-address:
    - 100.64.0.0/10

  inet6-route-exclude-address:
    - fd7a:115c:a1e0::/48
```

### 方法 3：GUI 设置（如果支持）

在 Clash Verge 设置中：

1. 设置 → TUN 模式
2. 找到 "绕过域名/IP" 或 "Bypass"
3. 添加：
   ```
   100.64.0.0/10
   fd7a:115c:a1e0::/48
   ```

---

## 🚀 启动 Tailscale

配置完 Clash 后，启动 Tailscale：

```bash
# 1. 启动 Tailscale
sudo tailscale up --accept-routes --accept-dns=false --operator=$USER

# 2. 获取登录链接（如果是首次）
# 复制输出的 URL 到浏览器完成认证

# 3. 验证连接
tailscale status

# 4. 获取 Tailscale IP
tailscale ip -4
```

---

## 🧪 测试共存

### 测试 1：Tailscale 可以访问

```bash
# 获取你的 Tailscale IP
tailscale ip -4

# 从另一台设备 ping 这个 IP
ping <your-tailscale-ip>
```

### 测试 2：Clash 代理仍然工作

```bash
# 访问需要代理的网站
curl -I https://www.google.com

# 查看路由（应该看到 Clash 和 Tailscale 的路由共存）
netstat -rn | grep -E "utun8|utun"
```

### 测试 3：本地服务通过 Tailscale 访问

```bash
# 从外网通过 Tailscale IP 访问本地服务
curl http://<tailscale-ip>:8005/api/health
```

---

## 🛠️ 故障排除

### 问题 1：Tailscale 连接后 Clash 不工作

**原因**：路由冲突，Tailscale 的路由优先级更高

**解决**：

```bash
# 重启 Clash Verge
pkill -f clash-verge
open "/Applications/Clash Verge.app"

# 或者调整 Tailscale 启动参数
sudo tailscale down
sudo tailscale up --accept-routes=false --accept-dns=false
```

### 问题 2：Tailscale 连接失败

**原因**：Clash TUN 模式劫持了所有流量

**解决**：

```bash
# 临时关闭 Clash 测试
pkill -f clash-verge

# 启动 Tailscale
sudo tailscale up

# 成功后重新打开 Clash
open "/Applications/Clash Verge.app"
```

### 问题 3：DNS 解析异常

**原因**：Clash 和 Tailscale 都想控制 DNS

**解决**：

```bash
# 禁用 Tailscale 的 DNS 管理
sudo tailscale up --accept-dns=false

# 在 Clash 中确保 DNS 设置正确
```

---

## 📊 验证配置

运行以下命令检查网络状态：

```bash
# 1. 查看所有 TUN 设备
ifconfig | grep -A 3 utun

# 2. 查看路由表
netstat -rn | head -50

# 3. 检查 Tailscale 状态
tailscale status

# 4. 检查 Clash 进程
ps aux | grep clash

# 5. 测试连通性
ping 100.100.100.100  # Tailscale DERP 服务器
curl https://www.google.com  # 测试 Clash 代理
```

---

## 💡 最佳实践

1. **优先级排序**：

   - 本地网络（192.168.x.x） → DIRECT
   - Tailscale 网络（100.64.x.x） → DIRECT
   - 其他流量 → PROXY

2. **DNS 管理**：

   - 使用 Clash 的 DNS（fake-ip 模式）
   - Tailscale 不接管 DNS（`--accept-dns=false`）

3. **开机自启动**：
   - Clash Verge：系统偏好设置 → 登录项
   - Tailscale：自动配置（macOS LaunchDaemon）

---

## 🎯 推荐配置（完整示例）

```yaml
# Clash 配置示例
mixed-port: 7890
allow-lan: true
mode: rule
log-level: info

tun:
  enable: true
  stack: system
  dns-hijack:
    - any:53
  auto-route: true
  auto-detect-interface: true
  inet4-route-exclude-address:
    - 100.64.0.0/10 # Tailscale
    - 192.168.0.0/16 # 本地网络
    - 10.0.0.0/8

dns:
  enable: true
  listen: 0.0.0.0:53
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  nameserver:
    - 223.5.5.5
    - 114.114.114.114

rules:
  # Tailscale 直连
  - IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
  - IP-CIDR,fd7a:115c:a1e0::/48,DIRECT,no-resolve

  # 本地网络直连
  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT
  - IP-CIDR,172.16.0.0/12,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT

  # 其他规则...
  - GEOIP,CN,DIRECT
  - MATCH,PROXY
```
