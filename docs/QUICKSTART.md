# 快速入门指南

## 5 分钟上手

### 第一步：安装

```bash
# 克隆项目（如果还没有）
git clone <your-repo>
cd ai-presentation-generator

# 一键安装所有依赖
make install
```

### 第二步：配置

```bash
# 复制配置模板
cp config/.env.example config/.env

# 编辑配置文件，填入你的 API 密钥
# 使用你喜欢的编辑器打开 config/.env
nano config/.env  # 或 vim, code 等
```

最少需要配置：
```env
OPENROUTER_API_KEY=sk-or-your-key-here
```

### 第三步：准备输入文件

将你的文档放入 `input/` 目录：

```bash
# 支持的格式
input/
  ├── my-document.json    # JSON 格式
  ├── report.md           # Markdown 格式
  └── presentation.docx   # Word 文档
```

### 第四步：运行

```bash
# 交互式模式（推荐新手）
python run.py

# 或使用 make 命令
make run
```

按照提示选择文件，确认后即可开始生成！

## 输出结果

生成完成后，在 `output/` 目录下会看到：

```
output/
  └── 文档名_20241204_143022/
      ├── presentation.html      # 完整 HTML
      ├── 文档名_20241204.pdf    # PDF 版本
      ├── 文档名_20241204.pptx   # PowerPoint 版本
      ├── pages/                 # 独立页面
      │   ├── page-01.html
      │   ├── page-02.html
      │   └── ...
      └── templates/
          └── template.html      # 使用的模板
```

## 常用命令

```bash
# 处理单个文档
python run.py input/document.json

# 批量处理所有文档
python run.py --batch

# 只生成 HTML，不生成 PDF
python run.py input/document.json --skip-pdf

# 指定输出目录
python run.py input/document.json -o my-output

# PDF 转 PPTX
python run.py --pdf-to-pptx input.pdf -o output.pptx

# 清理输出文件
make clean
```

## 输入格式示例

### JSON 格式

```json
{
  "title": "我的演示文稿",
  "style_guide": "现代商务风格",
  "pages": [
    {
      "type": "COVER",
      "title": "项目汇报",
      "content": "2024年度总结"
    },
    {
      "type": "CONTENT",
      "title": "核心数据",
      "content": "营收增长50%，用户突破100万"
    }
  ]
}
```

### Markdown 格式

```markdown
# 我的演示文稿

## 第一部分：背景

这里是背景介绍...

## 第二部分：数据分析

- 指标1：增长50%
- 指标2：用户100万
```

### DOCX 格式

直接使用 Word 文档，系统会自动解析标题和内容。

## 高级用法

### 自定义模型

在 `config/.env` 中修改：
```env
DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

### 调整并发数

```env
MAX_CONCURRENT_REQUESTS=10  # 增加并发数
```

### 调整超时时间

```env
TIMEOUT_SECONDS=300  # 5分钟超时
```

## 故障排除

### 问题：API 密钥错误

**解决**：检查 `config/.env` 文件，确保 API 密钥正确。

### 问题：PDF 生成失败

**解决**：
1. 确保已安装 Node.js
2. 运行 `npm install` 安装 puppeteer
3. 检查系统内存是否充足

### 问题：找不到输入文件

**解决**：确保文件在 `input/` 目录下，且格式正确（.json, .md, .docx）。

### 问题：生成速度慢

**解决**：
1. 增加并发数：`MAX_CONCURRENT_REQUESTS=10`
2. 使用更快的模型：`DEFAULT_MODEL=anthropic/claude-3.5-haiku`
3. 减少页面数量

## 下一步

- 阅读 [API 文档](API.md) 了解编程接口
- 查看 [架构设计](ARCHITECTURE.md) 了解系统原理
- 参考 [贡献指南](CONTRIBUTING.md) 参与开发

## 获取帮助

```bash
# 查看帮助信息
python run.py --help

# 查看 Makefile 命令
make help
```

祝使用愉快！🎉
