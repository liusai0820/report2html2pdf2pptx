import os
import re
import asyncio
from pathlib import Path
import PyPDF2

# 目标目录 (请根据实际情况确认路径)
TARGET_DIR = Path("/Users/qibaoba/VibeCoding/pptx/output/中共深圳市委关于制定深圳市国民经济和社会发展第十五个五年规划的建议_20251229_032046_v2/pages")
OUTPUT_PDF_NAME = "final_report.pdf"

def patch_html_files():
    print("👉 正在修正 HTML 文本...")
    count = 0
    if not TARGET_DIR.exists():
        print(f"❌ 目录不存在: {TARGET_DIR}")
        exit(1)
        
    files = sorted(TARGET_DIR.glob("page-*.html"))
    for f in files:
        content = f.read_text(encoding='utf-8')
        if "智库解读" in content:
            new_content = content.replace("智库解读", "解读")
            f.write_text(new_content, encoding='utf-8')
            count += 1
            # print(f"  - Repaired: {f.name}")
            
    print(f"✅ 已修正 {count} 个 HTML 文件。")

async def convert_and_merge():
    # 尝试导入 playwright
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("\n❌ 缺少必要库，请在终端执行以下命令安装：")
        print("pip install playwright PyPDF2")
        print("playwright install chromium")
        return

    print("\n🚀 正在启动浏览器进行 PDF 转换 (保持 1280x720)...")
    
    pdf_files = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 按数字顺序排序
        html_files = sorted(TARGET_DIR.glob("page-*.html"), key=lambda x: int(re.search(r'(\d+)', x.name).group(1)))
        
        total = len(html_files)
        print(f"📄 共 {total} 页，开始转换...")
        
        for i, f in enumerate(html_files, 1):
            pdf_path = f.with_suffix(".pdf")
            file_url = f"file://{f.resolve()}"
            
            await page.goto(file_url)
            
            # 生成 PDF (宽度 1280px，自适应高度，或者强制 720px)
            # print_background=True 是必须的，否则颜色没了
            await page.pdf(
                path=pdf_path,
                width="1280px",
                height="720px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                page_ranges="1"
            )
            
            pdf_files.append(pdf_path)
            # 打印进度条
            percent = int(i / total * 100)
            bar = "█" * (percent // 5) + "░" * (20 - percent // 5)
            print(f"\r[{bar}] {percent}% ({i}/{total}) {f.name}", end="")
            
        await browser.close()
        
    print("\n\n📦 正在合并所有 PDF...")
    merger = PyPDF2.PdfMerger()
    for pdf in pdf_files:
        merger.append(str(pdf))
        
    final_output = TARGET_DIR.parent / OUTPUT_PDF_NAME
    merger.write(str(final_output))
    merger.close()
    
    print(f"✨ 成功！最终文件已生成：\n{final_output}")
    # 自动打开文件所在文件夹
    os.system(f"open '{final_output.parent}'")

if __name__ == "__main__":
    patch_html_files()
    asyncio.run(convert_and_merge())
