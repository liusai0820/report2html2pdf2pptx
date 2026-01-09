"""
AI Designer - AI 原生设计引擎

@input:  design_system, OpenAI API, GenerationContext
@output: generate_outline(), generate_page() -> HTML字符串
@pos:    V2引擎的大脑，负责与AI对话生成幻灯片内容

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/v2/_FOLDER.md

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
    organization: str               # 汇报单位（用户填写的，作为 fallback）
    scenario: str                   # 场景类型
    design_system: DesignSystem     # 设计系统
    target_pages: int = 25          # 目标页数
    content_depth: str = "normal"   # 内容深度
    custom_instructions: str = ""   # 用户自定义指令
    bg_image_source: str = "none"   # 背景图来源: 'none', 'unsplash', 'ai'
    report_type: str = ""           # AI 提炼的报告类型（如"产业研究报告"）
    ai_org_name: str = ""           # AI 提炼的汇报单位（优先于 organization）
    images: List[Dict] = None       # 文档中提取的图片列表 (base64 格式)


# ============================================================================
# 核心 Prompt：这是"元指令"，告诉 AI 它是一个设计师
# ============================================================================

DESIGNER_SYSTEM_PROMPT = """
# 你是一位世界级的演示文稿视觉设计师

## ⚠️ 画布约束（最高优先级！必须严格遵守！）

**画布尺寸**：1280 × 720 像素（固定，不可改变）

**布局分区**：
```
┌─────────────────────────────────────────────┐
│                 顶部边距 50px                 │
├─────────────────────────────────────────────┤
│  左边距    [标题区] 高度约 80px      右边距   │
│   60px    ─────────────────────────   60px  │
│           [内容区] 最大高度 480px            │
│           ⚠️ 内容不要填满，留有余地          │
│           ─────────────────────────          │
│           [底部保留区 80px] ← 禁止放内容！    │
└─────────────────────────────────────────────┘
```

**硬性规则**：
1. ✘ **严禁内容进入底部 80px 区域**（预留给页码）
2. ✘ **严禁内容超出 1280px 宽度**
3. ✘ **严禁图表溢出容器**（图表必须设置 max-width）
4. ✔ 所有容器必须添加 `overflow: hidden`

## 🎯 核心使命

将信息转化为**有说服力的视觉故事**。每一页都应该：
1. **信息充实** - 内容丰富，有实质性信息
2. **视觉清晰** - 层次分明，重点突出
3. **样式统一** - 使用一致的设计语言

## 🎨 设计原则

### 内容精炼 (Less is More)
- 严禁使用超过 3 行的长段落
- 使用短句、关键词，列表项控制在 2 行以内
- 标题要完整表达整页的核心思想

### 视觉优先
- 能用图不用表，能用表不用字
- 使用“大数字”作为视觉锚点
- 重要概念使用卡片封装

### 布局自由
你可以自由使用：
- 左右两栏布局
- 三卡片网格
- 列表 + 说明
- 表格对比

## 🚫 禁止事项

- ✘ 卡片左侧彩色竖条装饰
- ✘ 任何 Emoji 和 Unicode 图标（会导致 PPTX 乱码）
- ✘ 底部结论框 / "So What" 总结
- ✘ Footer 页脚（不要添加 "STRATEGIC RESEARCH REPORT"、页码、"CONFIDENTIAL" 等）
- ✘ 内容进入底部 80px 区域（已在画布约束中强调）
- ✘ 内容超出 1280px 宽度（已在画布约束中强调）
- ✘ **禁止使用以下字体**：'PingFang SC', 'Microsoft YaHei', 'Heiti SC', 'SimHei', 'SimSun'（这些字体在服务器上不可用！）
- ✘ **禁止自定义 font-family**：必须使用 prompt 中提供的字体族，不要自己编造
- ✘ **禁止使用 Markdown 语法**：不要使用 `**加粗**`、`*斜体*`、`__下划线__` 等 Markdown 语法！必须使用 HTML 标签如 `<strong>`、`<em>`
- ✘ **禁止添加"底部预留空间" div**：`padding-bottom: 80px` 已经处理了，不要再加 `height: 80px` 的空 div！
- ✘ **⚠️ 严禁使用廉价的红/绿对比色块！** 这是典型的 AI 俗套设计：
  - ❌ 浅红色背景 (#fef2f2, #fee2e2, rgba(254,242,242,...))
  - ❌ 浅绿色背景 (#f0fdf4, #dcfce7, rgba(240,253,244,...))
  - ❌ 红色文字 + 绿色文字对比（"信号灯"配色）
  - ❌ 任何红/绿并列的"好/坏""优/劣"对比设计

## ✅ 颜色规范（严格遵守！）

**背景色只能使用**：
- 白色 #ffffff
- 中性浅灰 #f5f7fa 或 #f3f4f6
- 主题色 + 高透明度（如 rgba(26,54,93,0.05)）

**强调色只能使用**：
- 主题色（如 #1A365D）
- 主题色的浅色变体
- ⚠️ **禁止使用红色和绿色作为对比色**

**边框只能使用**：
- 浅灰色 #e5e7eb
- 虚线 (dashed) 用于流程连接

## 📊 图表支持（ECharts - 鼓励使用！）

**当内容包含数据时，优先用 ECharts 图表呈现**，比纯文字更有说服力！

```html
<div style="width: 100%; max-width: 800px; height: 250px;" id="chart_唯一ID"></div>
<script>
(function() {
    var chart = echarts.init(document.getElementById('chart_唯一ID'));
    chart.setOption({
        animation: false,
        color: ['主题色'],
        grid: { top: 30, bottom: 30, left: 50, right: 20, containLabel: true },
        xAxis: { type: 'category', data: ['数据标签'] },
        yAxis: { type: 'value' },
        series: [{ data: [数据值], type: 'bar' 或 'line' }]
    });
})();
</script>
```

**图表使用指南**：
- ✅ **积极使用图表** - 有数据就放图表
- ✅ 图表高度建议 200px ~ 280px
- ✅ 图表容器必须设置 `max-width`，防止溢出
- ⚠️ 图表数据必须来自原始文档（不能编造）
- ⚠️ 极端情况下（剩余空间不足 150px），才考虑不放图表

## ✅ 输出要求

1. 使用内联样式 (style 属性)
2. 字体使用 var(--font-family) 或指定的字体族
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
    ) -> Dict[str, Any]:
        """
        生成大纲
        
        让 AI 根据文档内容自主规划：
        - 文档的最佳标题（干净、专业）
        - 分几个章节
        - 每章几页
        - 每页的核心观点
        
        返回:
            {
                "title": "AI 提取的干净标题",
                "pages": [{"type": "SECTION", "title": "...", "content": "..."}, ...]
            }
        """
        prompt = self._build_outline_prompt(context)
        # 大纲规划开启 Reasoning，让 AI 深度思考结构
        # 如果有图片，传递给 AI 进行多模态理解
        response = await self._call_ai(prompt, use_reasoning=True, images=context.images)
        return self._parse_outline(response)
    
    async def generate_page(
        self,
        context: GenerationContext,
        page_info: PageInfo,
        custom_image_prompt: Optional[str] = None
    ) -> str:
        """
        生成单页 HTML
        
        这是核心方法：让 AI 自由设计每一页
        """
        # 只在封面页和结尾页使用背景图（章节页保持纯色以节省 API 消耗）
        bg_image_url = None
        if context.bg_image_source != "none" and page_info.type in ["COVER", "CLOSING"]:
            try:
                print(f"DEBUG: Requesting background image for {page_info.type}, source={context.bg_image_source}, custom_prompt={custom_image_prompt[:20] if custom_image_prompt else 'None'}...")
                bg_image_url = await self._get_background_image(context, page_info, custom_image_prompt)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Background image generation failed: {e}")
                bg_image_url = None  # 失败时继续使用纯色背景
        
        prompt = self._build_page_prompt(context, page_info, bg_image_url)
        
        # 检查是否是直接返回的 HTML（避免 base64 图片导致 token 溢出）
        if prompt.startswith("__DIRECT_HTML__"):
            # 直接返回 HTML 模板，不需要调用 AI
            html = prompt.replace("__DIRECT_HTML__", "").strip()
            return self._clean_html(html)
        
        # 正常流程：调用 AI 生成 HTML，并清理 Markdown 语法
        html = await self._call_ai(prompt)
        return self._clean_html(html)
    
    async def _get_background_image(self, context: GenerationContext, page_info: PageInfo, custom_prompt: Optional[str] = None) -> Optional[str]:
        """获取页面背景图 - 仅用于封面和结尾页"""
        try:
            from v2.image_generator import get_image_generator
            
            generator = get_image_generator()
            source = "unsplash" if context.bg_image_source == "unsplash" else "ai"
            
            if page_info.type == "COVER":
                result = await generator.generate_cover_image(
                    title=page_info.title,
                    scenario=context.scenario,
                    source=source,
                    custom_prompt=custom_prompt
                )
            elif page_info.type == "CLOSING":
                result = await generator.generate_closing_image(
                    organization=context.organization,
                    scenario=context.scenario,
                    source=source,
                    custom_prompt=custom_prompt
                )
            else:
                result = None
            
            if result:
                return result.url
            return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to get background image: {e}")
            return None
    
    def _build_outline_prompt(self, context: GenerationContext) -> str:
        """构建大纲生成 Prompt"""
        
        # 用户自定义指令（如果有的话）
        custom_section = ""
        if context.custom_instructions and context.custom_instructions.strip():
            custom_section = f"""
## ⚠️ 用户特别要求（最高优先级！）

用户提供了以下特别要求，**你必须严格遵循**：

```
{context.custom_instructions}
```

**提示**：如果用户要求深入、全面、更多内容等，你可以根据需要突破目标页数限制。内容质量和用户满意度优先。
"""
        
        # 根据内容深度决定页数指导
        depth_guidance = {
            "brief": "精简版，只保留核心观点",
            "normal": "标准版，平衡内容和篇幅",
            "detailed": "深入版，充分展开论述，可适当增加页数"
        }
        depth_hint = depth_guidance.get(context.content_depth, depth_guidance["normal"])
        
        # 图片说明（如果有的话）
        image_section = ""
        if context.images and len(context.images) > 0:
            image_section = f"""
### 📷 文档附图（共 {len(context.images)} 张）

⚠️ **请仔细分析附带的图片**，这些图片来自原始文档：
- 图片可能包含重要的数据图表、框架图、流程图等
- 请从图片中提取关键信息，整合到大纲规划中
- 图表中的数据是可信的原始数据，可以在正文页中引用
"""
        
        return f"""
# 大纲规划任务

你是一位 **Cathy Wood 级别的顶级分析师** 和 **麦肯锡级别的战略顾问**。
请根据以下文档内容，规划一份 **专业、深入、有洞察力** 的演示文稿大纲。

## 输入信息

### 文档内容
```
{context.document_content[:50000]}
```
{image_section}
### 项目信息
- 文档名称：{context.document_name}
- 汇报单位：{context.organization}
- 场景类型：{context.scenario}
- 目标页数：约 {context.target_pages} 页（{depth_hint}）
- 内容深度：{context.content_depth}
{custom_section}

## 🎯 核心目标

你的任务是生成一份 **收费级别** 的专业报告大纲：
- **像券商研究报告** 那样细致全面
- **像麦肯锡战略报告** 那样有框架有洞察
- **每一页都要有信息量**，绝不注水

## ⚠️ 页数硬性要求（必须遵守！）

**你必须生成 {context.target_pages} 页左右的大纲！**

- 最少不能低于 {int(context.target_pages * 0.9)} 页
- 如果原始内容不够，你必须扩充内容来达到页数要求
- 不要自作主张减少页数，用户已经明确选择了 {context.target_pages} 页
- 每个章节可以有多个 CONTENT 页，确保总页数达标

## 规划原则

### 1. 金字塔结构
- 整体遵循"总-分-总"的逻辑
- 每个章节有明确的核心观点
- 从宏观到微观，层层递进

### 2. 内容深度
- 每页只讲一个核心观点
- 复杂内容要拆分成多页（宁多勿少）
- 数据密集的内容单独成页
- **如果内容丰富，不要压缩，该用多少页就用多少页**

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

### 5. 内容扩充（⚠️ 严格限制）

如果原始文档内容不够丰富，你 **可以** 基于专业知识补充**文字性内容**：
- ✅ 补充行业背景知识和趋势分析
- ✅ 解释专业概念和术语
- ✅ 提供框架性分析和逻辑推理
- ✅ 给出定性的建议和行动方向

**⚠️ 严禁编造数据！这是最高优先级的禁令！**
- ❌ **绝对禁止编造任何具体数字**（如 "98.5%"、"同比增长 35%"、"4.9/5.0 评分"）
- ❌ **禁止捏造统计数据**（如 "市场规模 XX 亿"、"渗透率达 XX%"）
- ❌ **禁止虚构案例数据**（如 "销售额增长 X 倍"、"客户满意度 XX%"）
- 如果页面需要数据支撑但原文没有，使用定性描述代替：
  - ❌ "客户满意度达 98.5%" → ✅ "客户满意度持续提升"
  - ❌ "效率提升 35%" → ✅ "效率显著提升"
  - ❌ "市场规模 500 亿" → ✅ "市场规模快速增长"

### 6. 无数据时的视觉化策略

当原始文档缺乏具体数据时，使用以下**概念可视化**手段增强页面吸引力（不是编造数据！）：

**✅ 推荐使用**：
- **流程图/时间轴** - 用 HTML 盒子 + 箭头(→)展示步骤、阶段、发展历程
- **对比布局** - 左右对比（现状 vs 目标、问题 vs 方案、挑战 vs 对策）
- **金字塔/层级图** - 展示优先级、重要性层级
- **矩阵/象限** - 分类对比（如重要/紧急四象限）
- **关键词大字突出** - 核心概念用 36px+ 字体，配合小字解释
- **卡片网格** - 将要点用等大卡片呈现，视觉均衡
- **引言/金句框** - 用引号和浅色背景突出核心观点
- **序号标记** - 用 CSS 圆形/方形作为视觉锚点

## 输出格式

**必须严格按照以下顺序输出每一行（不要包含 markdown 代码块标记）：**

1. `TITLE|干净的演示文稿标题`
2. `REPORT_TYPE|报告类型标签`（2-8个字，如"产业研究报告"、"年度述职报告"、"项目可行性分析"）
3. `ORG_NAME|汇报单位名称`（从内容中提取，如"哈尔滨工业大学"、"某某科技有限公司"）
4. `COVER_IMG|封面图Prompt`
5. `CLOSING_IMG|封底图Prompt`
6. `SECTION|...` (章节)
7. `CONTENT|...`
...

**格式说明**：
- `TITLE`：提取的核心标题
- `REPORT_TYPE`：**根据内容智能提炼**的报告类型标签，2-8个字。示例：
  - 产业研究报告、行业深度分析、战略规划方案
  - 年度述职报告、季度工作总结、项目进展汇报
  - 开题报告、毕业论文答辩、学术研究汇报
  - 如果无法确定，输出空：`REPORT_TYPE|`
- `ORG_NAME`：**从文档内容中提取**的汇报单位/作者单位。优先级：
  1. 文档中明确提到的机构名称
  2. 作者所属单位
  3. 如果用户提供了汇报单位，使用用户提供的：{context.organization}
  4. 如果都找不到，输出空：`ORG_NAME|`
- `COVER_IMG`：封面图 ComfyUI 提示词（Symbolic Realism 风格，微距摄影）
- `CLOSING_IMG`：封底图提示词

**示例**：
TITLE|全球自动驾驶产业格局深度研究
REPORT_TYPE|产业研究报告
ORG_NAME|前瞻产业研究院
COVER_IMG|view from driver's seat inside a modern car, hands on steering wheel, motion blur city road ahead, realistic photography, evening, 4k, no text
CLOSING_IMG|empty highway road marking leading to infinity, sunset horizon, cinematic lighting, conceptual, realistic, no text
SECTION|第一部分 产业现状|
CONTENT|战新产业占比突破 40%，产业结构持续优化|2023年数据
SECTION|第二部分 核心问题|
CONTENT|研发投入不足是制约发展的首要瓶颈|全区研发强度仅2.1%

请开始规划（严格遵循格式）：
"""
    
    def _parse_outline(self, response: str) -> Dict[str, Any]:
        """解析大纲响应"""
        lines = response.strip().split('\n')
        title = "未命名演示文稿"
        report_type = ""  # AI 提炼的报告类型
        org_name = ""     # AI 提炼的汇报单位
        cover_prompt = ""
        closing_prompt = ""
        pages = []
        
        current_section_num = 0
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 去除可能的 markdown 标记
            line = line.replace('```', '')
            
            parts = line.split('|')
            if len(parts) < 2: continue
            
            type_ = parts[0].strip().upper()
            content = parts[1].strip()
            extra = parts[2].strip() if len(parts) > 2 else ""
            
            if type_ == "TITLE":
                title = content
            elif type_ == "REPORT_TYPE":
                report_type = content
            elif type_ == "ORG_NAME":
                org_name = content
            elif type_ == "COVER_IMG":
                cover_prompt = content
            elif type_ == "CLOSING_IMG":
                closing_prompt = content
            elif type_ == "SECTION":
                current_section_num += 1
                pages.append({
                    "type": "SECTION",
                    "title": content,
                    "content": extra,
                    "section_num": current_section_num
                })
            elif type_ == "CONTENT":
                pages.append({
                    "type": "CONTENT",
                    "title": content,
                    "content": extra,
                    "section_num": current_section_num
                })
                
        return {
            "title": title,
            "report_type": report_type,
            "org_name": org_name,
            "cover_image_prompt": cover_prompt,
            "closing_image_prompt": closing_prompt,
            "pages": pages
        }
    
    def _build_page_prompt(self, context: GenerationContext, page_info: PageInfo, bg_image_url: str = None) -> str:
        """构建页面生成 Prompt - 这是最核心的部分"""
        
        # 获取设计系统描述
        design_prompt = context.design_system.get_ai_prompt()
        design_tokens = context.design_system.get_tokens()
        colors = design_tokens.colors.to_dict()
        
        # 获取字体配置 - 根据 font_style 动态选择
        font_family = design_tokens.typography.font_family_base
        
        # 根据页面类型选择不同的 Prompt 策略
        if page_info.type == "COVER":
            return self._build_cover_prompt(context, page_info, design_prompt, colors, font_family, bg_image_url)
        elif page_info.type == "AGENDA":
            return self._build_agenda_prompt(context, page_info, design_prompt, colors, font_family)
        elif page_info.type == "SECTION":
            # 章节页使用纯色背景（不使用背景图以节省 API 消耗）
            return self._build_section_prompt(context, page_info, design_prompt, colors, font_family)
        elif page_info.type == "CLOSING":
            return self._build_closing_prompt(context, page_info, design_prompt, colors, font_family, bg_image_url)
        else:
            return self._build_content_prompt(context, page_info, design_prompt, colors, font_family)
    
    def _build_cover_prompt(
        self, context: GenerationContext, page_info: PageInfo, 
        design_prompt: str, colors: Dict[str, str], font_family: str,
        bg_image_url: str = None
    ) -> str:
        """封面页 Prompt - 内联样式，支持背景图"""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月")
        
        # 判断是否使用背景图
        if bg_image_url:
            # 有背景图时：直接返回完整的 HTML 模板
            return f"""__DIRECT_HTML__
<div style="width: 1280px; height: 720px; background: url('{bg_image_url}') center/cover no-repeat; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; box-sizing: border-box; font-family: {font_family}; position: relative; overflow: hidden;">
    <!-- 暗色蒙版 - 让文字更可读 -->
    <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.4) 100%);"></div>
    
    <!-- 内容层 -->
    <div style="position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1;">
        <h1 style="font-size: 52px; font-weight: 700; color: #ffffff; text-align: center; margin: 0; max-width: 1000px; line-height: 1.3; text-shadow: 0 2px 20px rgba(0,0,0,0.3);">{page_info.title}</h1>
        
        <!-- 装饰线 -->
        <div style="width: 100px; height: 4px; background: rgba(255,255,255,0.8); margin: 36px 0; border-radius: 2px;"></div>
    </div>
    
    <!-- 底部信息 -->
    <div style="position: absolute; bottom: 50px; left: 60px; right: 60px; display: flex; justify-content: space-between; font-size: 15px; color: rgba(255,255,255,0.9); z-index: 1;">
        <span>汇报单位：{context.organization}</span>
        <span>{current_date}</span>
    </div>
</div>
"""
        else:
            # 无背景图：使用简洁的高级版式
            # 使用 AI 提炼的报告类型和汇报单位，如果没有则使用备选
            report_type_text = context.report_type if context.report_type else ""
            org_text = context.ai_org_name if context.ai_org_name else context.organization
            
            # 报告类型徽章（如果有的话）
            badge_html = ""
            if report_type_text:
                badge_html = f'''
        <div class="cover-badge">
            <span class="badge-text">{report_type_text}</span>
        </div>'''
            
            return f"""__DIRECT_HTML__
<div class="slide slide-cover">
    <!-- 装饰元素 -->
    <div class="left-bar"></div>
    <div class="top-deco"></div>
    
    <!-- 内容区域 -->
    <div class="cover-content">{badge_html}

        <h1 class="cover-title">{page_info.title}</h1>

        <div class="cover-info-grid">
            <div class="cover-footer-item">
                <span class="cover-label">汇报单位</span>
                <span class="cover-value">{org_text}</span>
            </div>
            <div class="cover-footer-item">
                <span class="cover-label">日期</span>
                <span class="cover-value">{current_date}</span>
            </div>
        </div>
    </div>
</div>
"""

    def _build_agenda_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str], font_family: str
    ) -> str:
        """目录页 Prompt - 内联样式"""
        return f"""
# 目录页设计

## 章节列表
{page_info.content}

## 设计要求

- 纯白背景
- 标题"目录 / CONTENTS" 32px
- 每个章节一行：序号 + 标题
- 序号用主色 {colors['primary']}
- 分割线用浅灰色
- 可以用左右两栏布局（如果章节超过5个）

## ⚠️ 禁止事项

- ❌ **禁止添加任何概括性文字、引言或总结！**
- ❌ 不要添加类似"本报告旨在..."、"本文档主要介绍..."的描述
- ❌ 目录页只放目录，不放其他任何内容！

## 输出

直接输出 HTML，只包含标题和章节列表，不要任何额外文字：

<div style="width: 1280px; height: 720px; background: #ffffff; padding: 60px; box-sizing: border-box; font-family: {font_family};">
    <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0 0 40px 0;">目录 / CONTENTS</h1>
    <div style="display: flex; flex-direction: column; gap: 20px;">
        <!-- 每个章节一行 -->
        <div style="display: flex; align-items: center; gap: 24px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb;">
            <span style="font-size: 24px; font-weight: 700; color: {colors['primary']}; min-width: 40px;">01</span>
            <span style="font-size: 20px; color: {colors['text_primary']};">章节标题</span>
        </div>
        <!-- 以此类推，只放章节，不放其他内容！ -->
    </div>
</div>
"""

    def _build_section_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str], font_family: str
    ) -> str:
        """章节页 Prompt - 纯色背景（不使用背景图以节省 API 消耗）"""
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

<div style="width: 1280px; height: 720px; background: {colors['primary']}; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family};">
    <div style="font-size: 72px; font-weight: 300; color: rgba(255,255,255,0.3); margin-bottom: 16px;">0{section_num}</div>
    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.5); margin-bottom: 24px;"></div>
    <h1 style="font-size: 36px; font-weight: 700; color: #ffffff; margin: 0;">{page_info.title}</h1>
</div>
"""

    def _build_closing_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str], font_family: str,
        bg_image_url: str = None
    ) -> str:
        """封底页 Prompt - 内联样式，支持背景图"""
        
        # 使用 AI 提炼的汇报单位，如果没有则使用用户填写的
        org_text = context.ai_org_name if context.ai_org_name else context.organization
        
        if bg_image_url:
            # 有背景图：直接返回完整的 HTML 模板
            return f"""__DIRECT_HTML__
<div style="width: 1280px; height: 720px; background: url('{bg_image_url}') center/cover no-repeat; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family}; position: relative;">
    <!-- 蒙版 -->
    <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.4) 100%);"></div>
    
    <!-- 内容 -->
    <div style="position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center;">
        <div style="font-size: 72px; font-weight: 700; color: #ffffff; margin-bottom: 32px; letter-spacing: 8px; text-shadow: 0 2px 20px rgba(0,0,0,0.3);">谢谢</div>
        <div style="width: 80px; height: 4px; background: rgba(255,255,255,0.7); margin-bottom: 32px; border-radius: 2px;"></div>
        <div style="font-size: 20px; color: rgba(255,255,255,0.9);">{org_text}</div>
    </div>
</div>
"""
        else:
            # 无背景图：直接返回 HTML 模板
            return f"""__DIRECT_HTML__
<div style="width: 1280px; height: 720px; background: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family}; position: relative;">
    <!-- 顶部装饰 -->
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 8px; background: {colors['primary']}; opacity: 0.6;"></div>

    <div style="font-size: 64px; font-weight: 700; color: {colors['primary']}; margin-bottom: 32px; letter-spacing: 4px;">谢谢</div>
    
    <div style="width: 60px; height: 4px; background: {colors['text_secondary']}; margin-bottom: 32px; opacity: 0.3;"></div>
    
    <div style="font-size: 18px; color: {colors['text_secondary']};">{org_text}</div>
    
    <!-- 底部装饰 -->
    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 24px; background: {colors['primary']};"></div>
</div>
"""

    def _build_content_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str], font_family: str
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
5. **⚠️ 严禁编造数据！** - 所有数字必须来自上面的"参考素材"
   - 不要凭空编造任何具体数字（如"98.5%"、"增长35%"）
   - 如果素材中没有数据支撑，使用定性描述（如"显著提升"、"大幅增长"）
6. **⚠️ 禁止添加"底部预留空间" div！** - `padding-bottom: 80px` 已经处理了底部空间，不要再添加任何 `height: 80px` 的空 div！

## 无数据时的视觉化策略（重要！用代码绘制！）

当"参考素材"缺乏具体数据时，**必须使用 CSS 绘制视觉元素**来增强页面，不要只放纯文字！

### 流程图模板（横向，用 flexbox 绘制）
```html
<div style="display: flex; align-items: center; justify-content: space-between; padding: 30px; background: #f5f7fa; border-radius: 8px;">
    <div style="text-align: center; flex: 1;">
        <div style="font-size: 14px; color: #6b7280;">阶段一</div>
        <div style="font-size: 20px; font-weight: 700; color: #1A365D; margin-top: 8px;">核心概念</div>
    </div>
    <div style="color: #cbd5e1; font-size: 24px; padding: 0 15px;">→</div>
    <div style="text-align: center; flex: 1;">
        <div style="font-size: 14px; color: #6b7280;">阶段二</div>
        <div style="font-size: 20px; font-weight: 700; color: #1A365D; margin-top: 8px;">下一步</div>
    </div>
    <div style="color: #cbd5e1; font-size: 24px; padding: 0 15px;">→</div>
    <div style="text-align: center; flex: 1;">
        <div style="font-size: 14px; color: #6b7280;">阶段三</div>
        <div style="font-size: 20px; font-weight: 700; color: #1A365D; margin-top: 8px;">最终目标</div>
    </div>
</div>
```

### 对比布局模板（左右两栏）
```html
<div style="display: flex; gap: 40px;">
    <div style="flex: 1; padding: 30px; border: 1px solid #e5e7eb; border-radius: 8px;">
        <div style="font-size: 18px; font-weight: 700; color: #1A365D; margin-bottom: 20px;">现状/问题</div>
        <p style="color: #4b5563; line-height: 1.6;">描述当前状态或挑战...</p>
    </div>
    <div style="display: flex; align-items: center; color: #cbd5e1; font-size: 32px;">→</div>
    <div style="flex: 1; padding: 30px; background: #f5f7fa; border-radius: 8px;">
        <div style="font-size: 18px; font-weight: 700; color: #1A365D; margin-bottom: 20px;">目标/方案</div>
        <p style="color: #4b5563; line-height: 1.6;">描述目标状态或解决方案...</p>
    </div>
</div>
```

### 时间轴模板（CSS 绘制的圆点和线条）
```html
<div style="display: flex; align-items: flex-start; justify-content: space-between; position: relative; padding-top: 40px;">
    <!-- 连接线 -->
    <div style="position: absolute; top: 48px; left: 10%; right: 10%; height: 2px; background: #e5e7eb;"></div>
    <!-- 节点1 -->
    <div style="text-align: center; flex: 1; position: relative;">
        <div style="width: 16px; height: 16px; background: #1A365D; border-radius: 50%; margin: 0 auto 15px;"></div>
        <div style="font-size: 14px; color: #6b7280;">2024</div>
        <div style="font-size: 16px; font-weight: 600; color: #1A365D; margin-top: 5px;">里程碑一</div>
    </div>
    <!-- 更多节点... -->
</div>
```

### 关键词大字模板
```html
<div style="text-align: center; padding: 40px;">
    <div style="font-size: 48px; font-weight: 700; color: #1A365D; margin-bottom: 15px;">核心概念词</div>
    <div style="font-size: 18px; color: #6b7280; max-width: 600px; margin: 0 auto;">对这个概念的简短解释说明</div>
</div>
```

⚠️ **优先使用以上 CSS 模板绘制视觉元素，不要只放纯文字列表！**
{f'''
## 用户特别要求

用户提供了以下风格/内容偏好，请在设计时参考：

```
{context.custom_instructions}
```

请在遵守上述设计规范的前提下，尽量满足用户的要求。
''' if context.custom_instructions and context.custom_instructions.strip() else ''}

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

## 颜色（严格限制！）

**主题色**：
- 主色：{colors['primary']}
- 主文字：{colors['text_primary']}
- 次文字：{colors['text_secondary']}

**背景色只能用**：
- 白色 #ffffff
- 浅灰 #f5f7fa
- ⚠️ **禁止浅红色 (#fef2f2, #fee2e2)、浅绿色 (#f0fdf4, #dcfce7)！** 这是廉价 AI 设计

**特殊场景才用**：
- 成功色 {colors['success']}（仅用于真实的增长数据 ↑）
- 危险色 {colors['danger']}（仅用于真实的下降数据 ↓）
- ⚠️ **禁止红绿对比的"优劣对比"设计！**

## 图表（鼓励使用！）

**当"参考素材"中有数据时，优先使用 ECharts 图表来呈现**，图表比纯文字更有说服力！

📊 **图表使用指南**：
- ✅ **积极使用图表** - 有数据就放图表，视觉效果更好
- ✅ 图表高度建议 200px ~ 250px，保证可读性
- ✅ 数据必须来自参考素材（不能编造）
- ⚠️ 如果页面内容已经很满，图表可以适当缩小到 180px
- ⚠️ 极端情况下（剩余空间不足 150px），才考虑不放图表

```html
<div style="width: 100%; max-width: calc(100% - 120px); height: 220px;" id="chart_page{page_info.page_num}"></div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_page{page_info.page_num}'));
    chart.setOption({{
        animation: false,
        color: ['{colors["primary"]}', '{colors["accent"]}'],
        grid: {{ top: 30, bottom: 25, left: 45, right: 15, containLabel: true }},
        xAxis: {{ type: 'category', data: ['标签'] }},
        yAxis: {{ type: 'value' }},
        series: [{{ data: [数值], type: 'bar' }}]
    }});
}})();
</script>
```

## 输出

直接输出完整 HTML（注意：`padding-bottom: 80px` 已经预留了底部空间，**不要再添加额外的底部 div**！）：

<div style="width: 1280px; height: 720px; background: #ffffff; padding: 50px 60px 80px; box-sizing: border-box; font-family: {font_family}; display: flex; flex-direction: column; overflow: hidden;">
    <!-- 标题区 -->
    <div style="margin-bottom: 24px; flex-shrink: 0; max-width: 100%;">
        <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0; line-height: 1.3;">标题（核心观点）</h1>
        <p style="font-size: 16px; color: {colors['text_secondary']}; margin: 8px 0 0 0;">副标题/引导语</p>
    </div>
    
    <!-- 内容区 - 直接放内容，不要添加任何 "底部预留" 的 div！ -->
    <div style="flex: 1; display: flex; gap: 32px; overflow: hidden; max-width: 100%;">
        <!-- 你的创意内容 -->
    </div>
    
    <!-- ⚠️ 不要在这里添加任何 "底部预留空间" 的 div！padding-bottom: 80px 已经处理了！ -->
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

    async def _call_ai(self, prompt: str, retry_count: int = 0, use_reasoning: bool = False, images: List[Dict] = None) -> str:
        """调用 AI API
        
        Args:
            prompt: 用户提示词
            retry_count: 当前重试次数
            use_reasoning: 是否开启 Reasoning（仅对支持的模型如 gemini-3-flash-preview 生效）
            images: 图片列表（可选）[{'data_url': 'data:image/...', 'content_type': '...'}]
        """
        try:
            # 构建用户消息内容
            if images and len(images) > 0:
                # 多模态请求：包含文本和图片
                user_content = [
                    {"type": "text", "text": prompt}
                ]
                
                # 添加图片（最多 5 张，避免请求过大）
                for img in images[:5]:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": img['data_url'],
                            "detail": "low"  # 使用低分辨率节省 token
                        }
                    })
                
                console.print(f"[cyan]📷 多模态请求：包含 {min(len(images), 5)} 张图片[/cyan]")
            else:
                # 纯文本请求
                user_content = prompt
            
            # 构建基础请求参数
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                "temperature": self.temperature,
                "max_tokens": 16000,  # 增加输出长度限制，支持 80+ 页大纲
            }
            
            # 如果开启 Reasoning，添加 extra_body 参数
            if use_reasoning:
                request_params["extra_body"] = {
                    "reasoning": {"enabled": True}
                }
                console.print("[cyan]🧠 Reasoning 模式已开启，AI 正在深度思考...[/cyan]")
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(**request_params),
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
                return await self._call_ai(prompt, retry_count + 1, use_reasoning, images)
            raise
        
        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = 2 * (retry_count + 1)
                console.print(f"[yellow]⚠ 失败: {str(e)[:80]}，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._call_ai(prompt, retry_count + 1, use_reasoning, images)
            raise



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
        
        # 转换 Markdown 加粗语法 **text** 为 HTML <strong> 标签
        # 使用非贪婪匹配 (.*?) 并允许跨行 (re.DOTALL)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html, flags=re.DOTALL)
        
        # 转换 Markdown 加粗 __text__ 为 HTML <strong> 标签
        html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html, flags=re.DOTALL)
        
        # 也处理 Markdown 斜体 *text* 转换为 <em>（可选，但保持一致性）
        # 注意：这个模式要小心，只替换单独的 *text*，不要影响 CSS 选择器等
        # html = re.sub(r'(?<![*])\*([^*]+)\*(?![*])', r'<em>\1</em>', html)
        
        # ============================================
        # 字体清理：移除或替换不可用的字体声明
        # 这些字体在 Docker 服务器上不存在，会导致 Type3 字体问题
        # ============================================
        unavailable_font_patterns = [
            r"'PingFang SC'",
            r'"PingFang SC"',
            r"'Microsoft YaHei'",
            r'"Microsoft YaHei"',
            r"'Heiti SC'",
            r'"Heiti SC"',
            r"'SimHei'",
            r'"SimHei"',
            r"'SimSun'",
            r'"SimSun"',
            r"'Hiragino Sans GB'",
            r'"Hiragino Sans GB"',
        ]
        
        for pattern in unavailable_font_patterns:
            # 移除这些字体（保留字体列表中的其他字体）
            html = re.sub(rf"{pattern},?\s*", "", html)
            html = re.sub(rf",\s*{pattern}", "", html)
        
        # 如果 font-family 变成只剩 sans-serif 或 serif，添加可用的中文字体
        # 匹配类似 font-family: sans-serif 或 font-family: serif
        html = re.sub(
            r"font-family:\s*sans-serif",
            "font-family: 'Noto Sans CJK SC', sans-serif",
            html
        )
        html = re.sub(
            r"font-family:\s*serif",
            "font-family: 'AR PL UKai CN', 'Noto Serif CJK SC', serif",
            html
        )
        
        # ============================================
        # 移除 AI 可能错误添加的 "底部预留空间" div
        # 因为外层容器已经有 padding-bottom: 80px，不需要额外的 div
        # ============================================
        # 匹配类似: <!-- 底部预留空间 -->\n    <div style="height: 80px; ..."></div>
        html = re.sub(
            r'<!--\s*底部预留空间\s*-->\s*<div[^>]*height:\s*80px[^>]*>\s*</div>',
            '',
            html,
            flags=re.IGNORECASE
        )
        # 也匹配没有注释的情况
        html = re.sub(
            r'<div\s+style="height:\s*80px;\s*flex-shrink:\s*0;?">\s*</div>',
            '',
            html,
            flags=re.IGNORECASE
        )
        
        # ============================================
        # 替换廉价的红/绿背景色为中性灰
        # 这些是典型的 AI 俗套设计
        # ============================================
        cheap_color_replacements = [
            # 浅红色背景 -> 中性浅灰
            (r'background:\s*#fef2f2', 'background: #f5f7fa'),
            (r'background:\s*#fee2e2', 'background: #f5f7fa'),
            (r'background:\s*#fecaca', 'background: #f5f7fa'),
            (r'background-color:\s*#fef2f2', 'background-color: #f5f7fa'),
            (r'background-color:\s*#fee2e2', 'background-color: #f5f7fa'),
            # 浅绿色背景 -> 中性浅灰
            (r'background:\s*#f0fdf4', 'background: #f5f7fa'),
            (r'background:\s*#dcfce7', 'background: #f5f7fa'),
            (r'background:\s*#bbf7d0', 'background: #f5f7fa'),
            (r'background-color:\s*#f0fdf4', 'background-color: #f5f7fa'),
            (r'background-color:\s*#dcfce7', 'background-color: #f5f7fa'),
            # 红色文字 -> 主题色（保留 ef4444 用于真正的危险/下降指示）
            (r'color:\s*#dc2626', 'color: #1A365D'),
            (r'color:\s*#b91c1c', 'color: #1A365D'),
            # 绿色文字 -> 主题色（保留 10b981 用于真正的成功/上升指示）
            (r'color:\s*#16a34a', 'color: #1A365D'),
            (r'color:\s*#15803d', 'color: #1A365D'),
            (r'color:\s*#22c55e', 'color: #1A365D'),
        ]
        
        for pattern, replacement in cheap_color_replacements:
            html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
        
        return html.strip()
