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
