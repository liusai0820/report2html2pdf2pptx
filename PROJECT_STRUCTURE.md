# 项目结构说明

## 📁 目录结构

```
ai-presentation-generator/
│
├── 📂 src/                          # 核心源代码
│   ├── __init__.py                  # 模块初始化
│   ├── cli.py                       # 命令行界面 (入口)
│   ├── config.py                    # 配置管理
│   ├── ai_client.py                 # AI API 客户端
│   ├── slide_generator.py           # 幻灯片生成器 (核心)
│   ├── document_parser.py           # 文档解析器
│   ├── template_merger.py           # 模板合并器
│   ├── pdf_generator.py             # PDF 生成器
│   ├── adobe_integration.py         # Adobe PDF Services 集成
│   ├── adobe_pdf_to_pptx.py         # PDF 转 PPTX
│   ├── context_manager.py           # 上下文管理器
│   ├── font_fixer.py                # 字体修复工具
│   ├── convert_to_pdf.js            # Node.js PDF 转换脚本
│   └── templates/                   # HTML 模板
│       ├── index.html
│       └── index_inline.html
│
├── 📂 config/                       # 配置文件目录
│   ├── .env.example                 # 环境变量示例
│   ├── .env                         # 环境变量 (需自行创建)
│   ├── .gitignore                   # 配置忽略规则
│   └── pdfservices-api-credentials.json  # Adobe 凭证
│
├── 📂 docs/                         # 文档
│   ├── API.md                       # API 文档
│   ├── ARCHITECTURE.md              # 架构设计
│   ├── CONTRIBUTING.md              # 贡献指南
│   └── QUICKSTART.md                # 快速入门
│
├── 📂 tests/                        # 测试
│   ├── __init__.py
│   └── test_config.py               # 配置测试
│
├── 📂 input/                        # 输入文件目录
│   └── (放置待处理的文档)
│
├── 📂 output/                       # 输出文件目录
│   └── (生成的演示文稿)
│
├── 📄 run.py                        # 项目启动脚本 ⭐
├── 📄 setup.py                      # Python 包配置
├── 📄 requirements.txt              # Python 依赖
├── 📄 package.json                  # Node.js 依赖
├── 📄 Makefile                      # 便捷命令
├── 📄 .gitignore                    # Git 忽略规则
├── 📄 README.md                     # 项目说明
├── 📄 CHANGELOG.md                  # 更新日志
├── 📄 PROJECT_STRUCTURE.md          # 本文件
└── 📄 promptv4.md                   # AI 提示词模板

```

## 🎯 核心模块说明

### 用户界面层

| 文件 | 职责 | 关键功能 |
|------|------|----------|
| `run.py` | 项目入口 | 启动 CLI，设置 Python 路径 |
| `src/cli.py` | 命令行界面 | 参数解析、交互式选择、进度显示 |

### 业务逻辑层

| 文件 | 职责 | 关键功能 |
|------|------|----------|
| `src/slide_generator.py` | 核心生成器 | 流程编排、并发控制、错误处理 |
| `src/document_parser.py` | 文档解析 | 支持 JSON/MD/DOCX 格式 |
| `src/template_merger.py` | 模板合并 | HTML 模板注入、页面合并 |
| `src/pdf_generator.py` | PDF 生成 | HTML 转 PDF、页面渲染 |
| `src/adobe_integration.py` | Adobe 集成 | PDF 转 PPTX、批量处理 |
| `src/context_manager.py` | 上下文管理 | 智能上下文注入、内容检索 |

### 基础设施层

| 文件 | 职责 | 关键功能 |
|------|------|----------|
| `src/ai_client.py` | AI 客户端 | OpenRouter API 封装、重试机制 |
| `src/config.py` | 配置管理 | 环境变量加载、配置集中管理 |
| `src/font_fixer.py` | 字体修复 | PPTX 字体处理 |
| `src/convert_to_pdf.js` | PDF 转换 | Puppeteer 渲染引擎 |

## 🔄 数据流

```
1. 用户输入
   ↓
2. CLI 解析参数
   ↓
3. DocumentParser 解析文档
   ↓
4. SlideGenerator 生成大纲
   ↓
5. AIClient 并发生成内容
   ↓
6. TemplateMerger 合并模板
   ↓
7. 输出 HTML
   ↓
8. PDFGenerator 转换 PDF
   ↓
9. AdobeIntegration 转换 PPTX
   ↓
10. 完成
```

## 📦 依赖关系

### Python 依赖
- `openai`: AI API 调用
- `python-dotenv`: 环境变量管理
- `rich`: 美观的终端输出
- `python-docx`: Word 文档解析
- `PyPDF2`: PDF 处理
- `adobe-pdfservices-sdk`: Adobe API

### Node.js 依赖
- `puppeteer`: 无头浏览器，用于 HTML 转 PDF

## 🚀 启动流程

1. **用户执行**: `python run.py`
2. **run.py**: 设置 Python 路径，导入 `src.cli`
3. **cli.py**: 解析参数，启动交互式界面
4. **slide_generator.py**: 执行生成流程
5. **输出结果**: 保存到 `output/` 目录

## ⚙️ 配置系统

### 配置加载顺序
1. `config/.env` - 环境变量
2. `src/config.py` - 默认配置
3. 命令行参数 - 运行时覆盖

### 关键配置项
```env
# AI 配置
OPENROUTER_API_KEY=xxx
DEFAULT_MODEL=anthropic/claude-3.5-haiku

# 性能配置
MAX_CONCURRENT_REQUESTS=5
TIMEOUT_SECONDS=180
MAX_RETRIES=3

# Adobe 配置
ADOBE_CLIENT_ID=xxx
ADOBE_CLIENT_SECRET=xxx
```

## 🧪 测试

```bash
# 运行配置测试
python tests/test_config.py

# 运行所有测试
python -m pytest tests/
```

## 📝 开发规范

### 代码组织
- 每个模块单一职责
- 使用类型提示
- 编写文档字符串
- 保持函数简洁

### 命名规范
- 文件名: `snake_case.py`
- 类名: `PascalCase`
- 函数名: `snake_case()`
- 常量: `UPPER_CASE`

### 导入规范
```python
# 标准库
import os
from pathlib import Path

# 第三方库
from rich.console import Console

# 本地模块
from config import OPENROUTER_API_KEY
```

## 🔧 维护指南

### 添加新功能
1. 在 `src/` 下创建新模块
2. 在 `cli.py` 中添加命令
3. 更新文档
4. 添加测试

### 修改配置
1. 更新 `config/.env.example`
2. 更新 `src/config.py`
3. 更新文档

### 发布新版本
1. 更新版本号 (`setup.py`, `package.json`)
2. 更新 `CHANGELOG.md`
3. 创建 git tag
4. 推送到远程

## 📚 相关文档

- [README.md](README.md) - 项目介绍
- [QUICKSTART.md](docs/QUICKSTART.md) - 快速入门
- [API.md](docs/API.md) - API 文档
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - 贡献指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志

## 🎓 最佳实践

### 性能优化
- 使用异步并发生成
- 控制并发数避免过载
- 智能上下文注入减少 token

### 错误处理
- 使用重试机制
- 提供详细错误信息
- 优雅降级

### 安全性
- 敏感信息放在 `config/.env`
- 使用 `.gitignore` 保护配置
- 不在代码中硬编码密钥

---

**重构完成日期**: 2024-12-04  
**项目版本**: 1.0.0  
**Python 版本**: ≥3.8  
**Node.js 版本**: ≥14.0
