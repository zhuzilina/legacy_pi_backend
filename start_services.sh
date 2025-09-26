#!/bin/bash

# Legacy PI Backend 服务启动脚本
# 用于启动 Redis、MongoDB 等 Docker 服务

set -e

echo "🚀 启动 Legacy PI Backend 服务..."

# 检查是否启用强制清理
FORCE_CLEANUP=false
if [[ "$1" == "--force-cleanup" || "$1" == "-f" ]]; then
    FORCE_CLEANUP=true
    echo "⚠️  强制清理模式已启用，将清除所有数据"
fi

# 检查数据卷是否存在
check_data_volumes() {
    local mongodb_exists=false
    local postgresql_exists=false

    if docker volume ls | grep -q "legacy_pi_backend_mongodb_data"; then
        mongodb_exists=true
    fi

    if docker volume ls | grep -q "legacy_pi_backend_postgresql_data"; then
        postgresql_exists=true
    fi

    echo "📊 数据卷状态检查:"
    echo "  MongoDB: $([ "$mongodb_exists" = true ] && echo "✅ 存在" || echo "❌ 不存在")"
    echo "  PostgreSQL: $([ "$postgresql_exists" = true ] && echo "✅ 存在" || echo "❌ 不存在")"

    if [ "$mongodb_exists" = true ] || [ "$postgresql_exists" = true ]; then
        if [ "$FORCE_CLEANUP" = false ]; then
            echo "🛡️  检测到现有数据，将保护现有数据不被清除"
            return 0
        else
            echo "🗑️  强制清理模式：将清除所有现有数据"
            return 1
        fi
    fi
    return 0
}

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

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans

# 根据清理模式决定是否清除数据卷
if check_data_volumes; then
    echo "🛡️  保护现有数据卷，跳过数据清理"
else
    echo "🗑️  强制清理模式：清除所有数据卷"
    docker volume prune -f
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p mongo-init
mkdir -p postgresql-init
mkdir -p media/md_docs/images
mkdir -p media/tts

# 检查是否有旧镜像文件
IMAGE_NAME="legacy_pi_backend_django-app:latest"
if [[ "$(docker images -q ${IMAGE_NAME} 2> /dev/null)" != "" ]]; then
    echo "发现 Docker 镜像 '${IMAGE_NAME}'。正在删除..."
    docker rmi ${IMAGE_NAME}
    echo "镜像 '${IMAGE_NAME}' 已成功删除。"
else
    echo "Docker 镜像 '${IMAGE_NAME}' 不存在，无需任何操作。"
fi

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

# 检查 PostgreSQL
if docker-compose exec postgresql psql -U postgresuser -d legacy_pi_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL 服务正常"
else
    echo "❌ PostgreSQL 服务异常"
fi

# 检查 Django 应用
echo "🔍 检查 Django 应用..."
if curl -f http://localhost/api/ai-chat/health/ > /dev/null 2>&1; then
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
echo "  PostgreSQL: http://localhost:5432 (用户名: postgresuser, 密码: postgres123)"
echo "  Mongo Express: http://localhost:8081 (用户名: admin, 密码: admin123)"
echo ""
echo "🔧 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
echo "📝 使用说明:"
echo "  - 正常启动: ./start_services.sh"
echo "  - 强制清理: ./start_services.sh --force-cleanup 或 ./start_services.sh -f"
echo "  - 强制清理将清除所有数据卷和数据库数据，请谨慎使用！"
echo ""
echo "🎉 服务启动完成！"
