#!/usr/bin/env python3
"""
本地 Telegram Bot 监听器 - 自动下载 HTML 并转换为 PDF

使用方法:
1. 确保 config/.env 包含 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID
2. 安装依赖: pip install python-telegram-bot playwright python-dotenv
3. 安装浏览器: playwright install chromium
4. 运行: python3 local_pdf_bot.py

收到 HTML 文件后会自动:
1. 下载到 ./downloads/ 目录
2. 使用 Playwright 转换为 PDF
3. 将 PDF 发送回 Telegram
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 加载 .env 文件
script_dir = Path(__file__).parent
env_path = script_dir / "config" / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print(f"✓ Loaded config from: {env_path}")

# ========== 配置 ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DOWNLOAD_DIR = script_dir / "downloads"
PDF_OUTPUT_DIR = script_dir / "pdfs"
SEND_PDF_BACK = True  # 转换后是否发送回 Telegram

# ========== 初始化 ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DOWNLOAD_DIR.mkdir(exist_ok=True)
PDF_OUTPUT_DIR.mkdir(exist_ok=True)

async def convert_html_to_pdf(html_path: Path) -> Path:
    """使用 Playwright 将 HTML 转换为 PDF"""
    from playwright.async_api import async_playwright
    
    pdf_path = PDF_OUTPUT_DIR / f"{html_path.stem}_{datetime.now().strftime('%H%M%S')}.pdf"
    
    logger.info(f"🔄 Converting: {html_path.name} -> {pdf_path.name}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 加载 HTML
        await page.goto(f"file://{html_path.resolve()}", wait_until="networkidle")
        await page.wait_for_timeout(2000)  # 等待图表渲染
        
        # 生成 PDF
        await page.pdf(
            path=str(pdf_path),
            width="1280px",
            height="720px",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            scale=1
        )
        await browser.close()
    
    size_mb = pdf_path.stat().st_size / 1024 / 1024
    logger.info(f"✅ PDF generated: {pdf_path.name} ({size_mb:.2f} MB)")
    
    return pdf_path

async def handle_document(update, context):
    """处理收到的文档"""
    from telegram import Update
    from telegram.ext import ContextTypes
    
    message = update.message
    document = message.document
    chat_id = str(message.chat_id)
    
    # 安全检查：只允许指定的 chat_id
    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        logger.warning(f"⚠️ Unauthorized access from chat_id: {chat_id}")
        return
    
    # 只处理 HTML 文件
    file_name = document.file_name or ""
    if not file_name.endswith(".html"):
        logger.info(f"📄 Skipping non-HTML file: {file_name}")
        return
    
    logger.info(f"📥 Received HTML: {file_name}")
    
    try:
        # 下载文件
        file = await context.bot.get_file(document.file_id)
        html_path = DOWNLOAD_DIR / file_name
        await file.download_to_drive(str(html_path))
        logger.info(f"💾 Downloaded: {html_path}")
        
        # 转换为 PDF
        await message.reply_text(f"🔄 正在转换 PDF: {file_name}...")
        pdf_path = await convert_html_to_pdf(html_path)
        
        # 发送回 Telegram
        if SEND_PDF_BACK:
            await message.reply_document(
                document=open(pdf_path, 'rb'),
                filename=pdf_path.name,
                caption=f"✅ PDF 转换完成\n📊 大小: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB"
            )
            logger.info(f"📤 PDF sent to Telegram: {pdf_path.name}")
        else:
            await message.reply_text(f"✅ PDF 已保存: {pdf_path}")
            
    except Exception as e:
        logger.error(f"❌ Error processing {file_name}: {e}")
        await message.reply_text(f"❌ 转换失败: {e}")

async def main():
    """主函数"""
    from telegram.ext import Application, MessageHandler, filters
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
        logger.error("❌ 请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
    
    logger.info("🚀 Starting Local PDF Bot...")
    logger.info(f"📁 Download directory: {DOWNLOAD_DIR.resolve()}")
    logger.info(f"📁 PDF output directory: {PDF_OUTPUT_DIR.resolve()}")
    
    # 创建 Application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 添加文档处理器
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # 启动轮询
    logger.info("👂 Listening for HTML files...")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
