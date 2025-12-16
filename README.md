# SlideCraft AI - 智能演示文稿生成平台

一个基于 AI 驱动的全栈 Web 应用，能够从各种文档（PDF, DOCX, Markdown, Text）智能生成专业级的演示文稿。系统包含现代化的 React 前端界面和强大的 Python 后端处理引擎。

![SlideCraft Preview](./docs/preview.png)

## ✨ 核心特性

- **🤖 智能编排引擎**: 基于大语言模型（OpenRouter/Claude）自动分析文档结构，生成大纲与幻灯片内容。
- **🎨 动态主题系统**: 内置多种专业主题（咨询、年终总结、科技、创意等），支持动态配色与布局适配。
- **📊 智能数据可视化**: 能够识别文档中的数据并自动生成 ECharts 交互式图表。
- **🖥️ 实时预览**: 提供所见即所得的幻灯片预览，支持键盘导航和缩略图跳转。
- **� 多格式导出**: 一键生成高质量 HTML5 演示文稿、PDF 文档及 PPTX 源文件。
- **📱 响应式设计**: 完美适配各种屏幕尺寸的演示需求。

## 🏗️ 技术架构

项目采用现代化的前后端分离架构：

### Frontend (前端)

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS + CSS Modules
- **State Management**: React Hooks
- **Icons**: Lucide React

### Backend (后端)

- **Framework**: FastAPI (Python 3.10+)
- **AI Processing**: 自研 Prompt Engine + Context Orchestrator
- **PDF Generation**: Pyppeteer (基于 Chrome Headless)
- **Document Parsing**: python-docx, PyPDF2
- **Storage**: 本地文件系统 / Cloudflare R2 (Planned)

## 🚀 快速开始

### 环境要求

- Node.js 16+
- Python 3.10+
- Chrome/Chromium (用于 PDF 生成)

### 1. 后端设置

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp config/.env.example config/.env
# 编辑 config/.env 填入 OPENROUTER_API_KEY 等配置

# 4. 启动后端服务器 (运行在 8000 端口)
python src/server.py
```

### 2. 前端设置

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器 (运行在 5173 端口)
npm run dev
```

### 3. 使用说明

1. 打开浏览器访问 `http://localhost:5173`
2. 上传您的文档（支持 PDF, DOCX, MD, TXT）
3. 选择演示场景（如：咨询汇报、年终总结）
4. 选择视觉主题
5. 点击"立即生成"，观察 AI 实时思考与生成过程
6. 生成完成后，可在线预览或下载 PDF/PPTX

## 📂 项目结构

```
.
├── frontend/                 # React 前端应用
│   ├── src/
│   │   ├── components/       # UI 组件 (ResultView, Hero, etc.)
│   │   └── App.jsx          # 主应用逻辑
│
├── src/                      # Python 后端核心
│   ├── server.py             # FastAPI 服务入口
│   ├── core/                 # AI 编排核心 (Orchestrator, Parser)
│   ├── prompts/              # Prompt 工程引擎
│   ├── themes/               # CSS 生成器与主题注册表
│   └── utils/                # 工具函数
│
├── config/                   # 配置文件
├── input/                    # 用户上传临时目录
└── output/                   # 生成结果产物
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Pull Request 或 Issue 来改进这个项目！
