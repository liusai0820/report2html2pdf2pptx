#!/usr/bin/env python3
"""将现有的HTML页面转换为PDF和PPTX"""

import sys
import re
from pathlib import Path
from rich.console import Console

# 确保能找到 core.output_renderer
sys.path.insert(0, "/app/src")

from core.output_renderer import OutputRenderer

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[yellow]用法:[/yellow] python run_convert.py <output_directory>")
        sys.exit(1)
    
    # 容器内路径调整
    output_dir_str = sys.argv[1]
    if not output_dir_str.startswith("/app"):
        # 如果传入的是相对路径，尝试修正
        output_dir_str = str(Path("/app") / output_dir_str)
        
    output_path = Path(output_dir_str)
    
    if not output_path.exists():
        console.print(f"[red]✗[/red] 目录不存在: {output_path}")
        # 尝试列出 output 下的内容帮用户调试
        console.print(f"当前 output 目录内容: {list(Path('/app/output').glob('*'))}")
        sys.exit(1)
    
    pages_dir = output_path / "pages"
    if not pages_dir.exists():
        console.print(f"[red]✗[/red] pages 目录不存在: {pages_dir}")
        sys.exit(1)
    
    # 检查HTML页面
    html_files = list(pages_dir.glob("page-*.html"))
    if not html_files:
        console.print(f"[red]✗[/red] 未找到HTML页面")
        sys.exit(1)
    
    console.print(f"\n[bold cyan]HTML转PDF和PPTX工具[/bold cyan]")
    console.print(f"[dim]输入目录: {output_path}[/dim]")
    console.print(f"[dim]找到 {len(html_files)} 个HTML页面[/dim]\n")
    
    # 使用 OutputRenderer
    renderer = OutputRenderer(str(output_path))
    
    # 智能生成文档名称（去掉时间戳后缀）
    # 假设格式: DocName_YYYYMMDD_HHMMSS
    doc_name = output_path.name
    doc_name = re.sub(r'_\d{8}_\d{6}.*$', '', doc_name)
    
    try:
        # 生成 PDF
        console.print("[bold]步骤 1/2: 生成PDF[/bold]")
        pdf_path = renderer.generate_pdf(doc_name)
        
        # 生成 PPTX
        console.print(f"\n[bold]步骤 2/2: 转换为PPTX[/bold]")
        try:
            pptx_path = renderer.generate_pptx(pdf_path)
        except Exception as e:
            console.print(f"[yellow]PPTX 生成失败 (可能是缺少 Adobe 凭证): {e}[/yellow]")
            pptx_path = None
        
        # 完成
        console.print(f"\n[bold green]✨ 全部完成！[/bold green]")
        console.print(f"  PDF: [cyan]{pdf_path}[/cyan]")
        if pptx_path:
            console.print(f"  PPTX: [cyan]{pptx_path}[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]✗ 错误: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
