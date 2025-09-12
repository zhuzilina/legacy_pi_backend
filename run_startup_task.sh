#!/bin/sh

# 等待几秒钟，确保 uWSGI 和其他服务有足够的时间初始化
# 这是一个好的实践，特别是如果任务依赖数据库连接
echo "Waiting for 10 seconds before starting the initial crawl..."
sleep 10

echo "Executing one-time startup crawl task..."

# 切换到 app 目录
cd /app

# 执行 Django management command
# 输出会由 supervisor 重定向到日志文件
python manage.py start_daily_crawl

echo "Startup crawl task finished."