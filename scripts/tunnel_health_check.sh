#!/bin/bash
# Cloudflare Tunnel 健康检查脚本
# 每隔 N 分钟由 cron 调用，检测 ppt.gwy.life 是否可访问
# 如果连续失败，则重启 cloudflared 进程

HEALTH_URL="https://ppt.gwy.life/api/health"
LAUNCHD_LABEL="com.cloudflare.tunnel.ppt"
FAIL_COUNT_FILE="/tmp/tunnel_fail_count"
MAX_FAILURES=2  # 连续失败 2 次后重启

# 初始化失败计数
if [ ! -f "$FAIL_COUNT_FILE" ]; then
    echo "0" > "$FAIL_COUNT_FILE"
fi

# 发送请求，超时 10 秒
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    # 成功，重置计数器
    echo "0" > "$FAIL_COUNT_FILE"
    echo "[$(date)] ✅ Tunnel OK (HTTP $HTTP_CODE)"
else
    # 失败，增加计数
    CURRENT_FAILS=$(cat "$FAIL_COUNT_FILE")
    NEW_FAILS=$((CURRENT_FAILS + 1))
    echo "$NEW_FAILS" > "$FAIL_COUNT_FILE"
    
    echo "[$(date)] ❌ Tunnel FAIL (HTTP $HTTP_CODE), count: $NEW_FAILS/$MAX_FAILURES"
    
    if [ "$NEW_FAILS" -ge "$MAX_FAILURES" ]; then
        echo "[$(date)] 🔄 Restarting cloudflared tunnel..."
        
        # 方法1：杀掉旧进程（会有多余进程）
        pkill -f "cloudflared tunnel.*ppt-gwy-life"
        
        # 方法2：使用 launchctl 重启（更可靠）
        launchctl kickstart -k "gui/$(id -u)/$LAUNCHD_LABEL" 2>/dev/null || {
            # 如果 launchctl 失败，手动重启
            nohup /opt/homebrew/bin/cloudflared tunnel --config /Users/qibaoba/.cloudflared/config-ppt.yml run ppt-gwy-life > /tmp/cloudflared-ppt.log 2>&1 &
        }
        
        # 重置计数器
        echo "0" > "$FAIL_COUNT_FILE"
        
        # 等待几秒让 tunnel 重新连接
        sleep 10
        
        # 再次检查
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null)
        echo "[$(date)] 📊 After restart: HTTP $HTTP_CODE"
    fi
fi
