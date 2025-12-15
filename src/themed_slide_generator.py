"""
主题化幻灯片生成器 - 支持主题系统的生成器

功能:
1. 根据主题生成内容
2. 动态 CSS 注入
3. 用户配置支持
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from themed_ai_client import ThemedAIClient
from document_parser import DocumentParser
from template_merger import TemplateMerger
from pdf_generator import generate_pdf_from_html
from adobe_integration import pdf_to_pptx
from context_manager import ContextManager, SmartContextInjector
from themes import get_theme
from themes.css_generator import generate_theme_css
from user_config import UserConfig
from config import MAX_CONCURRENT_REQUESTS

console = Console()


class ThemedSlideGenerator:
    """主题化幻灯片生成器"""
    
    def __init__(
        self,
        theme_id: str = "consulting",
        user_config: Optional[Dict[str, Any]] = None,
        model: str = None,
        output_dir: str = None
    ):
        self.theme_id = theme_id
        self.user_config = user_config or {}
        
        # 初始化主题化 AI 客户端
        self.ai_client = ThemedAIClient(
            theme_id=theme_id,
            model=model,
            user_config=user_config
        )
        
        self.theme = self.ai_client.theme
        self.document_data = None
        self.template_path = None
        self.output_dir = output_dir or "generated-slides"
        self.pages_dir = f"{self.output_dir}/pages"
        self.final_html = f"{self.output_dir}/presentation.html"
        self.context_manager: Optional[ContextManager] = None
        self.context_injector: Optional[SmartContextInjector] = None
        
        console.print(f"[green]✓[/green] 主题化生成器已初始化")
        console.print(f"[dim]  主题: {self.theme.metadata.name}[/dim]")
        console.print(f"[dim]  输出: {self.output_dir}[/dim]")
    
    def load_document(self, file_path: str):
        """加载文档"""
        console.print(f"\n[cyan]📄 加载文档: {file_path}[/cyan]")
        self.document_data = DocumentParser.load_document(file_path)
        
        if 'full_content' in self.document_data and not self.document_data.get('pages'):
            console.print(f"[green]✓[/green] 已加载完整文档 ({len(self.document_data['full_content'])} 字符)")
            
            console.print(f"[cyan]🧠 初始化智能上下文管理器...[/cyan]")
            self.context_manager = ContextManager(
                full_document=self.document_data['full_content'],
                max_context_length=4000
            )
            self.context_injector = SmartContextInjector(self.context_manager)
            console.print(f"[green]✓[/green] 上下文管理器已就绪")
        else:
            console.print(f"[green]✓[/green] 已加载文档: {len(self.document_data['pages'])} 页")
    
    async def generate_outline(self):
        """生成演示文稿大纲"""
        if 'full_content' not in self.document_data:
            return
        
        console.print("\n[cyan]📋 AI 正在规划大纲...[/cyan]")
        
        full_content = self.document_data['full_content']
        target_pages = self.user_config.get('target_pages', 25)
        content_depth = self.user_config.get('content_depth', 'normal')
        keywords = self.user_config.get('keywords', [])
        
        # 根据内容深度调整页数
        depth_multiplier = {'brief': 0.7, 'normal': 1.0, 'detailed': 1.3}
        adjusted_pages = int(target_pages * depth_multiplier.get(content_depth, 1.0))
        
        outline_prompt = f"""
你是一位顶级咨询公司的项目经理。根据以下研究报告，规划一份专业的演示文稿大纲。

【最高原则：内容忠实度】
1. 严禁编造数据
2. 严禁虚构案例
3. 可以润色、总结、提炼，但不能改变原意

【核心要求】：
1. 目标生成 **{adjusted_pages}** 页左右的大纲
2. 内容深度: {content_depth}
3. 主题关键词: {', '.join(keywords) if keywords else '无'}

【结构化拆解】：
- 每个大章节开始前，安排一个【章节封面】(SECTION) 页
- 数据密集的内容单独成页
- 每个核心观点单独成页

【输出格式】：
每行一条，格式为：`类型|标题|详细内容指令`
类型可选：SECTION (章节封面), CONTENT (正文页)

【文档内容】：
{full_content[:8000]}

请开始规划大纲：
"""
        
        with console.status("[bold cyan]AI 正在规划大纲..."):
            outline_text = await self.ai_client.generate(outline_prompt)
        
        # 解析输出
        pages = []
        for line in outline_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                p_type = parts[0].strip().upper()
                p_title = parts[1].strip()
                p_content = parts[2].strip() if len(parts) > 2 else p_title
                
                pages.append({
                    'type': p_type,
                    'title': p_title,
                    'content': p_content
                })
        
        if pages:
            self.document_data['pages'] = pages
            console.print(f"[green]✓[/green] 大纲已生成: 共 {len(pages)} 页")
            
            console.print("\n[bold]大纲预览：[/bold]")
            for i, p in enumerate(pages[:8], 1):
                console.print(f"  {i}. [{p['type']}] {p['title']}")
            if len(pages) > 8:
                console.print(f"  ... (剩余 {len(pages)-8} 页)")
        else:
            console.print(f"[red]✗ 大纲生成失败[/red]")
            raise Exception("大纲生成失败")
    
    async def generate_template(self):
        """生成 HTML 模板"""
        console.print("\n[cyan]🎨 生成主题化 HTML 模板...[/cyan]")
        
        # 使用主题化模板
        template_html = await self.ai_client.generate_template()
        
        # 保存模板
        template_dir = f"{self.output_dir}/templates"
        os.makedirs(template_dir, exist_ok=True)
        self.template_path = f"{template_dir}/template.html"
        
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(template_html)
        
        console.print(f"[green]✓[/green] 主题模板已生成: {self.template_path}")
        console.print(f"[dim]  主题: {self.theme.metadata.name}[/dim]")
    
    async def generate_page_content(
        self,
        page_num: int,
        total_pages: int,
        page_data: Dict,
        retry_count: int = 0
    ) -> Dict:
        """生成单页内容"""
        from config import MAX_RETRIES, RETRY_DELAY
        
        # 获取智能上下文
        source_material = ""
        if self.context_injector:
            page_type = page_data.get('type', 'CONTENT')
            page_title = page_data.get('title', '')
            page_content = page_data.get('content', '')
            
            source_material = self.context_injector.get_context_for_page(
                page_type, page_title, page_content
            )
        
        try:
            content_html = await self.ai_client.generate_page_content(
                page_num, total_pages, page_data, source_material
            )
            
            return {
                'page_num': page_num,
                'title': page_data.get('title', f'第{page_num}页'),
                'content': content_html,
                'success': True
            }
        except Exception as e:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                wait_time = RETRY_DELAY * retry_count
                console.print(f"[yellow]⚠ 第{page_num}页生成失败，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate_page_content(page_num, total_pages, page_data, retry_count)
            else:
                console.print(f"[red]✗ 第{page_num}页生成失败: {str(e)[:100]}[/red]")
                return {
                    'page_num': page_num,
                    'title': page_data.get('title', f'第{page_num}页'),
                    'content': f'<div class="error">生成失败: {str(e)[:100]}</div>',
                    'success': False
                }
    
    async def generate_all_pages(self):
        """并行生成所有页面"""
        console.print(f"\n[cyan]📝 生成 {len(self.document_data['pages'])} 页内容...[/cyan]")
        
        pages = self.document_data['pages']
        total_pages = len(pages)
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def generate_with_semaphore(page_num, total_pages, page_data):
            async with semaphore:
                return await self.generate_page_content(page_num, total_pages, page_data)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]生成页面内容...", total=len(pages))
            
            tasks = [
                generate_with_semaphore(i + 1, total_pages, page_data)
                for i, page_data in enumerate(pages)
            ]
            
            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.update(task, advance=1)
        
        results.sort(key=lambda x: x['page_num'])
        
        success_count = sum(1 for r in results if r['success'])
        console.print(f"[green]✓[/green] 成功生成 {success_count}/{len(results)} 页")
        
        return results
    
    def save_individual_pages(self, pages_data: List[Dict]):
        """保存独立页面"""
        console.print(f"\n[cyan]💾 保存独立页面...[/cyan]")
        
        merger = TemplateMerger(self.template_path)
        total_pages = len(pages_data)
        
        os.makedirs(self.pages_dir, exist_ok=True)
        
        for page_data in pages_data:
            page_num = page_data['page_num']
            output_path = f"{self.pages_dir}/page-{page_num:02d}.html"
            
            merger.save_page(
                output_path,
                page_num,
                total_pages,
                page_data['title'],
                page_data['content']
            )
    
    def merge_pages(self, pages_data: List[Dict]):
        """合并所有页面"""
        console.print(f"\n[cyan]🔗 合并所有页面...[/cyan]")
        
        merger = TemplateMerger(self.template_path)
        merger.save_merged(self.final_html, pages_data)
    
    async def generate_pdf(self):
        """生成 PDF"""
        console.print(f"\n[cyan]📄 生成PDF...[/cyan]")
        
        import subprocess
        from PyPDF2 import PdfMerger
        import glob
        from datetime import datetime
        
        temp_pdf_dir = f"{self.output_dir}/temp_pdfs"
        os.makedirs(temp_pdf_dir, exist_ok=True)
        
        page_files = sorted(glob.glob(f"{self.pages_dir}/page-*.html"))
        
        if not page_files:
            console.print(f"[red]✗ 未找到页面文件[/red]")
            raise Exception("未找到页面文件")
        
        convert_script = os.path.join(os.path.dirname(__file__), 'convert_to_pdf.js')
        pdf_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]转换页面为PDF...", total=len(page_files))
            
            for page_file in page_files:
                page_name = os.path.basename(page_file).replace('.html', '')
                pdf_file = f"{temp_pdf_dir}/{page_name}.pdf"
                pdf_files.append(pdf_file)
                
                try:
                    result = subprocess.run(
                        ['node', convert_script, page_file, pdf_file],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode != 0:
                        console.print(f"[red]✗ {page_name} 转换失败[/red]")
                        raise Exception(f"{page_name} 转换失败")
                
                except subprocess.TimeoutExpired:
                    console.print(f"[red]✗ {page_name} 转换超时[/red]")
                    raise
                
                progress.update(task, advance=1)
        
        console.print(f"[green]✓[/green] 所有页面已转换为PDF")
        
        # 合并 PDF
        console.print(f"[cyan]🔗 合并PDF...[/cyan]")
        merger = PdfMerger()
        
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                merger.append(pdf_file)
        
        # 生成文件名
        if hasattr(self, 'document_path') and self.document_path:
            doc_name = os.path.splitext(os.path.basename(self.document_path))[0]
        else:
            doc_name = "presentation"
        
        date_str = datetime.now().strftime("%Y%m%d")
        pdf_filename = f"{doc_name}_{date_str}.pdf"
        final_pdf_path = f"{self.output_dir}/{pdf_filename}"
        
        merger.write(final_pdf_path)
        merger.close()
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_pdf_dir)
        
        file_size = os.path.getsize(final_pdf_path) / 1024 / 1024
        console.print(f"[green]✓[/green] PDF已生成: {final_pdf_path}")
        console.print(f"[dim]文件大小: {file_size:.2f} MB[/dim]")
        
        self.final_pdf_path = final_pdf_path
    
    async def convert_pdf_to_pptx(self):
        """转换 PDF 为 PPTX"""
        try:
            if not hasattr(self, 'final_pdf_path') or not os.path.exists(self.final_pdf_path):
                console.print(f"[yellow]⚠ PDF文件不存在，跳过PPTX转换[/yellow]")
                return
            
            console.print(f"\n[cyan]🎯 将PDF转换为PPTX...[/cyan]")
            
            pdf_name = os.path.splitext(os.path.basename(self.final_pdf_path))[0]
            pptx_filename = f"{pdf_name}.pptx"
            pptx_path = f"{self.output_dir}/{pptx_filename}"
            
            result = pdf_to_pptx(self.final_pdf_path, pptx_path)
            
            if result and os.path.exists(result):
                pptx_size = os.path.getsize(result) / 1024 / 1024
                console.print(f"[green]✓[/green] PPTX转换成功")
                console.print(f"[cyan]📊 输出: {result}[/cyan]")
                console.print(f"[dim]文件大小: {pptx_size:.2f} MB[/dim]")
                self.final_pptx_path = result
            else:
                console.print(f"[yellow]⚠ PPTX转换失败[/yellow]")
        
        except Exception as e:
            console.print(f"[yellow]⚠ PPTX转换出错: {str(e)}[/yellow]")
    
    async def run(self, document_path: str, skip_pdf: bool = False):
        """完整流程"""
        try:
            self.document_path = document_path
            
            # 1. 加载文档
            self.load_document(document_path)
            
            # 2. 生成大纲
            await self.generate_outline()
            
            # 3. 添加封面、目录、封底
            pages = self.document_data.get('pages', [])
            
            include_cover = self.user_config.get('include_cover', True)
            include_agenda = self.user_config.get('include_agenda', True)
            include_closing = self.user_config.get('include_closing', True)
            
            doc_title = self.document_data.get('title')
            if not doc_title or doc_title == "演示文稿":
                doc_title = self.user_config.get('project_name', '演示文稿')
            
            final_pages = []
            
            if include_cover:
                cover_page = {'type': 'COVER', 'title': doc_title, 'content': '专项咨询研究报告'}
                final_pages.append(cover_page)
            
            if include_agenda:
                agenda_text = "\n".join([f"- {p.get('title','部分')}" for p in pages if p.get('type') != 'SECTION'])
                agenda_page = {'type': 'AGENDA', 'title': '目录概览', 'content': agenda_text}
                final_pages.append(agenda_page)
            
            final_pages.extend(pages)
            
            if include_closing:
                closing_page = {'type': 'CLOSING', 'title': '谢谢观看', 'content': '如有疑问，请联系项目组'}
                final_pages.append(closing_page)
            
            self.document_data['pages'] = final_pages
            console.print(f"[green]✓[/green] 页面结构完成：{len(final_pages)} 页")
            
            # 4. 生成模板
            await self.generate_template()
            
            # 5. 生成所有页面
            pages_data = await self.generate_all_pages()
            
            # 6. 保存独立页面
            self.save_individual_pages(pages_data)
            
            # 7. 合并页面
            self.merge_pages(pages_data)
            
            # 8. 生成 PDF
            if not skip_pdf:
                await self.generate_pdf()
                
                # 9. 转换 PPTX
                if self.user_config.get('output_pptx', True):
                    await self.convert_pdf_to_pptx()
            
            # 完成
            console.print("\n[bold green]✨ 全部完成！[/bold green]")
            console.print(f"\n输出目录: [cyan]{self.output_dir}/[/cyan]")
            console.print(f"  - 主题: [dim]{self.theme.metadata.name}[/dim]")
            console.print(f"  - 模板: [dim]{self.template_path}[/dim]")
            console.print(f"  - 页面: [dim]{self.pages_dir}/[/dim]")
            console.print(f"  - HTML: [cyan]{self.final_html}[/cyan]")
            
        except Exception as e:
            console.print(f"\n[bold red]✗ 生成失败: {str(e)}[/bold red]")
            raise
