#!/usr/bin/env python3
"""
根据已发送邮箱列表，找出未发送成功的用户并重发
用法：
1. 从 Gmail 已发送邮件中导出收件人列表到 sent_emails.txt（每行一个邮箱）
2. 运行此脚本
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / "config/.env")

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import mailer

SENT_FILE = Path(__file__).parent / "sent_emails.txt"
RETRY_FILE = Path(__file__).parent / "retry_emails.txt"


def get_all_users():
    """从数据库获取所有用户"""
    from supabase import create_client
    import os
    
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase 配置缺失")
        return []
    
    client = create_client(url, key)
    res = client.table("profiles").select("email").execute()
    return [u['email'].lower() for u in res.data if u.get('email')]


def load_sent_emails():
    """从文件加载已发送的邮箱"""
    if not SENT_FILE.exists():
        return set()
    
    with open(SENT_FILE, 'r') as f:
        return {line.strip().lower() for line in f if line.strip() and '@' in line}


def main():
    print("=" * 50)
    print("  邮件重发工具（基于已发送列表）")
    print("=" * 50)
    print()
    
    # 1. 获取所有用户
    print("📊 获取用户列表...")
    all_users = get_all_users()
    print(f"   共 {len(all_users)} 个用户")
    
    # 2. 加载已发送列表
    print(f"\n📄 加载已发送列表: {SENT_FILE}")
    sent_emails = load_sent_emails()
    
    if not sent_emails:
        print("   ❌ 文件不存在或为空")
        print("\n请先创建 sent_emails.txt，每行一个已发送的邮箱地址")
        print("你可以从 Gmail 已发送邮件中复制收件人地址")
        return
    
    print(f"   已发送: {len(sent_emails)} 个")
    
    # 3. 计算差集
    not_sent = set(all_users) - sent_emails
    
    print()
    print("=" * 50)
    print(f"📈 统计结果:")
    print(f"   总用户: {len(all_users)}")
    print(f"   已发送: {len(sent_emails)}")
    print(f"   未发送: {len(not_sent)}")
    print("=" * 50)
    
    if not not_sent:
        print("\n✅ 所有用户都已收到邮件！")
        return
    
    # 4. 保存并显示未发送列表
    print(f"\n📋 未发送的用户 ({len(not_sent)} 个):")
    with open(RETRY_FILE, 'w') as f:
        for i, email in enumerate(sorted(not_sent), 1):
            print(f"   {i}. {email}")
            f.write(email + '\n')
    print(f"\n💾 列表已保存到: {RETRY_FILE}")
    
    # 5. 确认重发
    print()
    confirm = input("是否立即重发给这些用户？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n已取消")
        return
    
    # 6. 加载邮件模板并发送
    from scripts.send_update_notification import load_email_html, EMAIL_SUBJECT, CURRENT_EMAIL_TEMPLATE
    
    email_html = load_email_html(CURRENT_EMAIL_TEMPLATE)
    
    print(f"\n🚀 开始发送 {len(not_sent)} 封邮件...\n")
    
    success = 0
    fail = 0
    for i, email in enumerate(sorted(not_sent), 1):
        print(f"[{i}/{len(not_sent)}] {email}...", end="", flush=True)
        
        if mailer.send_email(email, EMAIL_SUBJECT, email_html):
            success += 1
            print(" ✅")
        else:
            fail += 1
            print(" ❌")
    
    print()
    print("=" * 50)
    print(f"✅ 完成: 成功 {success}, 失败 {fail}")
    print("=" * 50)


if __name__ == "__main__":
    main()
