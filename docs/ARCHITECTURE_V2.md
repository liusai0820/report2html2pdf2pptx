# AI 原生架构设计 v2.0

## 设计理念

### 传统方式 vs AI 原生方式

**传统方式（旧代码的问题）：**
```
用户输入 → 代码判断场景 → 选择模板 → 填充内容 → 输出
           ↓
        硬编码规则
        分散的配置
        重复的逻辑
```

**AI 原生方式（新架构）：**
```
用户输入 → 构建完整上下文 → AI 自主决策 → 输出
           ↓
        所有信息作为上下文
        AI 根据上下文决定
        最小化硬编码
```

### 核心原则

1. **上下文驱动** - 所有信息都是上下文的一部分
2. **AI 决策** - 让 AI 根据上下文自主决定
3. **单一职责** - 每个组件只做一件事
4. **最小硬编码** - 只硬编码元级别的指导

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  文档    │  │  场景    │  │  配置    │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              ContextBuilder (上下文构建器)               │
│                                                         │
│  职责：收集所有信息，构建完整上下文                       │
│  不做：任何决策                                          │
│                                                         │
│  输出：PresentationContext                              │
│  - 文档内容                                             │
│  - 场景描述（自然语言）                                  │
│  - 受众信息                                             │
│  - 风格偏好                                             │
│  - 质量要求                                             │
│  - 约束条件                                             │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              AIOrchestrator (AI 编排器)                  │
│                                                         │
│  职责：将上下文传递给 AI，获取结果                        │
│  不做：业务逻辑判断、模板选择                            │
│                                                         │
│  核心：MASTER_SYSTEM_PROMPT                             │
│  - 元级别的指导（金字塔原理、So What 等）                │
│  - CSS 类名参考                                         │
│  - 质量红线                                             │
│                                                         │
│  方法：                                                 │
│  - generate_outline() → AI 规划大纲                     │
│  - generate_page() → AI 生成页面                        │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              OutputRenderer (输出渲染器)                 │
│                                                         │
│  职责：将 AI 输出转换为最终格式                          │
│  不做：内容决策                                          │
│                                                         │
│  方法：                                                 │
│  - render_template() → 生成 HTML 模板                   │
│  - save_page() → 保存单页                               │
│  - merge_pages() → 合并页面                             │
│  - generate_pdf() → 生成 PDF                            │
│  - generate_pptx() → 生成 PPTX                          │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                      输出文件                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  HTML    │  │   PDF    │  │  PPTX    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 模块关系

### 新架构 (core/)

```
core/
├── __init__.py           # 模块入口
├── context_builder.py    # 上下文构建器
├── ai_orchestrator.py    # AI 编排器
├── output_renderer.py    # 输出渲染器
└── generator.py          # 统一生成器
```

### 旧模块（保留但不推荐）

```
# 这些模块仍然存在，但新代码应该使用 core/
themes/                   # 主题系统 → 视觉配置可以注入到 OutputRenderer
prompts/                  # Prompt 系统 → 方法论可以注入到 AIOrchestrator
ai_client.py             # 旧 AI 客户端 → 被 AIOrchestrator 替代
slide_generator.py       # 旧生成器 → 被 PresentationGenerator 替代
themed_ai_client.py      # 主题化客户端 → 被 AIOrchestrator 替代
themed_slide_generator.py # 主题化生成器 → 被 PresentationGenerator 替代
```

### 如何迁移

**旧方式：**
```python
from slide_generator import SlideGenerator
from themes import get_theme

theme = get_theme("consulting")
generator = SlideGenerator(theme_id="consulting")
await generator.run(document_path)
```

**新方式：**
```python
from core import PresentationGenerator

generator = PresentationGenerator()
await generator.generate(
    document_path,
    scenario="consulting",
    config={"organization": "XX公司"}
)
```

## 关键设计决策

### 1. 为什么用自然语言描述场景？

**旧方式：**
```python
if scenario == "consulting":
    use_template_a()
elif scenario == "annual_review":
    use_template_b()
```

**新方式：**
```python
scenario_description = """
这是一份咨询研究报告，需要呈现给政府领导或企业高管。
受众特点：时间有限，需要快速抓住重点...
"""
# 让 AI 根据描述自己决定
```

**好处：**
- AI 能理解细微差别
- 容易扩展新场景
- 不需要维护复杂的分支逻辑

### 2. 为什么只有一个 MASTER_SYSTEM_PROMPT？

**旧方式：**
- themes/prompt_generator.py 有一套 prompt
- prompts/prompt_engine.py 有另一套 prompt
- ai_client.py 还有硬编码的 prompt

**新方式：**
- 只有一个 MASTER_SYSTEM_PROMPT
- 包含元级别的指导（方法论、质量红线）
- 具体决策由 AI 根据上下文做出

**好处：**
- 没有冲突
- 容易维护
- AI 有更大的自主权

### 3. 为什么上下文用自然语言？

**旧方式：**
```python
config = {
    "theme_id": "consulting",
    "target_pages": 25,
    "include_cover": True,
    ...
}
```

**新方式：**
```python
context.to_prompt_context()
# 输出：
# "你需要帮助制作一份演示文稿。
#  场景：这是一份咨询研究报告...
#  受众：政府领导...
#  目标页数：约 25 页..."
```

**好处：**
- AI 更容易理解
- 可以包含更丰富的信息
- 不需要 AI 解析结构化数据

## 扩展指南

### 添加新场景

只需要在 `ContextBuilder.with_scenario()` 中添加场景描述：

```python
scenario_descriptions = {
    "new_scenario": """
    这是一份新类型的报告...
    受众特点：...
    风格要求：...
    """
}
```

不需要：
- 创建新模板
- 添加分支逻辑
- 修改 AI 客户端

### 自定义视觉风格

在 `OutputRenderer` 中注入自定义 CSS：

```python
renderer = OutputRenderer(output_dir)
custom_css = """
:root {
    --primary: #FF0000;
}
"""
template = renderer.render_template(custom_css)
```

### 增强 AI 能力

在 `MASTER_SYSTEM_PROMPT` 中添加新的指导：

```python
MASTER_SYSTEM_PROMPT = """
...
## 新增能力
- 支持生成 ECharts 图表
- 支持生成时间线
...
"""
```

## 性能考虑

### 并发生成

```python
# 使用信号量控制并发
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def generate_one(page_info, page_num):
    async with semaphore:
        return await orchestrator.generate_page(...)

# 并行生成所有页面
tasks = [generate_one(p, i) for i, p in enumerate(outline)]
results = await asyncio.gather(*tasks)
```

### 重试机制

```python
async def _generate(self, prompt, retry_count=0):
    try:
        return await self.client.chat.completions.create(...)
    except:
        if retry_count < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY * (retry_count + 1))
            return await self._generate(prompt, retry_count + 1)
        raise
```

## 总结

新架构的核心思想：

1. **让 AI 做决策** - 不要用代码限制 AI 的能力
2. **上下文是关键** - 给 AI 足够的信息
3. **最小化硬编码** - 只硬编码元级别的指导
4. **单一职责** - 每个组件只做一件事

这是真正的 AI 原生设计，充分利用 AI 的创意和能力。
