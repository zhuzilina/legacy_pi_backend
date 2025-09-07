#!/bin/bash

# Legacy PI Backend 生产环境启动脚本
# 使用 uWSGI + Nginx 架构

set -e

echo "🚀 启动 Legacy PI Backend 生产环境..."

# 检查环境变量
if [ -z "$ARK_API_KEY" ]; then
    echo "⚠️  警告: 未设置 ARK_API_KEY 环境变量"
    echo "请设置您的火山方舟 API 密钥:"
    echo "export ARK_API_KEY='your_api_key_here'"
    echo ""
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p media/md_docs/images media/tts static logs

# 设置权限
echo "🔐 设置文件权限..."
chmod +x manage.py
chmod +x start_production.sh

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans

# 构建和启动服务
echo "🔨 构建和启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查服务健康状态..."
echo "Django 应用:"
curl -f http://localhost:8000/api/ai-chat/health/ || echo "❌ Django 应用健康检查失败"

echo "Nginx 代理:"
curl -f http://localhost/health/ || echo "❌ Nginx 代理健康检查失败"

echo ""
echo "✅ 服务启动完成!"
echo ""
echo "📊 服务访问地址:"
echo "  - 主应用 (通过 Nginx): http://localhost"
echo "  - API 文档: http://localhost/api/"
echo "  - 管理后台: http://localhost/admin/"
echo "  - MongoDB 管理: http://localhost:8081"
echo ""
echo "📝 日志查看:"
echo "  - 查看所有服务日志: docker-compose logs -f"
echo "  - 查看 Django 日志: docker-compose logs -f django-app"
echo "  - 查看 Nginx 日志: docker-compose logs -f nginx"
echo ""
echo "🛠️  管理命令:"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 查看状态: docker-compose ps"
