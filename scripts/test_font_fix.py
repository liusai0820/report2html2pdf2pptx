#!/usr/bin/env python3
"""测试字体修复是否已集成到工作流"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.output_renderer import OutputRenderer, FONT_EMBED_CSS, BASE_CSS
from rich.console import Console

console = Console()

def test_font_in_template():
    """测试模板是否包含字体定义"""
    console.print("\n[bold cyan]测试字体修复集成[/bold cyan]\n")
    
    # 创建临时渲染器
    renderer = OutputRenderer("test_output")
    
    # 生成模板
    template = renderer.render_template()
    
    # 检查字体定义
    checks = [
        ("Noto Sans SC", "思源黑体导入"),
        ("Microsoft YaHei Web", "字体别名定义"),
        ("@font-face", "字体嵌入"),
        ("font-display: swap", "字体加载优化"),
    ]
    
    console.print("[bold]检查项：[/bold]\n")
    
    all_passed = True
    for keyword, description in checks:
        if keyword in template:
            console.print(f"  [green]✓[/green] {description}")
        else:
            console.print(f"  [red]✗[/red] {description} - 未找到 '{keyword}'")
            all_passed = False
    
    # 显示字体定义部分
    if "Microsoft YaHei Web" in template:
        console.print("\n[bold]字体定义预览：[/bold]")
        lines = template.split('\n')
        in_font_section = False
        for line in lines:
            if '@import url' in line or '@font-face' in line:
                in_font_section = True
            if in_font_section:
                console.print(f"  [dim]{line[:80]}[/dim]")
                if '}' in line and '@font-face' in template[:template.index(line)]:
                    in_font_section = False
    
    if all_passed:
        console.print("\n[bold green]✨ 所有检查通过！字体修复已成功集成到工作流[/bold green]")
    else:
        console.print("\n[bold red]✗ 部分检查失败[/bold red]")
    
    return all_passed

if __name__ == "__main__":
    success = test_font_in_template()
    sys.exit(0 if success else 1)
