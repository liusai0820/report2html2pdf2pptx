#!/bin/bash

# Docker 快速启动脚本
# 用法: ./docker-start.sh [start|stop|logs|rebuild]

set -e

COMMAND=${1:-start}
COMPOSE_FILE="docker-compose.yml"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  AI Presentation Generator - Docker${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    
    print_success "Docker 环境检查通过"
}

check_env() {
    if [ ! -f "config/.env" ]; then
        print_warning "config/.env 不存在，复制示例文件..."
        cp config/.env.example config/.env
        print_warning "请编辑 config/.env 填入你的 API 密钥"
    fi
}

start_services() {
    print_header
    check_docker
    check_env
    
    print_info "正在启动服务..."
    docker compose -f "$COMPOSE_FILE" up -d
    
    print_success "服务启动中..."
    sleep 3
    
    # 检查服务状态
    if docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "服务已启动"
        echo ""
        echo -e "${GREEN}访问地址：${NC}"
        echo -e "  前端: ${BLUE}http://localhost:5173${NC}"
        echo -e "  后端: ${BLUE}http://localhost:8005/api${NC}"
        echo -e "  健康检查: ${BLUE}http://localhost:8005/api/health${NC}"
        echo ""
        print_info "查看日志: docker compose logs -f"
        print_info "停止服务: ./docker-start.sh stop"
    else
        print_error "服务启动失败"
        docker compose -f "$COMPOSE_FILE" logs
        exit 1
    fi
}

stop_services() {
    print_header
    print_info "正在停止服务..."
    docker compose -f "$COMPOSE_FILE" down
    print_success "服务已停止"
}

show_logs() {
    print_header
    print_info "显示实时日志 (按 Ctrl+C 退出)..."
    docker compose -f "$COMPOSE_FILE" logs -f
}

rebuild_services() {
    print_header
    check_docker
    
    print_info "正在重新构建镜像..."
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    print_success "镜像构建完成"
    print_info "启动服务: ./docker-start.sh start"
}

status_services() {
    print_header
    docker compose -f "$COMPOSE_FILE" ps
}

case "$COMMAND" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild_services
        ;;
    status)
        status_services
        ;;
    *)
        echo "用法: $0 {start|stop|logs|rebuild|status}"
        echo ""
        echo "命令说明："
        echo "  start    - 启动所有服务"
        echo "  stop     - 停止所有服务"
        echo "  logs     - 显示实时日志"
        echo "  rebuild  - 重新构建镜像"
        echo "  status   - 显示服务状态"
        exit 1
        ;;
esac
