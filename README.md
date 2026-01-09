# AI-PPT 演示文稿生成工具

一个基于 AI 的智能 PPT 生成工具，支持从 Word 文档自动生成精美的演示文稿和演讲稿。

## ✨ 核心功能

- 📄 **智能文档解析**：支持 Word (.docx) 文档，提取文本和图片
- 🎨 **AI 设计生成**：使用顶尖 AI 模型自动设计 PPT 页面
- 🎤 **演讲稿生成**：自动生成专业的工作汇报演讲稿
  - 智能时长控制（精简/适中/详细）
  - 场景智能适配（工作汇报/项目答辩/述职报告）
  - 数据解读增强，互动技巧指导
- 📊 **多格式导出**：支持 PDF 预览
- 🎭 **精致阅读器**：编辑杂志风格的演讲稿阅读器
  - 3 套主题（日间/护眼/夜间）
  - 4 档字号调节
  - 一键复制和下载

## 🚀 快速开始

详见：[docs/QUICK_START.md](docs/QUICK_START.md)

```bash
# 克隆项目
git clone https://github.com/liusai0820/report2html2pdf2pptx.git
cd report2html2pdf2pptx

# 后端启动
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 前端启动
cd frontend
npm install
npm start
```

## 📚 文档

- [快速开始指南](docs/QUICK_START.md)
- [项目架构说明](docs/architecture/ARCHITECTURE.md)
- [部署文档](docs/deployment/)
- [更新日志](CHANGELOG.md)
- [完整文档索引](docs/README.md)

## 🏗️ 技术架构

- **后端**：Python + Flask + OpenAI API
- **前端**：React + Tailwind CSS
- **AI 模型**：Claude Sonnet 3.5 / GPT-4
- **部署**：Docker + Render

## 📈 最新更新

查看 [CHANGELOG.md](CHANGELOG.md) 了解最新功能和改进。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**项目作者**：刘赛  
**联系方式**：liusai0820（微信）
