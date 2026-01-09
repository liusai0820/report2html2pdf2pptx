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
            #speech-btn, .speech-modal {{ display: none !important; }}
        }}

        /* 演讲稿按钮样式 */
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .speech-btn {{
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            padding: 10px 20px; background: #1A365D; color: white;
            border: none; border-radius: 4px; cursor: pointer;
            font-family: sans-serif; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.2s; display: flex; align-items: center; gap: 8px;
        }}
        .speech-btn:hover {{ background: #2c5282; transform: translateY(-1px); }}
        .speech-modal {{
            display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
            z-index: 10000; justify-content: center; align-items: center;
            backdrop-filter: blur(4px);
        }}
        .speech-modal-content {{
            background: white; width: 800px; max-width: 90%; height: 80vh;
            border-radius: 12px; display: flex; flex-direction: column;
            overflow: hidden; box-shadow: 0 4px 30px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease-out;
        }}
        @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body>
    <!-- 演讲稿生成按钮 -->
    <button id="speech-btn" class="speech-btn">
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
        生成演讲稿
    </button>

    <!-- 演讲稿模态框 -->
    <div id="speech-modal" class="speech-modal">
        <div class="speech-modal-content">
            <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: #f8fafc;">
                <h3 style="margin: 0; font-size: 18px; color: #333; font-weight: 600;">🎙️ 演讲口播稿</h3>
                <button onclick="document.getElementById('speech-modal').style.display='none'" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #999; padding: 0 8px;">&times;</button>
            </div>
            <div id="speech-content" style="flex: 1; padding: 40px; overflow-y: auto; font-size: 16px; line-height: 1.8; color: #333; white-space: pre-wrap; font-family: 'PingFang SC', system-ui, sans-serif;">
                <!-- Content injected here -->
            </div>
            <div style="padding: 20px; border-top: 1px solid #eee; text-align: right; background: #f8fafc; display: flex; justify-content: flex-end; gap: 12px;">
                <button onclick="copySpeech()" style="padding: 8px 16px; background: #white; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; color: #475569; font-weight: 500;">复制全文</button>
                <button onclick="document.getElementById('speech-modal').style.display='none'" style="padding: 8px 16px; background: #1A365D; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">关闭</button>
            </div>
        </div>
    </div>

    <script>
    document.getElementById('speech-btn').onclick = async function() {{
        document.getElementById('speech-modal').style.display = 'flex';
        const contentDiv = document.getElementById('speech-content');
        contentDiv.innerHTML = `
            <div style="text-align: center; color: #64748b; margin-top: 100px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #1A365D; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
                <p style="font-size: 16px;">AI 正在阅读幻灯片并撰写演讲稿...</p>
                <p style="font-size: 14px; opacity: 0.7;">预计需要 15-30 秒</p>
            </div>
        `;

        try {{
            // Extract output name from URL
            const pathParts = window.location.pathname.split('/');
            let outputName = null;
            for(let i=0; i<pathParts.length; i++) {{
                if(pathParts[i] === 'output' && i+1 < pathParts.length) {{
                    outputName = pathParts[i+1];
                    break;
                }}
            }}

            if (!outputName) {{
                // Try getting from parent folder name if opened as file
                const path = window.location.pathname;
                const match = path.match(/\\/([^\\/]+)\\/presentation\\.html$/);
                if (match) {{
                    outputName = match[1];
                }} else {{
                    throw new Error("无法从 URL 获取演示文稿 ID，请确保在系统中打开");
                }}
            }}

            const response = await fetch('/api/generate-speech', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ output_name: outputName }})
            }});

            if (!response.ok) {{
                const errData = await response.json();
                throw new Error(errData.detail || "生成请求失败");
            }}

            const data = await response.json();

            // Simple markdown parsing
            let htmlContent = data.script
                .replace(/^# (.*$)/gim, '<h1 style="font-size: 24px; margin-top: 20px; margin-bottom: 10px; color: #1e293b;">$1</h1>')
                .replace(/^## (.*$)/gim, '<h2 style="font-size: 20px; margin-top: 15px; margin-bottom: 8px; color: #334155;">$1</h2>')
                .replace(/\\*\\*(.*)\\*\\*/gim, '<strong>$1</strong>')
                .replace(/\\n/g, '<br>');

            contentDiv.innerHTML = htmlContent;

        }} catch (e) {{
            contentDiv.innerHTML = `
                <div style="color: #ef4444; text-align: center; margin-top: 100px; padding: 20px; background: #fef2f2; border-radius: 8px; max-width: 400px; margin-left: auto; margin-right: auto;">
                    <svg style="width: 48px; height: 48px; margin-bottom: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <div style="font-weight: bold; margin-bottom: 8px;">生成失败</div>
                    <div>${{e.message}}</div>
                </div>`;
        }}
    }};

    function copySpeech() {{
        const text = document.getElementById('speech-content').innerText;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.querySelector('button[onclick="copySpeech()"]');
            const originalText = btn.innerText;
            btn.innerText = '已复制!';
            setTimeout(() => btn.innerText = originalText, 2000);
        }});
    }}
    </script>
    {"".join(wrapped_pages)}
</body>
</html>"""
