#!/usr/bin/env python3
"""字体修复模块 - 确保生成的 PDF 中的字体可以编辑

核心策略：
1. 使用 Web 字体 (@font-face + woff2) 而非系统字体
2. 这样 Puppeteer 渲染 PDF 时会正确嵌入字体
3. 避免 Type3 字体问题
"""
import re

# 黑体字体嵌入 CSS (默认)
FONT_STYLE_MODERN = """
    <style>
        /* Web字体 - 思源黑体 (Noto Sans SC) */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        
        /* @font-face 声明 - 确保 PDF 嵌入 */
        @font-face {
            font-family: 'Noto Sans SC';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url(https://fonts.gstatic.com/s/notosanssc/v26/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VH8V.0.woff2) format('woff2');
            unicode-range: U+4E00-9FFF, U+3400-4DBF;
        }
        @font-face {
            font-family: 'Noto Sans SC';
            font-style: normal;
            font-weight: 700;
            font-display: swap;
            src: url(https://fonts.gstatic.com/s/notosanssc/v26/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VH8V.0.woff2) format('woff2');
            unicode-range: U+4E00-9FFF, U+3400-4DBF;
        }
        
        /* 全局字体替换 */
        html, body, body * {
            font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        }
    </style>
"""

# 楷体字体嵌入 CSS
FONT_STYLE_CLASSIC = """
    <style>
        /* Web字体 - 霞鹜文楷 (LXGW WenKai) 和 Ma Shan Zheng */
        @import url('https://fonts.googleapis.com/css2?family=LXGW+WenKai:wght@300;400;700&family=Ma+Shan+Zheng&display=swap');
        
        /* @font-face 声明 - 楷体 (确保 PDF 嵌入) */
        @font-face {
            font-family: 'LXGW WenKai';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url(https://fonts.gstatic.com/s/lxgwwenkai/v3/1cXxaULGY-g1qwHiY2yBe_-7VBs2JG_T.woff2) format('woff2');
            unicode-range: U+4E00-9FFF, U+3400-4DBF, U+20000-2A6DF, U+2A700-2B73F;
        }
        @font-face {
            font-family: 'Ma Shan Zheng';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url(https://fonts.gstatic.com/s/mashanzheng/v10/NaPecZTIAOuHOAAy39FUqIcU0PJoDQ.woff2) format('woff2');
            unicode-range: U+4E00-9FFF, U+3400-4DBF;
        }
        
        /* 全局字体替换 - 楷体 */
        html, body, body * {
            font-family: 'LXGW WenKai', 'Ma Shan Zheng', 'STKaiti', 'KaiTi', serif !important;
        }
    </style>
"""

def get_font_style(font_type: str = "modern") -> str:
    """获取对应字体风格的 CSS
    
    Args:
        font_type: 'modern' (黑体) 或 'classic' (楷体)
    """
    if font_type == "classic":
        return FONT_STYLE_CLASSIC
    return FONT_STYLE_MODERN

def inject_font_style(html_content: str, font_type: str = "modern") -> str:
    """在 HTML 中注入字体定义
    
    Args:
        html_content: HTML 内容
        font_type: 'modern' (黑体) 或 'classic' (楷体)
    """
    font_style = get_font_style(font_type)
    
    # 如果已经有字体定义，就不需要再加了
    if 'Noto Sans SC' in html_content and font_type == "modern":
        return html_content
    if 'LXGW WenKai' in html_content and font_type == "classic":
        return html_content
    
    # 在 </head> 前插入字体定义
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', font_style + '\n</head>')
    elif '<head>' in html_content:
        # 如果没有 </head>，在 <head> 后插入
        html_content = html_content.replace('<head>', '<head>' + font_style)
    else:
        # 如果没有 head 标签，在最开始插入
        html_content = font_style + '\n' + html_content
    
    return html_content

def fix_font_family(html_content: str, font_type: str = "modern") -> str:
    """修复 font-family 定义，使用 Web 字体
    
    Args:
        html_content: HTML 内容
        font_type: 'modern' (黑体) 或 'classic' (楷体)
    """
    if font_type == "classic":
        # 楷体：替换所有字体定义为楷体
        html_content = re.sub(
            r'font-family:\s*[^;]+;',
            "font-family: 'LXGW WenKai', 'Ma Shan Zheng', 'STKaiti', serif !important;",
            html_content
        )
    else:
        # 黑体：替换所有字体定义为黑体
        html_content = re.sub(
            r'font-family:\s*"?Microsoft YaHei"?[^;]*;',
            "font-family: 'Noto Sans SC', sans-serif !important;",
            html_content
        )
    
    return html_content

def ensure_editable_fonts(html_content: str, font_type: str = "modern") -> str:
    """确保 HTML 中的字体可以在 PDF 中编辑
    
    Args:
        html_content: HTML 内容
        font_type: 'modern' (黑体) 或 'classic' (楷体)
    """
    html_content = inject_font_style(html_content, font_type)
    html_content = fix_font_family(html_content, font_type)
    return html_content
