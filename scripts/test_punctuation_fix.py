#!/usr/bin/env python3
"""测试中文标点符号修复功能"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.ai_orchestrator import AIOrchestrator
from rich.console import Console

console = Console()


def test_punctuation_conversion():
    """测试标点符号转换"""
    console.print("\n[bold cyan]测试中文标点符号转换[/bold cyan]\n")
    
    orchestrator = AIOrchestrator()
    
    test_cases = [
        # (输入, 期望输出, 描述)
        (
            '<div>构建"数据驱动"的决策体系,实现精准管理.</div>',
            '<div>构建"数据驱动"的决策体系，实现精准管理。</div>',
            '引号、逗号、句号'
        ),
        (
            '<h1 class="title">核心问题:如何提升效率?</h1>',
            '<h1 class="title">核心问题：如何提升效率？</h1>',
            '冒号、问号'
        ),
        (
            '<p>第一,加强培训;第二,优化流程.</p>',
            '<p>第一，加强培训；第二，优化流程。</p>',
            '逗号、分号、句号'
        ),
        (
            '<div style="color: #003366">这是"重点"内容!</div>',
            '<div style="color: #003366">这是"重点"内容！</div>',
            'HTML属性不受影响'
        ),
        (
            '<p>数据显示: 增长率达到48%, 效率提升3.5倍.</p>',
            '<p>数据显示： 增长率达到48%， 效率提升3.5倍。</p>',
            '混合数字和中文'
        ),
        (
            '<div>English text with "quotes", commas, and periods.</div>',
            '<div>English text with "quotes", commas, and periods.</div>',
            '纯英文不转换'
        ),
    ]
    
    all_passed = True
    
    for i, (input_html, expected, description) in enumerate(test_cases, 1):
        result = orchestrator._fix_chinese_punctuation(input_html)
        
        if result == expected:
            console.print(f"[green]✓[/green] 测试 {i}: {description}")
        else:
            console.print(f"[red]✗[/red] 测试 {i}: {description}")
            console.print(f"  输入: [dim]{input_html}[/dim]")
            console.print(f"  期望: [yellow]{expected}[/yellow]")
            console.print(f"  实际: [red]{result}[/red]")
            all_passed = False
    
    if all_passed:
        console.print("\n[bold green]✨ 所有测试通过！[/bold green]")
    else:
        console.print("\n[bold red]✗ 部分测试失败[/bold red]")
    
    return all_passed


if __name__ == "__main__":
    success = test_punctuation_conversion()
    sys.exit(0 if success else 1)
