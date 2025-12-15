#!/usr/bin/env python3
"""批量修改HTML页面样式，去掉侧边色条设计"""

import os
import re
from pathlib import Path

def fix_html_styles(html_content):
    """修改HTML中的样式，去掉侧边色条"""
    
    # 1. 去掉 .sub-head 的 border-left
    html_content = re.sub(
        r'\.sub-head\s*\{[^}]*border-left:\s*6px\s+solid[^;]+;[^}]*\}',
        lambda m: m.group(0).replace('border-left: 6px solid var(--primary-light);', ''),
        html_content
    )
    
    # 2. 去掉 .bottom-box 的 border-left
    html_content = re.sub(
        r'(\.bottom-box\s*\{[^}]*)(border-left:\s*8px\s+solid[^;]+;)',
        r'\1',
        html_content
    )
    
    # 3. 去掉 .compare-left 和 .compare-right 的 border-left
    html_content = re.sub(
        r'(\.compare-left\s*\{[^}]*)(border-left:\s*6px\s+solid[^;]+;)',
        r'\1',
        html_content
    )
    html_content = re.sub(
        r'(\.compare-right\s*\{[^}]*)(border-left:\s*6px\s+solid[^;]+;)',
        r'\1',
        html_content
    )
    
    # 4. 去掉内联样式中的 border-left
    html_content = re.sub(
        r'border-left:\s*[^;"]+;?\s*',
        '',
        html_content
    )
    
    # 5. 改善红色背景色 - 从深红改为柔和的蓝色
    html_content = html_content.replace('background-color: #b03a2e', 'background-color: #5DADE2')
    html_content = html_content.replace('color: #b03a2e', 'color: #2874A6')
    html_content = html_content.replace('#b03a2e', '#5DADE2')
    
    # 6. 改善对比布局的背景色
    html_content = html_content.replace('background: #FFF5F5', 'background: #EBF5FB')
    html_content = html_content.replace('background: #F0FFF4', 'background: #E8F8F5')
    
    # 7. 改善红色相关颜色
    html_content = html_content.replace('#E53935', '#5DADE2')
    html_content = html_content.replace('#C62828', '#2874A6')
    
    # 8. 添加顶部边框来替代侧边条
    html_content = re.sub(
        r'(\.sub-head\s*\{[^}]*)(font-weight:\s*bold;)',
        r'\1border-top: 3px solid var(--primary-light); padding-top: 10px; \2',
        html_content
    )
    
    html_content = re.sub(
        r'(\.bottom-box\s*\{[^}]*)(background:\s*var\(--background-alt\);)',
        r'\1\2 border-top: 3px solid var(--primary);',
        html_content
    )
    
    return html_content

def process_directory(pages_dir):
    """处理目录中的所有HTML文件"""
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        print(f"错误：目录不存在 {pages_dir}")
        return
    
    html_files = list(pages_path.glob("page-*.html"))
    print(f"找到 {len(html_files)} 个HTML文件")
    
    for html_file in html_files:
        print(f"处理: {html_file.name}")
        
        try:
            # 读取文件
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修改样式
            new_content = fix_html_styles(content)
            
            # 写回文件
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ 完成")
            
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    print(f"\n批量处理完成！共处理 {len(html_files)} 个文件")

if __name__ == "__main__":
    pages_dir = "output/新时代背景下智库型青年干部实战化培养模式创新与实践研究报告_20251204_173620/pages"
    process_directory(pages_dir)
