#!/usr/bin/env python3
"""将现有的HTML页面转换为PDF和PPTX"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.output_renderer import OutputRenderer
from rich.console import Console

console = Console()


def main():
    if len(sys.argv) < 2:
        console.print("[yellow]用法:[/yellow] python scripts/convert_existing_pages.py <output_directory>")
        console.print("[yellow]示例:[/yellow] python scripts/convert_existing_pages.py output/新时代背景下智库型青年干部实战化培养模式创新与实践研究报告_20251204_173620")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    output_path = Path(output_dir)
    
    if not output_path.exists():
        console.print(f"[red]✗[/red] 目录不存在: {output_dir}")
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
    console.print(f"[dim]输入目录: {output_dir}[/dim]")
    console.print(f"[dim]找到 {len(html_files)} 个HTML页面[/dim]\n")
    
    # 使用 OutputRenderer
    renderer = OutputRenderer(str(output_path))
    
    # 生成文档名称
    doc_name = output_path.name.replace("_20251204_173620", "")
    
    try:
        # 生成 PDF
        console.print("[bold]步骤 1/2: 生成PDF[/bold]")
        pdf_path = renderer.generate_pdf(doc_name)
        
        # 生成 PPTX
        console.print(f"\n[bold]步骤 2/2: 转换为PPTX[/bold]")
        pptx_path = renderer.generate_pptx(pdf_path)
        
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
