# 模块关系说明

## 问题背景

之前的代码存在多处重复和冲突：

| 模块 | 功能 | 问题 |
|------|------|------|
| `themes/prompt_generator.py` | 主题相关 prompt | 与其他 prompt 冲突 |
| `prompts/prompt_engine.py` | 场景相关 prompt | 与主题 prompt 重复 |
| `ai_client.py` | 硬编码 prompt | 难以维护 |
| `slide_generator.py` | 生成逻辑 | 与主题生成器重复 |
| `themed_ai_client.py` | 主题化 AI 客户端 | 与 ai_client 重复 |
| `themed_slide_generator.py` | 主题化生成器 | 与 slide_generator 重复 |

这是典型的"传统分段式思维"，不是 AI 原生设计。

## 新架构

```
src/
├── core/                      # 🆕 AI 原生统一架构（推荐使用）
│   ├── context_builder.py     # 上下文构建器
│   ├── ai_orchestrator.py     # AI 编排器
│   ├── output_renderer.py     # 输出渲染器
│   └── generator.py           # 统一生成器
│
├── main.py                    # 🆕 新入口
│
├── themes/                    # 保留，可选使用
│   ├── theme_registry.py      # 主题定义（视觉配置）
│   ├── css_generator.py       # CSS 生成
│   └── prompt_generator.py    # ⚠️ 不推荐，用 core/ 替代
│
├── prompts/                   # 保留，可选使用
│   ├── methodology.py         # 方法论（可注入到 core）
│   ├── scenario_prompts.py    # 场景 prompt（可注入到 core）
│   └── prompt_engine.py       # ⚠️ 不推荐，用 core/ 替代
│
├── ai_client.py               # ⚠️ 旧版，用 core/ai_orchestrator 替代
├── slide_generator.py         # ⚠️ 旧版，用 core/generator 替代
├── themed_ai_client.py        # ⚠️ 旧版，用 core/ai_orchestrator 替代
├── themed_slide_generator.py  # ⚠️ 旧版，用 core/generator 替代
├── cli.py                     # ⚠️ 旧版 CLI
└── cli_enhanced.py            # ⚠️ 旧版增强 CLI
```

## 推荐用法

### 新方式（推荐）

```python
from core import PresentationGenerator

generator = PresentationGenerator()
await generator.generate(
    document_path="input/report.docx",
    scenario="consulting",
    config={
        "organization": "XX公司",
        "target_pages": 30
    }
)
```

### 旧方式（兼容但不推荐）

```python
from slide_generator import SlideGenerator

generator = SlideGenerator()
await generator.run("input/report.docx")
```

## 模块职责

### core/context_builder.py

**职责**：收集所有信息，构建完整上下文

**不做**：任何决策

```python
builder = ContextBuilder()
builder.from_document("report.docx")
builder.with_scenario("consulting")
builder.with_organization("XX公司")
context = builder.build()

# 输出自然语言描述，供 AI 理解
prompt = context.to_prompt_context()
```

### core/ai_orchestrator.py

**职责**：与 AI 交互

**不做**：业务逻辑判断、模板选择

```python
orchestrator = AIOrchestrator()

# AI 自主规划大纲
outline = await orchestrator.generate_outline(context)

# AI 自主生成页面
html = await orchestrator.generate_page(context, page_info, page_num, total)
```

### core/output_renderer.py

**职责**：将 AI 输出转换为最终格式

**不做**：内容决策

```python
renderer = OutputRenderer("output/my_ppt")
template = renderer.render_template()
renderer.save_page(1, html, template)
pdf_path = renderer.generate_pdf("report")
```

## 如何扩展

### 添加新场景

在 `context_builder.py` 的 `with_scenario()` 中添加：

```python
scenario_descriptions = {
    "new_scenario": """
    这是一份新类型的报告...
    受众特点：...
    风格要求：...
    """
}
```

### 自定义视觉风格

在 `output_renderer.py` 中注入自定义 CSS：

```python
custom_css = ":root { --primary: #FF0000; }"
template = renderer.render_template(custom_css)
```

### 增强 AI 能力

在 `ai_orchestrator.py` 的 `MASTER_SYSTEM_PROMPT` 中添加：

```python
MASTER_SYSTEM_PROMPT = """
...
## 新增能力
- 支持生成 ECharts 图表
...
"""
```

## 迁移指南

### 从 slide_generator 迁移

```python
# 旧
from slide_generator import SlideGenerator
generator = SlideGenerator(output_dir="output")
await generator.run("report.docx")

# 新
from core import PresentationGenerator
generator = PresentationGenerator()
await generator.generate("report.docx", output_dir="output")
```

### 从 themed_slide_generator 迁移

```python
# 旧
from themed_slide_generator import ThemedSlideGenerator
generator = ThemedSlideGenerator(theme_id="consulting", user_config={...})
await generator.run("report.docx")

# 新
from core import PresentationGenerator
generator = PresentationGenerator()
await generator.generate("report.docx", scenario="consulting", config={...})
```

## 设计原则

1. **上下文驱动** - 所有信息作为上下文传递给 AI
2. **AI 决策** - 让 AI 根据上下文自主决定
3. **单一职责** - 每个组件只做一件事
4. **最小硬编码** - 只硬编码元级别的指导

## 总结

| 旧模块 | 新模块 | 说明 |
|--------|--------|------|
| `ai_client.py` | `core/ai_orchestrator.py` | AI 交互 |
| `slide_generator.py` | `core/generator.py` | 生成逻辑 |
| `themed_ai_client.py` | `core/ai_orchestrator.py` | 合并 |
| `themed_slide_generator.py` | `core/generator.py` | 合并 |
| `themes/prompt_generator.py` | `core/context_builder.py` | 上下文构建 |
| `prompts/prompt_engine.py` | `core/ai_orchestrator.py` | AI 指导 |

新架构的核心思想：**让 AI 做决策，代码只负责收集信息和输出结果**。
