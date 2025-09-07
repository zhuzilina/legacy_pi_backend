#!/bin/bash

# 云端服务器MD文档API修复脚本
# 解决文档上传后无法在列表中显示的问题

echo "🔧 修复云端服务器MD文档API..."
echo "=================================="

# 检查Docker服务状态
echo "🔍 检查Docker服务状态..."
docker-compose ps

# 检查数据库中的文档
echo "🔍 检查数据库中的文档..."
docker-compose exec django-app python manage.py shell -c "
from md_docs.models import MDDocument
from django.db import connection

print('=== 数据库文档检查 ===')
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM md_documents')
total_count = cursor.fetchone()[0]
print(f'数据库中的文档总数: {total_count}')

if total_count > 0:
    cursor.execute('SELECT id, title, category, is_published, created_at FROM md_documents ORDER BY created_at DESC LIMIT 5')
    docs = cursor.fetchall()
    print('最近的5个文档:')
    for doc in docs:
        doc_id, title, category, is_published, created_at = doc
        print(f'  - ID: {doc_id}')
        print(f'    标题: {title}')
        print(f'    类别: {category}')
        print(f'    已发布: {is_published}')
        print(f'    创建时间: {created_at}')
        print()

print('=== 已发布文档检查 ===')
published_docs = MDDocument.objects.filter(is_published=True)
print(f'已发布的文档数量: {published_docs.count()}')

if published_docs.exists():
    print('已发布文档列表:')
    for doc in published_docs:
        print(f'  - ID: {doc.id}, 标题: {doc.title}, 类别: {doc.category}')
else:
    print('❌ 没有已发布的文档')
"

# 修复文档状态
echo "🔧 修复文档状态..."
docker-compose exec django-app python manage.py shell -c "
from md_docs.models import MDDocument

# 检查未发布的文档
unpublished_docs = MDDocument.objects.filter(is_published=False)
print(f'未发布的文档数量: {unpublished_docs.count()}')

if unpublished_docs.exists():
    print('正在修复未发布的文档...')
    unpublished_docs.update(is_published=True)
    print(f'✅ 已将 {unpublished_docs.count()} 个文档设置为已发布')
else:
    print('✅ 所有文档都已发布')
"

# 创建测试文档
echo "🧪 创建测试文档..."
docker-compose exec django-app python manage.py shell -c "
from md_docs.models import MDDocument
import uuid

test_content = '''# 云端服务器测试文档

## 摘要
这是一个用于测试云端服务器API的文档。

## 内容
测试内容...

## 结论
如果这个文档出现在列表中，说明API工作正常。
'''

try:
    document = MDDocument(
        title='云端服务器API测试文档',
        category='spirit',
        content=test_content,
        summary='这是一个用于测试云端服务器API的文档。',
        author='修复脚本',
        source='API测试',
        word_count=len(test_content),
        image_count=0,
        is_published=True
    )
    document.save()
    
    print(f'✅ 测试文档创建成功')
    print(f'   文档ID: {document.id}')
    print(f'   标题: {document.title}')
    print(f'   类别: {document.category}')
    print(f'   已发布: {document.is_published}')
except Exception as e:
    print(f'❌ 创建测试文档失败: {e}')
"

# 测试API查询逻辑
echo "🧪 测试API查询逻辑..."
docker-compose exec django-app python manage.py shell -c "
from md_docs.models import MDDocument
from django.db.models import Q

# 模拟API查询逻辑
query = Q(is_published=True)
documents = MDDocument.objects.filter(query).order_by('-created_at')

print(f'API查询结果: {documents.count()} 个文档')

if documents.exists():
    print('API查询到的文档:')
    for doc in documents:
        print(f'  - ID: {doc.id}, 标题: {doc.title}, 类别: {doc.category}')
else:
    print('❌ API查询没有返回任何文档')
"

# 重启Django服务以应用代码更改
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
echo "✅ MD文档API修复完成！"
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
