"""
AI Designer - AI 原生设计引擎

核心理念：
1. 让 AI 成为设计师，而不是模板填充员
2. 给 AI 设计系统约束，让它自由创作
3. 不限制布局，不限制组件，只限制设计 Token

这是整个系统的核心模块，负责与 AI 交互，生成高质量的演示文稿。
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from openai import AsyncOpenAI
from rich.console import Console

from .design_system import DesignSystem, DesignTokens

console = Console()


@dataclass
class PageInfo:
    """页面信息"""
    type: str           # COVER, AGENDA, SECTION, CONTENT, CLOSING
    title: str          # 页面标题
    content: str        # 内容要点/指令
    page_num: int = 0   # 页码
    total_pages: int = 0  # 总页数
    section_num: int = 0  # 章节号（用于 SECTION 页）


@dataclass
class GenerationContext:
    """生成上下文"""
    document_content: str           # 原始文档内容
    document_name: str              # 文档名称
    organization: str               # 汇报单位
    scenario: str                   # 场景类型
    design_system: DesignSystem     # 设计系统
    target_pages: int = 25          # 目标页数
    content_depth: str = "normal"   # 内容深度


# ============================================================================
# 核心 Prompt：这是"元指令"，告诉 AI 它是一个设计师
# ============================================================================

DESIGNER_SYSTEM_PROMPT = """
# 你是一位世界级的演示文稿视觉设计师

你融合了：
- **麦肯锡**的结构化思维和金字塔原理
- **Apple Keynote** 的极简美学和视觉层次
- **政府公文**的严谨规范

## 🎯 核心使命

将信息转化为**有说服力的视觉故事**。每一页都应该：
1. **信息充实** - 内容丰富，有实质性信息
2. **视觉清晰** - 层次分明，重点突出
3. **样式统一** - 使用一致的设计语言

## 🎨 设计原则

### 1. 内容精炼 (Less is More)
- **拒绝长篇大论**：严禁使用超过 3 行的长段落
- **要点式写作**：使用短句、关键词，列表项控制在 2 行以内
- **高信噪比**：去除废话，保留核心数据和观点
- **标题即结论**：标题要完整表达整页的核心思想

### 2. 视觉优先
- **能用图不用表，能用表不用字**
- 使用“大数字”作为视觉锚点
- 重要概念使用卡片封装

### 3. 视觉层次
- 标题 32-36px，加粗
- 子标题/卡片标题 20-24px，加粗
- 正文 16-18px
- 小字/注释 14px

### 4. 布局自由
你可以自由使用：
- 左右两栏布局
- 三卡片网格
- 列表 + 说明
- 表格对比

## 🚫 禁止事项（重要！）

### 禁止侧边装饰
- ✘ 卡片左侧的彩色竖条 (border-left 装饰)
- ✘ 页面边缘的装饰色块
- ✘ 每个卡片不同颜色的左边框

### 禁止 Emoji 和图标
- ✘ 不要使用任何 Emoji（如 💡 🚀 ✅ ❌ ⭐）
- ✘ 不要使用 Unicode 特殊符号图标
- ✘ 不要使用 icon font
- 这会导致 PPTX 转换出现乱码

### 禁止触碰底部 (Bottom Safe Zone)
- ✘ **严禁内容进入底部 80px 区域**
- 底部 80px 是预留给页码和版权信息的
- 画布最大可用高度仅为 640px (720px - 80px)

### 禁止底部结论框
- ✘ 不要在页面底部添加 "So What" 结论框
- 核心观点应该放在标题和副标题中

## ✅ 允许使用

- 卡片背景色 (#f5f7fa)
- 简单边框 (1px solid #e5e7eb)
- 数据强调色
- 简单的箭头符号 (↑ ↓ →)

## 📊 图表支持（ECharts）

当内容包含数据趋势、对比时，可以生成 ECharts 图表：

```html
<div style="width: 100%; height: 300px;" id="chart_唯一ID"></div>
<script>
(function() {
    var chart = echarts.init(document.getElementById('chart_唯一ID'));
    chart.setOption({
        animation: false,
        color: ['主题色'],
        xAxis: { type: 'category', data: ['数据标签'] },
        yAxis: { type: 'value' },
        series: [{ data: [数据值], type: 'bar' 或 'line' }]
    });
})();
</script>
```

## 📐 画布约束

- **尺寸**：1280 × 720 像素
- **边距**：四周 60px
- **避免溢出**：但不要为了避免溢出而内容空洞

## ✅ 输出要求

1. 使用内联样式 (style 属性)
2. 字体使用 'Noto Sans SC', sans-serif
3. 直接输出 HTML，不要任何解释
"""


class AIDesigner:
    """
    AI 设计师
    
    核心理念：让 AI 自己设计，而不是填充模板
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        timeout: int = 120,
        max_retries: int = 3,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def generate_outline(
        self,
        context: GenerationContext,
    ) -> List[Dict[str, Any]]:
        """
        生成大纲
        
        让 AI 根据文档内容自主规划：
        - 分几个章节
        - 每章几页
        - 每页的核心观点
        """
        prompt = self._build_outline_prompt(context)
        response = await self._call_ai(prompt)
        return self._parse_outline(response)
    
    async def generate_page(
        self,
        context: GenerationContext,
        page_info: PageInfo,
    ) -> str:
        """
        生成单页 HTML
        
        这是核心方法：让 AI 自由设计每一页
        """
        prompt = self._build_page_prompt(context, page_info)
        html = await self._call_ai(prompt)
        return self._clean_html(html)
    
    def _build_outline_prompt(self, context: GenerationContext) -> str:
        """构建大纲生成 Prompt"""
        return f"""
# 大纲规划任务

你是一位顶级咨询公司的项目总监。请根据以下文档内容，规划一份专业的演示文稿大纲。

## 输入信息

### 文档内容
```
{context.document_content[:12000]}
```

### 项目信息
- 文档名称：{context.document_name}
- 汇报单位：{context.organization}
- 场景类型：{context.scenario}
- 目标页数：约 {context.target_pages} 页
- 内容深度：{context.content_depth}

## 规划原则

### 1. 金字塔结构
- 整体遵循"总-分-总"的逻辑
- 每个章节有明确的核心观点
- 从宏观到微观，层层递进

### 2. 颗粒度控制
- 每页只讲一个核心观点
- 复杂内容要拆分成多页
- 数据密集的内容单独成页
- 不要为了凑页数而注水

### 3. 故事节奏
- 开篇要抓人（背景/痛点/机遇）
- 中间要实在（分析/数据/洞察）
- 结尾要有力（结论/建议/行动）

### 4. 标题即结论
- 标题不是主题，是这一页的核心观点
- 读完标题就知道这页要说什么
- 例如：
  - ❌ "市场规模分析"（主题式，太空洞）
  - ✅ "市场规模 5 年翻倍，年复合增长率达 23%"（结论式，有信息量）

## 输出格式

每行一条，格式：`类型|标题|内容要点`

类型说明：
- `SECTION`：章节封面页（如"第一部分 市场分析"）
- `CONTENT`：正文内容页

**严禁**：
- 禁止生成 COVER、AGENDA、CLOSING 类型（系统自动添加）
- 禁止生成引言页、摘要页、概述页
- 禁止标题中出现"分析"、"研究"、"探讨"等空洞词汇（除非是章节名）

## 示例

```
SECTION|第一部分 产业现状|
CONTENT|战新产业占比突破 40%，产业结构持续优化|2023年数据：战新产业产值达500亿，占比从35%提升至42%；传统产业比重下降
CONTENT|头部企业集中度高，前三名占据 65% 份额|A公司280亿(32%)、B公司180亿(21%)、C公司100亿(12%)；中小企业生存空间受挤压
SECTION|第二部分 核心问题|
CONTENT|研发投入不足是制约发展的首要瓶颈|全区研发强度仅2.1%，低于全市平均3.5%；龙头企业研发投入占比逐年下降
```

请开始规划大纲（直接输出，不要解释）：
"""
    
    def _build_page_prompt(self, context: GenerationContext, page_info: PageInfo) -> str:
        """构建页面生成 Prompt - 这是最核心的部分"""
        
        # 获取设计系统描述
        design_prompt = context.design_system.get_ai_prompt()
        design_tokens = context.design_system.get_tokens()
        colors = design_tokens.colors.to_dict()
        
        # 根据页面类型选择不同的 Prompt 策略
        if page_info.type == "COVER":
            return self._build_cover_prompt(context, page_info, design_prompt, colors)
        elif page_info.type == "AGENDA":
            return self._build_agenda_prompt(context, page_info, design_prompt, colors)
        elif page_info.type == "SECTION":
            return self._build_section_prompt(context, page_info, design_prompt, colors)
        elif page_info.type == "CLOSING":
            return self._build_closing_prompt(context, page_info, design_prompt, colors)
        else:
            return self._build_content_prompt(context, page_info, design_prompt, colors)
    
    def _build_cover_prompt(
        self, context: GenerationContext, page_info: PageInfo, 
        design_prompt: str, colors: Dict[str, str]
    ) -> str:
        """封面页 Prompt - 内联样式"""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月")
        
        return f"""
# 封面页设计

## 封面信息
- 主标题：{page_info.title}
- 副标题：汇报材料
- 汇报单位：{context.organization}
- 日期：{current_date}

## 设计要求

- 纯白背景
- **使用主题色 {colors['primary']} 进行装饰**（如顶部/底部装饰条，或标题强调）
- 主标题居中，48px，深色文字
- 副标题 20px，可以使用主题色
- 底部左右分布：单位和日期

## 输出

直接输出 HTML，不要任何解释：

<div style="width: 1280px; height: 720px; background: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; box-sizing: border-box; font-family: 'Noto Sans SC', sans-serif; position: relative; overflow: hidden;">
    <!-- 顶部装饰条 -->
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 16px; background: {colors['primary']};"></div>
    
    <h1 style="font-size: 48px; font-weight: 700; color: {colors['text_primary']}; text-align: center; margin: 0; max-width: 900px; line-height: 1.3;">{page_info.title}</h1>
    
    <!-- 装饰线 -->
    <div style="width: 80px; height: 6px; background: {colors['primary']}; margin: 32px 0;"></div>
    
    <p style="font-size: 20px; color: {colors['text_secondary']}; margin: 0;">汇报材料</p>
    
    <div style="position: absolute; bottom: 60px; left: 60px; right: 60px; display: flex; justify-content: space-between; font-size: 14px; color: {colors['text_secondary']};">
        <span>{context.organization}</span>
        <span>{current_date}</span>
    </div>
</div>
"""

    def _build_agenda_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str]
    ) -> str:
        """目录页 Prompt - 内联样式"""
        return f"""
# 目录页设计

## 章节列表
{page_info.content}

## 设计要求

- 纯白背景
- 标题"目录" 32px
- 每个章节一行：序号 + 标题
- 序号用主色 {colors['primary']}
- 分割线用浅灰色

## 输出

直接输出 HTML，不要任何解释：

<div style="width: 1280px; height: 720px; background: #ffffff; padding: 60px; box-sizing: border-box; font-family: 'Noto Sans SC', sans-serif;">
    <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0 0 40px 0;">目录</h1>
    <div style="display: flex; flex-direction: column; gap: 20px;">
        <!-- 每个章节一行 -->
        <div style="display: flex; align-items: center; gap: 24px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb;">
            <span style="font-size: 24px; font-weight: 700; color: {colors['primary']}; min-width: 40px;">01</span>
            <span style="font-size: 20px; color: {colors['text_primary']};">章节标题</span>
        </div>
        <!-- 以此类推 -->
    </div>
</div>
"""

    def _build_section_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str]
    ) -> str:
        """章节页 Prompt - 内联样式"""
        section_num = page_info.section_num if page_info.section_num > 0 else 1
        
        return f"""
# 章节过场页设计

## 章节信息
- 章节序号：0{section_num}
- 章节标题：{page_info.title}

## 设计要求

- 主色背景 {colors['primary']}
- 序号 72px，白色，细体
- 标题 36px，白色，粗体
- 居中显示

## 输出

直接输出 HTML，不要任何解释：

<div style="width: 1280px; height: 720px; background: {colors['primary']}; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Noto Sans SC', sans-serif;">
    <div style="font-size: 72px; font-weight: 300; color: rgba(255,255,255,0.3); margin-bottom: 16px;">0{section_num}</div>
    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.5); margin-bottom: 24px;"></div>
    <h1 style="font-size: 36px; font-weight: 700; color: #ffffff; margin: 0;">{page_info.title}</h1>
</div>
"""

    def _build_closing_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str]
    ) -> str:
        """封底页 Prompt - 内联样式"""
        return f"""
# 封底页设计

## 设计要求

- 纯白背景
- 居中显示"谢谢" 48px，主色 {colors['primary']}
- 下方显示汇报单位
- **必须包含主题色装饰**（如底部色条）

## 输出

直接输出 HTML，不要任何解释：

<div style="width: 1280px; height: 720px; background: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Noto Sans SC', sans-serif; position: relative;">
    <!-- 顶部装饰 -->
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 8px; background: {colors['primary']}; opacity: 0.6;"></div>

    <div style="font-size: 64px; font-weight: 700; color: {colors['primary']}; margin-bottom: 32px; letter-spacing: 4px;">谢谢</div>
    
    <div style="width: 60px; height: 4px; background: {colors['text_secondary']}; margin-bottom: 32px; opacity: 0.3;"></div>
    
    <div style="font-size: 18px; color: {colors['text_secondary']};">{context.organization}</div>
    
    <!-- 底部装饰 -->
    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 24px; background: {colors['primary']};"></div>
</div>
"""

    def _build_content_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str]
    ) -> str:
        """正文页 Prompt - 内容丰富 + 内联样式"""
        
        # 提取相关的原始素材
        source_material = self._extract_relevant_content(
            context.document_content, 
            page_info.title, 
            page_info.content
        )
        
        return f"""
# 正文页设计（第 {page_info.page_num}/{page_info.total_pages} 页）

## 页面信息

### 标题（这是核心观点，要有信息量）
{page_info.title}

### 副标题/引导语（补充说明标题）
{page_info.content}

### 参考素材
```
{source_material}
```

## 设计目标

1. **内容核心化**：只保留最有价值的信息，**删除所有废话**。
2. **视觉化**：能用图表/数字/卡片展示的，绝不写长段文字。
3. **防止拥挤**：内容区域必须留有 30% 以上的空白呼吸感。

## 内容处理规则

- **列表项**：每项不超过 2 行，超过必须精简。
- **段落**：正文段落不超过 3 行，超过必须拆分或删减。
- **关键词**：重点词汇加粗。
- **数字**：重要数据放大显示。

## 禁止事项（重要！）

1. **禁止长篇大论** - 严禁堆砌文字
2. **禁止侧边装饰色块** - 不要卡片左侧彩色竖条
3. **禁止 Emoji 和图标** - 不要任何 emoji
4. **禁止内容触及底部** - 底部有页码保留区

## 布局规范（严格遵守！）

**画布尺寸**：1280 × 720 像素

**空间分配**：
- 顶部边距：50px
- 左右边距：60px
- **底部保留区：80px**（用于页码和留白，内容不可进入！）

**可用内容高度**：720 - 50 - 80 = **590px**

```
┌──────────────────────────────────────┐  ← 顶部 50px
│  [标题区] ~80px                       │
│  ────────────────────────────────    │
│                                      │
│  [内容区] 最大高度约 480px            │
│  内容不要太多，留有余地               │
│                                      │
│  ════════════════════════════════    │  ← 内容停止线
│  [底部保留区 80px - 页码/留白]        │  ← ⚠️ 不可放内容！
└──────────────────────────────────────┘
```

**重要**：内容区不要填满，底部要有明显留白！

## 颜色

- 主色：{colors['primary']}
- 成功色：{colors['success']}（增长 ↑）
- 危险色：{colors['danger']}（下降 ↓）
- 主文字：{colors['text_primary']}
- 次文字：{colors['text_secondary']}
- 卡片背景：#f5f7fa

## 图表（可选）

如果内容包含数据趋势，可以生成 ECharts（高度不超过 250px）：

```html
<div style="width: 100%; height: 250px;" id="chart_page{page_info.page_num}"></div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_page{page_info.page_num}'));
    chart.setOption({{
        animation: false,
        color: ['{colors["primary"]}', '{colors["accent"]}'],
        grid: {{ top: 30, bottom: 25, left: 45, right: 15 }},
        xAxis: {{ type: 'category', data: ['标签'] }},
        yAxis: {{ type: 'value' }},
        series: [{{ data: [数值], type: 'bar' }}]
    }});
}})();
</script>
```

## 输出

直接输出完整 HTML：

<div style="width: 1280px; height: 720px; background: #ffffff; padding: 50px 60px 80px; box-sizing: border-box; font-family: 'Noto Sans SC', sans-serif; display: flex; flex-direction: column;">
    <!-- 标题区 -->
    <div style="margin-bottom: 24px; flex-shrink: 0;">
        <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0; line-height: 1.3;">标题（核心观点）</h1>
        <p style="font-size: 16px; color: {colors['text_secondary']}; margin: 8px 0 0 0;">副标题/引导语</p>
    </div>
    
    <!-- 内容区 - 注意不要超出，底部有 80px 保留区 -->
    <div style="flex: 1; display: flex; gap: 32px; overflow: hidden;">
        <!-- 你的创意内容 -->
    </div>
</div>
"""

    def _extract_relevant_content(self, full_content: str, title: str, content_hint: str) -> str:
        """提取与当前页面相关的原始内容"""
        # 简单实现：搜索关键词匹配的段落
        keywords = []
        
        # 从标题提取关键词
        for word in title.replace("，", " ").replace("。", " ").split():
            if len(word) > 1:
                keywords.append(word)
        
        # 从内容提示提取关键词
        for word in content_hint.replace("，", " ").replace("。", " ").replace("；", " ").split():
            if len(word) > 1:
                keywords.append(word)
        
        # 搜索相关段落
        paragraphs = full_content.split("\n\n")
        relevant = []
        
        for para in paragraphs:
            score = sum(1 for kw in keywords if kw in para)
            if score >= 2:  # 至少匹配 2 个关键词
                relevant.append(para)
        
        # 限制长度
        result = "\n\n".join(relevant[:5])
        if len(result) > 2000:
            result = result[:2000] + "..."
        
        return result if result else content_hint

    async def _call_ai(self, prompt: str, retry_count: int = 0) -> str:
        """调用 AI API"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                ),
                timeout=self.timeout
            )
            
            if not response or not response.choices:
                raise ValueError("API 返回空响应")
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("API 返回内容为空")
            
            return content.strip()
        
        except asyncio.TimeoutError:
            if retry_count < self.max_retries:
                wait_time = 2 * (retry_count + 1)
                console.print(f"[yellow]⚠ 超时，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._call_ai(prompt, retry_count + 1)
            raise
        
        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = 2 * (retry_count + 1)
                console.print(f"[yellow]⚠ 失败: {str(e)[:80]}，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._call_ai(prompt, retry_count + 1)
            raise

    def _parse_outline(self, text: str) -> List[Dict[str, Any]]:
        """解析大纲"""
        pages = []
        auto_types = {'COVER', 'AGENDA', 'CLOSING'}
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('```'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                page_type = parts[0].strip().upper()
                
                # 过滤系统自动生成的类型
                if page_type in auto_types:
                    continue
                
                if page_type not in {'SECTION', 'CONTENT'}:
                    page_type = 'CONTENT'
                
                pages.append({
                    'type': page_type,
                    'title': parts[1].strip(),
                    'content': parts[2].strip() if len(parts) > 2 else ''
                })
        
        return pages

    def _clean_html(self, html: str) -> str:
        """清理 HTML"""
        import re
        
        html = html.strip()
        
        # 移除 markdown 代码块
        if html.startswith('```html'):
            html = html[7:]
        elif html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]
        
        # 移除 HTML 之前的解释文字
        first_tag = re.search(r'<div\s', html, re.IGNORECASE)
        if first_tag and first_tag.start() > 0:
            html = html[first_tag.start():]
        
        # 移除 style 和 header 标签
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        return html.strip()
