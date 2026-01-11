#!/usr/bin/env python3
"""
检查最新的 generations 记录
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / "config" / "slidecraft-backend.env"
load_dotenv(env_path)

from supabase import create_client

url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
client = create_client(url, key)

print("=" * 60)
print("🔍 最新 5 条 GENERATIONS 记录")
print("=" * 60)

# 获取最新记录
res = client.table("generations").select("*").order("created_at", desc=True).limit(5).execute()

if res.data:
    for i, row in enumerate(res.data):
        print(f"\n--- 记录 {i+1} ---")
        print(f"created_at: {row.get('created_at')}")
        print(f"scenario: {row.get('scenario')}")
        print(f"document_name: {row.get('document_name')[:30] if row.get('document_name') else 'NULL'}...")
        print(f"")
        print(f"🎨 配置字段:")
        print(f"  theme_color: {row.get('theme_color') or '❌ NULL'}")
        print(f"  font_style: {row.get('font_style') or '❌ NULL'}")
        print(f"  target_pages: {row.get('target_pages') or '❌ NULL'}")
        print(f"  content_depth: {row.get('content_depth') or '❌ NULL'}")
        print(f"  organization: {row.get('organization') or '❌ NULL'}")
        print(f"  custom_instructions: {row.get('custom_instructions') or '❌ NULL'}")
        print(f"")
        print(f"📊 结果字段:")
        print(f"  actual_pages: {row.get('actual_pages') or '❌ NULL'}")
        print(f"  pages: {row.get('pages') or '❌ NULL'}")
        print(f"  output_dir: {row.get('output_dir') or '❌ NULL'}")
        print(f"  output_path: {row.get('output_path')[:40] if row.get('output_path') else '❌ NULL'}...")

print("\n" + "=" * 60)
print("✅ 检查完成")
print("=" * 60)
