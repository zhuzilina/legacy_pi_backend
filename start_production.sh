#!/bin/bash

# Legacy PI Backend 生产环境启动脚本
# 使用 uWSGI + Nginx 架构

set -e

echo "🚀 启动 Legacy PI Backend 生产环境..."

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

# 检查环境变量
if [ -z "$ARK_API_KEY" ]; then
    echo "⚠️  警告: 未设置 ARK_API_KEY 环境变量"
    echo "请设置您的火山方舟 API 密钥:"
    echo "export ARK_API_KEY='your_api_key_here'"
    echo ""
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p media/md_docs/images media/tts static logs postgresql-init

# 设置权限
echo "🔐 设置文件权限..."
chmod +x manage.py
chmod +x start_production.sh

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans

# 检查是否有旧镜像文件
IMAGE_NAME="legacy_pi_backend_django-app:latest"
if [[ "$(docker images -q ${IMAGE_NAME} 2> /dev/null)" != "" ]]; then
    echo "发现 Docker 镜像 '${IMAGE_NAME}'。正在删除..."
    docker rmi ${IMAGE_NAME}
    echo "镜像 '${IMAGE_NAME}' 已成功删除。"
else
    echo "Docker 镜像 '${IMAGE_NAME}' 不存在，无需任何操作。"
fi

# 清理Docker缓存和镜像
echo "🧹 清理Docker缓存..."
docker system prune -f

# 根据清理模式决定是否清除数据卷
if check_data_volumes; then
    echo "🛡️  保护现有数据卷，只清理未使用的 volumes"
    docker volume prune -f
else
    echo "🗑️  强制清理模式：清除所有数据卷"
    docker volume prune -f
fi

# 清理本地缓存（保留媒体文件中的数据）
echo "🧹 清理本地缓存..."
rm -rf static/*
rm -rf logs/*.log
echo "💾 保留 media 目录中的用户数据"

# 构建和启动服务
echo "🔨 构建和启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 数据库迁移和初始化
echo "🔧 检查数据库迁移..."
docker-compose exec django-app python manage.py migrate

echo "🔍 验证数据库表..."
docker-compose exec django-app python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
tables = ['django_session', 'auth_user', 'django_admin_log', 'md_documents', 'md_images']
for table in tables:
    try:
        cursor.execute(f\"SELECT table_name FROM information_schema.tables WHERE table_name = '{table}'\")
        if cursor.fetchone():
            print(f'✅ 表 {table} 存在')
        else:
            print(f'❌ 表 {table} 不存在')
    except Exception as e:
        print(f'❌ 检查表 {table} 时出错: {e}')
"

echo "👤 检查超级用户..."
docker-compose exec django-app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户已创建')
else:
    print('✅ 超级用户已存在')
"

echo "📁 收集静态文件..."
docker-compose exec django-app python manage.py collectstatic --noinput

# 清理Django缓存
echo "🧹 清理Django缓存..."
docker-compose exec django-app python manage.py shell -c "
from django.core.cache import cache
try:
    cache.clear()
    print('✅ Django缓存已清理')
except Exception as e:
    print(f'⚠️ Django缓存清理失败: {e}')
"

# 重启Nginx以清理缓存
echo "🔄 重启Nginx服务..."
docker-compose restart nginx

# 重置crawler状态
echo "🔄 重置crawler状态..."
docker-compose exec django-app python manage.py shell -c "
from crawler.redis_service import redis_service
from crawler.redis_models import RedisStats
from datetime import datetime, timedelta
from django.utils import timezone
try:
    # 清理所有crawler相关数据
    today = timezone.now().date()
    today_str = today.isoformat()
    
    # 清理状态
    redis_service.redis_client.delete(f'crawl_status:{today_str}')
    redis_service.redis_client.delete(f'daily_crawl_lock:{today_str}')
    
    # 清理昨天的状态
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    redis_service.redis_client.delete(f'crawl_status:{yesterday_str}')
    redis_service.redis_client.delete(f'daily_crawl_lock:{yesterday_str}')
    
    # 清理旧数据
    deleted_count = RedisStats.clear_old_data(days_to_keep=1)
    
    print(f'✅ Crawler状态已重置，清理了 {deleted_count} 篇旧文章')
except Exception as e:
    print(f'⚠️ Crawler状态重置失败: {e}')
"

# 检查健康状态
echo "🏥 检查服务健康状态..."
echo "Django 应用:"
curl -f http://localhost/api/ai-chat/health/ || echo "❌ Django 应用健康检查失败"

echo "Nginx 代理:"
curl -f http://localhost/api/ai-chat/health/ || echo "❌ Nginx 代理健康检查失败"

# 功能验证
echo "🧪 功能验证..."
echo "管理后台访问测试:"
if curl -s http://localhost/admin/login/ | grep -q "Django 站点管理员"; then
    echo "✅ 管理后台可以正常访问"
else
    echo "❌ 管理后台访问失败"
fi

echo "API健康检查:"
if curl -s http://localhost/api/ai-chat/health/ | grep -q "healthy"; then
    echo "✅ API服务正常"
else
    echo "❌ API服务异常"
fi

echo "缓存清理验证:"
echo "测试crawler API (应该返回新数据):"
crawler_response=$(curl -s http://localhost/api/crawler/daily/)
if echo "$crawler_response" | grep -q "crawling\|cached\|success"; then
    echo "✅ Crawler API正常响应"
    echo "响应: $crawler_response"
else
    echo "❌ Crawler API响应异常"
    echo "响应: $crawler_response"
fi

echo "测试MD文档API:"
md_response=$(curl -s http://localhost/api/md-docs/category/)
if echo "$md_response" | grep -q "success"; then
    echo "✅ MD文档API正常响应"
    echo "响应: $md_response"
else
    echo "❌ MD文档API响应异常"
    echo "响应: $md_response"
fi

echo ""
echo "✅ 服务启动完成!"
echo ""
echo "📊 服务访问地址:"
echo "  - 主应用 (通过 Nginx): http://localhost"
echo "  - API 文档: http://localhost/api/"
echo "  - 管理后台: http://localhost/admin/"
echo "  - MongoDB 管理: http://localhost:8081"
echo "  - PostgreSQL 数据库: localhost:5432 (用户名: postgresuser, 密码: postgres123)"
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
echo ""
echo "🧹 缓存清理命令:"
echo "  - 清理Redis缓存: docker-compose exec django-app python manage.py shell -c \"import redis; redis.Redis(host='redis', port=6379, db=0, password='redis123').flushdb()\""
echo "  - 清理Django缓存: docker-compose exec django-app python manage.py shell -c \"from django.core.cache import cache; cache.clear()\""
echo "  - 重置crawler状态: curl -X POST http://localhost/api/crawler/reset/"
echo "  - 重新启动crawler: docker-compose exec django-app python manage.py start_daily_crawl"
echo "  - 清理Nginx缓存: docker-compose restart nginx"
echo ""
echo "📝 使用说明:"
echo "  - 正常启动: ./start_production.sh"
echo "  - 强制清理: ./start_production.sh --force-cleanup 或 ./start_production.sh -f"
echo "  - 强制清理将清除所有数据卷和数据库数据，请谨慎使用！"
