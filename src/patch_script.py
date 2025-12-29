import os
import asyncio
import re
from pathlib import Path
import PyPDF2

# 尝试导入 pyppeteer，如果失败则提示
try:
    from pyppeteer import launch
except ImportError:
    print("Error: pyppeteer not found. Please install headers: pip install pyppeteer")
    exit(1)

# 目标目录 - 使用绝对路径
BASE_DIR = Path("/app/output/中共深圳市委关于制定深圳市国民经济和社会发展第十五个五年规划的建议_20251229_032046_v2/pages")

def patch_html():
    print("🚀 开始批量替换文本...")
    count = 0
    if not BASE_DIR.exists():
        print(f"❌ 错误: 目录不存在: {BASE_DIR}")
        return False
        
    for file in BASE_DIR.glob("page-*.html"):
        content = file.read_text(encoding="utf-8")
        if "智库解读" in content:
            # 替换所有出现的词
            new_content = content.replace("智库解读", "解读")
            file.write_text(new_content, encoding="utf-8")
            count += 1
            print(f"  - 已修复: {file.name}")
            
    print(f"✅ 文本替换完成，共修改 {count} 个文件。")
    return True

async def generate_pdfs():
    print("\n🔄 开始重新生成 PDF 页面 (Playwright/Pyppeteer)...")
    
    # 启动浏览器 - 注意容器内需要 --no-sandbox
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    
    # 获取排序后的文件列表
    files = sorted(BASE_DIR.glob("page-*.html"), key=lambda f: int(re.search(r'(\d+)', f.name).group(1)))
    
    pdf_files = []
    total = len(files)
    
    for i, html_file in enumerate(files, 1):
        output_pdf = html_file.with_suffix(".pdf")
        # 容器内文件路径
        url = f"file://{html_file.absolute()}"
        
        # print(f"[{i}/{total}] Rendering {html_file.name}...")
        
        await page.goto(url, {'waitUntil': 'networkidle0'})
        
        # 只有在宽度变化时才重新设置视口
        await page.setViewport({'width': 1280, 'height': 720})
        
        await page.pdf({
            'path': str(output_pdf),
            'width': '1280px', 
            'height': '720px',
            'printBackground': True,
            'margin': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        })
        pdf_files.append(output_pdf)
        print(f"  - Generated PDF: {output_pdf.name}")
        
    await browser.close()
    return pdf_files

def merge_pdfs(pdf_files):
    print("\n📦 开始合并 PDF 文件...")
    merger = PyPDF2.PdfMerger()
    for pdf in pdf_files:
        merger.append(str(pdf))
    
    # 输出到上级目录
    output_path = BASE_DIR.parent / "merged_report_fixed.pdf"
    merger.write(str(output_path))
    merger.close()
    print(f"\n✨ 大功告成！合并后的文件已保存至:\n{output_path}")

async def main():
    if patch_html():
        pdf_files = await generate_pdfs()
        if pdf_files:
            merge_pdfs(pdf_files)
        else:
            print("❌ 未生成任何 PDF 文件")

if __name__ == "__main__":
    asyncio.run(main())
