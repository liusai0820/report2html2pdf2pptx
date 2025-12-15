#!/usr/bin/env python3
"""字体修复模块 - 确保生成的 PDF 中的字体可以编辑"""
import re

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

def inject_font_style(html_content: str) -> str:
    """在 HTML 中注入字体定义"""
    
    # 如果已经有字体定义，就不需要再加了
    if 'Microsoft YaHei Web' in html_content:
        return html_content
    
    # 在 </head> 前插入字体定义
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', FONT_STYLE + '\n</head>')
    elif '<head>' in html_content:
        # 如果没有 </head>，在 <head> 后插入
        html_content = html_content.replace('<head>', '<head>' + FONT_STYLE)
    else:
        # 如果没有 head 标签，在最开始插入
        html_content = FONT_STYLE + '\n' + html_content
    
    return html_content

def fix_font_family(html_content: str) -> str:
    """修复 font-family 定义，使用 Web 字体"""
    
    # 替换所有 font-family 定义中的 "Microsoft YaHei" 为 "Microsoft YaHei Web"
    html_content = re.sub(
        r'font-family:\s*"?Microsoft YaHei"?',
        'font-family: "Microsoft YaHei Web"',
        html_content
    )
    
    return html_content

def ensure_editable_fonts(html_content: str) -> str:
    """确保 HTML 中的字体可以在 PDF 中编辑"""
    html_content = inject_font_style(html_content)
    html_content = fix_font_family(html_content)
    return html_content
