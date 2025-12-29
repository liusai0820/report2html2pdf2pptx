#!/usr/bin/env python3
import argparse
import sys
import re
import asyncio
from pathlib import Path
import PyPDF2

# 尝试导入可选库以获得更好的显示效果
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    console = Console()
except ImportError:
    class Mock:
        def print(self, *args, **kwargs): print(*args)
    console = Mock()
    Progress = None

async def convert_to_pdf(input_dir: Path, output_file: Path, replace_rules: dict = None):
    """
    核心转换逻辑
    """
    # 检查依赖
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[red]错误: 未安装 playwright。请运行: pip install playwright && playwright install chromium[/red]")
        sys.exit(1)

    # 1. 扫描文件
    if not input_dir.exists():
        console.print(f"[red]错误: 目录不存在 {input_dir}[/red]")
        return

    # 优先查找 page-01.html 这种格式，并按数字排序
    html_files = sorted(input_dir.glob("page-*.html"), key=lambda x: int(re.search(r'(\d+)', x.name).group(1) or 0))
    
    # 如果没找到，尝试所有 html
    if not html_files:
        console.print(f"[yellow]提示: 在 {input_dir} 中未找到 page-*.html 文件，尝试查找所有 .html[/yellow]")
        html_files = sorted(input_dir.glob("*.html"))
        # 排除 presentation.html 自身，防止递归
        html_files = [f for f in html_files if f.name != "presentation.html" and f.name != "index.html"]
    
    if not html_files:
        console.print("[red]错误: 未找到任何有效 HTML 文件[/red]")
        return

    # 2. 文本修正 (可选)
    if replace_rules:
        console.print(f"[cyan]执行文本修正: {replace_rules}[/cyan]")
        replace_count = 0
        for f in html_files:
            content = f.read_text(encoding='utf-8')
            modified = False
            for old, new in replace_rules.items():
                if old in content:
                    content = content.replace(old, new)
                    modified = True
            if modified:
                f.write_text(content, encoding='utf-8')
                replace_count += 1
        console.print(f"[green]已修正 {replace_count} 个文件[/green]")

    # 3. 转换 PDF
    temp_pdfs = []
    
    async with async_playwright() as p:
        console.print(f"[bold cyan]启动浏览器渲染引擎...[/bold cyan]")
        browser = await p.chromium.launch()
        # 创建 1280x720 的上下文
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        console.print(f"[bold green]开始转换 {len(html_files)} 个页面...[/bold green]")
        
        # 使用 rich 进度条
        if Progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("PDF 渲染中...", total=len(html_files))
                
                for f in html_files:
                    pdf_path = f.with_suffix(".pdf")
                    # 使用 file:// 协议访问本地文件
                    await page.goto(f"file://{f.resolve()}")
                    
                    # 只有在必要时才等待加载（比如有动画），这里默认直接打印
                    # await page.wait_for_timeout(100) 
                    
                    await page.pdf(
                        path=pdf_path,
                        width="1280px",
                        height="720px",
                        print_background=True, # 关键：打印背景图
                        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                        page_ranges="1"
                    )
                    temp_pdfs.append(pdf_path)
                    progress.advance(task)
        else:
            # 降级模式
            for i, f in enumerate(html_files, 1):
                print(f"Converting [{i}/{len(html_files)}]: {f.name}...")
                pdf_path = f.with_suffix(".pdf")
                await page.goto(f"file://{f.resolve()}")
                await page.pdf(path=pdf_path, width="1280px", height="720px", print_background=True)
                temp_pdfs.append(pdf_path)

        await browser.close()

    # 4. 合并 PDF
    console.print("[cyan]正在合并 PDF 文件...[/cyan]")
    merger = PyPDF2.PdfMerger()
    for pdf in temp_pdfs:
        merger.append(str(pdf))
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    merger.write(str(output_file))
    merger.close()
    
    console.print(f"\n[bold green]✨ 任务完成！[/bold green]")
    console.print(f"📂 输出文件: [link=file://{output_file}]{output_file}[/link]")
    
    # Mac/Linux 尝试选中文件
    if sys.platform == "darwin":
        import os
        os.system(f"open -R '{output_file}'")

def main():
    parser = argparse.ArgumentParser(
        description="Skill Agent: HTML to Presentation PDF Converter",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_dir", help="包含 page-*.html 文件的目录路径")
    parser.add_argument("-o", "--output", help="输出 PDF 的路径或文件名 (默认为 merged_presentation.pdf)", default="merged_presentation.pdf")
    parser.add_argument("--fix-text", action="store_true", help="[可选] 自动将页面中的 '智库解读' 替换为 '解读'")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir).resolve()
    
    # 处理输出路径
    if Path(args.output).is_absolute():
        output_path = Path(args.output)
    else:
        # 如果不是绝对路径，默认输出到 input_dir 的上级目录（通常是 output/ReportName/merged.pdf）
        output_path = input_path.parent / args.output
        
    replace_Map = {"智库解读": "解读"} if args.fix_text else None
    
    try:
        asyncio.run(convert_to_pdf(input_path, output_path, replace_Map))
    except KeyboardInterrupt:
        console.print("\n[yellow]任务已取消[/yellow]")

if __name__ == "__main__":
    main()
