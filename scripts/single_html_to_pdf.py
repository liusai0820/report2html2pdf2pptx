#!/usr/bin/env python3
import sys
import re
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def fix_html_fonts(content):
    """
    针对 Mac 平台生成可编辑 PDF 的核心修复逻辑：
    1. 移除外部 Google Fonts 链接
    2. 强制使用宋体 (Songti SC)，这是 Mac 上生成 TrueType 嵌入而不变位图的唯一方案
    3. 降级字重 800/900 -> 700，防止合成粗体导致的 Type 3 位图化
    """
    # 移除 Google Fonts 链接
    content = re.sub(r'<link[^>]*fonts\.googleapis[^>]*>', '', content)

    # 强制替换所有 font-family (CSS 变量、普通CSS规则、内联样式)
    # 目标：Arial, 'Songti SC', 'SimSun', serif, sans-serif
    safe_font = "font-family: Arial, 'Songti SC', 'SimSun', serif, sans-serif;"
    content = re.sub(r'font-family:\s*[^;"]*(?:;|(?="))', safe_font, content)

    # 特别处理 CSS 变量 --font-family
    content = re.sub(r'--font-family:\s*[^;]+;', f"--font-family: Arial, 'Songti SC', 'SimSun', serif, sans-serif;", content)

    # 降级字重 (800/900 -> 700)
    content = re.sub(r'font-weight:\s*800', 'font-weight: 700', content)
    content = re.sub(r'font-weight:\s*900', 'font-weight: 700', content)
    
    return content

def convert_html_to_pdf(html_path, pdf_path):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    temp_html_path = html_path.parent / f"{html_path.stem}_tmp_printable.html"

    print(f"🚀 正在处理: {html_path.name}")
    
    try:
        # 1. 读取并修复 HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_html_fonts(content)
        
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ 字体修复完成 (强制宋体 + 字重修正)")

        # 2. 调用 Playwright 生成 PDF
        print(f"📄 正在启动浏览器生成 PDF...")
        with sync_playwright() as p:
            # 增加 --font-render-hinting=medium 参数有时能改善某些环境下的效果
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 使用 file:// 协议加载
            page.goto(f"file://{temp_html_path}", wait_until="networkidle")
            
            # 给 ECharts 等可能存在的动画一点渲染时间
            print("⏳ 等待页面渲染 (3秒)...")
            page.wait_for_timeout(3000)
            
            page.pdf(
                path=str(pdf_path),
                width="1280px",
                height="720px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                scale=1
            )
            browser.close()

        print(f"🎉 成功生成 PDF: {pdf_path}")
        size_mb = pdf_path.stat().st_size / 1024 / 1024
        print(f"📦 文件大小: {size_mb:.2f} MB")

    finally:
        # 清理临时文件
        if temp_html_path.exists():
            os.remove(temp_html_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("💡 使用方法: python3 scripts/single_html_to_pdf.py <输入HTML> [输出PDF]")
        sys.exit(1)
        
    input_html = sys.argv[1]
    if len(sys.argv) > 2:
        output_pdf = sys.argv[2]
    else:
        output_pdf = str(Path(input_html).with_suffix(".pdf").name).replace(".pdf", "_printable.pdf")
        output_pdf = str(Path(input_html).parent / output_pdf)
        
    convert_html_to_pdf(input_html, output_pdf)
