import os
import boto3
import requests
import logging
from datetime import datetime, timezone, timedelta
from botocore.exceptions import NoCredentialsError

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))

logger = logging.getLogger(__name__)

# 配置从环境变量获取
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN") # e.g., https://pub-xxx.r2.dev

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def get_r2_client():
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        logger.warning("R2 配置缺失，无法上传")
        return None
    
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY
    )

def upload_to_r2(file_path, object_name=None):
    """
    上传文件到 Cloudflare R2 并返回下载链接
    """
    if not object_name:
        # 统一上传到 ppt/ 目录，与现有文件结构保持一致
        object_name = f"ppt/{os.path.basename(file_path)}"
    
    s3 = get_r2_client()
    if not s3:
        return None
        
    try:
        logger.info(f"开始上传文件到 R2: {object_name}")
        s3.upload_file(file_path, R2_BUCKET_NAME, object_name)
        
        # 构造下载链接
        from urllib.parse import quote
        
        # 我们确保 object_name 总是以 ppt/ 开头
        # 只需要对剩余的文件名部分进行编码
        if object_name.startswith("ppt/"):
            filename_part = object_name[4:]
            encoded_filename = quote(filename_part, safe='')
            final_path = f"ppt/{encoded_filename}"
        else:
            # 万一外部传入了不带 ppt/ 的 object_name (虽然现在只在内部调用)
            final_path = quote(object_name, safe='')

        # 使用 file.gwy.life 域名，并包含 ppt/ 路径
        url = f"https://file.gwy.life/{final_path}"
            
        logger.info(f"R2 上传成功: {url}")
        return url
    except FileNotFoundError:
        logger.error("文件未找到")
        return None
    except NoCredentialsError:
        logger.error("R2 凭证错误")
        return None
    except Exception as e:
        logger.error(f"R2 上传失败: {e}")
        return None

def send_telegram_notify(doc_name, download_url, email=None):
    """
    发送 Telegram 通知
    """
    if not all([TG_BOT_TOKEN, TG_CHAT_ID]):
        logger.warning("Telegram 配置缺失，无法发送通知")
        return False
        
    
    # 获取北京时间
    current_time = datetime.now(BEIJING_TZ).strftime("%H:%M:%S")
    
    # 尝试获取文件大小（如果 doc_name 是路径）或者传入大小
    # 这里为了简单，我们加上 Email 信息
    
    user_info = f"👤 *用户*: `{email}`\n" if email else ""
    
    # 更加丰富的格式，参考用户截图
    message = (
        f"⬇️ *新文件上传*\n"
        f"────────────────\n"
        f"📄 *文档*: {doc_name}\n"
        f"{user_info}"
        f"🔗 *下载*: [点击下载]({download_url})\n"
        f"🕒 *时间*: `{current_time}`\n"
        f"\n_请复制链接发送给客户_"
    )
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",  # 重新启用 Markdown，但需确保内容安全
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Telegram 通知发送成功")
            return True
        else:
            logger.error(f"Telegram 通知发送失败: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram 请求异常: {e}")
        return False

def send_user_action_notify(action_type, details, email=None):
    """
    发送用户行为通知 (上传、注册等)
    """
    if not all([TG_BOT_TOKEN, TG_CHAT_ID]):
        return

    current_time = datetime.now(BEIJING_TZ).strftime("%H:%M:%S")
    
    user_info = f"👤 *用户*: `{email}`\n" if email else "👤 *用户*: `匿名`\n"
    
    if action_type == "upload":
        title = "📂 *新文档上传*"
        content = f"📄 *文件名*: {details}"
    elif action_type == "signup":
        title = "👋 *新用户注册*"
        content = f"🎉 *欢迎新伙伴加入!*"
    else:
        title = f"📢 *{action_type}*"
        content = details

    message = (
        f"{title}\n"
        f"────────────────\n"
        f"{user_info}"
        f"{content}\n"
        f"🕒 *时间*: `{current_time}`"
    )
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Telegram Action通知发送异常: {e}")

def send_document_to_telegram(file_path, caption=None, email=None):
    """
    发送文档文件到 Telegram
    """
    if not all([TG_BOT_TOKEN, TG_CHAT_ID]):
        logger.warning("Telegram 配置缺失，无法发送文档")
        return False
    
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False
    
    current_time = datetime.now(BEIJING_TZ).strftime("%H:%M:%S")
    filename = os.path.basename(file_path)
    
    # 构建 caption
    user_info = f"👤 用户: {email}\n" if email else ""
    if not caption:
        caption = f"📂 新文档上传\n{user_info}📄 {filename}\n🕒 {current_time}"
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'document': (filename, f)}
            data = {
                'chat_id': TG_CHAT_ID,
                'caption': caption
            }
            response = requests.post(url, files=files, data=data, timeout=30)
            
        if response.status_code == 200:
            logger.info(f"文档发送到 Telegram 成功: {filename}")
            return True
        else:
            logger.error(f"文档发送失败: {response.text}")
            return False
    except Exception as e:
        logger.error(f"发送文档异常: {e}")
        return False
