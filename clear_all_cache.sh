#!/bin/bash

# 清理所有缓存的脚本
# 用于解决API返回缓存数据的问题

set -e

echo "🧹 开始清理所有缓存..."

# 检查Docker服务是否运行
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker服务未运行，请先启动服务: ./start_production.sh"
    exit 1
fi

echo "1. 清理Redis缓存..."
docker-compose exec django-app python manage.py shell -c "
import redis
from django.conf import settings
try:
    redis_client = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        password=getattr(settings, 'REDIS_PASSWORD', 'redis123'),
        decode_responses=True
    )
    redis_client.flushdb()
    print('✅ Redis缓存已清理')
except Exception as e:
    print(f'⚠️ Redis缓存清理失败: {e}')
"

echo "2. 清理Django缓存..."
docker-compose exec django-app python manage.py shell -c "
from django.core.cache import cache
try:
    cache.clear()
    print('✅ Django缓存已清理')
except Exception as e:
    print(f'⚠️ Django缓存清理失败: {e}')
"

echo "3. 重置crawler状态..."
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

echo "4. 重启Nginx服务..."
docker-compose restart nginx

echo "5. 清理本地静态文件缓存..."
rm -rf static/*
docker-compose exec django-app python manage.py collectstatic --noinput

echo "6. 验证缓存清理效果..."
echo "测试crawler API:"
crawler_response=$(curl -s http://localhost/api/crawler/daily/)
echo "响应: $crawler_response"

echo ""
echo "测试MD文档API:"
md_response=$(curl -s http://localhost/api/md-docs/category/)
echo "响应: $md_response"

echo ""
echo "✅ 所有缓存清理完成！"
echo ""
echo "💡 如果API仍然返回缓存数据，请尝试："
echo "  1. 等待几秒钟让服务完全重启"
echo "  2. 使用不同的浏览器或隐私模式访问"
echo "  3. 检查浏览器缓存设置"
echo "  4. 重新运行: ./clear_all_cache.sh"
