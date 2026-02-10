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
    local max_retries=10
    local retry_delay=10
    local count=0

    echo "正在探测: $url"

    while [ $count -lt $max_retries ]; do
        # 获取 HTTP 状态码
        status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

        if [ "$status" == "200" ]; then
            echo -e "\033[0;32m[ 成功 ]\033[0m 服务已激活 (Status: $status)"
            return 0
        elif [ "$status" == "503" ] || [ "$status" == "502" ] || [ "$status" == "000" ]; then
            # 503/502 通常表示正在启动中 (Render Cold Start)
            echo -e "\033[0;33m[ 启动中 ]\033[0m 服务正在唤醒... ($status)"
            echo "等待 ${retry_delay} 秒后重试... ($((count+1))/$max_retries)"
            sleep $retry_delay
            count=$((count + 1))
        else
            echo -e "\033[0;31m[ 错误 ]\033[0m 发生异常 (Status: $status)"
            # 其他错误也重试，以防短暂网络抖动
            sleep $retry_delay
            count=$((count + 1))
        fi
    done

    echo -e "\033[0;31m[ 失败 ]\033[0m 超过最大重试次数，服务未响应。"
    return 1
}

# 执行一次探测
ping_url "$BACKEND_URL"
ping_url "$FRONTEND_URL"

echo "----------------------------------------------------"
echo "提示: 已在 .github/workflows/keep_awake.yml 配置自动保活"
echo "只需要将代码推送到 GitHub，即可实现每 10 分钟自动 Ping 探测。"
