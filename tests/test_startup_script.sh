#!/bin/bash

# 测试启动脚本的数据库迁移功能
cd ../
echo "🧪 测试启动脚本的数据库迁移功能..."

# 模拟数据库迁移步骤
echo "🔧 检查数据库迁移..."
docker-compose exec django-app python manage.py migrate

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

echo "🎉 测试完成！"
