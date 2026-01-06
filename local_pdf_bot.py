#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/pdf_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载配置
load_dotenv(Path(__file__).parent / "config/.env")

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))

if not API_ID or not API_HASH:
    logger.error("❌ API_ID or API_HASH missing in config/.env")
    sys.exit(1)

# 会话文件路径
SESSION_FILE = Path(__file__).parent / "config/userbot.session"

# 初始化客户端
# 注意：这里会生成 userbot.session 文件保存登录状态
client = TelegramClient(str(SESSION_FILE), int(API_ID), API_HASH)

async def convert_html_to_pdf(html_path: Path) -> Path:
    """调用外部脚本将 HTML 转换为 PDF"""
    import subprocess
    
    script_path = Path(__file__).parent / "scripts" / "single_html_to_pdf.py"
    pdf_path = html_path.with_suffix(".pdf")
    
    logger.info(f"🔄 Converting {html_path.name} using external script...")
    
    try:
        # 调用外部脚本
        # python3 scripts/single_html_to_pdf.py <input> <output>
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            str(html_path),
            str(pdf_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Script error: {stderr.decode()}")
            raise Exception(f"PDF conversion script failed: {stderr.decode()}")
            
        logger.info(f"Script output: {stdout.decode()}")
        logger.info(f"✅ PDF generated: {pdf_path.name}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise e

@client.on(events.NewMessage(chats=CHAT_ID))
async def handler(event):
    """监听群组消息"""
    try:
        # 必须包含文件
        if not event.message.file:
            return

        # 获取文件名 (Telethon 处理文件属性的方式)
        file_name = None
        if event.message.document and event.message.document.attributes:
            for attr in event.message.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    file_name = attr.file_name
                    break
        
        if not file_name or not file_name.endswith(".html"):
            return

        logger.info(f"📥 Received HTML: {file_name}")
        
        # 下载文件
        temp_dir = Path(__file__).parent / "pdfs" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载路径
        download_path = await event.message.download_media(file=temp_dir / file_name)
        download_path = Path(download_path)
        
        # 发送"处理中"提示 (userbot 可以回复任何人)
        status_msg = await event.reply("🔄 收到 HTML，正在本地转换 PDF...")
        
        try:
            # 转换 PDF
            pdf_path = await convert_html_to_pdf(download_path)
            
            # 发回 PDF
            # Telethon send_file 支持 progress_callback，这里暂不需要
            await client.send_file(
                event.chat_id,
                pdf_path,
                caption=f"✅ **转换完成**\n📄 `{pdf_path.name}`\n#HTMLToPDF",
                reply_to=event.message.id
            )
            
            # 删除处理中提示
            await status_msg.delete()
            
            # 清理 HTML 文件
            os.remove(download_path)
            
        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            await status_msg.edit(f"❌ 转换失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")

async def main():
    logger.info("🚀 SlideCraft Userbot starting...")
    
    # 这里会尝试连接，如果没登录会提示输入手机号
    # 在非交互式环境中，如果 session 文件不存在，这一步会失败
    await client.start()
    
    me = await client.get_me()
    logger.info(f"✅ Logged in as: {me.first_name} (@{me.username})")
    
    # 确保加入群组/能够访问群组
    try:
        chat = await client.get_entity(CHAT_ID)
        logger.info(f"🎧 Listening on chat: {chat.title} (ID: {CHAT_ID})")
    except ValueError:
        logger.error(f"❌ Cannot access chat ID {CHAT_ID}. Make sure you have joined the group.")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    # 停止旧的 bot 进程 (如果有)
    # 注意：手动运行时不要自杀，交由外部管理
    # os.system("pkill -f local_pdf_bot || true")
    
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("👋 Userbot stopped.")
