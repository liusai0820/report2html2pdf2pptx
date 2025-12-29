#!/bin/bash
# Cloudflare Tunnel 健康检查脚本 v2
# 用于定期检查 Tunnel 连接状态并在断开时自动重启

LOG_FILE="/Users/qibaoba/VibeCoding/pptx/logs/tunnel_health.log"
CONTAINER_NAME="cloudflared_tunnel"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# 检查容器是否在运行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "ERROR: Container ${CONTAINER_NAME} is not running. Attempting restart..."
    docker start ${CONTAINER_NAME}
    if [ $? -eq 0 ]; then
        log "SUCCESS: Container restarted successfully"
    else
        log "FAILED: Could not restart container"
    fi
    exit 1
fi

# 检查最近的连接日志
LAST_LOG=$(docker logs ${CONTAINER_NAME} --tail 5 2>&1)

# 检查是否有成功连接的记录
if echo "$LAST_LOG" | grep -q "Registered tunnel connection"; then
    log "OK: Tunnel is connected"
    exit 0
fi

# 检查是否有严重的连接错误
if echo "$LAST_LOG" | grep -q "no free edge addresses\|Connection terminated\|connection refused"; then
    log "WARNING: Connection issues detected. Restarting container..."
    docker restart ${CONTAINER_NAME}
    sleep 10
    
    # 验证重启后是否恢复
    NEW_LOG=$(docker logs ${CONTAINER_NAME} --tail 3 2>&1)
    if echo "$NEW_LOG" | grep -q "Registered tunnel connection"; then
        log "SUCCESS: Tunnel recovered after restart"
    else
        log "WARNING: Tunnel may still have issues after restart"
    fi
fi

exit 0
