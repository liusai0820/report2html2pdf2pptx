import sys
import os
import time
import logging

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

# 邮件主题：亲切、直白，highlight 核心功能
EMAIL_SUBJECT = "【SlideCraft】见信好：AI 绘图功能正式上线，封面设计支持 ComfyUI"

# HTML 正文 (Swiss Magazine Style)
EMAIL_BODY_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&family=Noto+Serif+SC:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0F172A;
            --accent: #2563EB;
            --secondary: #64748B;
            --bg: #F1F5F9;
            --card-bg: #FFFFFF;
            --border: #E2E8F0;
            --highlight: #EFF6FF;
        }

        body {
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #E2E8F0;
            margin: 0;
            padding: 20px;
            color: var(--primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            width: 100%;
            max-width: 520px;
            margin: 0 auto;
            background: var(--card-bg);
            box-shadow: 0 20px 60px -10px rgba(15, 23, 42, 0.1);
            position: relative;
            overflow: hidden;
            border-bottom: 4px solid var(--accent);
        }

        /* Header */
        .brand-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 32px;
            border-bottom: 1px solid var(--border);
        }

        .brand-logo { font-weight: 900; font-size: 14px; letter-spacing: 1px; color: var(--primary); }
        .brand-date { font-size: 11px; color: var(--secondary); letter-spacing: 1px; text-transform: uppercase; }

        .content-wrapper { padding: 48px 32px; }

        /* Hero */
        .hero { margin-bottom: 48px; }
        .hero-label {
            font-size: 12px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 16px;
            display: inline-block;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 2px;
        }

        h1 {
            font-family: 'Noto Serif SC', serif;
            font-size: 32px;
            line-height: 1.3;
            font-weight: 700;
            color: var(--primary);
            margin-top: 0;
            margin-bottom: 24px;
        }

        .intro {
            font-size: 15px;
            color: var(--secondary);
            margin-bottom: 32px;
            text-align: justify;
        }

        /* Section */
        .section-label {
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #94A3B8;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

        /* Features */
        .feature-item {
            margin-bottom: 24px;
            padding-left: 16px;
            border-left: 2px solid var(--accent);
        }
        .feature-title { font-weight: 700; font-size: 15px; margin-bottom: 4px; color: var(--primary); }
        .feature-desc { font-size: 13px; color: var(--secondary); margin: 0; }

        /* Status Box */
        .status-box {
            background: #F8FAFC;
            padding: 20px;
            border: 1px solid var(--border);
            margin-bottom: 40px;
        }
        .status-title { font-size: 12px; font-weight: 700; color: var(--primary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .status-text { font-size: 13px; color: var(--secondary); margin-bottom: 8px; }

        /* CTA */
        .cta-btn {
            display: block;
            background: var(--primary);
            color: white !important;
            text-align: center;
            padding: 16px;
            text-decoration: none;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 1px;
            margin-top: 32px;
            transition: opacity 0.2s;
        }
        .cta-btn:hover { opacity: 0.9; }

        .footer {
            padding: 32px;
            background: #F8FAFC;
            text-align: center;
            font-size: 12px;
            color: #94A3B8;
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="brand-bar">
            <div class="brand-logo">SlideCraft</div>
            <div class="brand-date">DECEMBER 2025</div>
        </div>

        <div class="content-wrapper">
            <div class="hero">
                <span class="hero-label">MAJOR UPDATE</span>
                <h1>AI 绘图引擎<br>正式上线</h1>
                <div class="intro">
                    自内测开启以来，我们收到了大量用户的真实反馈与建议。感谢每一位“发声”的你，是你们让 SlideCraft 进化得更快。<br><br>
                    今天，我们高兴地通知您：<strong>ComfyUI 绘图引擎</strong>现已本地集成。
                </div>
            </div>

            <div class="section-label">HIGHLIGHTS</div>
            
            <div class="feature-item">
                <div class="feature-title">AI 驱动的原创设计</div>
                <p class="feature-desc">AI 因地制宜。它会深入理解您的大纲，构思出如“微距下的精密机械”或“深邃的棋局”等视觉隐喻，生成具有电影级质感的高级背景。</p>
            </div>

            <div class="feature-item">
                <div class="feature-title">性能倍增</div>
                <p class="feature-desc">通过底层 Turbo 流程优化，图片生成速度提升 200%。清晰度锁定 720p HD 高清标准，即刻呈现。</p>
            </div>

            <div class="section-label">A SPECIAL GIFT</div>

            <!-- 福利卡片 -->
            <div style="background: #EFF6FF; border: 2px solid #2563EB; padding: 24px; position: relative; margin-bottom: 40px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #2563EB; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;">Quota Reset</div>
                <div style="font-size: 16px; color: #1E3A8A; font-weight: bold; margin-bottom: 8px;">用量已重置 ✅</div>
                <div style="font-size: 14px; color: #3B82F6; margin-bottom: 0;">
                    为感谢您的支持，后台已清空所有历史记录<br>
                    您现在拥有 <span style="font-size: 24px; font-weight: 900; color: #2563EB; vertical-align: -2px; margin: 0 4px;">3</span> 次全新的免费生成机会
                </div>
            </div>

            <div class="section-label">STATUS</div>

            <div class="status-box">
                <div class="status-title">温馨提示</div>
                <p class="status-text">AI 绘图功能采用本地 GPU 队列处理。如遇多人同时使用，生成时间可能略有延迟（约 10-30 秒）。若追求极速体验，建议选择「无背景图（纯色）」模式，内容生成将秒级完成。</p>
            </div>

            <div class="status-box">
                <div class="status-title">未来规划</div>
                <p class="status-text">收到许多用户关于“更多模板风格”的建议，我们正在加紧开发。包括极简大字风、学术严谨风等新模版将在近期陆续上线。</p>
            </div>

            <a href="http://ppt.gwy.life" class="cta-btn">前往体验新功能 →</a>
        </div>

        <div class="footer">
            HIIC INNOVATION DEPARTMENT · 2025<br>
            让工具服务于思想
        </div>
    </div>
</body>
</html>
"""

def get_test_users():
    """手动指定测试用户列表"""
    # 优先从环境变量获取，如果没有则使用默认
    default_email = config.SMTP_USER
    if not default_email:
        print("错误: config.SMTP_USER 未设置，无法进行测试发送。")
        return []
        
    return [
        {"email": default_email}, 
    ]

def get_db_users():
    """从数据库获取真实用户"""
    client = db.get_client()
    if not client:
        return []
        
    try:
        # 尝试从 profiles 表获取 email
        res = client.table("profiles").select("email").execute()
        valid_users = [u for u in res.data if u.get('email')]
        return valid_users
    except Exception as e:
        logger.error(f"Failed to fetch users from DB: {e}")
        return []

if __name__ == "__main__":
    print("-" * 40)
    print("SlideCraft 更新通知发送脚本")
    print("-" * 40)
    
    # 模式选择
    print("模式选择:")
    print("  1: 测试发给自己")
    print("  2: 群发所有用户 (慎用)")
    mode = input("输入模式编号 (1/2): ")
    # mode = "1" # 默认先测试
    
    if mode == "2":
        users = get_db_users()
        print("⚠️  注意：即将进行群发！")
    else:
        users = get_test_users()
        print("ℹ️  测试模式：仅发送给自己")
    
    if not users:
        print("❌ 未找到有效用户列表。")
        sys.exit(0)
        
    print(f"📊 目标用户数: {len(users)}")
    print(f"📧 邮件主题: {EMAIL_SUBJECT}")
    
    # 确认发送
    if mode == "2":
        confirm = input(f"确认向 {len(users)} 位用户发送邮件? (必须输入 'confirm'): ")
        if confirm != 'confirm':
            print("已取消")
            sys.exit(0)
    
    # 批量发送
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users):
        email = user.get('email')
        if not email: continue
        
        print(f"[{i+1}/{len(users)}] 发送至 {email}...", end="", flush=True)
        
        if mailer.send_email(email, EMAIL_SUBJECT, EMAIL_BODY_HTML):
            success_count += 1
            print(" ✅")
        else:
            fail_count += 1
            print(" ❌")
            
        # 避免触发反垃圾限制
        if len(users) > 5:
            time.sleep(2)
        
    print("-" * 40)
    print(f"任务完成。成功: {success_count}, 失败: {fail_count}")
