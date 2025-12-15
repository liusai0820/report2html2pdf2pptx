#!/usr/bin/env python3
"""
AI 演示文稿生成器 - 项目入口

使用方式：
  python run.py                    # 交互式模式
  python run.py document.docx      # 命令行模式
  python run.py --help             # 查看帮助

架构说明：
  - core/: AI 原生的统一架构（推荐）
  - cli.py: 旧版 CLI（兼容）
"""
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 使用新的 AI 原生架构
from main import main

if __name__ == '__main__':
    main()
