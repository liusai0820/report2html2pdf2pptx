#!/usr/bin/env python3
"""修复现有 HTML 文件的字体，然后转 PDF 并合并"""
import os
import re
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()

# 字体嵌入 CSS
FONT_STYLE = """
    <style>
        /* Web字体 - 思源黑体（微软雅黑的完美替代品，支持PDF嵌入） */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        
        /* 字体优先级：本地微软雅黑 > Web字体思源黑体 > 系统字体 */
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei'), 
                 local('微软雅黑'),
                 url('https://fonts.gstatic.com/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 400;
            font-display: swap;
        }
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei Bold'), 
                 local('微软雅黑 Bold'),
                 url('https://fonts.gstatic.com/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 700;
            font-display: swap;
        }
        
        /* 全局字体替换 */
        body, * {
            font-family: 'Microsoft YaHei Web', 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
        }
    </style>
"""

def fix_html_fonts(html_content: str) -> str:
    """修复 HTML 中的字体"""
    
    # 1. 如果已经有 @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC
    # 就不需要再加了，但要确保有 @font-face 定义
    
    # 2. 检查是否已经有字体定义
    if 'Microsoft YaHei Web' in html_content:
        console.print("[yellow]⚠[/yellow] 该文件已经包含字体定义，跳过")
        return html_content
    
    # 3. 在 </head> 前插入字体定义
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', FONT_STYLE + '\n</head>')
    elif '<head>' in html_content:
        # 如果没有 </head>，在 <head> 后插入
        html_content = html_content.replace('<head>', '<head>' + FONT_STYLE)
    else:
        # 如果没有 head 标签，在最开始插入
        html_content = FONT_STYLE + '\n' + html_content
    
    # 4. 替换所有 font-family 定义中的 "Microsoft YaHei" 为 "Microsoft YaHei Web"
    # 但要保留原有的字体堆栈
    html_content = re.sub(
        r'font-family:\s*"?Microsoft YaHei"?',
        'font-family: "Microsoft YaHei Web"',
        html_content
    )
    
    return html_content

def convert_html_to_pdf(html_path: str, pdf_path: str) -> bool:
    """使用 Node.js Puppeteer 将 HTML 转换为 PDF（快速）"""
    # 尝试多个可能的路径
    possible_paths = [
        Path(__file__).parent.parent / "src" / "convert_to_pdf_local.js",
        Path(__file__).parent.parent / "src" / "convert_to_pdf.js",
        Path(__file__).parent / "convert_to_pdf.js",
    ]
    
    convert_script = None
    for path in possible_paths:
        if path.exists():
            convert_script = path
            break
    
    if not convert_script:
        console.print(f"[red]✗[/red] 转换脚本不存在")
        return False
    
    try:
        result = subprocess.run(
            ['node', str(convert_script), html_path, pdf_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            console.print(f"[red]✗[/red] 转换失败")
            console.print(f"[dim]{result.stderr}[/dim]")
            return False
        
        # 检查 PDF 文件是否被创建
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            console.print(f"[red]✗[/red] PDF 文件未生成: {pdf_path}")
            return False
        
        return True
    
    except subprocess.TimeoutExpired:
        console.print(f"[red]✗[/red] 转换超时")
        return False
    except Exception as e:
        console.print(f"[red]✗[/red] 转换错误: {str(e)}")
        return False

def process_html_files(pages_dir: str):
    """处理目录中的所有 HTML 文件"""
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        console.print(f"[red]✗[/red] 目录不存在: {pages_dir}")
        return
    
    # 查找所有 HTML 文件
    html_files = sorted(pages_path.glob("page-*.html"))
    
    if not html_files:
        console.print(f"[red]✗[/red] 未找到 HTML 文件")
        return
    
    console.print(f"\n[bold cyan]找到 {len(html_files)} 个 HTML 文件[/bold cyan]\n")
    
    # 1. 修复字体
    console.print("[cyan]📝 修复字体...[/cyan]")
    fixed_files = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]修复字体...", total=len(html_files))
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                fixed_content = fix_html_fonts(content)
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                fixed_files.append(html_file)
                progress.update(task, advance=1)
            except Exception as e:
                console.print(f"[red]✗[/red] 处理失败 {html_file.name}: {str(e)}")
                progress.update(task, advance=1)
    
    console.print(f"[green]✓[/green] 已修复 {len(fixed_files)} 个文件\n")
    
    # 2. 转换为 PDF
    console.print("[cyan]🔄 转换为 PDF...[/cyan]")
    pdf_dir = pages_path.parent / "pdfs"
    pdf_dir.mkdir(exist_ok=True)
    
    pdf_files = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]转换 PDF...", total=len(fixed_files))
        
        for html_file in fixed_files:
            pdf_file = pdf_dir / (html_file.stem.replace('page-', 'page_') + '.pdf')
            
            success = convert_html_to_pdf(str(html_file), str(pdf_file))
            
            if success:
                pdf_files.append(pdf_file)
            
            progress.update(task, advance=1)
    
    console.print(f"[green]✓[/green] 已生成 {len(pdf_files)} 个 PDF 文件\n")
    
    # 3. 合并 PDF
    if pdf_files:
        console.print("[cyan]📦 合并 PDF...[/cyan]")
        merge_pdfs(sorted(pdf_files), pages_path.parent / "presentation_fixed.pdf")
    else:
        console.print("[yellow]⚠[/yellow] 没有 PDF 文件可以合并")

def merge_pdfs(pdf_files: list, output_path: Path):
    """合并 PDF 文件"""
    try:
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        for pdf_file in pdf_files:
            merger.append(str(pdf_file))
        
        merger.write(str(output_path))
        merger.close()
        
        console.print(f"[green]✓[/green] PDF 已合并: {output_path}")
        
        # 显示文件大小
        file_size = output_path.stat().st_size / 1024 / 1024
        console.print(f"[dim]文件大小: {file_size:.2f} MB[/dim]")
        
    except ImportError:
        console.print("[yellow]⚠[/yellow] 需要安装 PyPDF2: pip install PyPDF2")
    except Exception as e:
        console.print(f"[red]✗[/red] 合并失败: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pages_dir = sys.argv[1]
    else:
        pages_dir = "tools/ai-generator/output/人才专题_20251121_095339/pages"
    
    process_html_files(pages_dir)
