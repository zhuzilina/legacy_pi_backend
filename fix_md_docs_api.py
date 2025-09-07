#!/usr/bin/env python3
"""
修复MD文档API问题
解决文档上传后无法在列表中显示的问题
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from md_docs.models import MDDocument
from django.db import connection

def check_database_documents():
    """检查数据库中的文档"""
    print("🔍 检查数据库中的文档...")
    
    # 使用原始SQL查询
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, category, is_published, created_at FROM md_documents ORDER BY created_at DESC")
    documents = cursor.fetchall()
    
    print(f"   数据库中的文档总数: {len(documents)}")
    
    if documents:
        print("   文档列表:")
        for doc in documents:
            doc_id, title, category, is_published, created_at = doc
            print(f"     - ID: {doc_id}")
            print(f"       标题: {title}")
            print(f"       类别: {category}")
            print(f"       已发布: {is_published}")
            print(f"       创建时间: {created_at}")
            print()
    else:
        print("   ❌ 数据库中没有文档")
    
    return documents

def check_published_documents():
    """检查已发布的文档"""
    print("🔍 检查已发布的文档...")
    
    # 使用Django ORM查询
    published_docs = MDDocument.objects.filter(is_published=True)
    print(f"   已发布的文档数量: {published_docs.count()}")
    
    if published_docs.exists():
        print("   已发布文档列表:")
        for doc in published_docs:
            print(f"     - ID: {doc.id}")
            print(f"       标题: {doc.title}")
            print(f"       类别: {doc.category}")
            print(f"       创建时间: {doc.created_at}")
            print()
    else:
        print("   ❌ 没有已发布的文档")
    
    return published_docs

def fix_document_status():
    """修复文档状态"""
    print("🔧 修复文档状态...")
    
    # 检查所有文档的is_published状态
    all_docs = MDDocument.objects.all()
    unpublished_docs = all_docs.filter(is_published=False)
    
    print(f"   总文档数: {all_docs.count()}")
    print(f"   未发布文档数: {unpublished_docs.count()}")
    
    if unpublished_docs.exists():
        print("   发现未发布的文档，正在修复...")
        unpublished_docs.update(is_published=True)
        print(f"   ✅ 已将 {unpublished_docs.count()} 个文档设置为已发布")
    else:
        print("   ✅ 所有文档都已发布")

def test_api_query():
    """测试API查询逻辑"""
    print("🧪 测试API查询逻辑...")
    
    # 模拟API查询逻辑
    from django.db.models import Q
    
    # 构建查询（与API中的逻辑相同）
    query = Q(is_published=True)
    documents = MDDocument.objects.filter(query).order_by('-created_at')
    
    print(f"   API查询结果: {documents.count()} 个文档")
    
    if documents.exists():
        print("   API查询到的文档:")
        for doc in documents:
            print(f"     - ID: {doc.id}, 标题: {doc.title}, 类别: {doc.category}")
    else:
        print("   ❌ API查询没有返回任何文档")

def create_test_document():
    """创建测试文档"""
    print("🧪 创建测试文档...")
    
    test_content = """# 测试文档

## 摘要
这是一个用于测试API的文档。

## 内容
测试内容...

## 结论
测试完成。
"""
    
    try:
        document = MDDocument(
            title='API测试文档',
            category='spirit',
            content=test_content,
            summary='这是一个用于测试API的文档。',
            author='测试脚本',
            source='API测试',
            word_count=len(test_content),
            image_count=0,
            is_published=True
        )
        document.save()
        
        print(f"   ✅ 测试文档创建成功")
        print(f"   文档ID: {document.id}")
        print(f"   标题: {document.title}")
        print(f"   类别: {document.category}")
        print(f"   已发布: {document.is_published}")
        
        return document
    except Exception as e:
        print(f"   ❌ 创建测试文档失败: {e}")
        return None

def main():
    """主函数"""
    print("🔧 MD文档API问题修复工具")
    print("=" * 50)
    
    # 检查数据库中的文档
    documents = check_database_documents()
    
    # 检查已发布的文档
    published_docs = check_published_documents()
    
    # 修复文档状态
    fix_document_status()
    
    # 测试API查询逻辑
    test_api_query()
    
    # 创建测试文档
    test_doc = create_test_document()
    
    print("\n" + "=" * 50)
    print("🎯 修复建议:")
    
    if not documents:
        print("1. 数据库中没有文档，需要重新上传文档")
    elif not published_docs.exists():
        print("1. 所有文档都未发布，已自动修复")
    else:
        print("1. 文档状态正常")
    
    print("2. 检查API代码中的硬编码缓存状态")
    print("3. 确保文档上传后正确设置is_published=True")
    print("4. 测试文档列表API是否正常工作")
    
    if test_doc:
        print(f"\n✅ 测试文档已创建，ID: {test_doc.id}")
        print("   现在可以测试API是否正常工作")

if __name__ == '__main__':
    main()
