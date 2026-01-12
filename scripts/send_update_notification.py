#!/usr/bin/env python3
"""
SlideCraft 版本更新邮件发送脚本

功能：
1. 从 docs/announcements/ 读取邮件模板
2. 支持测试发送（给自己）和群发
3. 支持定时发送
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    import config
    import db
    import mailer
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationSender")

# 配置
ANNOUNCEMENTS_DIR = Path(__file__).parent.parent / "docs" / "announcements"

# 当前使用的邮件模板
CURRENT_EMAIL_TEMPLATE = "版本更新公告_2026年1月_email.html"
EMAIL_SUBJECT = "【SlideCraft】v2.0 重磅更新：多模态理解 + 演讲稿生成 + 移动端适配，随时随地让 AI 真正看懂你的文档"


def load_email_html(template_name: str) -> str:
    """从文件加载邮件 HTML"""
    template_path = ANNOUNCEMENTS_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"邮件模板不存在: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_test_users():
    """手动指定测试用户列表"""
    default_email = config.SMTP_USER
    if not default_email:
        print("错误: config.SMTP_USER 未设置，无法进行测试发送。")
        return []
    return [{"email": default_email}]


def get_db_users():
    """从数据库获取真实用户"""
    client = db.get_client()
    if not client:
        return []

    try:
        res = client.table("profiles").select("email").execute()
        valid_users = [u for u in res.data if u.get('email')]
        return valid_users
    except Exception as e:
        logger.error(f"Failed to fetch users from DB: {e}")
        return []


def wait_until(target_time: datetime):
    """等待到指定时间"""
    now = datetime.now()
    wait_seconds = (target_time - now).total_seconds()

    if wait_seconds <= 0:
        print("⚠️  目标时间已过，立即发送")
        return

    print(f"⏰ 定时发送已设置")
    print(f"   目标时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   等待时间: {int(wait_seconds // 3600)}小时 {int((wait_seconds % 3600) // 60)}分钟")
    print(f"   按 Ctrl+C 可取消")
    print("-" * 40)

    # 每分钟更新一次倒计时
    while True:
        now = datetime.now()
        remaining = (target_time - now).total_seconds()

        if remaining <= 0:
            print("\n⏰ 时间到！开始发送...")
            break

        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        print(f"\r   剩余: {hours}小时 {minutes}分钟    ", end="", flush=True)

        # 睡眠，但最多到目标时间
        sleep_time = min(60, remaining)
        time.sleep(sleep_time)


def send_emails(users: list, subject: str, html_body: str, delay_seconds: float = 2.0):
    """批量发送邮件"""
    success_count = 0
    fail_count = 0

    for i, user in enumerate(users):
        email = user.get('email')
        if not email:
            continue

        print(f"[{i+1}/{len(users)}] 发送至 {email}...", end="", flush=True)

        if mailer.send_email(email, subject, html_body):
            success_count += 1
            print(" ✅")
        else:
            fail_count += 1
            print(" ❌")

        # 避免触发反垃圾限制
        if len(users) > 5 and i < len(users) - 1:
            time.sleep(delay_seconds)

    return success_count, fail_count


def main():
    print("=" * 50)
    print("  SlideCraft 更新通知发送脚本")
    print("=" * 50)
    print()

    # 加载邮件模板
    print(f"📄 邮件模板: {CURRENT_EMAIL_TEMPLATE}")
    try:
        email_html = load_email_html(CURRENT_EMAIL_TEMPLATE)
        print("   ✅ 模板加载成功")
    except FileNotFoundError as e:
        print(f"   ❌ {e}")
        sys.exit(1)

    print(f"📧 邮件主题: {EMAIL_SUBJECT}")
    print()

    # 模式选择
    print("请选择发送模式:")
    print("  1: 测试发给自己")
    print("  2: 群发所有用户")
    print("  3: 定时群发（明天 9:30）")
    print("  4: 自定义定时群发")
    print()
    mode = input("输入模式编号 (1/2/3/4): ").strip()
    print()

    # 根据模式获取用户
    if mode == "1":
        users = get_test_users()
        print("ℹ️  测试模式：仅发送给自己")
        scheduled_time = None
    elif mode == "2":
        users = get_db_users()
        print("⚠️  注意：即将进行群发！")
        scheduled_time = None
    elif mode == "3":
        users = get_db_users()
        # 计算明天 9:30
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)
        print(f"⏰ 定时群发模式")
    elif mode == "4":
        users = get_db_users()
        # 自定义时间
        time_str = input("请输入发送时间 (格式: YYYY-MM-DD HH:MM，如 2026-01-13 09:30): ").strip()
        try:
            scheduled_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("❌ 时间格式错误")
            sys.exit(1)
        print(f"⏰ 自定义定时群发模式")
    else:
        print("无效选择")
        sys.exit(0)

    if not users:
        print("❌ 未找到有效用户列表。")
        sys.exit(0)

    print(f"📊 目标用户数: {len(users)}")
    print()

    # 群发确认
    if mode in ["2", "3", "4"]:
        print("-" * 40)
        confirm = input(f"确认向 {len(users)} 位用户发送邮件? (输入 'confirm' 确认): ").strip()
        if confirm != 'confirm':
            print("已取消")
            sys.exit(0)
        print()

    # 定时等待
    if scheduled_time:
        wait_until(scheduled_time)

    # 发送邮件
    print("-" * 40)
    print("📤 开始发送邮件...")
    print()

    start_time = time.time()
    success_count, fail_count = send_emails(users, EMAIL_SUBJECT, email_html)
    elapsed = time.time() - start_time

    print()
    print("=" * 50)
    print(f"  任务完成")
    print(f"  成功: {success_count} | 失败: {fail_count}")
    print(f"  耗时: {elapsed:.1f} 秒")
    print("=" * 50)


if __name__ == "__main__":
    main()
