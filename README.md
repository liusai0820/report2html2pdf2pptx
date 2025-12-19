# SlideCraft AI - 智能演示文稿生成平台

一个基于 AI 驱动的全栈 Web 应用，能够从各种文档（PDF, DOCX, Markdown, Text）智能生成专业级的演示文稿。系统包含现代化的 React 前端界面和强大的 Python 后端处理引擎。

![SlideCraft Preview](./docs/preview.png)

## ✨ 核心特性

- **🤖 智能编排引擎 (V2)**: 基于最新的大语言模型，自动执行内容提取、逻辑规划、大纲生成与幻灯片排版。
- **📝 自定义 AI 指令**: 允许用户输入特定要求（如：「第一章重点讲市场分析」、「使用更正式的语言」），让 AI 灵活适配不同需求。
- **🖼️ 全向预览体验**:
  - **分屏视图**: 左侧内容微调，右侧实时幻灯片预览，支持点击定位。
  - **幻灯片浏览 (Grid View)**: 类似 PowerPoint 的网格视图，支持 **1-6 列自由缩放**，快速纵览项目全貌。
  - **侧边栏折叠**: 一键折叠左侧功能区，让预览区占满全屏，提升沉浸感。
  - **全屏沉浸模式**: 支持键盘（方向键、空格、Enter）及鼠标点击导航，完美模拟实际演说环境。
- **🎨 动态设计系统**: 基于场景（如：咨询汇报、政务公文、学术研究）的自动风格适配，内置高品质颜色索引与排版规范。
- **📊 ECharts 图表支持**: 自动将数据内容转换为柱状图、折线图、饼图等专业可视化图表。
- **🛠️ 高质量导出**:
  - **PDF 文档**: 优化字体嵌入策略，使用国内镜像 CDN 确保字体加载稳定。
  - **PPTX 源文件**: 支持直接导出可编辑的微软 PowerPoint 格式（通过 Adobe 引擎转换）。
- **📄 增强型文档解析**: 支持文字型 PDF、DOCX、Markdown、TXT 等格式的深度解析，自动提取文字与表格。

## 🆕 最新更新 (2024-12-20)

### UI/UX 优化
- ✅ **网格缩放功能**: 网格预览视图支持 1-6 列自由缩放，类似 PowerPoint 的缩略图浏览体验
- ✅ **侧边栏折叠**: 左侧功能区可一键折叠，预览区获得更大空间
- ✅ **封面优化**: 移除冗余的「汇报材料」副标题，封面更简洁专业

### AI 生成优化  
- ✅ **画布约束强化**: 将布局约束放在 System Prompt 最前面，确保 AI 严格遵守 1280×720 画布尺寸
- ✅ **内容溢出防护**: 强化图表和内容区的 overflow 控制，防止内容超出画布
- ✅ **页数要求强化**: AI 会更严格地遵守用户指定的目标页数（如 80 页）
- ✅ **Footer 禁止**: 禁止 AI 生成页脚，保持页面风格统一

### 技术改进
- ✅ **字体 CDN 国内镜像**: 将 Google Fonts 替换为 fonts.loli.net 国内镜像，解决字体加载失败问题
- ✅ **max_tokens 调整**: 增加到 16000，支持生成更长的大纲
- ✅ **模型升级**: 默认模型更新为 `google/gemini-3-flash-preview`

## 🏗️ 技术架构

项目采用现代化的前后端分离架构：

### Frontend (前端)

- **UI 框架**: React 18 + Vite
- **交互动画**: Framer Motion
- **图标系统**: Lucide React
- **样式方案**: Vanilla CSS (CSS Modules) + Tailwind CSS (Partial)

### Backend (后端)

- **基础框架**: FastAPI (Python 3.10+)
- **AI 编排**: 自研 Prompt Engine + Context Orchestrator
- **PDF 渲染**: Puppeteer (Node.js) + Pyppeteer (Python)
- **文档解析**: pdfplumber (PDF), python-docx (Word)
- **PPTX 转换**: Adobe PDF Services API / Cloud Convert
- **图表引擎**: ECharts 5.4

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Chrome/Chromium (用于 PDF 生成)

### 1. 全自动启动 (推荐)

```bash
./start_all.sh
```

### 2. 手动启动

#### 后端设置

```bash
# 激活环境并安装依赖
pip install -r requirements.txt
# 配置环境变量 (config/.env)
python src/server.py
```

#### 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 📂 项目结构

```
.
├── frontend/                 # React 前端应用
│   ├── src/
│   │   ├── components/       # UI 组件 (ResultView, ConfigPanel, etc.)
│   │   └── App.jsx          # 主应用逻辑
│
├── src/                      # Python 后端核心
│   ├── v2/                   # V2 引擎核心 (设计师逻辑、设计系统、样式)
│   │   ├── ai_designer.py   # AI 设计师 - Prompt 工程核心
│   │   ├── unified_styles.py # 统一样式系统
│   │   ├── engine.py        # 生成引擎
│   │   └── page_templates.py # 页面模板
│   ├── server.py             # FastAPI 服务入口
│   ├── document_parser.py    # 多格式分拣解析器
│   └── v2_adapter.py         # 前后端流式通信适配器
│
├── config/                   # 配置文件
│   └── .env                  # 环境变量 (API Keys 等)
├── docs/                     # 截图与文档
├── input/                    # 用户上传临时目录
└── output/                   # 生成结果产物
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Pull Request 或 Issue 来改进这个项目！
