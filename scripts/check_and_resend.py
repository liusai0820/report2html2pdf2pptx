#!/usr/bin/env python3
"""
检查邮件发送状态并重发失败的邮件
通过 Gmail IMAP 获取已发送邮件，对比用户列表，找出未收到的用户
"""

import sys
import os
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import config as src_config
from src import db as src_db
from src import mailer

# 邮件主题关键词（用于匹配已发送的邮件）
SUBJECT_KEYWORD = "v2.0 重磅更新"

def get_sent_emails_from_gmail(since_date: str = "12-Jan-2026") -> set:
    """从 Gmail 已发送文件夹获取收件人列表"""
    
    print("📬 连接 Gmail IMAP...")
    
    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(src_config.SMTP_USER, src_config.SMTP_PASSWORD)
        
        # 选择已发送文件夹
        # Gmail 的已发送文件夹名称
        sent_folders = ['[Gmail]/Sent Mail', '[Gmail]/已发送邮件', 'Sent', '[Gmail]/&XfJT0ZAB-']
        
        folder_found = None
        for folder in sent_folders:
            try:
                status, _ = imap.select(f'"{folder}"')
                if status == 'OK':
                    folder_found = folder
                    print(f"   找到已发送文件夹: {folder}")
                    break
            except:
                continue
        
        if not folder_found:
            print("❌ 无法找到已发送文件夹")
            return set()
        
        # 搜索包含关键词的邮件
        print(f"🔍 搜索包含 '{SUBJECT_KEYWORD}' 的邮件...")
        
        # 搜索条件：主题包含关键词，且日期在指定之后
        search_criteria = f'(SINCE "{since_date}" SUBJECT "{SUBJECT_KEYWORD}")'
        status, messages = imap.search(None, search_criteria)
        
        if status != 'OK':
            print("❌ 搜索失败")
            return set()
        
        message_ids = messages[0].split()
        print(f"   找到 {len(message_ids)} 封相关邮件")
        
        # 提取收件人
        sent_to = set()
        for msg_id in message_ids:
            try:
                status, msg_data = imap.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (TO)])')
                if status == 'OK':
                    raw = msg_data[0][1].decode('utf-8', errors='ignore')
                    # 解析 To 字段
                    if 'To:' in raw:
                        to_line = raw.split('To:')[1].strip()
                        # 提取邮箱地址
                        import re
                        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', to_line)
                        for e in emails:
                            sent_to.add(e.lower())
            except Exception as e:
                continue
        
        imap.logout()
        print(f"✅ 成功提取 {len(sent_to)} 个已发送邮箱")
        return sent_to
        
    except Exception as e:
        print(f"❌ IMAP 错误: {e}")
        return set()


def get_all_users() -> list:
    """获取所有用户"""
    from supabase import create_client
    import os
    
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase 配置缺失")
        return []
    
    try:
        client = create_client(url, key)
        res = client.table("profiles").select("email").execute()
        return [u for u in res.data if u.get('email')]
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return []


def main():
    print("=" * 50)
    print("  邮件发送状态检查 & 重发工具")
    print("=" * 50)
    print()
    
    # 1. 获取所有用户
    print("📊 获取用户列表...")
    all_users = get_all_users()
    all_emails = {u['email'].lower() for u in all_users}
    print(f"   共 {len(all_emails)} 个用户")
    
    # 2. 获取已发送邮件
    sent_emails = get_sent_emails_from_gmail()
    
    # 3. 计算差集（未收到邮件的用户）
    not_sent = all_emails - sent_emails
    
    print()
    print("=" * 50)
    print(f"📈 统计结果:")
    print(f"   总用户数: {len(all_emails)}")
    print(f"   已发送: {len(sent_emails)}")
    print(f"   未发送: {len(not_sent)}")
    print("=" * 50)
    
    if not not_sent:
        print("\n✅ 所有用户都已收到邮件！")
        return
    
    # 4. 显示未发送的用户
    print("\n📋 未收到邮件的用户:")
    for i, email in enumerate(sorted(not_sent), 1):
        print(f"   {i}. {email}")
    
    # 5. 保存到文件
    retry_file = Path(__file__).parent / "retry_emails.txt"
    with open(retry_file, 'w') as f:
        for email in sorted(not_sent):
            f.write(email + '\n')
    print(f"\n💾 未发送列表已保存到: {retry_file}")
    
    # 6. 询问是否重发
    print()
    confirm = input("是否立即重发给这些用户？(y/n): ").strip().lower()
    
    if confirm == 'y':
        # 加载邮件模板
        from scripts.send_update_notification import load_email_html, EMAIL_SUBJECT, CURRENT_EMAIL_TEMPLATE
        
        email_html = load_email_html(CURRENT_EMAIL_TEMPLATE)
        
        # 过滤出需要重发的用户
        retry_users = [u for u in all_users if u['email'].lower() in not_sent]
        
        print(f"\n🚀 开始重发 {len(retry_users)} 封邮件...")
        
        success = 0
        fail = 0
        for i, user in enumerate(retry_users, 1):
            email = user['email']
            print(f"[{i}/{len(retry_users)}] {email}...", end="", flush=True)
            
            if mailer.send_email(email, EMAIL_SUBJECT, email_html):
                success += 1
                print(" ✅")
            else:
                fail += 1
                print(" ❌")
        
        print()
        print(f"✅ 重发完成: 成功 {success}, 失败 {fail}")
    else:
        print("\n已取消。如需手动重发，请运行:")
        print(f"   python3 {__file__} --resend")


if __name__ == "__main__":
    main()
