"""AI客户端 - 适配 Prompt v4 (深蓝商务风)"""
import asyncio
import os
from typing import Optional
from openai import AsyncOpenAI
from rich.console import Console
from config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    DEFAULT_MODEL, 
    TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY,
    TEMPERATURE,
    PROMPT_TEMPLATE_PATH
)

console = Console()

class AIClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://ppt.gwy.life",
                "X-Title": "SlideAI"
            }
        )
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """加载系统prompt模板 (promptv4.md)"""
        try:
            if os.path.exists(PROMPT_TEMPLATE_PATH):
                with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的清理
                    if content.startswith('```markdown'):
                        content = content[len('```markdown'):].strip()
                    if content.endswith('```'):
                        content = content[:-3].strip()
                    console.print(f"[green]✓[/green] 已加载设计规范 ({len(content)} 字符)")
                    return content
            else:
                console.print(f"[red]✗[/red] 未找到 promptv3.md，请检查路径！")
                return "你是专业的咨询报告设计师。"
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] 加载prompt模板失败: {e}")
            return "你是专业的咨询报告设计师。"
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, retry_count: int = 0) -> str:
        """基础生成函数（带重试机制）"""
        try:
            messages = []
            final_system_prompt = system_prompt if system_prompt else self.system_prompt
            
            if final_system_prompt:
                messages.append({"role": "system", "content": final_system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=TEMPERATURE, # 建议 0.7 保持创意但不过于发散
                ),
                timeout=TIMEOUT_SECONDS
            )
            
            return response.choices[0].message.content.strip()
        
        except asyncio.TimeoutError:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                wait_time = RETRY_DELAY * retry_count  # 指数退避
                console.print(f"[yellow]⚠ 请求超时，{wait_time}秒后进行第{retry_count}次重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate(prompt, system_prompt, retry_count)
            else:
                console.print(f"[red]✗ 请求超时 ({TIMEOUT_SECONDS}秒)，已重试{MAX_RETRIES}次仍失败[/red]")
                raise
        except Exception as e:
            if retry_count < MAX_RETRIES and "timeout" in str(e).lower():
                retry_count += 1
                wait_time = RETRY_DELAY * retry_count
                console.print(f"[yellow]⚠ 请求失败，{wait_time}秒后进行第{retry_count}次重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate(prompt, system_prompt, retry_count)
            else:
                console.print(f"[red]✗ AI调用失败: {str(e)}[/red]")
                raise
    
    async def generate_template(self, style_guide: str) -> str:
        """
        生成基础 HTML 骨架 (注入 ECharts 库，全局微软雅黑字体)
        """
        prompt = f"""
任务：生成演示文稿的 HTML 基础模板。

要求：
1. 输出完整的 <!DOCTYPE html> 结构。
2. 在 <head> 中引入 ECharts 库：
   <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
3. 在 <head> 中添加字体声明（在 <style> 之前）：
   <style>
   @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
   </style>
4. 将 System Prompt 中定义的 CSS 样式放入 <style>。
5. 包含 CSS 变量，确保所有元素都使用微软雅黑字体。
6. <body> 内部只放占位符：{{{{CONTENT_PLACEHOLDER}}}}

字体要求：
- 所有文本必须使用微软雅黑（Microsoft YaHei）
- 备选字体：微软雅黑 > Heiti SC > sans-serif
- 在 body 和所有主要元素上明确指定 font-family

输出格式：仅输出 HTML 代码。
"""
        html = await self.generate(prompt)
        return self._clean_markdown(html)
    
    async def generate_page_content(self, page_num: int, total_pages: int, page_data: dict, style_guide: str, source_material: str = "") -> str:
        """
        生成单页内容 (Prompt v4: 大字号公文版，支持章节过场页)
        
        Args:
            page_num: 页码
            total_pages: 总页数
            page_data: 页面数据
            style_guide: 样式指南
            source_material: 源文档内容（用于上下文注入）
        """
        
        # 1. 获取页面类型（从大纲中指定）
        specified_type = page_data.get('type', 'CONTENT')
        current_title = page_data.get('title', '无标题')
        current_content = page_data.get('content', '')
        
        # 2. 页面类型判断与指令生成
        page_type_instruction = ""
        
        if specified_type == 'COVER' or page_num == 1:
            page_type_instruction = f"""
            这是【封面页】。
            1. 必须严格使用模板 A (Cover)。
            2. 主标题必须**原封不动**地使用："{current_title}"。
            3. 绝对禁止自己编造"自动化生成方案"之类的标题。
            4. doc-type（文档类型）必须使用：河套深港科技创新合作区深圳园区创新体系建设综合咨询研究课题
            5. 副标题使用：汇报材料
            6. 日期必须使用当前日期（2025年11月）
            7. 移除所有英文装饰（如 Company Confidential）。
            """
        elif specified_type == 'AGENDA' or page_num == 2:
            page_type_instruction = "这是【目录页】。使用模板 B，列出核心章节。"
        elif specified_type == 'SECTION':
            page_type_instruction = f"""
            这是【章节过场页】。
            1. 必须使用模板 C (Section Divider)。
            2. 深蓝背景，大号标题。
            3. 标题："{current_title}"
            4. 绝对禁止添加任何额外的描述文本、内容、汇报单位、内部资料等信息。
            5. 只显示章节标题，保持极简设计。
            6. 不要有页眉、页脚、数据来源等任何其他元素。
            """
        elif specified_type == 'CLOSING' or page_num == total_pages:
            page_type_instruction = "这是【封底页】。请使用极简设计，仅保留'谢 谢 观 看'及联系方式（中文）。"
        else:
            page_type_instruction = "这是【正文页】。使用模板 D。"

        # 3. 构建强化 Prompt (加入防幻觉指令 + 高密度策略)
        prompt = f"""
任务：生成第 {page_num}/{total_pages} 页 HTML 代码。
{page_type_instruction}

【输入数据 (Source of Truth)】：
标题：{current_title}
内容详情：
{current_content}

【高密度信息展示策略 (High Density Strategy)】：
1. **版式选择**：
   - 如果内容包含大量文字分析或复杂逻辑，**务必使用 类型 D (Deep Dive) 模板**。
   - 仅当内容主要是"一个核心结论 + 一个关键数据"时，才使用 类型 C (Content) 模板。

2. **电报式写作 (Telegraphic Style)**：
   - **禁止**写"我们可以看到..."、"根据数据显示..."这种废话。
   - **禁止**写完整的"主谓宾"长句。
   - **必须**使用短语。例如：
     - ❌ 错误：该园区的年产值增长了50%，达到了100亿元。
     - ✅ 正确：产值100亿元（+50%）；或是：营收：100亿（YoY +50%）
   - 通过这种方式，在保持 20px 字号的前提下，塞入 2 倍的信息量。

3. **数据保留原则**：
   - 这里的每一个具体数字（如金额、人数、比例）都是黄金信息，**绝不许删除**。
   - 如果数据实在太多，请将其放入 `<div class="metric-stack">` 或 `<table class="clean-table">` 中，而不是删掉。

4. **排版规范（高密度版）**：
   - 正文使用 16px 字号，这意味着你可以放入更多细节。
   - **不要**为了省空间而删除数据。
   - 如果遇到密集数据，请生成 `<table class="clean-table">`，表格字号会自动降为 14px。
   - 列表项 `<li>` 里的文字允许换行，允许写满 2-3 行的深度分析。
   - 绝对禁止 CSS `<style>` 标签。
   - 绝对禁止页眉 `<header>`。

5. **专业图表**：
   - 遇到对比数据，优先使用 ECharts。
   - 图表代码必须包含 `animation: false`。

【严格执行令】：
1. **忠实还原**：请仔细阅读"内容详情"。PPT 正文的每一条观点、每一个数据，都必须能从"内容详情"中找到依据。**不要自己脑补原文中不存在的政策条款或数据。**

2. **河套背景植入 (修正版)**：仅在"内容详情"确实与河套相关，或属于通用建议时，才关联河套背景。如果"内容详情"是关于某个具体企业的客观介绍，不要强行修改其属性。

3. **字号与排版**：正文 > 20px，标题 > 36px。

4. **禁止页眉**：
   - 绝对禁止生成 `<header class="slide-header">` 元素。
   - 不要添加任何页眉内容。
   - 页面从顶部直接开始内容区域。

5. **禁止添加页码**：
   - 绝对禁止在页脚中添加页码（如 <span>1</span>, <span>2</span> 等）。
   - 页脚只能包含数据来源或其他信息，不能有任何数字页码。

6. **禁止生成 CSS**：
   - 绝对禁止在输出中包含 `<style>` 标签。
   - 绝对禁止添加任何 CSS 定义。
   - 所有样式由外部模板提供，你只需要生成 HTML 结构和内容。
   - 使用预定义的 CSS 类名（如 .page-title, .big-list, .data-card 等）。

7. **处理空白**：如果"内容详情"很短，请使用【居中大字引用】或【大号核心观点】的布局，不要强行用废话填满两栏布局。

8. **使用专业图表**：
   - 如果内容包含对比数据（如"增长率"、"占比"、"分布"），**必须**生成 ECharts 代码块（div + script）。
   - 图表配色要使用河套深蓝 (#0F2B51) 和 科技蓝 (#005EB8)。
   - 确保 script 中的 DOM ID 是唯一的（例如加上随机数或页码后缀）。
   - 关闭图表动画 (`animation: false`) 以确保 PDF 转换时不留白。

9. **去标签**：结论框里直接写结论句子，不要写 "核心洞察：" 或 "So What："。

输出格式：直接输出代码块。
"""
        
        html = await self.generate(prompt)
        html = self._clean_markdown(html)
        html = self._remove_header(html)  # 移除页眉
        return html

    def _clean_markdown(self, text: str) -> str:
        """清理 Markdown 代码块标记"""
        text = text.strip()
        if text.startswith('```html'):
            text = text[7:].strip()
        elif text.startswith('```'):
            text = text[3:].strip()
        if text.endswith('```'):
            text = text[:-3].strip()
        return text
    
    def _remove_header(self, html: str) -> str:
        """移除页眉元素和相关 CSS"""
        import re
        
        # 1. 移除 <header class="slide-header">...</header> 元素
        html = re.sub(r'<header\s+class="slide-header"[^>]*>.*?</header>\s*', '', html, flags=re.DOTALL)
        
        # 2. 移除 .slide-header CSS 定义
        html = re.sub(r'\.slide-header\s*\{[^}]*\}', '', html)
        
        return html