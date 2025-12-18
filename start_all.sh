#!/bin/bash

# SlideCraft.ai 一键启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}      SlideCraft.ai 启动器          ${NC}"
echo -e "${BLUE}=======================================${NC}"

# 1. 检查 Python 环境
echo -e "${YELLOW}[1/3] 检查后端环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 2. 检查 Node.js 环境
echo -e "${YELLOW}[2/3] 检查前端环境...${NC}"
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到 npm"
    exit 1
fi

# 3. 启动后端
echo -e "${GREEN}[3/3] 正在启动服务...${NC}"

# 清理旧进程函数
cleanup() {
    echo -e "\n${YELLOW}正在停止所有服务...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# 捕获 Ctrl+C
trap cleanup SIGINT SIGTERM

# 启动后端 (端口 8005)
echo -e "${BLUE}-> 启动后端服务器 (http://localhost:8005)${NC}"
python3 src/server.py &
BACKEND_PID=$!

# 等待后端就绪 (可选)
sleep 2

# 启动前端 (端口 5173)
echo -e "${BLUE}-> 启动前端开发服务器 (http://localhost:5173)${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  🚀 服务已成功启动！${NC}"
echo -e "${GREEN}  - 前端: http://localhost:5173${NC}"
echo -e "${GREEN}  - 后端: http://localhost:8005${NC}"
echo -e "${GREEN}  按 Ctrl+C 停止所有服务${NC}"
echo -e "${GREEN}=======================================${NC}"

# 保持脚本运行
wait
