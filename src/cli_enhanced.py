#!/usr/bin/env python3
"""
增强版 CLI - 支持主题系统的命令行界面

功能:
1. 主题选择
2. 用户配置
3. 预设模板
4. 交互式配置
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

from config import OPENROUTER_API_KEY, DEFAULT_MODEL
from themes import ThemeManager, list_themes, get_theme
from user_config import (
    UserConfig, ConfigManager, 
    get_preset_config, list_preset_configs, PRESET_CONFIGS
)

console = Console()


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🎨 AI演示文稿生成器 v2.0                              ║
║                                                           ║
║     支持多主题 · 个性化配置 · 专业输出                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_api_key():
    """检查API密钥"""
    if not OPENROUTER_API_KEY:
        console.print(Panel(
            "[red]错误: 未设置OPENROUTER_API_KEY[/red]\n\n"
            "请在 config/.env 文件中设置:\n"
            "OPENROUTER_API_KEY=your_api_key_here",
            title="配置错误",
            border_style="red"
        ))
        sys.exit(1)


def select_theme() -> str:
    """交互式选择主题"""
    console.print("\n[bold cyan]🎨 选择演示文稿主题：[/bold cyan]\n")
    
    themes = list_themes()
    
    # 按分类分组显示
    categories = {}
    for theme in themes:
        cat = theme["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(theme)
    
    # 显示主题表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="cyan", width=6)
    table.add_column("主题", style="green", width=20)
    table.add_column("说明", style="white")
    
    theme_list = []
    idx = 1
    for cat, cat_themes in categories.items():
        for theme in cat_themes:
            table.add_row(str(idx), theme["name"], theme["description"])
            theme_list.append(theme["id"])
            idx += 1
    
    console.print(table)
    
    # 选择主题
    choice = Prompt.ask(
        "\n[cyan]请选择主题序号[/cyan]",
        choices=[str(i) for i in range(1, len(theme_list) + 1)],
        default="1"
    )
    
    selected_theme = theme_list[int(choice) - 1]
    theme = get_theme(selected_theme)
    console.print(f"\n[green]✓[/green] 已选择主题: [bold]{theme.metadata.name}[/bold]")
    
    return selected_theme


def select_preset() -> Optional[UserConfig]:
    """选择预设配置"""
    console.print("\n[bold cyan]📋 选择预设模板（可选）：[/bold cyan]\n")
    
    presets = list_preset_configs()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="cyan", width=6)
    table.add_column("模板", style="green", width=15)
    table.add_column("主题", style="yellow", width=15)
    table.add_column("说明", style="white")
    
    table.add_row("0", "自定义", "-", "手动配置所有选项")
    
    for idx, preset in enumerate(presets, 1):
        table.add_row(str(idx), preset["name"], preset["theme"], preset["description"])
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[cyan]请选择预设序号 (0 为自定义)[/cyan]",
        choices=[str(i) for i in range(len(presets) + 1)],
        default="0"
    )
    
    if choice == "0":
        return None
    
    preset_name = list(PRESET_CONFIGS.keys())[int(choice) - 1]
    config = get_preset_config(preset_name)
    console.print(f"\n[green]✓[/green] 已加载预设: [bold]{config.project_name}[/bold]")
    
    return config


def configure_user_settings(base_config: Optional[UserConfig] = None) -> UserConfig:
    """交互式配置用户设置"""
    console.print("\n[bold cyan]⚙️ 配置演示文稿参数：[/bold cyan]\n")
    
    config = base_config or UserConfig()
    
    # 基本信息
    config.organization = Prompt.ask(
        "汇报单位",
        default=config.organization or "深圳国家高技术产业创新中心"
    )
    
    config.project_name = Prompt.ask(
        "项目名称",
        default=config.project_name or "演示文稿"
    )
    
    config.doc_type = Prompt.ask(
        "文档类型",
        default=config.doc_type or "专项咨询研究报告"
    )
    
    # 内容配置
    config.target_pages = int(Prompt.ask(
        "目标页数",
        default=str(config.target_pages)
    ))
    
    depth_choices = {"1": "brief", "2": "normal", "3": "detailed"}
    depth_display = {"brief": "简洁版", "normal": "标准版", "detailed": "详细版"}
    current_depth = next(k for k, v in depth_choices.items() if v == config.content_depth)
    
    console.print("\n内容深度: 1=简洁版, 2=标准版, 3=详细版")
    depth_choice = Prompt.ask(
        "选择内容深度",
        choices=["1", "2", "3"],
        default=current_depth
    )
    config.content_depth = depth_choices[depth_choice]
    
    # 关键词
    keywords_str = Prompt.ask(
        "主题关键词 (逗号分隔)",
        default=", ".join(config.keywords) if config.keywords else ""
    )
    config.keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
    
    # 页面配置
    console.print("\n[dim]页面配置:[/dim]")
    config.include_cover = Confirm.ask("生成封面", default=config.include_cover)
    config.include_agenda = Confirm.ask("生成目录", default=config.include_agenda)
    config.include_closing = Confirm.ask("生成封底", default=config.include_closing)
    
    # 输出配置
    console.print("\n[dim]输出格式:[/dim]")
    config.output_pdf = Confirm.ask("输出 PDF", default=config.output_pdf)
    config.output_pptx = Confirm.ask("输出 PPTX", default=config.output_pptx)
    config.output_html = Confirm.ask("输出 HTML", default=config.output_html)
    
    return config


def select_input_file() -> str:
    """交互式选择输入文件"""
    input_dir = Path("input")
    if not input_dir.exists():
        input_dir = Path("../input")
    if not input_dir.exists():
        input_dir = Path("../../input")
    
    if not input_dir.exists():
        console.print(f"[red]✗ 输入目录不存在: {input_dir}[/red]")
        sys.exit(1)
    
    supported_extensions = ['.docx', '.doc', '.md', '.json']
    files = []
    for ext in supported_extensions:
        files.extend(input_dir.rglob(f"*{ext}"))
    
    files = sorted(files)
    
    if not files:
        console.print(f"[red]✗ 输入目录中没有找到支持的文件[/red]")
        sys.exit(1)
    
    console.print("\n[bold cyan]📁 可用的输入文件：[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="cyan", width=6)
    table.add_column("文件路径", style="green")
    table.add_column("大小", style="yellow")
    
    for idx, file in enumerate(files, 1):
        size = file.stat().st_size / 1024
        size_str = f"{size:.1f} KB" if size < 1024 else f"{size/1024:.1f} MB"
        rel_path = file.relative_to(input_dir)
        table.add_row(str(idx), str(rel_path), size_str)
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[cyan]请选择文件序号[/cyan]",
        choices=[str(i) for i in range(1, len(files) + 1)]
    )
    
    return str(files[int(choice) - 1])


def create_output_dir(document_name: str) -> str:
    """创建输出目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_name = Path(document_name).stem
    output_dir = Path("output") / f"{doc_name}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


def show_config_summary(theme_id: str, config: UserConfig, document_path: str):
    """显示配置摘要"""
    theme = get_theme(theme_id)
    
    console.print("\n[bold cyan]📋 配置摘要：[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("项目", style="dim")
    table.add_column("值", style="green")
    
    table.add_row("主题", theme.metadata.name)
    table.add_row("文档", Path(document_path).name)
    table.add_row("单位", config.organization)
    table.add_row("项目", config.project_name)
    table.add_row("页数", f"{config.target_pages} 页")
    table.add_row("深度", {"brief": "简洁版", "normal": "标准版", "detailed": "详细版"}[config.content_depth])
    
    outputs = []
    if config.output_pdf:
        outputs.append("PDF")
    if config.output_pptx:
        outputs.append("PPTX")
    if config.output_html:
        outputs.append("HTML")
    table.add_row("输出", ", ".join(outputs))
    
    console.print(table)


async def run_generation(
    document_path: str,
    theme_id: str,
    config: UserConfig,
    output_dir: str
):
    """运行生成流程"""
    from themed_slide_generator import ThemedSlideGenerator
    
    generator = ThemedSlideGenerator(
        theme_id=theme_id,
        user_config=config.to_dict(),
        output_dir=output_dir
    )
    
    await generator.run(
        document_path,
        skip_pdf=not config.output_pdf,
    )


def interactive_mode():
    """交互式模式"""
    print_banner()
    check_api_key()
    
    console.print("\n[bold]欢迎使用 AI 演示文稿生成器！[/bold]\n")
    
    # 1. 选择预设或自定义
    preset_config = select_preset()
    
    # 2. 选择主题
    if preset_config:
        theme_id = preset_config.theme_id
        console.print(f"[dim]使用预设主题: {theme_id}[/dim]")
    else:
        theme_id = select_theme()
    
    # 3. 配置参数
    if preset_config:
        # 询问是否修改预设配置
        if Confirm.ask("\n是否修改预设配置?", default=False):
            config = configure_user_settings(preset_config)
        else:
            config = preset_config
    else:
        config = configure_user_settings()
    
    config.theme_id = theme_id
    
    # 4. 选择文件
    document_path = select_input_file()
    
    # 5. 创建输出目录
    output_dir = create_output_dir(document_path)
    
    # 6. 显示配置摘要
    show_config_summary(theme_id, config, document_path)
    
    # 7. 确认开始
    if not Confirm.ask("\n确认开始生成?", default=True):
        console.print("[yellow]已取消[/yellow]")
        sys.exit(0)
    
    # 8. 执行生成
    try:
        asyncio.run(run_generation(document_path, theme_id, config, output_dir))
    except Exception as e:
        console.print(f"\n[bold red]✗ 生成失败: {str(e)}[/bold red]")
        sys.exit(1)


def list_themes_command():
    """列出所有主题"""
    console.print("\n[bold cyan]🎨 可用主题列表：[/bold cyan]\n")
    
    themes = list_themes()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("分类", style="yellow")
    table.add_column("说明", style="white")
    
    for theme in themes:
        table.add_row(
            theme["id"],
            theme["name"],
            theme["category"],
            theme["description"]
        )
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="AI演示文稿生成器 v2.0 - 支持多主题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式模式（推荐）
  python cli_enhanced.py
  
  # 指定主题
  python cli_enhanced.py --theme company_intro document.json
  
  # 使用预设
  python cli_enhanced.py --preset hetao document.json
  
  # 列出所有主题
  python cli_enhanced.py --list-themes
  
  # 列出所有预设
  python cli_enhanced.py --list-presets
        """
    )
    
    parser.add_argument(
        'document',
        nargs='?',
        help='文档路径 (JSON、Markdown或DOCX格式)'
    )
    
    parser.add_argument(
        '--theme', '-t',
        default='consulting',
        help='主题 ID (默认: consulting)'
    )
    
    parser.add_argument(
        '--preset', '-p',
        help='使用预设配置'
    )
    
    parser.add_argument(
        '--list-themes',
        action='store_true',
        help='列出所有可用主题'
    )
    
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='列出所有预设配置'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='输出目录'
    )
    
    parser.add_argument(
        '--org',
        help='汇报单位'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=25,
        help='目标页数 (默认: 25)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.list_themes:
            list_themes_command()
        elif args.list_presets:
            console.print("\n[bold cyan]📋 可用预设配置：[/bold cyan]\n")
            for preset in list_preset_configs():
                console.print(f"  [cyan]{preset['id']}[/cyan] - {preset['name']} ({preset['theme']})")
        elif args.document:
            # 命令行模式
            check_api_key()
            
            # 加载配置
            if args.preset:
                config = get_preset_config(args.preset)
                if not config:
                    console.print(f"[red]✗ 预设不存在: {args.preset}[/red]")
                    sys.exit(1)
            else:
                config = UserConfig(
                    theme_id=args.theme,
                    target_pages=args.pages,
                )
            
            if args.org:
                config.organization = args.org
            
            output_dir = args.output_dir or create_output_dir(args.document)
            
            asyncio.run(run_generation(args.document, config.theme_id, config, output_dir))
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
