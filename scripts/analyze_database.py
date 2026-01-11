#!/usr/bin/env python3
"""
分析 Supabase 数据库真实结构
"""

import sys
import os
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / "config" / "slidecraft-backend.env"
load_dotenv(env_path)

from supabase import create_client

# 初始化客户端
url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Missing Supabase credentials")
    sys.exit(1)

client = create_client(url, key)
print(f"✅ Connected to Supabase: {url}\n")

# ============================================
# 1. 查询所有表
# ============================================
print("=" * 60)
print("📋 PUBLIC SCHEMA TABLES")
print("=" * 60)

# 直接查询各表（无法通过 RPC 查询 information_schema）
known_tables = [
    'profiles', 'generations', 'feedback', 'speech_scripts',
    'plans', 'user_events'
]

for table in known_tables:
    try:
        res = client.table(table).select("*", count="exact").limit(1).execute()
        count = res.count if res.count is not None else len(res.data)
        print(f"  ✓ {table}: {count} rows")
    except Exception as e:
        if "does not exist" in str(e):
            print(f"  ✗ {table}: NOT EXISTS")
        else:
            print(f"  ? {table}: {e}")

# ============================================
# 2. 查询 generations 表结构
# ============================================
print("\n" + "=" * 60)
print("📊 GENERATIONS TABLE STRUCTURE")
print("=" * 60)

try:
    res = client.table("generations").select("*").limit(5).execute()
    if res.data and len(res.data) > 0:
        sample = res.data[0]
        print("\nColumns (from sample row):")
        for key, value in sample.items():
            val_type = type(value).__name__
            val_preview = str(value)[:50] if value else "NULL"
            print(f"  • {key}: {val_type} = {val_preview}")
    else:
        print("  (empty table)")
except Exception as e:
    print(f"Error: {e}")

# ============================================
# 3. 查询 profiles 表结构
# ============================================
print("\n" + "=" * 60)
print("👤 PROFILES TABLE STRUCTURE")
print("=" * 60)

try:
    res = client.table("profiles").select("*").limit(3).execute()
    if res.data and len(res.data) > 0:
        sample = res.data[0]
        print("\nColumns (from sample row):")
        for key, value in sample.items():
            val_type = type(value).__name__
            val_preview = str(value)[:50] if value else "NULL"
            print(f"  • {key}: {val_type} = {val_preview}")
    else:
        print("  (empty table)")
except Exception as e:
    print(f"Error: {e}")

# ============================================
# 4. 查询 feedback 表结构
# ============================================
print("\n" + "=" * 60)
print("💬 FEEDBACK TABLE STRUCTURE")
print("=" * 60)

try:
    res = client.table("feedback").select("*").limit(3).execute()
    if res.data and len(res.data) > 0:
        sample = res.data[0]
        print("\nColumns (from sample row):")
        for key, value in sample.items():
            val_type = type(value).__name__
            val_preview = str(value)[:50] if value else "NULL"
            print(f"  • {key}: {val_type} = {val_preview}")
    else:
        print("  (empty table)")
except Exception as e:
    print(f"Error: {e}")

# ============================================
# 5. 分析 generations 表中的 NULL 字段
# ============================================
print("\n" + "=" * 60)
print("🔍 GENERATIONS - NULL FIELD ANALYSIS")
print("=" * 60)

try:
    res = client.table("generations").select("*").limit(50).execute()
    if res.data:
        total = len(res.data)
        null_counts = {}

        for row in res.data:
            for key, value in row.items():
                if key not in null_counts:
                    null_counts[key] = 0
                if value is None:
                    null_counts[key] += 1

        print(f"\nSample size: {total} rows")
        print("\nNULL percentage by column:")
        for key, null_count in sorted(null_counts.items(), key=lambda x: -x[1]):
            pct = (null_count / total) * 100
            status = "⚠️" if pct > 80 else "✓"
            print(f"  {status} {key}: {pct:.0f}% NULL ({null_count}/{total})")
except Exception as e:
    print(f"Error: {e}")

# ============================================
# 6. 检查 speech_scripts 表
# ============================================
print("\n" + "=" * 60)
print("🎤 SPEECH_SCRIPTS TABLE")
print("=" * 60)

try:
    res = client.table("speech_scripts").select("*", count="exact").limit(3).execute()
    count = res.count if res.count is not None else len(res.data)
    print(f"\nTotal rows: {count}")
    if res.data and len(res.data) > 0:
        sample = res.data[0]
        print("\nColumns:")
        for key, value in sample.items():
            val_type = type(value).__name__
            if key == 'content':
                val_preview = f"({len(str(value))} chars)" if value else "NULL"
            else:
                val_preview = str(value)[:50] if value else "NULL"
            print(f"  • {key}: {val_type} = {val_preview}")
except Exception as e:
    if "does not exist" in str(e):
        print("  ❌ Table does not exist - needs migration!")
    else:
        print(f"Error: {e}")

# ============================================
# 7. 检查视图
# ============================================
print("\n" + "=" * 60)
print("👁️ VIEWS")
print("=" * 60)

views = ['admin_users', 'admin_generations', 'feedback_cn']
for view in views:
    try:
        res = client.table(view).select("*", count="exact").limit(1).execute()
        count = res.count if res.count is not None else "?"
        print(f"  ✓ {view}: {count} rows")
        if res.data:
            print(f"    Columns: {list(res.data[0].keys())}")
    except Exception as e:
        if "does not exist" in str(e):
            print(f"  ✗ {view}: NOT EXISTS")
        else:
            print(f"  ? {view}: {str(e)[:50]}")

print("\n" + "=" * 60)
print("✅ Analysis Complete")
print("=" * 60)
