#!/usr/bin/env python3
"""CLI入口 - 命令行交互界面"""
import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from slide_generator import SlideGenerator
from config import OPENROUTER_API_KEY, DEFAULT_MODEL, AVAILABLE_MODELS
from adobe_integration import pdf_to_pptx, batch_pdf_to_pptx

console = Console()

def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🎨 AI演示文稿生成器 - 混合路径方案                    ║
║                                                           ║
║     基于OpenRouter + Claude的工业级实现                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def check_api_key():
    """检查API密钥"""
    if not OPENROUTER_API_KEY:
        console.print(Panel(
            "[red]错误: 未设置OPENROUTER_API_KEY[/red]\n\n"
            "请创建.env文件并设置:\n"
            "OPENROUTER_API_KEY=your_api_key_here\n\n"
            "或者设置环境变量:\n"
            "export OPENROUTER_API_KEY=your_api_key_here",
            title="配置错误",
            border_style="red"
        ))
        sys.exit(1)

def select_input_file():
    """交互式选择输入文件"""
    # 查找 input 目录（可能在当前目录或上级目录）
    input_dir = Path("input")
    if not input_dir.exists():
        input_dir = Path("../input")
    if not input_dir.exists():
        input_dir = Path("../../input")
    
    if not input_dir.exists():
        console.print(f"[red]✗ 输入目录不存在: {input_dir}[/red]")
        sys.exit(1)
    
    # 查找所有支持的文件（递归搜索，包括子文件夹）
    supported_extensions = ['.docx', '.doc', '.md', '.json']
    files = []
    for ext in supported_extensions:
        files.extend(input_dir.rglob(f"*{ext}"))
    
    files = sorted(files)
    
    if not files:
        console.print(f"[red]✗ 输入目录中没有找到支持的文件[/red]")
        console.print(f"[dim]支持的格式: {', '.join(supported_extensions)}[/dim]")
        sys.exit(1)
    
    # 显示文件列表
    console.print("\n[bold cyan]📁 可用的输入文件：[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="cyan", width=6)
    table.add_column("文件路径", style="green")
    table.add_column("大小", style="yellow")
    
    for idx, file in enumerate(files, 1):
        size = file.stat().st_size / 1024
        size_str = f"{size:.1f} KB" if size < 1024 else f"{size/1024:.1f} MB"
        # 显示相对于input目录的路径
        rel_path = file.relative_to(input_dir)
        table.add_row(str(idx), str(rel_path), size_str)
    
    console.print(table)
    
    # 选择文件
    choice = Prompt.ask(
        "\n[cyan]请选择文件序号[/cyan]",
        choices=[str(i) for i in range(1, len(files) + 1)]
    )
    
    return str(files[int(choice) - 1])

def create_output_dir(document_name: str):
    """创建独立的输出目录"""
    # 使用文档名称和时间戳创建目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_name = Path(document_name).stem  # 获取文件名（不含扩展名）
    output_dir = Path("output") / f"{doc_name}_{timestamp}"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"\n[green]✓[/green] 输出目录: [cyan]{output_dir}[/cyan]")
    
    return str(output_dir)

def get_all_input_files():
    """获取所有输入文件（递归搜索，包括子文件夹）"""
    input_dir = Path("input")
    if not input_dir.exists():
        input_dir = Path("../input")
    if not input_dir.exists():
        input_dir = Path("../../input")
    
    if not input_dir.exists():
        console.print(f"[red]✗ 输入目录不存在: {input_dir}[/red]")
        return []
    
    supported_extensions = ['.docx', '.doc', '.md', '.json']
    files = []
    for ext in supported_extensions:
        files.extend(input_dir.rglob(f"*{ext}"))
    
    return sorted(files)

def interactive_mode():
    """交互式模式 - 简化版（选择文件后直接启动）"""
    print_banner()
    check_api_key()
    
    console.print("\n[bold]欢迎使用AI演示文稿生成器！[/bold]\n")
    
    # 选择文件
    document_path = select_input_file()
    
    # 创建输出目录
    output_dir = create_output_dir(document_path)
    
    # 确认开始
    console.print("\n[bold cyan]准备开始生成:[/bold cyan]")
    console.print(f"  文档: [cyan]{Path(document_path).name}[/cyan]")
    console.print(f"  输出: [cyan]{output_dir}[/cyan]")
    
    if not Confirm.ask("\n确认开始?", default=True):
        console.print("[yellow]已取消[/yellow]")
        sys.exit(0)
    
    # 执行生成（使用默认模型和生成PDF）
    generator = SlideGenerator(output_dir=output_dir)
    asyncio.run(generator.run(document_path, skip_pdf=False))

def batch_process_files(files):
    """批量处理多个文件（使用默认模型和生成PDF）"""
    console.print(f"\n[bold cyan]开始批量处理 {len(files)} 个文件...[/bold cyan]\n")
    
    results = []
    
    for idx, file_path in enumerate(files, 1):
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold cyan]处理文件 {idx}/{len(files)}: {file_path.name}[/bold cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        try:
            # 创建输出目录
            output_dir = create_output_dir(str(file_path))
            
            # 执行生成（使用默认模型和生成PDF）
            generator = SlideGenerator(output_dir=output_dir)
            asyncio.run(generator.run(str(file_path), skip_pdf=False))
            
            results.append({
                'file': file_path.name,
                'status': '✓ 成功',
                'output': output_dir
            })
            
            console.print(f"\n[green]✓ {file_path.name} 处理完成[/green]")
            
        except Exception as e:
            results.append({
                'file': file_path.name,
                'status': f'✗ 失败: {str(e)[:50]}',
                'output': '-'
            })
            console.print(f"\n[red]✗ {file_path.name} 处理失败: {str(e)}[/red]")
    
    # 显示处理结果摘要
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]批量处理完成[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
    
    result_table = Table(show_header=True, header_style="bold magenta")
    result_table.add_column("文件名", style="green")
    result_table.add_column("状态", style="yellow")
    result_table.add_column("输出目录", style="cyan")
    
    for result in results:
        result_table.add_row(result['file'], result['status'], result['output'])
    
    console.print(result_table)
    
    # 统计
    success_count = sum(1 for r in results if '成功' in r['status'])
    console.print(f"\n[bold]总计: {success_count}/{len(files)} 个文件处理成功[/bold]")

def cli_mode(args):
    """命令行模式"""
    check_api_key()
    
    # 创建输出目录
    output_dir = create_output_dir(args.document) if not args.output_dir else args.output_dir
    
    generator = SlideGenerator(output_dir=output_dir)
    asyncio.run(generator.run(args.document, skip_pdf=False))

def pdf_to_pptx_mode(args):
    """PDF转PPTX模式"""
    console.print("\n[bold cyan]📄 PDF转PPTX转换工具[/bold cyan]\n")
    
    # 验证输入文件
    if not os.path.exists(args.pdf_file):
        console.print(f"[red]✗ PDF文件不存在: {args.pdf_file}[/red]")
        sys.exit(1)
    
    # 确定输出路径
    if args.output_pptx:
        output_path = args.output_pptx
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    else:
        output_path = None
    
    try:
        console.print(f"[cyan]📄 输入文件: {args.pdf_file}[/cyan]")
        console.print(f"[cyan]📊 文件大小: {os.path.getsize(args.pdf_file) / 1024:.2f} KB[/cyan]\n")
        
        console.print("[cyan]🚀 开始转换...[/cyan]")
        result = pdf_to_pptx(args.pdf_file, output_path)
        
        if result:
            output_size = os.path.getsize(result) / 1024
            console.print(f"\n[green]✓ 转换成功![/green]")
            console.print(f"[cyan]📁 输出文件: {result}[/cyan]")
            console.print(f"[cyan]📊 输出大小: {output_size:.2f} KB[/cyan]")
        else:
            console.print("[red]✗ 转换失败[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ 转换失败: {str(e)}[/red]")
        sys.exit(1)

def batch_pdf_to_pptx_mode(args):
    """批量PDF转PPTX模式"""
    console.print("\n[bold cyan]📦 批量PDF转PPTX转换工具[/bold cyan]\n")
    
    # 验证输入目录
    if not os.path.isdir(args.pdf_dir):
        console.print(f"[red]✗ 目录不存在: {args.pdf_dir}[/red]")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = args.output_dir or "output/PDFToPPTX"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        console.print(f"[cyan]📁 输入目录: {args.pdf_dir}[/cyan]")
        console.print(f"[cyan]📁 输出目录: {output_dir}[/cyan]\n")
        
        console.print("[cyan]🚀 开始批量转换...[/cyan]")
        results = batch_pdf_to_pptx(args.pdf_dir, output_dir)
        
        if results:
            console.print(f"\n[green]✓ 批量转换完成![/green]")
            console.print(f"[cyan]📊 成功转换 {len(results)} 个文件[/cyan]\n")
            
            # 显示结果表格
            result_table = Table(show_header=True, header_style="bold magenta")
            result_table.add_column("输出文件", style="green")
            result_table.add_column("大小", style="yellow")
            
            for result in results:
                size = os.path.getsize(result) / 1024
                size_str = f"{size:.2f} KB" if size < 1024 else f"{size/1024:.2f} MB"
                result_table.add_row(os.path.basename(result), size_str)
            
            console.print(result_table)
        else:
            console.print("[yellow]⚠ 没有文件被转换[/yellow]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ 批量转换失败: {str(e)}[/red]")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="AI演示文稿生成器 + PDF转PPTX工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式模式（推荐）- 选择文件后确认即启动
  python cli.py
  
  # 命令行模式 - 单个文档
  python cli.py document.json
  
  # 批量处理所有文档
  python cli.py --batch
  
  # 指定输出目录
  python cli.py document.json -o output_folder
  
  # PDF转PPTX - 单个文件
  python cli.py --pdf-to-pptx input.pdf
  
  # PDF转PPTX - 单个文件，指定输出
  python cli.py --pdf-to-pptx input.pdf -o output.pptx
  
  # PDF转PPTX - 批量转换
  python cli.py --batch-pdf-to-pptx pdf_folder -o output_folder
        """
    )
    
    parser.add_argument(
        'document',
        nargs='?',
        help='文档路径 (JSON、Markdown或DOCX格式)'
    )
    
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='批量处理input目录中的所有文档'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='输出目录（默认自动生成）'
    )
    
    parser.add_argument(
        '--pdf-to-pptx',
        metavar='PDF_FILE',
        help='将PDF文件转换为PPTX'
    )
    
    parser.add_argument(
        '--batch-pdf-to-pptx',
        metavar='PDF_DIR',
        help='批量将PDF目录中的文件转换为PPTX'
    )
    
    args = parser.parse_args()
    
    try:
        if args.pdf_to_pptx:
            # PDF转PPTX单个文件模式
            args.pdf_file = args.pdf_to_pptx
            args.output_pptx = args.output_dir
            pdf_to_pptx_mode(args)
        
        elif args.batch_pdf_to_pptx:
            # PDF转PPTX批量模式
            args.pdf_dir = args.batch_pdf_to_pptx
            args.output_dir = args.output_dir
            batch_pdf_to_pptx_mode(args)
        
        elif args.batch:
            # 批量处理模式
            check_api_key()
            files = get_all_input_files()
            
            if not files:
                console.print("[red]✗ 输入目录中没有找到支持的文件[/red]")
                sys.exit(1)
            
            console.print(f"\n[bold cyan]找到 {len(files)} 个文件，开始批量处理...[/bold cyan]")
            batch_process_files(files)
        
        elif args.document:
            cli_mode(args)
        else:
            interactive_mode()
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]错误: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
