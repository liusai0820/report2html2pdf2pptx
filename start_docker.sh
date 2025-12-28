#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 正在准备启动 Docker 环境...${NC}"

# 1. 检查环境变量文件
if [ ! -f config/.env ]; then
    echo -e "${RED}❌ 错误: config/.env 文件不存在！请先配置该文件。${NC}"
    exit 1
fi

# 2. 导出环境变量，供 docker-compose 使用
echo -e "${GREEN}📦 加载环境变量...${NC}"
set -a
source config/.env
set +a

# 2.1 智能设置 API 地址
if [ -n "$TUNNEL_TOKEN" ]; then
    # 如果有 Tunnel Token，使用相对路径 (由 Tunnel 处理路由)
    export VITE_API_URL=${VITE_API_URL:-/api}
    echo -e "${GREEN}🌍 检测到 Tunnel Token，使用相对 API 路径: $VITE_API_URL${NC}"
else
    # 否则使用本地绝对路径
    export VITE_API_URL=${VITE_API_URL:-http://localhost:8005/api}
    echo -e "${YELLOW}🏠 未检测到 Tunnel Token，使用本地 API 地址: $VITE_API_URL${NC}"
fi

# 3. 停止本地可能占用端口的服务
echo -e "${YELLOW}🧹 清理并在本地停止端口占用 (8005, 5173)...${NC}"
lsof -t -i:8005 | xargs kill -9 2>/dev/null
lsof -t -i:5173 | xargs kill -9 2>/dev/null

# 4. 启动 Docker Compose
echo -e "${GREEN}🐳 启动 Docker Compose (构建模式)...${NC}"
docker-compose up --build -d

# 5. 检查状态
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo -e "   后端 API: http://localhost:8005"
    echo -e "   前端页面: http://localhost:5173"
    echo -e "${YELLOW}正在查看日志 (按 Ctrl+C 退出日志查看)...${NC}"
    docker-compose logs -f
else
    echo -e "${RED}❌ Docker 启动失败。${NC}"
fi
