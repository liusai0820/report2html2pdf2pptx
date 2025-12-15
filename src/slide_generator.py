"""幻灯片生成器 - 主要业务逻辑"""
import asyncio
import os
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from ai_client import AIClient
from document_parser import DocumentParser
from template_merger import TemplateMerger
from pdf_generator import generate_pdf_from_html
from adobe_integration import pdf_to_pptx
from context_manager import ContextManager, SmartContextInjector
from font_fixer import ensure_editable_fonts
from config import (
    OUTPUT_DIR, TEMPLATE_DIR, PAGES_DIR, 
    FINAL_HTML, FINAL_PDF, MAX_CONCURRENT_REQUESTS
)

console = Console()

class SlideGenerator:
    def __init__(self, model: str = None, output_dir: str = None):
        self.ai_client = AIClient(model) if model else AIClient()
        self.document_data = None
        self.template_path = None
        self.output_dir = output_dir or OUTPUT_DIR
        self.pages_dir = f"{self.output_dir}/pages"
        self.final_html = f"{self.output_dir}/presentation.html"
        self.context_manager: Optional[ContextManager] = None
        self.context_injector: Optional[SmartContextInjector] = None
    
    def load_document(self, file_path: str):
        """加载文档"""
        console.print(f"\n[cyan]📄 加载文档: {file_path}[/cyan]")
        self.document_data = DocumentParser.load_document(file_path)
        
        # 如果文档有 full_content，说明需要 AI 生成大纲
        if 'full_content' in self.document_data and not self.document_data.get('pages'):
            console.print(f"[green]✓[/green] 已加载完整文档 ({len(self.document_data['full_content'])} 字符)")
            
            # 初始化上下文管理器（关键改进！）
            console.print(f"[cyan]🧠 初始化智能上下文管理器...[/cyan]")
            self.context_manager = ContextManager(
                full_document=self.document_data['full_content'],
                max_context_length=4000  # 每页最多注入 4000 字的上下文
            )
            self.context_injector = SmartContextInjector(self.context_manager)
            console.print(f"[green]✓[/green] 上下文管理器已就绪")
        else:
            console.print(f"[green]✓[/green] 已加载文档: {len(self.document_data['pages'])} 页")
    
    async def generate_outline(self):
        """生成演示文稿大纲 (深度扩充版 + 防幻觉 + 强拆解)"""
        if 'full_content' not in self.document_data:
            return  # 已经有拆分好的页面，跳过
        
        console.print("\n[cyan]📋 AI 正在进行深度拆解，规划长篇报告大纲...[/cyan]")
        
        full_content = self.document_data['full_content']
        
        # 这是一个"逼迫"AI 把报告写长的 Prompt + 防幻觉指令 + 强制拆分
        outline_prompt = f"""
你是一位顶级咨询公司的项目经理。你需要根据以下研究报告，规划一份**展示工作量、内容详实、深度分析**的汇报演示文稿大纲。

【最高原则：内容忠实度】
1. **严禁编造数据**：绝对不允许为了排版好看而编造虚假的增长率、金额、人数等数据。如果原文没有数据，就不要写数据卡片。
2. **严禁虚构案例**：不要编造不存在的企业名称或合作项目。
3. **信达雅**：你可以对文字进行润色、总结、提炼，使其符合咨询风格，但不能改变原意。

【核心要求】：
1. **页数要求**：目标生成 **25-35 页** 的大纲。为了充分展示工作量，**绝对不能少于 25 页**。
2. **颗粒度细化（强制拆分）**：
   - 严禁将一个大章节（如"产业现状"、"机制分析"）压缩在 1-2 页内。
   - **必须**按以下逻辑强行拆分：
     - 【数据页】：单独一页展示总体规模、增长率（适合放 ECharts 图表）。
     - 【细分页】：每个核心细分领域（如生物医药、人工智能）各占一页，深入分析。
     - 【企业页】：单独一页列举龙头企业或典型案例表格。
     - 【问题页】：单独一页深入分析痛点。
   - 例如："产业现状"章节至少要拆出 4-5 个 CONTENT 页面。
3. **结构化拆解**：
   - 对于"对策建议"：每一条大建议（如"强链补链"）单独一页，并配上具体的实施举措。
   - 对于"机制/策略"：拆分为现状问题、对标案例、改进方案。
4. **增加过场**：在每个大章节开始前，必须安排一个【章节封面】(SECTION) 页。

【信息密度控制 (The Rule of "Split")】：
- 如果某个章节包含"现状分析"、"存在问题"和"对策建议"三部分，**绝对不能**写在一个 CONTENT 页面里。
- 必须拆分为：
  - CONTENT|产业现状数据与图表|...
  - CONTENT|核心痛点与根因分析|...
  - CONTENT|针对性对策与实施路径|...
- **宁可页数多，不可单页挤。**

【详细内容指令 (Data Injection)】：
- 在生成 CONTENT 类型的页面时，`详细内容指令` 这一栏，**必须尽可能多地摘录原文中的干货（数据、具体举措、核心观点）**。
- 不要只写"分析了什么"，要写"分析得出的具体结论是A、B、C"。
- **直接把原文中的关键数据（数字、百分比）复制进去**。
- 不要写"分析营收"，要写"分析营收（2023年达500亿，增长20%）"。这样后续生成页面时才不会丢失数据。

【文档内容】：
{full_content} 

【输出格式（严格执行）】：
每行一条，格式为：`类型|标题|详细内容指令`
类型可选：
- SECTION (章节封面，如"第二部分 产业分析")
- CONTENT (普通内容页)

【重要提示】：
- 绝对禁止生成 COVER、AGENDA、CLOSING 类型的页面 (系统会自动加)
- 请确保生成足够多的 CONTENT 页面以满足页数要求

【输出示例】：
SECTION|第一部分 研究背景|
CONTENT|国家战略定位分析|详细列举大湾区、深港合作等战略要求，引用具体文件和政策条款
CONTENT|河套区域独特优势|分析一区两园、跨境便利等核心优势，列举具体的制度创新点
SECTION|第二部分 产业现状|
CONTENT|企业总量与结构概览|使用饼图展示战新产业与传统产业比例，突出二元结构。如原文有具体数字，必须包含
CONTENT|新一代信息技术产业分析|列举龙头企业名称、分析细分赛道、展示增长数据。所有数据必须来自原文
CONTENT|生物医药产业深度剖析|分析创新药、医疗器械等细分领域，列举典型企业
...

请开始规划大纲：
"""
        
        with console.status("[bold cyan]AI 正在规划 30+ 页的详细大纲..."):
            # 这里建议稍微调高 temperature，让 AI 有胆量拆分得更细
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
            console.print(f"[green]✓[/green] 深度大纲已生成: 共 {len(pages)} 页")
            
            # 预览
            console.print("\n[bold]大纲预览：[/bold]")
            for i, p in enumerate(pages[:8], 1):
                console.print(f"  {i}. [{p['type']}] {p['title']}")
            console.print(f"  ... (剩余 {len(pages)-8} 页)")
            
        else:
            console.print(f"[red]✗ 大纲生成失败，AI 未按格式输出[/red]")
            raise Exception("大纲生成失败")
    
    async def generate_template(self):
        """生成HTML模板"""
        console.print("\n[cyan]🎨 生成HTML模板...[/cyan]")
        
        style_guide = self.document_data.get('style_guide', '默认企业风格')
        
        with console.status("[bold cyan]AI正在生成模板..."):
            template_html = await self.ai_client.generate_template(style_guide)
        
        # 保存模板
        template_dir = f"{self.output_dir}/templates"
        os.makedirs(template_dir, exist_ok=True)
        self.template_path = f"{template_dir}/template.html"
        
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(template_html)
        
        console.print(f"[green]✓[/green] 模板已生成: {self.template_path}")
        
        # 显示token估算
        token_count = len(template_html) // 4
        console.print(f"[dim]Token消耗: ~{token_count}[/dim]")

    
    async def generate_page_content(self, page_num: int, total_pages: int, page_data: Dict, retry_count: int = 0) -> Dict:
        """生成单页内容（带重试机制 + 智能上下文注入）"""
        from config import MAX_RETRIES, RETRY_DELAY
        
        style_guide = self.document_data.get('style_guide', '默认企业风格')
        
        # 获取智能上下文（关键改进！）
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
                page_num, total_pages, page_data, style_guide, source_material
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
                console.print(f"[yellow]⚠ 第{page_num}页生成失败，{wait_time}秒后进行第{retry_count}次重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate_page_content(page_num, total_pages, page_data, retry_count)
            else:
                console.print(f"[red]✗ 第{page_num}页生成失败（已重试{MAX_RETRIES}次）: {str(e)[:100]}[/red]")
                return {
                    'page_num': page_num,
                    'title': page_data.get('title', f'第{page_num}页'),
                    'content': f'<div class="error">生成失败（已重试{MAX_RETRIES}次）: {str(e)[:100]}</div>',
                    'success': False
                }
    
    async def generate_all_pages(self):
        """并行生成所有页面内容"""
        console.print(f"\n[cyan]📝 生成 {len(self.document_data['pages'])} 页内容...[/cyan]")
        
        pages = self.document_data['pages']
        
        # === 新增：获取总页数 ===
        total_pages = len(pages) 
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        # === 修改：这里也需要接收 total_pages ===
        async def generate_with_semaphore(page_num, total_pages, page_data):
            async with semaphore:
                # 调用刚才修改过的函数
                return await self.generate_page_content(page_num, total_pages, page_data)
        
        # 并行生成
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]生成页面内容...", 
                total=len(pages)
            )
            
            # === 修改：在循环里把 total_pages 传进去 ===
            tasks = [
                generate_with_semaphore(i + 1, total_pages, page_data)
                for i, page_data in enumerate(pages)
            ]
            
            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.update(task, advance=1)
        
        # 按页码排序
        results.sort(key=lambda x: x['page_num'])
        
        # 统计
        success_count = sum(1 for r in results if r['success'])
        console.print(f"[green]✓[/green] 成功生成 {success_count}/{len(results)} 页")
        
        if success_count < len(results):
            console.print(f"[yellow]⚠ {len(results) - success_count} 页生成失败，请检查[/yellow]")
        
        return results

    def save_individual_pages(self, pages_data: List[Dict]):
        """保存独立的页面文件"""
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
        """生成PDF - 每页独立转换后合并"""
        console.print(f"\n[cyan]📄 生成PDF...[/cyan]")
        
        import subprocess
        from PyPDF2 import PdfMerger
        import glob
        from datetime import datetime
        
        # 创建临时PDF目录
        temp_pdf_dir = f"{self.output_dir}/temp_pdfs"
        os.makedirs(temp_pdf_dir, exist_ok=True)
        
        # 获取所有独立页面
        page_files = sorted(glob.glob(f"{self.pages_dir}/page-*.html"))
        
        if not page_files:
            console.print(f"[red]✗ 未找到页面文件[/red]")
            raise Exception("未找到页面文件")
        
        console.print(f"[dim]找到 {len(page_files)} 个页面[/dim]")
        
        # 使用Node.js的puppeteer转换每一页
        convert_script = os.path.join(os.path.dirname(__file__), 'convert_to_pdf.js')
        pdf_files = []
        
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]转换页面为PDF...", 
                total=len(page_files)
            )
            
            for page_file in page_files:
                page_name = os.path.basename(page_file).replace('.html', '')
                pdf_file = f"{temp_pdf_dir}/{page_name}.pdf"
                pdf_files.append(pdf_file)
                
                try:
                    result = subprocess.run(
                        ['node', convert_script, page_file, pdf_file],
                        capture_output=True,
                        text=True,
                        timeout=60  # 增加到60秒
                    )
                    
                    if result.returncode != 0:
                        console.print(f"[red]✗ {page_name} 转换失败[/red]")
                        console.print(result.stderr)
                        raise Exception(f"{page_name} 转换失败")
                    
                except subprocess.TimeoutExpired:
                    console.print(f"[red]✗ {page_name} 转换超时[/red]")
                    raise
                
                progress.update(task, advance=1)
        
        console.print(f"[green]✓[/green] 所有页面已转换为PDF")
        
        # 合并PDF
        console.print(f"[cyan]🔗 合并PDF（{len(pdf_files)}个文件）...[/cyan]")
        merger = PdfMerger()
        
        for i, pdf_file in enumerate(pdf_files, 1):
            if os.path.exists(pdf_file):
                console.print(f"[dim]  合并 {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}[/dim]")
                merger.append(pdf_file)
            else:
                console.print(f"[yellow]⚠ 文件不存在: {pdf_file}[/yellow]")
        
        # 生成PDF文件名：文档名+日期
        if hasattr(self, 'document_path') and self.document_path:
            doc_name = os.path.splitext(os.path.basename(self.document_path))[0]
        else:
            doc_name = "presentation"
        
        date_str = datetime.now().strftime("%Y%m%d")
        pdf_filename = f"{doc_name}_{date_str}.pdf"
        final_pdf_path = f"{self.output_dir}/{pdf_filename}"
        
        # 保存合并后的PDF
        console.print(f"[cyan]💾 保存PDF到: {final_pdf_path}[/cyan]")
        os.makedirs(os.path.dirname(final_pdf_path), exist_ok=True)
        
        try:
            merger.write(final_pdf_path)
            merger.close()
            console.print(f"[green]✓[/green] PDF写入完成")
        except Exception as e:
            console.print(f"[red]✗ PDF写入失败: {e}[/red]")
            merger.close()
            raise
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_pdf_dir)
        
        # 显示文件大小
        file_size = os.path.getsize(final_pdf_path) / 1024 / 1024
        console.print(f"[green]✓[/green] PDF已生成: {final_pdf_path}")
        console.print(f"[dim]文件大小: {file_size:.2f} MB[/dim]")
        
        # 保存PDF路径供后续使用
        self.final_pdf_path = final_pdf_path
    
    async def convert_pdf_to_pptx(self):
        """将生成的PDF转换为PPTX，并进行后处理清洗"""
        try:
            if not hasattr(self, 'final_pdf_path') or not os.path.exists(self.final_pdf_path):
                console.print(f"[yellow]⚠ PDF文件不存在，跳过PPTX转换[/yellow]")
                return
            
            console.print(f"\n[cyan]🎯 将PDF转换为PPTX...[/cyan]")
            console.print(f"[dim]输入: {self.final_pdf_path}[/dim]")
            
            # 生成PPTX输出路径
            pdf_name = os.path.splitext(os.path.basename(self.final_pdf_path))[0]
            pptx_filename = f"{pdf_name}.pptx"
            pptx_path = f"{self.output_dir}/{pptx_filename}"
            
            # 调用Adobe PDF转PPTX功能
            result = pdf_to_pptx(self.final_pdf_path, pptx_path)
            
            if result and os.path.exists(result):
                pptx_size = os.path.getsize(result) / 1024 / 1024
                console.print(f"[green]✓[/green] PPTX转换成功")
                console.print(f"[cyan]📊 原始输出: {result}[/cyan]")
                console.print(f"[dim]文件大小: {pptx_size:.2f} MB[/dim]")
                
                # 后处理：清洗 PPTX（已禁用 - 清洗脚本会破坏文件）
                # 原因：清洗脚本过度修改导致 PPTX 质量下降
                # TODO: 需要重新设计清洗策略，采用更保守的方法
                console.print(f"[dim]⏭️  跳过 PPTX 后处理（清洗脚本已禁用）[/dim]")
                
                # 保存PPTX路径
                self.final_pptx_path = result
            else:
                console.print(f"[yellow]⚠ PPTX转换失败或输出文件不存在[/yellow]")
        
        except Exception as e:
            console.print(f"[yellow]⚠ PPTX转换出错: {str(e)}[/yellow]")
            console.print(f"[dim]继续处理其他任务...[/dim]")
    
    async def run(self, document_path: str, skip_pdf: bool = False, skip_generation: bool = False):
        """完整流程"""
        try:
            # 保存文档路径用于PDF命名
            self.document_path = document_path
            # 检测是否已有HTML文件
            if skip_generation or (os.path.exists(FINAL_HTML) and os.path.exists(self.template_path or f"{TEMPLATE_DIR}/template.html")):
                if not skip_generation:
                    console.print("\n[yellow]⚠ 检测到已有HTML文件[/yellow]")
                    from rich.prompt import Confirm
                    if Confirm.ask("是否跳过AI生成，直接使用现有HTML?", default=True):
                        skip_generation = True
                
                if skip_generation:
                    console.print("\n[cyan]⏭️  跳过AI生成，使用现有HTML[/cyan]")
                    console.print(f"[dim]HTML文件: {FINAL_HTML}[/dim]")
                    
                    # 直接跳到PDF生成
                    if not skip_pdf:
                        await self.generate_pdf()
                    
                    console.print("\n[bold green]✨ 完成！[/bold green]")
                    console.print(f"\n输出目录: [cyan]{self.output_dir}/[/cyan]")
                    console.print(f"  - 完整HTML: [cyan]{self.final_html}[/cyan]")
                    return
            
            # 1. 加载文档
            self.load_document(document_path)
            
            # 2. 生成大纲（这一步生成的是正文内容的列表）
            # 如果是 DOCX，这里会把长文切分成 [{'title': '...', 'content': '...', 'type': 'SECTION|CONTENT'}, ...]
            await self.generate_outline()
            
            # 获取生成的页面列表
            pages = self.document_data.get('pages', [])
            
            # 检查是否已经有COVER页面（防止重复）
            has_cover = any(p.get('type') == 'COVER' for p in pages)
            has_agenda = any(p.get('type') == 'AGENDA' for p in pages)
            has_closing = any(p.get('type') == 'CLOSING' for p in pages)
            
            # 获取文档标题用于封面
            doc_title = self.document_data.get('title')
            if not doc_title or doc_title == "演示文稿":
                if pages and pages[0].get('title'):
                    doc_title = pages[0]['title']
                else:
                    if hasattr(self, 'document_path') and self.document_path:
                        doc_title = os.path.splitext(os.path.basename(self.document_path))[0]
                    else:
                        doc_title = "河套深港科技创新合作区专项咨询报告"
            
            # 构造完整页面列表：[封面, 目录, 大纲生成的页面..., 封底]
            final_pages = []
            
            # 只在没有COVER时添加
            if not has_cover:
                cover_page = {'type': 'COVER', 'title': doc_title, 'content': '专项咨询研究报告'}
                final_pages.append(cover_page)
            
            # 只在没有AGENDA时添加
            if not has_agenda:
                agenda_text = "\n".join([f"- {p.get('title','部分')}" for p in pages if p.get('type') != 'SECTION'])
                agenda_page = {'type': 'AGENDA', 'title': '目录概览', 'content': agenda_text}
                final_pages.append(agenda_page)
            
            # 添加所有生成的页面
            final_pages.extend(pages)
            
            # 只在没有CLOSING时添加
            if not has_closing:
                closing_page = {'type': 'CLOSING', 'title': '谢谢观看', 'content': '如有疑问，请联系项目组'}
                final_pages.append(closing_page)
            
            self.document_data['pages'] = final_pages
            
            console.print(f"[green]✓[/green] 页面结构完成：{len(final_pages)} 页")


            # 3. 生成模板
            await self.generate_template()
            
            # 4. 生成所有页面内容
            pages_data = await self.generate_all_pages()
            
            # 5. 保存独立页面
            self.save_individual_pages(pages_data)
            
            # 6. 合并页面
            self.merge_pages(pages_data)
            
            # 7. 生成PDF
            if not skip_pdf:
                await self.generate_pdf()
                
                # 8. 将PDF转换为PPTX
                await self.convert_pdf_to_pptx()
            
            # 完成
            console.print("\n[bold green]✨ 全部完成！[/bold green]")
            console.print(f"\n输出目录: [cyan]{self.output_dir}/[/cyan]")
            console.print(f"  - 模板: [dim]{self.template_path}[/dim]")
            console.print(f"  - 独立页面: [dim]{self.pages_dir}/[/dim]")
            console.print(f"  - 完整HTML: [cyan]{self.final_html}[/cyan]")
            
        except Exception as e:
            console.print(f"\n[bold red]✗ 生成失败: {str(e)}[/bold red]")
            raise
