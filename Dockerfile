# ============================================
# AI Presentation Generator - ARM64 兼容版
# 使用 Chromium 而不是 Chrome
# ============================================

FROM python:3.11-slim

WORKDIR /app

# 安装 Chromium、Node.js 和依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium 浏览器
    chromium \
    # 中文字体 - 完整安装
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-liberation \
    fontconfig \
    # 文档解析工具
    antiword \
    # Node.js 依赖
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # 刷新字体缓存
    && fc-cache -fv

# 安装 Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 设置 Chromium 环境变量
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Node.js 依赖 (Puppeteer for PDF)
COPY package.json package-lock.json* ./
RUN npm ci --only=production 2>/dev/null || npm install --only=production

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY promptv4.md ./
COPY run.py ./

# 创建目录（output 目录通过 docker-compose volume 挂载）
RUN mkdir -p input output

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

EXPOSE 8005

CMD ["python", "src/server.py"]