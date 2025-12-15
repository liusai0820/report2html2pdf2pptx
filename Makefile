.PHONY: help install run clean test

help:
	@echo "AI 演示文稿生成器 - 可用命令："
	@echo ""
	@echo "  make install    - 安装所有依赖"
	@echo "  make run        - 启动交互式模式"
	@echo "  make clean      - 清理输出文件"
	@echo "  make test       - 运行测试"
	@echo ""

install:
	@echo "📦 安装 Python 依赖..."
	pip install -r requirements.txt
	@echo "📦 安装 Node.js 依赖..."
	npm install
	@echo "✅ 依赖安装完成"

run:
	@python run.py

clean:
	@echo "🧹 清理输出文件..."
	rm -rf output/*
	rm -rf generated-slides/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成"

test:
	@echo "🧪 运行测试..."
	@python -m pytest tests/ -v
