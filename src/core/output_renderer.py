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
        
        # 修复 PDF 生成时的图片路径问题
        # HTML 中的路径通常是 /output/assets/... (Web 路径)
        # 本地 PDF 生成(use file://) 需要相对路径: ../../assets/...
        
        # 将绝对路径 /output/ 替换为相对路径 ../../
        # 结果: url('../../assets/...')
        full_html = full_html.replace("url('/output/", "url('../../")
        
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
        """生成 PDF
        
        策略：
        1. Render 环境：跳过 PDF 生成，仅返回 HTML。用户需下载 HTML 在本地转换。
        2. 本地环境：使用 Playwright 生成完美 PDF。
        """
        console.print(f"\n[cyan]📄 生成 PDF...[/cyan]")
        
        date_str = datetime.now().strftime("%Y%m%d")
        final_pdf_path = self.output_dir / f"{doc_name}_{date_str}.pdf"
        source_html = self.output_dir / "presentation.html"
        
        if not source_html.exists():
            console.print("[red]✗ presentation.html 不存在[/red]")
            return None

        # 检测环境
        is_render = os.getenv('RENDER') or os.getenv('render')
        
        if is_render:
            console.print("[yellow]☁️ Render环境：跳过 PDF 生成 (请下载 HTML 在本地转换)[/yellow]")
            return None

        # --- 本地 Playwright (唯一方案) ---
        try:
            console.print("[cyan]🖥 使用 Playwright 生成 PDF (本地)...[/cyan]")
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 加载 HTML
                page.goto(f"file://{source_html.resolve()}", wait_until="networkidle")
                page.wait_for_timeout(2000) # 给 ECharts 更多时间
                
                page.pdf(
                    path=str(final_pdf_path),
                    width="1280px",
                    height="720px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    scale=1
                )
                browser.close()
            
            if final_pdf_path.exists():
                size_mb = final_pdf_path.stat().st_size / 1024 / 1024
                console.print(f"[green]✓[/green] PDF 已生成: {final_pdf_path.name} ({size_mb:.2f} MB)")
                # 尝试压缩 (可选)
                self._compress_pdf(final_pdf_path)
                return str(final_pdf_path.resolve())
                
        except ImportError:
            console.print("[yellow]⚠ 未安装 Playwright，请运行: pip install playwright && playwright install chromium[/yellow]")
        except Exception as e:
            console.print(f"[red]⚠ Playwright 失败: {e}[/red]")

        return None

    def _compress_pdf(self, file_path: Path):
        """简单压缩 PDF (去除未使用的对象)"""
        try:
            old_size = file_path.stat().st_size / 1024 / 1024
            
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(str(file_path))
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
                
            # 压缩元数据
            writer.add_metadata(reader.metadata)
            
            temp_path = file_path.parent / f"compressed_{file_path.name}"
            with open(temp_path, "wb") as f:
                writer.write(f)
            
            new_size = temp_path.stat().st_size / 1024 / 1024
            
            if new_size < old_size:
                # 只有变小了才替换
                os.remove(file_path)
                temp_path.rename(file_path)
                console.print(f"[green]✓[/green] PDF 已压缩: {old_size:.2f}MB -> {new_size:.2f}MB")
            else:
                os.remove(temp_path)
                console.print(f"[dim]PDF 压缩未变小 ({old_size:.2f}MB)[/dim]")
                
        except Exception as e:
            console.print(f"[yellow]⚠ PDF压缩跳过: {e}[/yellow]")
    
    def generate_pptx(self, pdf_path: str) -> str:
        """生成 PPTX (已禁用云端转换)"""
        console.print("[yellow]⚠ PPTX 生成：建议使用 WPS/Office 打开生成的 PDF 进行转换，效果最佳[/yellow]")
        return None
