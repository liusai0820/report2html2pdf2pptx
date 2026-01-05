#!/bin/bash

# =================================================================
# Render Keep-Awake Script
# 用于规避 Render 免费版 50s 冷启动问题的脚本
# =================================================================

# 替换为你的真实后端地址
BACKEND_URL="https://slidecraft-backend.onrender.com/api/health"
FRONTEND_URL="https://slidecraft-frontend.onrender.com"

echo "----------------------------------------------------"
echo "Render 应用保活脚本启动 [$(date)]"
echo "----------------------------------------------------"

ping_url() {
    local url=$1
    echo -n "正在请求 $url ... "
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    if [ "$status" == "200" ]; then
        echo -e "\033[0;32m[ 成功 $status ]\033[0m"
    else
        echo -e "\033[0;31m[ 异常 $status ]\033[0m"
    fi
}

# 执行一次探测
ping_url "$BACKEND_URL"
ping_url "$FRONTEND_URL"

echo "----------------------------------------------------"
echo "提示: 已在 .github/workflows/keep_awake.yml 配置自动保活"
echo "只需要将代码推送到 GitHub，即可实现每 10 分钟自动 Ping 探测。"
