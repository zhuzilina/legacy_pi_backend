#!/usr/bin/env python3
"""
云端服务器数据库详细检查脚本
用于检查MD文档数据库的具体问题
"""

import requests
import json
import sys
import time

def check_database_content(server_url):
    """检查数据库内容"""
    print("🔍 检查数据库内容...")
    
    try:
        # 检查文档列表API
        response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   文档列表API响应: {data}")
            
            # 检查是否有缓存问题
            if data.get('status') == 'cached':
                print("   ⚠️  API返回缓存状态，可能存在缓存问题")
            
            total_articles = data.get('total_articles', 0)
            article_ids = data.get('article_ids', [])
            
            print(f"   总文档数: {total_articles}")
            print(f"   文档ID列表: {article_ids}")
            
            return total_articles, article_ids
        else:
            print(f"❌ 文档列表API失败: {response.status_code}")
            return 0, []
    except Exception as e:
        print(f"❌ 检查数据库内容失败: {e}")
        return 0, []

def test_document_upload(server_url):
    """测试文档上传"""
    print("\n🧪 测试文档上传...")
    
    test_content = """# 云端服务器测试文档

## 摘要
这是一个用于测试云端服务器数据库的文档。

## 内容
测试内容...

## 结论
如果这个文档出现在列表中，说明数据库工作正常。
"""
    
    upload_data = {
        'title': '云端服务器数据库测试文档',
        'category': 'spirit',
        'content': test_content,
        'summary': '这是一个用于测试云端服务器数据库的文档。',
        'author': '测试脚本',
        'source': '数据库测试',
        'word_count': len(test_content),
        'image_count': 0,
        'is_published': True
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/md-docs/upload/",
            json=upload_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('document_id')
            print(f"✅ 测试文档上传成功")
            print(f"   文档ID: {doc_id}")
            print(f"   响应: {result}")
            
            # 等待一下让数据库同步
            time.sleep(3)
            
            # 再次检查文档列表
            print("\n🔍 上传后检查文档列表...")
            docs_response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                total_articles = docs_data.get('total_articles', 0)
                article_ids = docs_data.get('article_ids', [])
                
                print(f"   总文档数: {total_articles}")
                print(f"   文档ID列表: {article_ids}")
                
                if doc_id in article_ids:
                    print("✅ 文档已出现在列表中")
                    return True
                else:
                    print("❌ 文档未出现在列表中")
                    return False
            else:
                print(f"❌ 无法获取文档列表: {docs_response.status_code}")
                return False
        else:
            print(f"❌ 测试文档上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试上传失败: {e}")
        return False

def check_api_endpoints(server_url):
    """检查API端点"""
    print("\n🔍 检查API端点...")
    
    endpoints = [
        ("/api/md-docs/category/", "文档列表"),
        ("/api/md-docs/upload/", "文档上传"),
        ("/api/ai-chat/health/", "API健康检查"),
        ("/admin/login/", "管理后台"),
    ]
    
    for endpoint, description in endpoints:
        try:
            if endpoint == "/api/md-docs/upload/":
                # 上传端点需要POST请求，这里只检查是否可访问
                response = requests.options(f"{server_url}{endpoint}", timeout=5)
            else:
                response = requests.get(f"{server_url}{endpoint}", timeout=5)
            
            print(f"   {description}: {response.status_code}")
        except Exception as e:
            print(f"   {description}: 连接失败 - {e}")

def check_cache_issue(server_url):
    """检查缓存问题"""
    print("\n🔍 检查缓存问题...")
    
    try:
        # 多次请求文档列表，检查是否有缓存问题
        for i in range(3):
            response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   请求 {i+1}: 总文档数 {data.get('total_articles', 0)}, 状态 {data.get('status', 'unknown')}")
            time.sleep(1)
    except Exception as e:
        print(f"❌ 检查缓存问题失败: {e}")

def provide_solutions():
    """提供解决方案"""
    print("\n" + "=" * 60)
    print("🔧 云端服务器数据库问题解决方案")
    print("=" * 60)
    
    print("\n📋 可能的问题:")
    print("1. 数据库表存在但数据为空")
    print("2. API缓存问题")
    print("3. 数据库连接问题")
    print("4. 文档上传逻辑问题")
    
    print("\n🛠️ 解决方案:")
    print("1. 清除API缓存:")
    print("   docker-compose exec django-app python manage.py shell -c \"")
    print("   from django.core.cache import cache")
    print("   cache.clear()")
    print("   print('缓存已清除')")
    print("   \"")
    
    print("\n2. 检查数据库连接:")
    print("   docker-compose exec django-app python manage.py shell -c \"")
    print("   from django.db import connection")
    print("   cursor = connection.cursor()")
    print("   cursor.execute('SELECT COUNT(*) FROM md_documents')")
    print("   count = cursor.fetchone()[0]")
    print("   print(f'数据库中的文档数量: {count}')")
    print("   \"")
    
    print("\n3. 重启服务:")
    print("   docker-compose restart django-app")
    print("   docker-compose restart nginx")
    
    print("\n4. 检查日志:")
    print("   docker-compose logs django-app")
    print("   docker-compose logs nginx")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 check_cloud_database.py <服务器URL>")
        print("示例: python3 check_cloud_database.py http://121.36.87.174")
        sys.exit(1)
    
    server_url = sys.argv[1].rstrip('/')
    
    print("🔧 云端服务器数据库详细检查工具")
    print("=" * 50)
    
    # 检查数据库内容
    total_articles, article_ids = check_database_content(server_url)
    
    # 检查API端点
    check_api_endpoints(server_url)
    
    # 检查缓存问题
    check_cache_issue(server_url)
    
    # 测试文档上传
    upload_success = test_document_upload(server_url)
    
    # 提供解决方案
    if total_articles == 0 or not upload_success:
        provide_solutions()
    else:
        print("\n✅ 数据库状态正常，无需修复")

if __name__ == '__main__':
    main()
