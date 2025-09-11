# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 安装 uWSGI 服务器 (包含Python支持)
RUN pip install uwsgi[python3]

# 复制项目文件
COPY . .

# 复制 chromedriver 并为其添加执行权限
COPY chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver

# 创建必要的目录
RUN mkdir -p media/md_docs/images media/tts static /var/log/uwsgi

# 设置权限
RUN chmod +x manage.py

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=legacy_pi_backend.settings

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ai-chat/health/ || exit 1

# 启动命令
CMD ["uwsgi", "--ini", "uwsgi.ini"]
