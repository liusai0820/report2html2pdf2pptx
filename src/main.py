#!/usr/bin/env python3
"""
AI 演示文稿生成器 - 主入口

使用 AI 原生的统一架构：
- ContextBuilder: 收集所有信息
- AIOrchestrator: 与 AI 交互
- OutputRenderer: 输出结果
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from config import OPENROUTER_API_KEY
from core import PresentationGenerator

console = Console()


def print_banner():
    """打印欢迎横幅"""
    console.print(Panel.fit(
        "[bold cyan]AI 演示文稿生成器[/bold cyan]\n"
        "[dim]AI 原生架构 · 智能生成 · 专业输出[/dim]",
        border_style="cyan"
    ))


def check_api_key():
    """检查 API 密钥"""
    if not OPENROUTER_API_KEY:
        console.print("[red]错误: 未设置 OPENROUTER_API_KEY[/red]")
        console.print("[dim]请在 config/.env 中配置[/dim]")
        sys.exit(1)


def select_scenario() -> str:
    """选择场景"""
    scenarios = [
        ("consulting", "咨询研究/汇报", "政府汇报、咨询报告、研究课题"),
        ("annual_review", "年终述职/总结", "年终总结、工作汇报、述职报告"),
        ("company_intro", "公司/项目介绍", "公司介绍、项目路演、产品发布"),
        ("academic", "学术研究/答辩", "学术报告、论文答辩、研究分享"),
        ("creative", "创意/营销", "品牌推广、营销方案、创意提案"),
        ("government", "政府公文", "政府报告、政策解读、党建汇报"),
    ]
    
    console.print("\n[bold cyan]选择场景：[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("序号", width=6)
    table.add_column("场景", width=20)
    table.add_column("说明")
    
    for i, (_, name, desc) in enumerate(scenarios, 1):
        table.add_row(str(i), name, desc)
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n选择",
        choices=[str(i) for i in range(1, len(scenarios) + 1)],
        default="1"
    )
    
    return scenarios[int(choice) - 1][0]


def select_file() -> str:
    """选择输入文件"""
    input_dir = Path("input")
    if not input_dir.exists():
        input_dir = Path("../input")
    
    if not input_dir.exists():
        console.print("[red]错误: 找不到 input 目录[/red]")
        sys.exit(1)
    
    files = []
    for ext in ['.docx', '.doc', '.md', '.json', '.txt']:
        files.extend(input_dir.rglob(f"*{ext}"))
    
    files = sorted(files)
    
    if not files:
        console.print("[red]错误: input 目录中没有文件[/red]")
        sys.exit(1)
    
    console.print("\n[bold cyan]选择文件：[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("序号", width=6)
    table.add_column("文件")
    table.add_column("大小", width=12)
    
    for i, f in enumerate(files, 1):
        size = f.stat().st_size / 1024
        size_str = f"{size:.1f} KB" if size < 1024 else f"{size/1024:.1f} MB"
        table.add_row(str(i), f.name, size_str)
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n选择",
        choices=[str(i) for i in range(1, len(files) + 1)]
    )
    
    return str(files[int(choice) - 1])


def get_config() -> dict:
    """获取用户配置"""
    console.print("\n[bold cyan]配置参数：[/bold cyan]\n")
    
    config = {}
    
    config["organization"] = Prompt.ask(
        "汇报单位",
        default="深圳国家高技术产业创新中心"
    )
    
    config["target_pages"] = int(Prompt.ask(
        "目标页数",
        default="25"
    ))
    
    depth = Prompt.ask(
        "内容深度 (1=简洁 2=标准 3=详细)",
        choices=["1", "2", "3"],
        default="2"
    )
    config["content_depth"] = {"1": "brief", "2": "normal", "3": "detailed"}[depth]
    
    return config


async def run_interactive():
    """交互式模式"""
    print_banner()
    check_api_key()
    
    # 选择场景
    scenario = select_scenario()
    
    # 选择文件
    document_path = select_file()
    
    # 获取配置
    config = get_config()
    
    # 确认
    console.print("\n[bold cyan]确认配置：[/bold cyan]")
    console.print(f"  场景: {scenario}")
    console.print(f"  文件: {Path(document_path).name}")
    console.print(f"  单位: {config['organization']}")
    console.print(f"  页数: {config['target_pages']}")
    
    if not Confirm.ask("\n开始生成?", default=True):
        console.print("[yellow]已取消[/yellow]")
        return
    
    # 生成
    generator = PresentationGenerator()
    await generator.generate(
        document_path=document_path,
        scenario=scenario,
        config=config
    )


async def run_cli(args):
    """命令行模式"""
    check_api_key()
    
    config = {
        "organization": args.org or "",
        "target_pages": args.pages,
        "content_depth": args.depth,
    }
    
    generator = PresentationGenerator()
    await generator.generate(
        document_path=args.document,
        scenario=args.scenario,
        config=config,
        output_dir=args.output,
        skip_pdf=args.skip_pdf,
        skip_pptx=args.skip_pptx,
    )


def main():
    parser = argparse.ArgumentParser(
        description="AI 演示文稿生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式模式
  python main.py
  
  # 命令行模式
  python main.py document.docx --scenario consulting --pages 30
  
  # 指定输出目录
  python main.py document.docx -o output/my_ppt
"""
    )
    
    parser.add_argument("document", nargs="?", help="输入文档路径")
    parser.add_argument("--scenario", "-s", default="consulting",
                        choices=["consulting", "annual_review", "company_intro", 
                                "academic", "creative", "government"],
                        help="场景类型")
    parser.add_argument("--org", help="汇报单位")
    parser.add_argument("--pages", type=int, default=25, help="目标页数")
    parser.add_argument("--depth", default="normal",
                        choices=["brief", "normal", "detailed"],
                        help="内容深度")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--skip-pdf", action="store_true", help="跳过 PDF")
    parser.add_argument("--skip-pptx", action="store_true", help="跳过 PPTX")
    
    args = parser.parse_args()
    
    try:
        if args.document:
            asyncio.run(run_cli(args))
        else:
            asyncio.run(run_interactive())
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消[/yellow]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
