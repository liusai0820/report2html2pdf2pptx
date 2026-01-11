"""
输出渲染器 - 将 AI 生成的内容转换为最终格式

职责：
1. 生成 HTML 模板
2. 合并页面
3. 转换 PDF/PPTX
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from themes.css_generator import CSSGenerator
from .context_builder import PresentationContext

console = Console()


class OutputRenderer:
    """输出渲染器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir = self.output_dir / "pages"
        self.pages_dir.mkdir(exist_ok=True)
    
    def render_template(self, context: PresentationContext) -> str:
        """根据上下文中的主题动态生成 HTML 模板"""
        
        css = ""
        theme = context.theme
        
        if theme:
            # 动态生成主题 CSS
            generator = CSSGenerator(theme)
            css = generator.generate_full_css()
        else:
            # 回退到基本样式（如果需要）
            css = "body { font-family: sans-serif; }"
            
        # 解决字体问题
        # 注意: 这里的字体链接也应该由主题管理，暂时保留作为修复的一部分
        font_fix_css = """
        /* Web字体 - 思源黑体（微软雅黑的完美替代品，支持PDF嵌入） */
        @import url('https://fonts.font.im/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        """
        css = font_fix_css + "\n" + css
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
{css}
    </style>
    <!-- 注入演讲稿生成功能的样式 -->
    <style>
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .speech-btn {{
        position: fixed; top: 20px; right: 20px; z-index: 9999;
        padding: 10px 20px; background: #1A365D; color: white;
        border: none; border-radius: 4px; cursor: pointer;
        font-family: sans-serif; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        transition: all 0.2s; display: flex; align-items: center; gap: 8px;
    }}
    .speech-btn:hover {{ background: #2c5282; transform: translateY(-1px); }}
    .speech-modal {{
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
        z-index: 10000; justify-content: center; align-items: center;
        backdrop-filter: blur(4px);
    }}
    .speech-modal-content {{
        background: white; width: 800px; max-width: 90%; height: 80vh;
        border-radius: 12px; display: flex; flex-direction: column;
        overflow: hidden; box-shadow: 0 4px 30px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease-out;
    }}
    @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body>
    <!-- 演讲稿生成按钮 -->
    <button id="speech-btn" class="speech-btn">
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
        生成演讲稿
    </button>

    <!-- 演讲稿模态框 -->
    <div id="speech-modal" class="speech-modal">
        <div class="speech-modal-content">
            <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: #f8fafc;">
                <h3 style="margin: 0; font-size: 18px; color: #333; font-weight: 600;">🎙️ 演讲口播稿</h3>
                <button onclick="document.getElementById('speech-modal').style.display='none'" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #999; padding: 0 8px;">&times;</button>
            </div>
            <div id="speech-content" style="flex: 1; padding: 40px; overflow-y: auto; font-size: 16px; line-height: 1.8; color: #333; white-space: pre-wrap; font-family: 'PingFang SC', system-ui, sans-serif;">
                <!-- Content injected here -->
            </div>
            <div style="padding: 20px; border-top: 1px solid #eee; text-align: right; background: #f8fafc; display: flex; justify-content: flex-end; gap: 12px;">
                <button onclick="copySpeech()" style="padding: 8px 16px; background: #white; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; color: #475569; font-weight: 500;">复制全文</button>
                <button onclick="document.getElementById('speech-modal').style.display='none'" style="padding: 8px 16px; background: #1A365D; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">关闭</button>
            </div>
        </div>
    </div>

    <script>
    document.getElementById('speech-btn').onclick = async function() {{
        document.getElementById('speech-modal').style.display = 'flex';
        const contentDiv = document.getElementById('speech-content');
        contentDiv.innerHTML = `
            <div style="text-align: center; color: #64748b; margin-top: 100px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #1A365D; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
                <p style="font-size: 16px;">AI 正在阅读幻灯片并撰写演讲稿...</p>
                <p style="font-size: 14px; opacity: 0.7;">预计需要 15-30 秒</p>
            </div>
        `;

        try {{
            // Extract output name from URL: /output/{{output_name}}/presentation.html
            const pathParts = window.location.pathname.split('/');
            // Usually path is empty or /output/xxx/presentation.html
            // If local file, this logic might fail, but this is designed for the web app context
            let outputName = null;
            for(let i=0; i<pathParts.length; i++) {{
                if(pathParts[i] === 'output' && i+1 < pathParts.length) {{
                    outputName = pathParts[i+1];
                    break;
                }}
            }}

            if (!outputName) {{
                // Fallback for dev environment or weird paths
                console.warn("Could not parse output_name from URL, trying to guess...");
                // Maybe check if there is a meta tag or something?
                // For now, fail gracefully.
                throw new Error("无法从 URL 获取演示文稿 ID，请确保在系统中打开");
            }}

            const response = await fetch('/api/generate-speech', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ output_name: outputName }})
            }});

            if (!response.ok) {{
                const errData = await response.json();
                throw new Error(errData.detail || "生成请求失败");
            }}

            const data = await response.json();
            // Simple markdown parsing for better display
            let htmlContent = data.script
                .replace(/^# (.*$)/gim, '<h1 style="font-size: 24px; margin-top: 20px; margin-bottom: 10px; color: #1e293b;">$1</h1>')
                .replace(/^## (.*$)/gim, '<h2 style="font-size: 20px; margin-top: 15px; margin-bottom: 8px; color: #334155;">$1</h2>')
                .replace(/\\*\\*(.*)\\*\\*/gim, '<strong>$1</strong>');

            contentDiv.innerHTML = htmlContent;

        }} catch (e) {{
            contentDiv.innerHTML = `
                <div style="color: #ef4444; text-align: center; margin-top: 100px; padding: 20px; background: #fef2f2; border-radius: 8px; max-width: 400px; margin-left: auto; margin-right: auto;">
                    <svg style="width: 48px; height: 48px; margin-bottom: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <div style="font-weight: bold; margin-bottom: 8px;">生成失败</div>
                    <div>${{e.message}}</div>
                </div>`;
        }}
    }};

    function copySpeech() {{
        const text = document.getElementById('speech-content').innerText;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.querySelector('button[onclick="copySpeech()"]');
            const originalText = btn.innerText;
            btn.innerText = '已复制!';
            setTimeout(() => btn.innerText = originalText, 2000);
        }});
    }}
    </script>
{{{{CONTENT_PLACEHOLDER}}}}
</body>
</html>
"""
    
    def save_page(self, page_num: int, html_content: str, template: str) -> str:
        """保存单页"""
        full_html = template.replace("{{CONTENT_PLACEHOLDER}}", html_content)
        
        # 修复 PDF 生成时的图片路径问题
        # HTML 中的路径通常是 /output/assets/... (Web 路径)
        # 本地 PDF 生成(use file://) 需要相对路径: ../../assets/...
        
        # 将绝对路径 /output/ 替换为相对路径 ../../
        # 结果: url('../../assets/...')
        full_html = full_html.replace("url('/output/", "url('../../")
        
        page_path = self.pages_dir / f"page-{page_num:02d}.html"
        page_path.write_text(full_html, encoding='utf-8')
        return str(page_path)
    
    def merge_pages(self, pages_html: List[str], template: str) -> str:
        """合并所有页面"""
        all_content = "\n".join(pages_html)
        full_html = template.replace("{{CONTENT_PLACEHOLDER}}", all_content)
        
        merged_path = self.output_dir / "presentation.html"
        merged_path.write_text(full_html, encoding='utf-8')
        
        console.print(f"[green]✓[/green] HTML 已生成: {merged_path}")
        return str(merged_path)
    
    def generate_pdf(self, doc_name: str = "presentation") -> str:
        """生成 PDF
        
        策略：
        1. Render 环境：跳过 PDF 生成，仅返回 HTML。用户需下载 HTML 在本地转换。
        2. 本地环境：使用 Playwright 生成完美 PDF。
        """
        console.print(f"\n[cyan]📄 生成 PDF...[/cyan]")
        
        date_str = datetime.now().strftime("%Y%m%d")
        final_pdf_path = self.output_dir / f"{doc_name}_{date_str}.pdf"
        source_html = self.output_dir / "presentation.html"
        
        if not source_html.exists():
            console.print("[red]✗ presentation.html 不存在[/red]")
            return None

        # 检测环境
        is_render = os.getenv('RENDER') or os.getenv('render')
        
        if is_render:
            console.print("[yellow]☁️ Render环境：跳过 PDF 生成 (请下载 HTML 在本地转换)[/yellow]")
            return None

        # --- 本地 Playwright (唯一方案) ---
        try:
            console.print("[cyan]🖥 使用 Playwright 生成 PDF (本地)...[/cyan]")
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 加载 HTML
                page.goto(f"file://{source_html.resolve()}", wait_until="networkidle")
                page.wait_for_timeout(2000) # 给 ECharts 更多时间
                
                page.pdf(
                    path=str(final_pdf_path),
                    width="1280px",
                    height="720px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    scale=1
                )
                browser.close()
            
            if final_pdf_path.exists():
                size_mb = final_pdf_path.stat().st_size / 1024 / 1024
                console.print(f"[green]✓[/green] PDF 已生成: {final_pdf_path.name} ({size_mb:.2f} MB)")
                # 尝试压缩 (可选)
                self._compress_pdf(final_pdf_path)
                return str(final_pdf_path.resolve())
                
        except ImportError:
            console.print("[yellow]⚠ 未安装 Playwright，请运行: pip install playwright && playwright install chromium[/yellow]")
        except Exception as e:
            console.print(f"[red]⚠ Playwright 失败: {e}[/red]")

        return None

    def _compress_pdf(self, file_path: Path):
        """简单压缩 PDF (去除未使用的对象)"""
        try:
            old_size = file_path.stat().st_size / 1024 / 1024
            
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(str(file_path))
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
                
            # 压缩元数据
            writer.add_metadata(reader.metadata)
            
            temp_path = file_path.parent / f"compressed_{file_path.name}"
            with open(temp_path, "wb") as f:
                writer.write(f)
            
            new_size = temp_path.stat().st_size / 1024 / 1024
            
            if new_size < old_size:
                # 只有变小了才替换
                os.remove(file_path)
                temp_path.rename(file_path)
                console.print(f"[green]✓[/green] PDF 已压缩: {old_size:.2f}MB -> {new_size:.2f}MB")
            else:
                os.remove(temp_path)
                console.print(f"[dim]PDF 压缩未变小 ({old_size:.2f}MB)[/dim]")
                
        except Exception as e:
            console.print(f"[yellow]⚠ PDF压缩跳过: {e}[/yellow]")
    
    def generate_pptx(self, pdf_path: str) -> str:
        """生成 PPTX (已禁用云端转换)"""
        console.print("[yellow]⚠ PPTX 生成：建议使用 WPS/Office 打开生成的 PDF 进行转换，效果最佳[/yellow]")
        return None
