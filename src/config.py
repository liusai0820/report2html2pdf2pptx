"""配置文件"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载配置目录中的 .env 文件
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
load_dotenv(env_path)

# OpenRouter配置
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-haiku")

# Adobe PDF Services 配置 (用于 PDF → PPTX 转换)
# 注意: adobe_pdf_to_pptx.py 使用 PDF_SERVICES_CLIENT_ID 和 PDF_SERVICES_CLIENT_SECRET
# 我们在这里做一个兼容层，将 ADOBE_CLIENT_ID 映射过去
_adobe_client_id = os.getenv("ADOBE_CLIENT_ID") or os.getenv("PDF_SERVICES_CLIENT_ID", "")
_adobe_client_secret = os.getenv("ADOBE_CLIENT_SECRET") or os.getenv("PDF_SERVICES_CLIENT_SECRET", "")

# 确保 Adobe SDK 能读取到凭证 (设置到环境变量)
if _adobe_client_id:
    os.environ["PDF_SERVICES_CLIENT_ID"] = _adobe_client_id
if _adobe_client_secret:
    os.environ["PDF_SERVICES_CLIENT_SECRET"] = _adobe_client_secret

ADOBE_AVAILABLE = bool(_adobe_client_id and _adobe_client_secret)

# 全局禁用 PPTX 转换开关 (设为 true 时，后端将完全跳过 PPTX 转换)
DISABLE_PPTX = os.getenv("DISABLE_PPTX", "false").lower() in ("true", "1", "yes")

# 从 .env 读取可用模型列表
def get_available_models():
    """从 .env 文件中读取所有可用的模型"""
    models = []
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    if not env_file.exists():
        return [DEFAULT_MODEL]
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            # 如果是 DEFAULT_MODEL 行，提取模型名
            if line.startswith('DEFAULT_MODEL='):
                model = line.split('=', 1)[1].strip()
                if model:
                    models.append(model)
            # 如果是单独的模型名（不包含=）
            elif '=' not in line and '/' in line:
                models.append(line)
    return models if models else [DEFAULT_MODEL]

AVAILABLE_MODELS = get_available_models()

# 生成配置
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "180"))  # 增加到 180 秒
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # 最多重试 3 次
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # 重试延迟 5 秒
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Telegram 反馈通知配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# SMTP 邮件发送配置
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SSL = os.getenv("SMTP_SSL", "true").lower() == "true"
SMTP_ENABLED = bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)

# Prompt模板路径
PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "promptv4.md")

# 输出目录
OUTPUT_DIR = "generated-slides"
TEMPLATE_DIR = "templates"
PAGES_DIR = f"{OUTPUT_DIR}/pages"
FINAL_HTML = f"{OUTPUT_DIR}/presentation.html"
FINAL_PDF = f"{OUTPUT_DIR}/presentation.pdf"

# 页面配置
PAGE_WIDTH = "1280px"
PAGE_HEIGHT = "720px"

# Supabase
VITE_SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


# ComfyUI Configuration
COMFYUI_ENABLED = os.getenv("COMFYUI_ENABLED", "false").lower() == "true"
COMFYUI_HOST = os.getenv("COMFYUI_HOST", "host.docker.internal:8188") # Docker访问宿主机的默认地址
COMFYUI_WORKFLOW_FILE = os.path.join(os.path.dirname(__file__), "workflow_api.json")

# 虎皮椒支付配置 (XunHuPay) - 商业化
# 从 https://www.xunhupay.com 获取 APPID 和 APPSECRET
XUNHU_APPID = os.getenv("XUNHU_APPID", "")
XUNHU_APPSECRET = os.getenv("XUNHU_APPSECRET", "")
XUNHU_NOTIFY_URL = os.getenv("XUNHU_NOTIFY_URL", "")  # 异步回调地址
XUNHU_ENABLED = bool(XUNHU_APPID and XUNHU_APPSECRET)
DOWNLOAD_PRICE_YUAN = float(os.getenv("DOWNLOAD_PRICE_YUAN", "9.9"))  # 下载价格（元）

# 商业化模式开关
COMMERCIAL_MODE = os.getenv("COMMERCIAL_MODE", "false").lower() == "true"


