# SlideCraft AI - 智能演示文稿生成平台

> **⚠️ 分形文档规则 (Fractal Documentation)**
>
> 本项目采用**分形文档结构**，任何功能、架构、写法的更新，**必须**在工作结束后同步更新：
>
> 1. 被修改文件的头部注释 (`@input/@output/@pos`)
> 2. 该文件所在目录的 `_FOLDER.md`
> 3. 如涉及跨模块变更，需更新 `/ARCHITECTURE.md`
>
> 详见 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解完整的分形规则。

一个基于 AI 驱动的全栈 Web 应用，能够从各种文档（PDF, DOCX, Markdown, Text）智能生成专业级的演示文稿。系统包含现代化的 React 前端界面和强大的 Python 后端处理引擎。

![SlideCraft Preview](./docs/preview.png)

## ✨ 核心特性

- **🤖 智能编排引擎 (V2)**: 基于最新的大语言模型，自动执行内容提取、逻辑规划、大纲生成与幻灯片排版。
- **📝 自定义 AI 指令**: 允许用户输入特定要求（如：「第一章重点讲市场分析」、「使用更正式的语言」），让 AI 灵活适配不同需求。
- **🖼️ 全向预览体验**:
  - **分屏视图**: 左侧内容微调，右侧实时幻灯片预览，支持点击定位。
  - **幻灯片浏览 (Grid View)**: 类似 PowerPoint 的网格视图，支持 **1-6 列自由缩放**，快速纵览项目全貌。
  - **侧边栏折叠**: 一键折叠左侧功能区，让预览区占满全屏，提升沉浸感。
  - **全量沉浸预览**: 支持全屏模式，使用左右方向键翻页，完美模拟演说。
- **🌄 背景图智能生成 (New)**:
  - **Nano Banana Pro**: 调用顶级 AI 图像模型为封面和封底生成高度契合主题的专业视觉。
  - **Unsplash 集成**: 自动搜索高质量图库作为章节背景。
  - **智能遮罩**: 自动为背景图叠加暗色线性渐变，确保文字可读性与高级感并存。
- **🎨 动态设计系统**: 基于场景（如：咨询汇报、政务公文、学术研究）的自动风格适配，内置高品质颜色索引与排版规范。
- **📊 ECharts 图表支持**: 自动将数据内容转换为柱状图、折线图、饼图等专业可视化图表。

## 🆕 最新更新 (2024-12-20)

### 图像生成与背景系统 🚀

- ✅ **Nano Banana Pro 集成**: 封面与封底支持 AI 图像生成，大幅提升视觉震撼力
- ✅ **Unsplash 图库对接**: 支持从 Unsplash 自动抓取风景/商务背景图
- ✅ **Token 溢出保护**: 采用 `__DIRECT_HTML__` 技术处理 Base64 图像，完美解决长图片导致的 AI 响应溢出问题
- ✅ **章节页策略**: 为平衡性能与效果，封面/结尾使用图像，章节页保持品牌主色纯色风格

### UI/UX 优化

- ✅ **网格缩放功能**: 网格预览视图支持 1-6 列自由缩放，类似 PowerPoint 的缩略图浏览体验
- ✅ **侧边栏折叠**: 左侧功能区可一键折叠，预览区获得更大空间
- ✅ **封面优化**: 封面模板重构，支持「图片+蒙版+白色文字」的高级杂志感布局

### 引擎进阶

- ✅ **画布约束强化**: 确保 AI 严格遵守 1280×720 画布尺寸，全屏预览无黑边
- ✅ **字体方案升级**: 采用 Google Fonts 国内镜像 + Puppeteer 强制嵌入，PDF 导出文字可编辑，告别 Type3 字体问题
- ✅ **模型升级**: 支持 `google/gemini-2.5-flash-image` (Nano Banana) 进行高质量配图生成

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
