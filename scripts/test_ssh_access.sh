#!/bin/bash
# SSH 远程访问测试脚本

echo "🔍 测试 SSH 端点是否配置成功..."
echo ""

# 测试 DNS 解析
echo "1️⃣ DNS 解析测试:"
nslookup ssh.ppt.gwy.life
echo ""

# 测试 SSH 端口
echo "2️⃣ SSH 连接测试:"
echo "尝试连接到 ssh.ppt.gwy.life..."
timeout 5 nc -zv ssh.ppt.gwy.life 22 2>&1 || echo "如果显示超时，可能需要等待 DNS 生效"
echo ""

echo "✅ 如果上面显示连接成功，您就可以使用以下命令远程连接："
echo ""
echo "   ssh qibaoba@ssh.ppt.gwy.life"
echo ""
echo "💡 从手机连接（使用 Termius 或 Blink Shell）："
echo "   主机: ssh.ppt.gwy.life"
echo "   用户: qibaoba"
echo "   端口: 22"
