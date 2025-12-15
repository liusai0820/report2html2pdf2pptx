"""模板合并器 - 将模板和内容合并成完整HTML"""
import os
import re
from typing import List, Dict
from pathlib import Path
from rich.console import Console

console = Console()

class TemplateMerger:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template_content = self._load_template()
    
    def _load_template(self) -> str:
        """加载模板文件"""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_single_page(self, page_num: int, total_pages: int, 
                            page_title: str, content: str) -> str:
        """生成单个页面的完整HTML"""
        from datetime import datetime
        
        html = self.template_content
        html = html.replace('{{PAGE_TITLE}}', page_title)
        html = html.replace('{{CONTENT_PLACEHOLDER}}', content)
        
        # 替换页脚信息
        current_date = datetime.now().strftime("%Y年%m月")
        html = html.replace('{{PAGE_FOOTER_DATE}}', current_date)
        html = html.replace('{{PAGE_FOOTER_TEXT}}', page_title[:30])  # 限制长度
        
        # 移除可能存在的页码占位符
        html = html.replace('{{PAGE_NUM}}', '')
        html = html.replace('{{TOTAL_PAGES}}', '')
        
        # 确保包含字体定义 - 解决 Type 3 字体问题
        if 'Microsoft YaHei Web' not in html:
            font_style = """
    <style>
        /* Web字体 - 思源黑体（微软雅黑的完美替代品，支持PDF嵌入） */
        @import url('https://fonts.font.im/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        
        /* 字体优先级：本地微软雅黑 > Web字体思源黑体 > 系统字体 */
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei'), 
                 local('微软雅黑'),
                 url('https://fonts.gstatic.font.im/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 400;
            font-display: swap;
        }
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei Bold'), 
                 local('微软雅黑 Bold'),
                 url('https://fonts.gstatic.font.im/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 700;
            font-display: swap;
        }
        
        /* 全局字体替换 */
        body, * {
            font-family: 'Microsoft YaHei Web', 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
        }
    </style>
"""
            if '</head>' in html:
                html = html.replace('</head>', font_style + '\n</head>')
            elif '<head>' in html:
                html = html.replace('<head>', '<head>' + font_style)
        
        return html
    
    def merge_all_pages(self, pages_data: List[Dict]) -> str:
        """合并所有页面成一个完整HTML文档"""
        # 提取<head>部分
        head_match = re.search(r'<head>(.*?)</head>', self.template_content, re.DOTALL)
        if not head_match:
            raise ValueError("模板中未找到<head>标签")
        
        head_content = head_match.group(0)
        
        # 尝试提取单页容器结构（新格式：直接使用 {{CONTENT_PLACEHOLDER}}）
        if '{{CONTENT_PLACEHOLDER}}' in self.template_content:
            # 新格式：内容直接替换占位符
            container_template = '{{CONTENT_PLACEHOLDER}}'
        else:
            # 旧格式：查找 slide-container
            container_match = re.search(
                r'<div class="slide-container">(.*?)</div>\s*</body>',
                self.template_content,
                re.DOTALL
            )
            if not container_match:
                raise ValueError("模板中未找到slide-container或{{CONTENT_PLACEHOLDER}}")
            
            container_template = '<div class="slide-container">' + container_match.group(1) + '</div>'
        
        # 构建完整HTML
        total_pages = len(pages_data)
        
        # 添加字体嵌入 - 解决 Type 3 字体问题
        font_style = """
    <style>
        /* Web字体 - 思源黑体（微软雅黑的完美替代品，支持PDF嵌入） */
        @import url('https://fonts.font.im/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        
        /* 字体优先级：本地微软雅黑 > Web字体思源黑体 > 系统字体 */
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei'), 
                 local('微软雅黑'),
                 url('https://fonts.gstatic.font.im/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 400;
            font-display: swap;
        }
        @font-face {
            font-family: 'Microsoft YaHei Web';
            src: local('Microsoft YaHei Bold'), 
                 local('微软雅黑 Bold'),
                 url('https://fonts.gstatic.font.im/s/notosanssc/v21/PbynFmwt4aIE7Lssw6LLW-2xvzCvQcMhWA.woff2') format('woff2');
            font-weight: 700;
            font-display: swap;
        }
        
        /* 全局字体替换 */
        body, * {{
            font-family: 'Microsoft YaHei Web', 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
        }}
    </style>
"""
        
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
{head_content}
{font_style}
<body>
"""
        
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月")
        
        for i, page_data in enumerate(pages_data, 1):
            page_html = container_template
            page_title = page_data.get('title', f'第{i}页')
            page_html = page_html.replace('{{PAGE_TITLE}}', page_title)
            page_html = page_html.replace('{{CONTENT_PLACEHOLDER}}', page_data.get('content', ''))
            
            # 替换页脚信息
            page_html = page_html.replace('{{PAGE_FOOTER_DATE}}', current_date)
            page_html = page_html.replace('{{PAGE_FOOTER_TEXT}}', page_title[:30])
            
            # 移除可能存在的页码占位符
            page_html = page_html.replace('{{PAGE_NUM}}', '')
            page_html = page_html.replace('{{TOTAL_PAGES}}', '')
            
            full_html += page_html + '\n'
            
            # 添加分页符（除了最后一页）
            if i < total_pages:
                full_html += '<div style="page-break-after: always;"></div>\n'
        
        full_html += """</body>
</html>"""
        
        return full_html
    
    def save_page(self, output_path: str, page_num: int, total_pages: int,
                  page_title: str, content: str):
        """保存单个页面"""
        from font_fixer import ensure_editable_fonts
        
        html = self.generate_single_page(page_num, total_pages, page_title, content)
        # 确保字体可以在 PDF 中编辑
        html = ensure_editable_fonts(html)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        console.print(f"[green]✓[/green] 已保存: {output_path}")
    
    def save_merged(self, output_path: str, pages_data: List[Dict]):
        """保存合并后的完整HTML"""
        from font_fixer import ensure_editable_fonts
        
        html = self.merge_all_pages(pages_data)
        # 确保字体可以在 PDF 中编辑
        html = ensure_editable_fonts(html)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        console.print(f"[green]✓[/green] 已保存合并文件: {output_path}")
