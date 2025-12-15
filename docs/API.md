# API 文档

## 核心类

### SlideGenerator

主要的生成器类，负责整个生成流程。

```python
from src.slide_generator import SlideGenerator

# 创建生成器
generator = SlideGenerator(
    model="anthropic/claude-3.5-haiku",  # 可选，指定模型
    output_dir="output/my_presentation"   # 可选，指定输出目录
)

# 运行生成流程
await generator.run(
    document_path="input/document.json",
    skip_pdf=False,           # 是否跳过 PDF 生成
    skip_generation=False     # 是否跳过 AI 生成
)
```

### AIClient

AI API 客户端，封装了与 OpenRouter 的交互。

```python
from src.ai_client import AIClient

# 创建客户端
client = AIClient(model="anthropic/claude-3.5-haiku")

# 生成内容
content = await client.generate(
    prompt="生成一个关于 AI 的演示文稿",
    system_prompt="你是专业的演示文稿设计师"  # 可选
)

# 生成模板
template = await client.generate_template(
    style_guide="现代商务风格"
)

# 生成页面内容
page_html = await client.generate_page_content(
    page_num=1,
    total_pages=10,
    page_data={
        'type': 'CONTENT',
        'title': '标题',
        'content': '内容'
    },
    style_guide="商务风格",
    source_material="原始文档内容"  # 可选
)
```

### DocumentParser

文档解析器，支持多种格式。

```python
from src.document_parser import DocumentParser

# 加载文档
data = DocumentParser.load_document("input/document.json")

# 返回格式
{
    'title': '文档标题',
    'style_guide': '样式指南',
    'pages': [
        {
            'type': 'COVER',
            'title': '封面标题',
            'content': '封面内容'
        },
        # ...
    ],
    'full_content': '完整文档内容'  # 仅 DOCX/MD
}
```

### TemplateMerger

模板合并器，处理 HTML 模板。

```python
from src.template_merger import TemplateMerger

# 创建合并器
merger = TemplateMerger("templates/template.html")

# 保存单个页面
merger.save_page(
    output_path="output/page-01.html",
    page_num=1,
    total_pages=10,
    title="页面标题",
    content="<div>页面内容</div>"
)

# 合并所有页面
merger.save_merged(
    output_path="output/presentation.html",
    pages_data=[
        {
            'page_num': 1,
            'title': '标题',
            'content': '<div>内容</div>'
        },
        # ...
    ]
)
```

### PDFGenerator

PDF 生成器。

```python
from src.pdf_generator import generate_pdf_from_html

# 生成 PDF
generate_pdf_from_html(
    html_path="output/presentation.html",
    pdf_path="output/presentation.pdf"
)
```

### AdobeIntegration

Adobe PDF Services 集成。

```python
from src.adobe_integration import pdf_to_pptx, batch_pdf_to_pptx

# 单个文件转换
pptx_path = pdf_to_pptx(
    pdf_path="output/presentation.pdf",
    output_path="output/presentation.pptx"  # 可选
)

# 批量转换
results = batch_pdf_to_pptx(
    pdf_dir="output/pdfs",
    output_dir="output/pptx"
)
```

## 配置

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
RETRY_DELAY=5
TEMPERATURE=0.7

# Adobe PDF Services
ADOBE_CLIENT_ID=xxx
ADOBE_CLIENT_SECRET=xxx
```

### 配置类

```python
from src.config import (
    OPENROUTER_API_KEY,
    DEFAULT_MODEL,
    MAX_CONCURRENT_REQUESTS,
    TIMEOUT_SECONDS,
    # ...
)
```

## 命令行接口

```bash
# 交互式模式
python run.py

# 处理单个文档
python run.py input/document.json

# 批量处理
python run.py --batch

# 指定输出目录
python run.py input/document.json -o output/custom

# PDF 转 PPTX
python run.py --pdf-to-pptx input.pdf -o output.pptx

# 批量 PDF 转 PPTX
python run.py --batch-pdf-to-pptx pdf_folder -o output_folder
```

## 错误处理

所有主要函数都会抛出异常，建议使用 try-except 捕获：

```python
try:
    await generator.run(document_path)
except Exception as e:
    print(f"生成失败: {e}")
```

常见异常：

- `FileNotFoundError`: 文件不存在
- `ValueError`: 参数错误
- `TimeoutError`: 请求超时
- `Exception`: 其他错误
