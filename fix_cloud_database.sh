#!/bin/bash

# 云端服务器数据库修复脚本
# 用于修复MD文档上传问题

echo "🔧 修复云端服务器数据库..."
echo "=================================="

# 检查Docker服务状态
echo "🔍 检查Docker服务状态..."
docker-compose ps

# 应用数据库迁移
echo "🔧 应用数据库迁移..."
docker-compose exec django-app python manage.py migrate

# 验证关键表是否存在
echo "🔍 验证数据库表..."
docker-compose exec django-app python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
tables = ['django_session', 'auth_user', 'django_admin_log', 'md_documents', 'md_images']
for table in tables:
    cursor.execute(f\"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'\")
    if cursor.fetchone():
        print(f'✅ 表 {table} 存在')
    else:
        print(f'❌ 表 {table} 不存在')
"

# 检查超级用户
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

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec django-app python manage.py collectstatic --noinput

# 测试API功能
echo "🧪 测试API功能..."
echo "文档列表API:"
curl -s "http://localhost/api/md-docs/category/" | jq .

echo "API健康检查:"
curl -s "http://localhost/api/ai-chat/health/" | jq .

echo ""
echo "✅ 数据库修复完成！"
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
