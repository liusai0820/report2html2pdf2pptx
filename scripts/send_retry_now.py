#!/usr/bin/env python3
"""
直接发送 retry_emails.txt 中的邮件（无需确认）
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 加载环境变量
load_dotenv(PROJECT_ROOT / "config/.env")

# 确保 src 目录在 Python 路径中（mailer.py 需要导入同目录的 config）
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src import mailer

# 邮件配置
EMAIL_SUBJECT = "【SlideCraft】v2.0 重磅更新：多模态理解 + 演讲稿生成 + 移动端适配，随时随地让 AI 真正看懂你的文档"
TEMPLATE_PATH = Path(__file__).parent.parent / "docs/announcements/版本更新公告_2026年1月_email.html"
RETRY_FILE = Path(__file__).parent / "retry_emails.txt"

def main():
    print("=" * 60)
    print("  📧 邮件重发工具（直接发送模式）")
    print("=" * 60)
    print()
    
    # 加载邮件列表
    if not RETRY_FILE.exists():
        print(f"❌ 文件不存在: {RETRY_FILE}")
        return 1
    
    emails = [line.strip() for line in RETRY_FILE.read_text().split('\n') if line.strip()]
    
    if not emails:
        print("❌ 邮件列表为空")
        return 1
    
    # 加载模板
    if not TEMPLATE_PATH.exists():
        print(f"❌ 模板不存在: {TEMPLATE_PATH}")
        return 1
    
    email_html = TEMPLATE_PATH.read_text(encoding='utf-8')
    
    print(f"📧 待发送: {len(emails)} 封邮件")
    print(f"📄 模板: {TEMPLATE_PATH.name}")
    print(f"📝 主题: {EMAIL_SUBJECT[:50]}...")
    print()
    print("🚀 开始发送...\n")
    
    success = 0
    fail = 0
    failed_emails = []
    
    for i, email in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] {email}...", end="", flush=True)
        
        if mailer.send_email(email, EMAIL_SUBJECT, email_html):
            success += 1
            print(" ✅")
        else:
            fail += 1
            failed_emails.append(email)
            print(" ❌")
    
    print()
    print("=" * 60)
    print(f"✅ 完成: 成功 {success}, 失败 {fail}")
    print("=" * 60)
    
    # 保存失败的邮件
    if failed_emails:
        failed_file = Path(__file__).parent / "still_failed.txt"
        failed_file.write_text('\n'.join(failed_emails))
        print(f"\n❌ 失败的邮件已保存到: {failed_file}")
    
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
