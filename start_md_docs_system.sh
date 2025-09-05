#!/bin/bash

# MD文档管理系统启动脚本

echo "🚀 启动MD文档管理系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 启动MongoDB容器
echo "📦 启动MongoDB容器..."
docker-compose up -d

# 等待MongoDB启动
echo "⏳ 等待MongoDB启动..."
sleep 5

# 检查容器状态
if docker-compose ps | grep -q "Up"; then
    echo "✅ MongoDB容器启动成功"
else
    echo "❌ MongoDB容器启动失败"
    exit 1
fi

# 激活虚拟环境并启动Django服务器
echo "🐍 启动Django服务器..."
source venv/bin/activate

# 检查数据库迁移
echo "📊 检查数据库迁移..."
python manage.py migrate

# 启动服务器
echo "🌐 启动Web服务器..."
echo "服务器将在 http://localhost:8000 启动"
echo "Mongo Express将在 http://localhost:8081 启动"
echo "按 Ctrl+C 停止服务器"

python manage.py runserver 0.0.0.0:8000
