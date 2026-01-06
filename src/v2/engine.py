"""
Presentation Engine - 核心引擎

@input:  ai_designer, design_system, validator, unified_styles
@output: PresentationEngine.generate() -> {html_path, pages[]}
@pos:    V2引擎的调度中心，协调所有组件完成端到端生成

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/v2/_FOLDER.md

职责：
1. 协调 AI 设计师、设计系统、验证器
2. 管理生成流程（解析 -> 大纲 -> 页面 -> 合并）
3. 提供统一的 API
"""

import os
import asyncio
from typing import List, Dict, Optional, Any
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .design_system import DesignSystem, ScenarioType
from .ai_designer import AIDesigner, GenerationContext, PageInfo
from .validator import SlideValidator
from .unified_styles import generate_unified_css

console = Console()


class PresentationEngine:
    """
    演示文稿生成引擎 v2
    
    AI 原生设计，端到端生成。
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "google/gemini-3-flash-preview", # 默认模型
        output_dir: str = "output",
        max_concurrent: int = 5
    ):
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        
        # 初始化组件
        self.designer = AIDesigner(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "pages").mkdir(exist_ok=True)
    
    async def generate(
        self,
        document_content: str,
        document_name: str,
        scenario: str = "consulting",
        theme_color: Optional[str] = None,
        font_style: str = "modern",  # 'modern' (黑体) 或 'classic' (楷体)
        organization: str = "汇报单位",
        target_pages: int = 25,
        content_depth: str = "normal",
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """执行完整的生成流程"""
        
        # 1. 初始化设计系统和上下文
        ds = DesignSystem.from_scenario(scenario, custom_primary=theme_color, font_style=font_style)
        
        context = GenerationContext(
            document_content=document_content,
            document_name=document_name,
            organization=organization,
            scenario=scenario,
            design_system=ds,
            target_pages=target_pages,
            content_depth=content_depth
        )
        
        validator = SlideValidator(ds)
        
        # 2. 生成大纲
        if on_progress: on_progress("outline", "AI 正在规划大纲...", 10)
        
        outline_result = await self.designer.generate_outline(context)
        # 提取 AI 生成的标题和页面列表
        ai_title = outline_result.get("title")  # AI 生成的干净标题
        outline_pages = outline_result.get("pages", [])
        
        outline_pages = self._complete_outline(outline_pages, context, ai_title)
        total_pages = len(outline_pages)
        
        if on_progress: 
            on_progress("outline", f"大纲规划完成，共 {total_pages} 页", 20, result={"outline": outline_pages})
        
        # 3. 并行生成页面
        if on_progress: on_progress("content", "AI 设计师正在创作页面...", 30)
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        completed_count = 0
        pages_html = [None] * total_pages
        
        async def generate_single_page(index: int, page_data: Dict):
            nonlocal completed_count
            async with semaphore:
                try:
                    # 构建页面信息
                    info = PageInfo(
                        type=page_data['type'],
                        title=page_data.get('title', ''),
                        content=page_data.get('content', ''),
                        page_num=index + 1,
                        total_pages=total_pages,
                        section_num=page_data.get('section_num', 0)
                    )
                    
                    # 生成 HTML
                    html = await self.designer.generate_page(context, info)
                    
                    # 验证并尝试修复
                    validation = validator.validate(html)
                    if not validation.is_valid:
                        console.print(f"[yellow]⚠ 第 {info.page_num} 页验证警告: {validation.errors}，尝试自动修复...[/yellow]")
                        html = validator.fix_html(html)
                    
                    pages_html[index] = html
                    
                    # 更新进度
                    completed_count += 1
                    if on_progress:
                        percent = 30 + int(60 * completed_count / total_pages)
                        on_progress("content", f"正在生成页面 ({completed_count}/{total_pages})", percent, current=completed_count, total=total_pages)
                        
                except Exception as e:
                    console.print(f"[red]✗ 第 {index+1} 页生成失败: {e}[/red]")
                    pages_html[index] = f"<div class='error'>生成失败: {e}</div>"
        
        # 创建并执行任务
        tasks = [
            generate_single_page(i, page) 
            for i, page in enumerate(outline_pages)
        ]
        await asyncio.gather(*tasks)
        
        # 4. 保存和合并
        if on_progress: on_progress("merge", "正在合并页面...", 90)
        
        # 保存独立页面
        pages_result = []
        for i, html in enumerate(pages_html):
            page_path = self.output_dir / "pages" / f"page-{i+1:02d}.html"
            full_page_html = self._wrap_page_html(html, ds)
            page_path.write_text(full_page_html, encoding='utf-8')
            
            pages_result.append({
                "index": i + 1,
                "title": outline_pages[i].get('title', f'Page {i+1}'),
                "type": outline_pages[i].get('type', 'CONTENT'),
                "url": f"/output/{self.output_dir.name}/pages/page-{i+1:02d}.html"
            })
            
        # 合并所有页面 - 使用文档名作为文件名
        safe_filename = self._clean_document_title(document_name)
        # 去除可能导致文件名问题的字符
        safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in (' ', '-', '_', '（', '）', '(', ')')).strip()
        if not safe_filename:
            safe_filename = "presentation"
        merged_path = self.output_dir / f"{safe_filename}.html"
        merged_html = self._merge_all_pages(pages_html, ds)
        merged_path.write_text(merged_html, encoding='utf-8')
        
        if on_progress: on_progress("done", "生成完成", 100)
        
        return {
            "html_path": str(merged_path),
            "pages": pages_result
        }
    
    def _complete_outline(self, outline: List[Dict], context: GenerationContext, ai_title: str = None) -> List[Dict]:
        """补全大纲（添加封面、目录、封底）"""
        complete = []
        
        # 检查是否已有特殊页面
        has_cover = any(p['type'] == 'COVER' for p in outline)
        has_agenda = any(p['type'] == 'AGENDA' for p in outline)
        has_closing = any(p['type'] == 'CLOSING' for p in outline)
        
        # 1. 添加封面 - 优先使用 AI 生成的干净标题，否则回退到清理后的文件名
        if not has_cover:
            cover_title = ai_title if ai_title else self._clean_document_title(context.document_name)
            complete.append({
                "type": "COVER", 
                "title": cover_title, 
                "content": ""
            })
        
        # 2. 添加目录
        if not has_agenda:
            # 提取所有章节标题
            sections = [p['title'] for p in outline if p['type'] == 'SECTION']
            if not sections:
                # 如果没有章节，就用前 5 页标题
                sections = [p['title'] for p in outline[:5] if p['type'] == 'CONTENT']
            
            agenda_content = "\n".join(sections)
            complete.append({
                "type": "AGENDA", 
                "title": "目录", 
                "content": agenda_content
            })
        
        # 3. 添加中间页面（在此过程中标记章节号）
        section_counter = 0
        for page in outline:
            # 跳过 AI 错误生成的特殊页面
            if page['type'] in ('COVER', 'AGENDA', 'CLOSING'):
                continue
                
            if page['type'] == 'SECTION':
                section_counter += 1
                page['section_num'] = section_counter
            
            complete.append(page)
        
        # 4. 添加封底
        if not has_closing:
            complete.append({
                "type": "CLOSING", 
                "title": "谢谢观看", 
                "content": context.organization
            })
            
        return complete
    
    def _clean_document_title(self, raw_name: str) -> str:
        """
        清理文档名称，生成适合作为封面标题的干净标题
        
        示例：
        - "正文_自动驾驶的终局之战.md" -> "自动驾驶的终局之战" 
        - "2025-01-15_市场分析报告_v2.pdf" -> "市场分析报告"
        - "AI落地研究_20251222.docx" -> "AI落地研究"
        """
        import re
        
        title = raw_name
        
        # 1. 移除文件扩展名  
        title = re.sub(r'\.(md|pdf|docx|doc|txt|pptx|ppt|xlsx|xls)$', '', title, flags=re.IGNORECASE)
        
        # 2. 移除日期格式 (各种格式)
        # 20251222, 2025-12-22, 2025_12_22, 2025.12.22
        title = re.sub(r'[_\-\.]?20\d{6}[_\-\.]?', '', title)
        title = re.sub(r'[_\-\.]?20\d{2}[_\-\.]\d{2}[_\-\.]\d{2}[_\-\.]?', '', title)
        title = re.sub(r'[_\-\.]?20\d{2}年\d{1,2}月\d{1,2}日?[_\-\.]?', '', title)
        
        # 3. 移除版本号 (_v1, _v2, -final, _最终版 等)
        title = re.sub(r'[_\-]?v\d+[_\-]?', '', title, flags=re.IGNORECASE)
        title = re.sub(r'[_\-]?(final|最终版|修订版|定稿)[_\-]?', '', title, flags=re.IGNORECASE)
        
        # 4. 移除常见前缀 (正文_, 附件_, 文档_ 等)
        title = re.sub(r'^(正文|附件|文档|报告|材料|slides)[_\-]', '', title, flags=re.IGNORECASE)
        
        # 5. 将下划线和连字符替换为空格，然后清理多余空格
        title = re.sub(r'[_\-]+', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 6. 如果清理后为空，返回"演示文稿"
        if not title:
            title = "演示文稿"
        
        return title

    def _wrap_page_html(self, content_html: str, ds: DesignSystem) -> str:
        """为单页 HTML 添加 head 和 body，注入统一 CSS"""
        tokens = ds.get_tokens()
        font_style = tokens.typography.font_style if hasattr(tokens.typography, 'font_style') else 'modern'
        unified_css = generate_unified_css(tokens.colors.primary, font_style=font_style)
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Page</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f0f2f5;
        }}
        
        /* 统一样式系统 */
        {unified_css}
    </style>
</head>
<body>
    {content_html}
</body>
</html>"""

    def _merge_all_pages(self, pages_html: List[str], ds: DesignSystem) -> str:
        """合并所有页面，注入统一 CSS"""
        tokens = ds.get_tokens()
        font_style = tokens.typography.font_style if hasattr(tokens.typography, 'font_style') else 'modern'
        unified_css = generate_unified_css(tokens.colors.primary, font_style=font_style)
        
        # 每个页面包裹在一个容器中，用于 print/pdf
        wrapped_pages = []
        for html in pages_html:
            wrapped_pages.append(f"""
            <div class="slide-wrapper">
                {html}
            </div>
            """)
            
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        /* 统一样式系统 */
        {unified_css}
        
        /* 页面容器样式 */
        body {{
            margin: 0;
            padding: 20px;
            background: #f0f2f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}
        
        /* 幻灯片容器包装 */
        .slide-wrapper {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            background: white;
            page-break-after: always; /* 用于打印/PDF */
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
                background: white;
                display: block;
            }}
            .slide-wrapper {{
                box-shadow: none;
                page-break-after: always;
                margin: 0;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    {"".join(wrapped_pages)}
</body>
</html>"""
