#!/bin/bash

# Docker 部署配置验证脚本

# 不使用 set -e，因为我们需要继续执行即使某些检查失败

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Docker 部署配置验证${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

check_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAIL++))
}

check_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 检查 Docker 安装
echo "检查 Docker 环境..."
if command -v docker &> /dev/null; then
    check_pass "Docker 已安装"
else
    check_fail "Docker 未安装"
fi

if docker compose version &> /dev/null || command -v docker-compose &> /dev/null; then
    check_pass "Docker Compose 已安装"
else
    check_fail "Docker Compose 未安装"
fi

echo ""
echo "检查配置文件..."

# 检查必要的文件
files=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    "frontend/Dockerfile"
    "requirements.txt"
    "package.json"
    "frontend/package.json"
    "config/.env.example"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "文件存在: $file"
    else
        check_fail "文件缺失: $file"
    fi
done

echo ""
echo "检查环境变量..."

if [ -f "config/.env" ]; then
    check_pass "config/.env 已存在"
    
    # 检查必要的环境变量
    if grep -q "OPENROUTER_API_KEY" config/.env; then
        if grep -q "OPENROUTER_API_KEY=your_" config/.env; then
            check_warning "OPENROUTER_API_KEY 未配置（使用示例值）"
        else
            check_pass "OPENROUTER_API_KEY 已配置"
        fi
    else
        check_warning "OPENROUTER_API_KEY 未在 .env 中"
    fi
else
    check_warning "config/.env 不存在（需要从 .env.example 复制）"
fi

echo ""
echo "检查 Dockerfile 内容..."

# 检查后端 Dockerfile
if grep -q "FROM python:3.11-slim" Dockerfile; then
    check_pass "后端 Dockerfile 基础镜像正确"
else
    check_fail "后端 Dockerfile 基础镜像不正确"
fi

if grep -q "EXPOSE 8005" Dockerfile; then
    check_pass "后端 Dockerfile 端口配置正确"
else
    check_fail "后端 Dockerfile 端口配置不正确"
fi

if grep -q "CMD \[\"python\", \"src/server.py\"\]" Dockerfile; then
    check_pass "后端 Dockerfile 启动命令正确"
else
    check_fail "后端 Dockerfile 启动命令不正确"
fi

# 检查前端 Dockerfile
if grep -q "FROM node:20-alpine" frontend/Dockerfile; then
    check_pass "前端 Dockerfile 基础镜像正确"
else
    check_fail "前端 Dockerfile 基础镜像不正确"
fi

if grep -q "EXPOSE 5173" frontend/Dockerfile; then
    check_pass "前端 Dockerfile 端口配置正确"
else
    check_fail "前端 Dockerfile 端口配置不正确"
fi

echo ""
echo "检查 docker-compose 配置..."

if grep -q "services:" docker-compose.yml; then
    check_pass "docker-compose.yml 结构正确"
else
    check_fail "docker-compose.yml 结构不正确"
fi

if grep -q "backend:" docker-compose.yml; then
    check_pass "docker-compose.yml 包含后端服务"
else
    check_fail "docker-compose.yml 缺少后端服务"
fi

if grep -q "frontend:" docker-compose.yml; then
    check_pass "docker-compose.yml 包含前端服务"
else
    check_fail "docker-compose.yml 缺少前端服务"
fi

if grep -q "8005:8005" docker-compose.yml; then
    check_pass "docker-compose.yml 后端端口映射正确"
else
    check_fail "docker-compose.yml 后端端口映射不正确"
fi

if grep -q "5173:5173" docker-compose.yml; then
    check_pass "docker-compose.yml 前端端口映射正确"
else
    check_fail "docker-compose.yml 前端端口映射不正确"
fi

echo ""
echo "检查端口可用性..."

# 检查端口是否被占用
if lsof -Pi :8005 -sTCP:LISTEN -t >/dev/null 2>&1; then
    check_warning "端口 8005 已被占用"
else
    check_pass "端口 8005 可用"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    check_warning "端口 5173 已被占用"
else
    check_pass "端口 5173 可用"
fi

echo ""
echo "检查磁盘空间..."

# 检查磁盘空间（需要至少 5GB）
available_space=$(df . | awk 'NR==2 {print $4}')
if [ "$available_space" -gt 5242880 ]; then  # 5GB in KB
    check_pass "磁盘空间充足 ($(numfmt --to=iec $((available_space * 1024)) 2>/dev/null || echo "$available_space KB"))"
else
    check_warning "磁盘空间可能不足 ($(numfmt --to=iec $((available_space * 1024)) 2>/dev/null || echo "$available_space KB"))"
fi

echo ""
echo "========================================${NC}"
echo -e "验证结果: ${GREEN}通过 $PASS${NC} / ${RED}失败 $FAIL${NC}"
echo "========================================${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 所有检查通过！可以开始部署${NC}"
    echo ""
    echo "下一步："
    echo "  1. 编辑 config/.env 填入 API 密钥"
    echo "  2. 运行: ./docker-start.sh start"
    echo "  3. 访问: http://localhost:5173"
    exit 0
else
    echo ""
    echo -e "${RED}✗ 存在 $FAIL 个检查失败，请修复后重试${NC}"
    exit 1
fi
