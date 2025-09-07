#!/bin/bash

# 云端服务器缓存清除脚本
# 用于解决MD文档API缓存问题

echo "🔧 清除云端服务器缓存..."
echo "=================================="

# 检查Docker服务状态
echo "🔍 检查Docker服务状态..."
docker-compose ps

# 清除Django缓存
echo "🧹 清除Django缓存..."
docker-compose exec django-app python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('✅ Django缓存已清除')
"

# 清除Redis缓存
echo "🧹 清除Redis缓存..."
docker-compose exec redis redis-cli FLUSHALL
echo "✅ Redis缓存已清除"

# 检查数据库中的文档数量
echo "🔍 检查数据库中的文档数量..."
docker-compose exec django-app python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM md_documents')
count = cursor.fetchone()[0]
print(f'数据库中的文档数量: {count}')

if count > 0:
    cursor.execute('SELECT id, title, category, is_published FROM md_documents LIMIT 5')
    docs = cursor.fetchall()
    print('前5个文档:')
    for doc in docs:
        print(f'  - ID: {doc[0]}, 标题: {doc[1]}, 类别: {doc[2]}, 已发布: {doc[3]}')
"

# 重启Django服务以清除内存缓存
echo "🔄 重启Django服务..."
docker-compose restart django-app

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 测试API功能
echo "🧪 测试API功能..."
echo "文档列表API:"
curl -s "http://localhost/api/md-docs/category/" | jq .

echo "API健康检查:"
curl -s "http://localhost/api/ai-chat/health/" | jq .

echo ""
echo "✅ 缓存清除完成！"
echo ""
echo "📊 现在可以测试文档上传功能："
echo "1. 使用md_upload_tool.py上传文档"
echo "2. 检查文档是否出现在列表中"
echo "3. 验证文档内容是否可以正常访问"
echo ""
echo "🔗 管理后台访问地址:"
echo "   http://your-server-ip/admin/"
echo "   用户名: admin"
echo "   密码: admin123"
