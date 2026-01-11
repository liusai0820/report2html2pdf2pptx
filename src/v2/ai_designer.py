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
from .prompts import build_speech_prompt, get_detail_config, SCENARIO_PROMPTS, SCENARIO_ALIASES, get_scenario_prompts

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
    image_indices: List[int] = None  # 该页关联的图片索引列表（0-indexed）


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
    image_descriptions: List[str] = None  # 预解析的图片内容描述（每张图片的详细文字提取）


# ============================================================================
# 核心 Prompt：这是"元指令"，告诉 AI 它是一个设计师
# ============================================================================

DESIGNER_SYSTEM_PROMPT = """
# Role: Senior Information Designer (Swiss Style) & Data Analyst (McKinsey)

## 🗣️ LANGUAGE (Dominant: Chinese)
- **Output Language**: Simplified Chinese (简体中文).
- **Translation**: Translate ALL structural terms (e.g., "Strategy", "Overview", "Timeline") into professional Chinese business terminology.
- **Exceptions**: Keep specific English proper nouns (e.g., "AI", "SaaS", "GDP") if they are standard industry terms.
- **NO Bilingual Redundancy**:
   - ❌ NO English subtitles/translations below Chinese titles (e.g., "战略\nStrategy").
   - ❌ NO English parentheticals (e.g., "转化率 (Conversion Rate)" -> "转化率").
   - ❌ NO "Chinese Title | English Title".
   - **Rule**: If it's in Chinese, DO NOT add English translation.

## 🎯 DESIGN PHILOSOPHY (High Information Density)
1. **Pyramid Principle (SCQA)**: ONE key message per slide. Title is the Conclusion.
2. **Swiss International Style**: Mathematical grids (Bento Box), asymmetric balance, high contrast typography.
3. **Defensive CSS Layout**:
   - Use `flexbox` or `grid` for EVERYTHING.
   - `* { box-sizing: border-box; min-width: 0; min-height: 0; }` (Prevent overflow).
   - Images: `object-fit: contain; max-width: 100%; max-height: 100%;`.
   - Containers: `overflow: hidden;` is MANDATORY.
   - **Global**: `::-webkit-scrollbar { display: none; }` (No scrollbars allowed).
4. **Data Visualization**: "A chart is worth 1000 words." Use ECharts for ALL data.

## 🛡️ CANVAS LAWS (Immutable)
- **Dimensions**: 1280px × 720px (Fixed).
- **Safe Zone**: Padding 60px. **Bottom 80px is RESERVED (No Content).**
- **Typography**: Use var(--font-family). NO custom fonts. NO Markdown.
- **Colors**: Professional Palette only. NO "Traffic Light" (Red/Green) combinations.
- **Unified Header (Content Pages)**: Title MUST be top-left (32px). Section pages use Centered layout.

## 🚫 STRICT BANS
- NO Scrollbars (Static Page).
- NO Overflow (Content MUST fit 590px height).
- **NO Footers / Page Numbers / Confidential marks** (Leave bottom 80px empty).
- NO Emoji/Unicode icons.
- NO Gradients/Shadows (Flat Design only).
- NO "Bottom Spacer" divs.
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
    
    async def analyze_images(self, images: List[Dict]) -> List[str]:
        """
        【图片预解析阶段】- 提取每张图片的完整文字和结构信息
        
        这是关键步骤：确保图片中的所有文字、数据、关系都被精确提取，
        而不是让 AI 在后续步骤中"看"图片然后遗忘细节。
        
        使用并行调用加速处理。
        
        Args:
            images: 图片列表 [{'data_url': '...', 'content_type': '...'}]
            
        Returns:
            每张图片的完整内容描述列表
        """
        if not images:
            return []
        
        console.print(f"[cyan]🔍 并行解析 {len(images)} 张图片内容...[/cyan]")

        prompt = """
# TASK: Visual Semantic Extraction (OCR + Structural Analysis)

## TARGET
Convert image pixels into a structured "Digital Twin" text format for HTML reconstruction.

## REQUIREMENTS
1. **OCR Precision**: Extract ALL visible text. Don't summarize.
2. **Structure Detection**: Identify the layout pattern (Matrix, Flow, Hierarchy, Quadrant).
3. **Data Integrity**: Preserve exact numbers, units, and labels.
4. **Entity Recognition**: List specific proper nouns (Companies, Products, Locations).

## OUTPUT TEMPLATE
```
[TYPE]: {Visual Pattern Name, e.g., 2x2 Matrix, Flowchart, Bar Chart}
[TITLE]: {Main Heading}
[SUBTITLE]: {Subheading or Context}
[CONTENT_TREE]:
- {Group/Section Name}:
  - {Item 1}
  - {Item 2}
[DATA_POINTS]:
- {Label}: {Value} (if chart/graph)
[ENTITIES]: {Comma-separated list of specific names found}
[VISUAL_CUES]: {Color coding, Arrows, Layout relationships}
```
"""

        async def analyze_single_image(i: int, img: Dict) -> str:
            """分析单张图片"""
            try:
                response = await self._call_ai(prompt, images=[img])
                console.print(f"[green]   ✓ 图片 {i+1} 解析完成[/green]")
                return response
            except Exception as e:
                console.print(f"[yellow]   ⚠️ 图片 {i+1} 解析失败: {e}[/yellow]")
                return f"[图片 {i+1} 解析失败]"
        
        # 并行调用 AI 解析所有图片
        tasks = [analyze_single_image(i, img) for i, img in enumerate(images)]
        descriptions = await asyncio.gather(*tasks)
        
        console.print(f"[green]✓ 全部 {len(images)} 张图片并行解析完成[/green]")
        return list(descriptions)
    
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

        # 【方案 C】描述 + 图片双保险
        # prompt 中已包含预解析的图片描述，同时发送原图供 AI 验证
        images_to_pass = None
        if page_info.type == "CONTENT" and context.images and len(context.images) > 0:
            if page_info.image_indices:
                images_to_pass = []
                for idx in page_info.image_indices:
                    if 0 <= idx < len(context.images):
                        images_to_pass.append(context.images[idx])
                if images_to_pass:
                    console.print(f"[cyan]📷 页面 {page_info.page_num}：描述+图片双保险（{len(images_to_pass)} 张图）[/cyan]")
        
        # 调用 AI：prompt 包含描述，images 包含原图
        html = await self._call_ai(prompt, images=images_to_pass)
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
        """构建大纲生成 Prompt - High Density"""

        # 获取场景专有 Prompt
        scenario_prompts = get_scenario_prompts(context.scenario)
        scenario_guide = scenario_prompts.get("outline_guide", "")

        # User Custom Instructions
        custom_block = ""
        if context.custom_instructions and context.custom_instructions.strip():
            custom_block = f"""
## 👤 USER OVERRIDE (Top Priority)
{context.custom_instructions}
"""

        # Image Context
        img_context = ""
        if context.images:
            img_desc = ""
            # 如果有预解析的图片描述，提取前200字作为摘要
            if context.image_descriptions:
                img_desc = "\n".join([f"- Image {i+1}: {d[:100]}..." for i, d in enumerate(context.image_descriptions)])

            img_context = f"""
## 📷 VISUAL ASSETS ({len(context.images)} Images)
The user provided images. You MUST include them in the outline using `[IMG:1,2]` tags in CONTENT lines.
{img_desc}
"""

        depth_map = {
            "brief": "Executive Summary (High Level)",
            "normal": "Standard Consulting Report",
            "detailed": "Deep Dive Research (Comprehensive)"
        }
        style = depth_map.get(context.content_depth, "Standard Consulting Report")

        return f"""
# TASK: Architect a {style} Presentation Structure

## 🗣️ LANGUAGE: Simplified Chinese (简体中文)
**ALL output must be in Chinese**, except for specific English proper nouns (e.g., AI, SaaS).
**Strict Rule**: NO bilingual titles. NO "中文 (English)". NO "Title | 标题". If a term has a Chinese equivalent, use Chinese ONLY.
{scenario_guide}
## 📄 INPUT CONTEXT
**Doc Name**: {context.document_name}
**Org**: {context.organization}
**Target**: ~{context.target_pages} Pages
**Content**:
```
{context.document_content[:50000]}
```
{custom_block}
{img_context}

## 🧠 STRUCTURING LOGIC (McKinsey/Bain Style)

1.  **Pyramid Principle**:
    - Top-down structure.
    - Title = Core Message (Conclusion), NOT Topic.
    - Example: ✅ "营收同比增长20%" vs ❌ "营收分析".

2.  **Narrative Arc (SCQA)**:
    - **S**ituation (现状)
    - **C**omplication (问题/机会)
    - **Q**uestion (挑战)
    - **A**nswer (方案/路线图)

3.  **MECE**: Ensure sections are Mutually Exclusive, Collectively Exhaustive.

4.  **Content Density**:
    - **No Fluff**. Every page must deliver value.
    - If source is thin, **Synthesize** using domain knowledge (Trends, Frameworks, Best Practices).
    - **Strict Ban**: DO NOT hallucinate specific numbers. Use qualitative terms (High Growth, Significant Share) if data is missing.

## 📐 OUTPUT FORMAT (Strict Line-by-Line)

1. `TITLE|...` (Professional Title in Chinese)
2. `REPORT_TYPE|...` (e.g., 战略规划, 行业分析)
3. `ORG_NAME|...` (Extracted or inferred)
4. `COVER_IMG|...` (ComfyUI Prompt: Realistic, Cinematic, No Text)
5. `CLOSING_IMG|...` (ComfyUI Prompt: Abstract, Hopeful)
6. `SECTION|...`
7. `CONTENT|Title (Message)|Details [IMG:x]`

**Example**:
TITLE|2025数字化转型战略规划
REPORT_TYPE|战略规划报告
ORG_NAME|某某科技集团
COVER_IMG|futuristic office with holographic data interface, cinematic lighting
CLOSING_IMG|sunrise over smart city skyline, hopeful atmosphere
SECTION|01 市场格局|Context
CONTENT|AI在各行业应用加速渗透|关键驱动力：效率、创新 [IMG:1]
SECTION|02 核心挑战|Problem
CONTENT|传统架构限制了业务敏捷性|技术债务分析

**Constraint**: Target ~{context.target_pages} pages.

Begin Architecture:
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
                # 从 extra 中提取图片索引标记 [IMG:1,2,3]
                image_indices = []
                content_text = extra
                import re
                img_match = re.search(r'\[IMG:([0-9,]+)\]', extra)
                if img_match:
                    # 提取图片索引并从 extra 中移除标记
                    indices_str = img_match.group(1)
                    image_indices = [int(i.strip()) - 1 for i in indices_str.split(',') if i.strip().isdigit()]  # 转为 0-indexed
                    content_text = re.sub(r'\[IMG:[0-9,]+\]\s*', '', extra).strip()
                
                pages.append({
                    "type": "CONTENT",
                    "title": content,
                    "content": content_text,
                    "section_num": current_section_num,
                    "image_indices": image_indices  # 该页需要的图片索引列表
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
        """目录页 Prompt - High Density"""
        return f"""
# TASK: Design Agenda Slide

## INPUT
{page_info.content}

## SPECS (Swiss Style)
- **Background**: White #ffffff.
- **Typography**: Sans-serif. Title 32px.
- **Layout**: List or 2-Column Grid (if >5 items).
- **Safety**: `overflow: hidden`.

## 🚫 STRICT RULES
- **Title MUST be exactly "目录"** (NOT "会议议程", NOT "CONTENTS", NOT "Agenda")
- NO Intro/Outro text. ONLY the list.

## OUTPUT (HTML Only)
```html
<div style="width: 1280px; height: 720px; background: #ffffff; padding: 60px; box-sizing: border-box; font-family: {font_family}; overflow: hidden;">
    <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0 0 40px 0;">目录</h1>
    <div style="display: flex; flex-direction: column; gap: 20px;">
        <div style="display: flex; align-items: center; gap: 24px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb;">
            <span style="font-size: 24px; font-weight: 700; color: {colors['primary']}; min-width: 40px;">01</span>
            <span style="font-size: 20px; color: {colors['text_primary']};">章节标题</span>
        </div>
    </div>
</div>
```
"""

    def _build_section_prompt(
        self, context: GenerationContext, page_info: PageInfo,
        design_prompt: str, colors: Dict[str, str], font_family: str
    ) -> str:
        """章节页 Prompt - High Density (Centered Transition)"""
        section_num = page_info.section_num if page_info.section_num > 0 else 1

        return f"""
# TASK: Design Section Transition Slide

## INPUT
- Num: 0{section_num}
- Title: {page_info.title}

## SPECS
- **Background**: {colors['primary']} (Solid).
- **Alignment**: Center/Center (Transition Style).
- **Safety**: `overflow: hidden`.

## OUTPUT (HTML Only)
```html
<div style="width: 1280px; height: 720px; background: {colors['primary']}; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family}; overflow: hidden;">
    <div style="font-size: 72px; font-weight: 300; color: rgba(255,255,255,0.3); margin-bottom: 16px;">0{section_num}</div>
    <div style="width: 60px; height: 4px; background: rgba(255,255,255,0.5); margin-bottom: 32px;"></div>
    <h1 style="font-size: 48px; font-weight: 700; color: #ffffff; margin: 0; text-align: center; max-width: 800px; line-height: 1.2;">{page_info.title}</h1>
</div>
```
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
<div style="width: 1280px; height: 720px; background: url('{bg_image_url}') center/cover no-repeat; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family}; position: relative; overflow: hidden;">
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
<div style="width: 1280px; height: 720px; background: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: {font_family}; position: relative; overflow: hidden;">
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
        """正文页 Prompt - High Density + Defensive CSS"""

        # 获取场景专有风格
        scenario_prompts = get_scenario_prompts(context.scenario)
        scenario_style = scenario_prompts.get("content_style", "")

        # 提取相关的原始素材
        source_material = self._extract_relevant_content(
            context.document_content,
            page_info.title,
            page_info.content
        )

        # 图片说明 logic
        image_instruction = ""
        if page_info.image_indices and context.image_descriptions and len(context.image_descriptions) > 0:
            related_descriptions = []
            for idx in page_info.image_indices:
                if 0 <= idx < len(context.image_descriptions):
                    related_descriptions.append(f"### Image {idx+1} Content:\n{context.image_descriptions[idx]}")

            if related_descriptions:
                all_descriptions = "\n\n".join(related_descriptions)
                image_instruction = f"""
## 📷 VISUAL REFERENCES (Must Visualize)
The user provided images for this slide. Use their content:
{all_descriptions}
**Visualization Rule**: Don't just copy text. Create a "Digital Twin" of the image structure (Matrix, Process, Hierarchy) using HTML/CSS.
"""

        # ECharts Template (Compressed)
        echarts_template = f"""
<div style="width: 100%; height: 250px;" id="chart_page{page_info.page_num}"></div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_page{page_info.page_num}'));
    chart.setOption({{
        animation: false,
        color: ['{colors["primary"]}', '{colors.get("accent", "#4A90D9")}', '#7FB3E8'],
        grid: {{ top: 30, bottom: 30, left: 50, right: 20, containLabel: true }},
        xAxis: {{ type: 'category', data: ['X'] }},
        yAxis: {{ type: 'value' }},
        series: [{{ data: [100], type: 'bar' }}]
    }});
}})();
</script>
"""

        return f"""
# TASK: Design Content Slide {page_info.page_num}/{page_info.total_pages}
{scenario_style}
## 📄 INPUT DATA
**Title (Conclusion)**: {page_info.title}
**Subtitle**: {page_info.content}
**Source Material**:
```
{source_material}
```
{image_instruction}

## 🎨 DESIGN SPECS (Swiss Style)

**1. Layout Physics (Defensive CSS)**
- **Container**: Flexbox (Row or Column).
- **Growth**: `flex: 1` to fill remaining space.
- **Safety**: `overflow: hidden` on ALL cards is MANDATORY.
- **Images**: `object-fit: contain` always.
- **Typography**: No walls of text. Use Cards, Grids, or big numbers.

**2. Visual Hierarchy**
- **Title**: {colors['text_primary']} (Bold)
- **Highlights**: {colors['primary']}

**3. Data Visualization (Preferred)**
If data exists, use ECharts:
```html
{echarts_template}
```

**4. Concept Visualization (No Data)**
Use CSS Shapes for:
- **Process**: Flex row with arrows (→).
- **Comparison**: Split view (Left vs Right).
- **Grid**: Equal-height cards.

{f'''
## 👤 USER OVERRIDE
{context.custom_instructions}
''' if context.custom_instructions and context.custom_instructions.strip() else ''}

## 🚀 OUTPUT (HTML Only)
**Canvas**: 1280x720. **Padding**: 50px 60px 80px.
**Bottom 80px**: RESERVED (Do not touch).

### ⚠️ HEADER TEMPLATE (DO NOT MODIFY - Copy exactly as shown)
The header section below is a FIXED template. You MUST use it exactly as provided.
Do NOT add: vertical bars, borders, decorations, different colors, or any modifications.

```html
<div style="width: 1280px; height: 720px; background: #ffffff; padding: 50px 60px 80px; box-sizing: border-box; font-family: {font_family}; display: flex; flex-direction: column; overflow: hidden;">
    <!-- FIXED HEADER - DO NOT MODIFY -->
    <div style="margin-bottom: 30px; flex-shrink: 0;">
        <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 0; line-height: 1.3;">{page_info.title}</h1>
        <p style="font-size: 16px; color: {colors['text_secondary']}; margin: 12px 0 0 0;">{page_info.content}</p>
    </div>

    <!-- BODY - Design freely here -->
    <div style="flex: 1; min-height: 0; display: flex; gap: 30px; overflow: hidden;">
        <!-- INSERT YOUR CONTENT HERE -->
    </div>
</div>
```
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
                
                # 添加图片
                for img in images:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": img['data_url'],
                            "detail": "high"  # 使用高分辨率模式以识别图片中的文字和细节
                        }
                    })
                
                console.print(f"[cyan]📷 多模态请求：包含 {len(images)} 张图片[/cyan]")
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

        # 注入全局无滚动条样式
        no_scrollbar_style = """<style>
::-webkit-scrollbar { display: none; }
* { -ms-overflow-style: none; scrollbar-width: none; }
</style>"""
        if not html.startswith("<style>"):
            html = no_scrollbar_style + "\n" + html

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

    async def generate_speech_script(self, context: GenerationContext, pages: List[Dict[str, Any]]) -> str:
        """
        生成演讲口播稿

        结合：
        1. 原始文档内容 (context.document_content)
        2. 生成的幻灯片结构 (pages)

        目标：生成一份适合工作汇报场景的、逻辑清晰、专业得体的演讲稿
        """
        # 构建幻灯片结构描述
        slides_text = ""
        for i, page in enumerate(pages):
            slides_text += f"\n[第 {i+1} 页] {page.get('type', 'CONTENT')} | {page.get('title', '无标题')}\n"
            slides_text += f"核心内容: {page.get('content', '')}\n"
            if 'image_indices' in page and page['image_indices']:
                slides_text += f"(包含 {len(page['image_indices'])} 张图片)\n"

        # 估算演讲时长
        estimated_minutes = max(5, len(pages) * 2)

        # 使用原子化的 prompt 模块
        detail_level, detail_guide = get_detail_config(estimated_minutes)

        # 获取场景专有的演讲稿语调指导
        scenario_prompts = get_scenario_prompts(context.scenario)
        scenario_guide = scenario_prompts.get("speech_tone", """
**场景特点：一般性汇报**
- 保持专业、客观、逻辑清晰的风格
- 根据听众调整语言正式程度""")

        # 使用原子化的 prompt 构建函数
        prompt = build_speech_prompt(
            document_content=context.document_content,
            slides_text=slides_text,
            organization=context.organization,
            scenario=context.scenario,
            estimated_minutes=estimated_minutes,
            detail_level=detail_level,
            detail_guide=detail_guide,
            scenario_guide=scenario_guide
        )

        return await self._call_ai(prompt, use_reasoning=False)

