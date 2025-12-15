# AI 演示文稿生成器

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node Version](https://img.shields.io/badge/node-14.0+-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

基于 OpenRouter + Claude 的智能演示文稿生成系统，支持从文档自动生成专业的 HTML/PDF/PPTX 演示文稿。

## 特性

- 🤖 AI 驱动的内容生成和排版
- 📄 支持多种输入格式（JSON、Markdown、DOCX）
- 🎨 专业的商务风格模板
- 📊 自动生成数据可视化图表
- 🔄 PDF 转 PPTX 功能
- ⚡ 并发处理，高效生成

## 项目结构

```
.
├── src/                    # 核心代码
│   ├── cli.py             # 命令行入口
│   ├── config.py          # 配置管理
│   ├── ai_client.py       # AI 客户端
│   ├── slide_generator.py # 幻灯片生成器
│   ├── document_parser.py # 文档解析器
│   ├── pdf_generator.py   # PDF 生成器
│   ├── adobe_integration.py # Adobe PDF Services
│   └── templates/         # HTML 模板
├── config/                # 配置文件
│   ├── .env.example       # 环境变量示例
│   └── pdfservices-api-credentials.json # Adobe 凭证
├── input/                 # 输入文件目录
├── output/                # 输出文件目录
├── run.py                 # 项目启动脚本
├── requirements.txt       # Python 依赖
└── package.json          # Node.js 依赖

```

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖（用于 PDF 生成）
npm install
```

### 2. 配置 API 密钥

复制配置示例并填入你的 API 密钥：

```bash
cp config/.env.example config/.env
```

编辑 `config/.env`：

```env
OPENROUTER_API_KEY=your_api_key_here
ADOBE_CLIENT_ID=your_adobe_client_id
ADOBE_CLIENT_SECRET=your_adobe_client_secret
```

### 3. 运行

```bash
# 交互式模式（推荐）
python run.py

# 命令行模式 - 处理单个文档
python run.py input/document.json

# 批量处理所有文档
python run.py --batch

# PDF 转 PPTX
python run.py --pdf-to-pptx input.pdf -o output.pptx
```

## 使用指南

### 输入格式

支持三种输入格式：

1. **JSON 格式**：结构化的演示文稿数据
2. **Markdown 格式**：简单的文本文档
3. **DOCX 格式**：Word 文档

将输入文件放入 `input/` 目录即可。

### 输出文件

生成的文件会保存在 `output/文档名_时间戳/` 目录下：

- `presentation.html` - 完整的 HTML 演示文稿
- `文档名_日期.pdf` - PDF 版本
- `文档名_日期.pptx` - PowerPoint 版本
- `pages/` - 独立的 HTML 页面

### 高级选项

```bash
# 指定输出目录
python run.py document.json -o custom_output

# 跳过 PDF 生成
python run.py document.json --skip-pdf

# 批量 PDF 转 PPTX
python run.py --batch-pdf-to-pptx pdf_folder -o output_folder
```

## 配置说明

### 环境变量

在 `config/.env` 中配置：

```env
# OpenRouter API
OPENROUTER_API_KEY=sk-or-xxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-haiku

# 生成配置
MAX_CONCURRENT_REQUESTS=5
TIMEOUT_SECONDS=180
MAX_RETRIES=3
TEMPERATURE=0.7

# Adobe PDF Services
ADOBE_CLIENT_ID=xxx
ADOBE_CLIENT_SECRET=xxx
```

### Adobe PDF Services

如需使用 PDF 转 PPTX 功能，需要：

1. 注册 [Adobe PDF Services](https://developer.adobe.com/document-services/)
2. 下载凭证文件
3. 将凭证文件保存为 `config/pdfservices-api-credentials.json`

## 开发

### 项目架构

- **cli.py**: 命令行界面和用户交互
- **config.py**: 集中管理所有配置
- **ai_client.py**: 封装 AI API 调用
- **slide_generator.py**: 核心生成逻辑
- **document_parser.py**: 解析各种文档格式
- **template_merger.py**: HTML 模板合并
- **pdf_generator.py**: PDF 生成
- **adobe_integration.py**: Adobe API 集成

### 代码规范

- 使用 Python 3.8+
- 遵循 PEP 8 代码风格
- 使用类型提示
- 编写清晰的文档字符串

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 检查 `config/.env` 文件是否正确配置
   - 确认 API 密钥有效且有足够额度

2. **PDF 生成失败**
   - 确保已安装 Node.js 和 puppeteer
   - 检查系统是否有足够的内存

3. **PPTX 转换失败**
   - 确认 Adobe 凭证文件路径正确
   - 检查 Adobe API 配额

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
