# ============================================
# AI Presentation Generator - Backend Dockerfile
# 支持 Puppeteer (Chrome) 用于 HTML → PDF 转换
# ============================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (Chrome 和 Node.js)
RUN apt-get update && apt-get install -y \
    # Chrome 依赖
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    # 中文字体 (包含黑体和楷体)
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-arphic-ukai \
    # Node.js
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    # 清理
    && rm -rf /var/lib/apt/lists/*

# 安装 Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 设置 Chrome 路径环境变量
ENV CHROME_PATH=/usr/bin/google-chrome-stable
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

# 复制 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制 Node.js 依赖并安装
COPY package.json package-lock.json* ./
RUN npm ci --only=production || npm install puppeteer

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY promptv4.md ./

# 创建必要的目录
RUN mkdir -p input output

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# 暴露端口
EXPOSE 8005

# 启动命令
CMD ["python", "src/server.py"]
