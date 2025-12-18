"""
输出渲染器 - 将 AI 生成的内容转换为最终格式

职责：
1. 生成 HTML 模板
2. 合并页面
3. 转换 PDF/PPTX
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from themes.css_generator import CSSGenerator
from .context_builder import PresentationContext

console = Console()


class OutputRenderer:
    """输出渲染器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir = self.output_dir / "pages"
        self.pages_dir.mkdir(exist_ok=True)
    
    def render_template(self, context: PresentationContext) -> str:
        """根据上下文中的主题动态生成 HTML 模板"""
        
        css = ""
        theme = context.theme
        
        if theme:
            # 动态生成主题 CSS
            generator = CSSGenerator(theme)
            css = generator.generate_full_css()
        else:
            # 回退到基本样式（如果需要）
            css = "body { font-family: sans-serif; }"
            
        # 解决字体问题
        # 注意: 这里的字体链接也应该由主题管理，暂时保留作为修复的一部分
        font_fix_css = """
        /* Web字体 - 思源黑体（微软雅黑的完美替代品，支持PDF嵌入） */
        @import url('https://fonts.font.im/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        """
        css = font_fix_css + "\n" + css
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
{css}
    </style>
</head>
<body>
{{{{CONTENT_PLACEHOLDER}}}}
</body>
</html>
"""
    
    def save_page(self, page_num: int, html_content: str, template: str) -> str:
        """保存单页"""
        full_html = template.replace("{{CONTENT_PLACEHOLDER}}", html_content)
        page_path = self.pages_dir / f"page-{page_num:02d}.html"
        page_path.write_text(full_html, encoding='utf-8')
        return str(page_path)
    
    def merge_pages(self, pages_html: List[str], template: str) -> str:
        """合并所有页面"""
        all_content = "\n".join(pages_html)
        full_html = template.replace("{{CONTENT_PLACEHOLDER}}", all_content)
        
        merged_path = self.output_dir / "presentation.html"
        merged_path.write_text(full_html, encoding='utf-8')
        
        console.print(f"[green]✓[/green] HTML 已生成: {merged_path}")
        return str(merged_path)
    
    def generate_pdf(self, doc_name: str = "presentation") -> str:
        """生成 PDF"""
        console.print(f"\n[cyan]📄 生成 PDF...[/cyan]")
        
        from PyPDF2 import PdfMerger
        import glob
        
        # 临时 PDF 目录
        temp_dir = self.output_dir / "temp_pdfs"
        temp_dir.mkdir(exist_ok=True)
        
        # 获取所有页面
        page_files = sorted(glob.glob(str(self.pages_dir / "page-*.html")))
        if not page_files:
            raise Exception("未找到页面文件")
        
        # 优先使用本地转换脚本
        convert_script = Path(__file__).parent.parent / "convert_to_pdf_local.js"
        if not convert_script.exists():
            # 回退到云服务版本
            convert_script = Path(__file__).parent.parent / "convert_to_pdf.js"
        
        pdf_files = []
        failed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]转换页面...", total=len(page_files))
            
            # 并行转换 PDF
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def convert_single_page(page_file):
                page_name = Path(page_file).stem
                pdf_file = temp_dir / f"{page_name}.pdf"
                
                try:
                    result = subprocess.run(
                        ['node', str(convert_script), page_file, str(pdf_file)],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode != 0:
                        return (False, page_name, result.stderr)
                    return (True, str(pdf_file), None)
                    
                except subprocess.TimeoutExpired:
                    return (False, page_name, "Timeout")
                except Exception as e:
                    return (False, page_name, str(e))

            # 根据 CPU 核心数决定并发数，但不超过 8
            import multiprocessing
            max_workers = min(multiprocessing.cpu_count(), 8)
            
            # 保持原始顺序
            future_to_page = {}
            ordered_pdf_files = [None] * len(page_files)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                for i, page_file in enumerate(page_files):
                    future = executor.submit(convert_single_page, page_file)
                    future_to_page[future] = i
                
                # 处理结果
                for future in as_completed(future_to_page):
                    i = future_to_page[future]
                    success, result, error = future.result()
                    
                    if success:
                        ordered_pdf_files[i] = result
                    else:
                        failed_count += 1
                        if failed_count <= 3:
                            console.print(f"[red]✗ {result} 转换失败: {error}[/red]")
                            
                    progress.update(task, advance=1)
            
            # 过滤掉失败的（None）
            pdf_files = [f for f in ordered_pdf_files if f]
        
        if failed_count > 0:
            console.print(f"[yellow]⚠ {failed_count}/{len(page_files)} 页转换失败[/yellow]")
        
        # 合并 PDF
        console.print(f"[cyan]🔗 合并 PDF...[/cyan]")
        merger = PdfMerger()
        
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                merger.append(pdf_file)
        
        date_str = datetime.now().strftime("%Y%m%d")
        pdf_path = self.output_dir / f"{doc_name}_{date_str}.pdf"
        
        merger.write(str(pdf_path))
        merger.close()
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        size_mb = pdf_path.stat().st_size / 1024 / 1024
        console.print(f"[green]✓[/green] PDF 已生成: {pdf_path.resolve()} ({size_mb:.2f} MB)")
        
        return str(pdf_path.resolve())
    
    def generate_pptx(self, pdf_path: str) -> str:
        """生成 PPTX"""
        try:
            from adobe_integration import pdf_to_pptx
            
            console.print(f"\n[cyan]🎯 转换 PPTX...[/cyan]")
            
            pptx_path = pdf_path.replace('.pdf', '.pptx')
            result = pdf_to_pptx(pdf_path, pptx_path)
            
            if result and os.path.exists(result):
                size_mb = os.path.getsize(result) / 1024 / 1024
                console.print(f"[green]✓[/green] PPTX 已生成: {result} ({size_mb:.2f} MB)")
                return result
            
        except Exception as e:
            console.print(f"[yellow]⚠ PPTX 转换失败: {e}[/yellow]")
        
        return ""
