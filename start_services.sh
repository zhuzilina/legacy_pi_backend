#!/bin/bash

# Legacy PI Backend 服务启动脚本
# 用于启动 Redis、MongoDB 等 Docker 服务

set -e

echo "🚀 启动 Legacy PI Backend 服务..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker-compose 是否可用
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p mongo-init
mkdir -p media/md_docs/images
mkdir -p media/tts

# 启动服务
echo "🐳 启动 Docker 服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."

# 检查 Redis
if docker-compose exec redis redis-cli -a redis123 ping > /dev/null 2>&1; then
    echo "✅ Redis 服务正常"
else
    echo "❌ Redis 服务异常"
fi

# 检查 MongoDB
if docker-compose exec mongodb mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB 服务正常"
else
    echo "❌ MongoDB 服务异常"
fi

# 检查 Django 应用
echo "🔍 检查 Django 应用..."
if curl -f http://localhost:8000/api/ai-chat/health/ > /dev/null 2>&1; then
    echo "✅ Django 应用正常"
else
    echo "❌ Django 应用异常"
fi

# 显示服务信息
echo ""
echo "📋 服务信息:"
echo "  Django 应用: http://localhost:8000"
echo "  Redis:     http://localhost:6379 (密码: redis123)"
echo "  MongoDB:   http://localhost:27017 (用户名: admin, 密码: password123)"
echo "  Mongo Express: http://localhost:8081 (用户名: admin, 密码: admin123)"
echo ""
echo "🔧 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
echo "🎉 服务启动完成！"
