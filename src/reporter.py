"""
运营日报发送模块

@input:  db, config
@output: send_daily_report()
@pos:    运营工具，被定时任务调用

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/_FOLDER.md
"""
import requests
import config
import logging
import db
import asyncio

logger = logging.getLogger(__name__)

async def send_daily_report():
    """生成并发送运营日报"""
    logger.info("Generating daily report...")
    
    # 1. Check Config
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        logger.warning("Telegram config missing, skipping daily report")
        return

    # 2. Get Data
    # 运行在线程池中以免阻塞 async loop（因为 db 是同步的）
    stats = await asyncio.to_thread(db.get_daily_report)
    
    if not stats:
        logger.error("Failed to generate report statistics")
        return

    # 3. Format Message
    rating_bar = "⭐" * int(stats['avg_rating'])
    
    # Escape Markdown Special Chars (minimal)
    
    msg = f"""
📅 *SlideCraft 运营日报 ({stats['date']})*
───────────────────
👥 *新增用户*: `{stats['new_users']}`
🎨 *今日生成*: `{stats['total_generations']}`
⭐ *平均评分*: {stats['avg_rating']} {rating_bar}

📝 *用户原声*:
"""
    if stats['feedbacks']:
        for fb in stats['feedbacks'][:8]: # 只发前5条
            star = "⭐" * int(fb['rating'])
            comment = fb['comment'].replace("_", "\_").replace("*", "\*")
            if len(comment) > 60:
                comment = comment[:60] + "..."
            msg += f"• {star} {comment}\n"
    else:
        msg += "_今日暂无文字评价_\n"

    msg += "\n#Report #Daily"

    # 4. Send
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    try:
        # Run request in thread
        resp = await asyncio.to_thread(requests.post, url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Daily report sent successfully")
    except Exception as e:
        logger.error(f"Failed to send telegram report: {e}")

if __name__ == "__main__":
    # Manual test
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    from dotenv import load_dotenv
    import os
    load_dotenv("config/.env")
    
    # Mock config manually if needed to test standalone
    # config.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    asyncio.run(send_daily_report())
