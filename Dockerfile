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
    supervisor \
    cron \
    # 为 ChromeDriver 添加的额外依赖
    libglib2.0-0 \
    libnspr4 \
    libnss3 \
    libxcb1 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
	libxdamage1 \
	libxfixes3 \
	libxrandr2 \
	libgbm1 \
	libcairo2 \
	libpango-1.0-0 \
	libasound2 \
    wget

# 下载google chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 安装google chrome
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb -f && \
    rm -f google-chrome-stable_current_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip && \
    pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple && \
    pip install --no-cache-dir -r requirements.txt

# 安装 uWSGI 服务器 (包含Python支持)
RUN pip install uwsgi[python3]

# 复制项目文件
COPY . .

# 复制 chromedriver 并为其添加执行权限
COPY chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver

# 复制我们创建的 crontab 文件到 /etc/cron.d/ 目录
COPY daily_crawl_cron_jobs /etc/cron.d/daily_crawl_cron_jobs

# 为 crontab 文件设置正确的权限，这是 cron 安全要求的一部分
RUN chmod 0644 /etc/cron.d/daily_crawl_cron_jobs

# 创建 cron 任务使用的日志文件，确保它存在
RUN touch /var/log/supervisor/cron.log

# 复制首次启动测试脚本
COPY run_startup_task.sh /app/run_startup_task.sh
RUN chmod +x /app/run_startup_task.sh

# 将 Supervisor 配置文件复制到镜像中
COPY supervisor_conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建必要的目录
RUN mkdir -p media/md_docs/images media/tts static /var/log/uwsgi

# 设置权限
RUN chmod +x manage.py

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=legacy_pi_backend.settings

# 创建 Supervisor 日志目录
RUN mkdir -p /var/log/supervisor

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
