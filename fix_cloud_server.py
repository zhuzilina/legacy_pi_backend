#!/usr/bin/env python3
"""
云端服务器修复脚本
用于修复云端服务器的数据库迁移问题
"""

import requests
import json
import sys
import time

def check_database_tables(server_url):
    """检查数据库表状态"""
    print("🔍 检查数据库表状态...")
    
    # 这里我们无法直接访问数据库，但可以通过API行为推断
    # 如果上传成功但文档不出现，很可能是数据库表不存在
    
    try:
        # 尝试获取文档列表
        response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total_articles', 0)
            print(f"   当前文档总数: {total_articles}")
            
            if total_articles == 0:
                print("❌ 数据库表可能不存在或为空")
                return False
            else:
                print("✅ 数据库表存在且有数据")
                return True
        else:
            print(f"❌ 无法获取文档列表: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查数据库表失败: {e}")
        return False

def test_upload_and_verify(server_url):
    """测试上传并验证"""
    print("🧪 测试上传并验证...")
    
    test_content = """# 数据库修复测试文档

## 摘要
这是一个用于测试数据库修复的文档。

## 内容
测试内容...

## 结论
如果这个文档出现在列表中，说明数据库修复成功。
"""
    
    upload_data = {
        'title': '数据库修复测试文档',
        'category': 'spirit',
        'content': test_content,
        'summary': '这是一个用于测试数据库修复的文档。',
        'author': '修复脚本',
        'source': '数据库修复测试',
        'word_count': len(test_content),
        'image_count': 0,
        'is_published': True
    }
    
    try:
        # 上传文档
        response = requests.post(
            f"{server_url}/api/md-docs/upload/",
            json=upload_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('document_id')
            print(f"✅ 测试文档上传成功，ID: {doc_id}")
            
            # 等待一下让数据库同步
            time.sleep(2)
            
            # 检查文档是否出现在列表中
            docs_response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                total_articles = docs_data.get('total_articles', 0)
                article_ids = docs_data.get('article_ids', [])
                
                print(f"   当前文档总数: {total_articles}")
                
                if doc_id in article_ids:
                    print("✅ 文档已出现在列表中，数据库正常")
                    return True
                else:
                    print("❌ 文档未出现在列表中，数据库有问题")
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

def provide_solution():
    """提供解决方案"""
    print("\n" + "=" * 60)
    print("🔧 云端服务器数据库修复方案")
    print("=" * 60)
    
    print("\n📋 问题诊断:")
    print("   云端服务器的数据库迁移没有应用，导致md_documents表不存在")
    print("   文档上传成功但无法保存到数据库，因此不会出现在列表中")
    
    print("\n🛠️ 解决方案:")
    print("   需要在云端服务器上执行以下命令:")
    print("")
    print("   1. 连接到云端服务器")
    print("   2. 进入项目目录")
    print("   3. 执行数据库迁移:")
    print("      docker-compose exec django-app python manage.py migrate")
    print("")
    print("   4. 验证数据库表:")
    print("      docker-compose exec django-app python manage.py shell -c \"")
    print("      from django.db import connection")
    print("      cursor = connection.cursor()")
    print("      cursor.execute(\\\"SELECT name FROM sqlite_master WHERE type='table' AND name='md_documents'\\\")")
    print("      result = cursor.fetchone()")
    print("      print('md_documents table exists:', result is not None)")
    print("      \"")
    print("")
    print("   5. 重新测试上传功能")
    
    print("\n🚀 快速修复脚本:")
    print("   可以在云端服务器上运行以下脚本:")
    print("")
    print("   #!/bin/bash")
    print("   echo '🔧 修复云端服务器数据库...'")
    print("   docker-compose exec django-app python manage.py migrate")
    print("   echo '✅ 数据库迁移完成'")
    print("   echo '🧪 测试文档上传...'")
    print("   # 这里可以添加测试上传的代码")
    
    print("\n📞 联系信息:")
    print("   如果需要帮助，请提供云端服务器的访问信息")
    print("   或者将修复脚本发送给服务器管理员执行")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 fix_cloud_server.py <服务器URL>")
        print("示例: python3 fix_cloud_server.py http://121.36.87.174")
        sys.exit(1)
    
    server_url = sys.argv[1].rstrip('/')
    
    print("🔧 云端服务器修复工具")
    print("=" * 50)
    
    # 检查数据库表状态
    tables_ok = check_database_tables(server_url)
    
    if not tables_ok:
        # 测试上传并验证
        upload_ok = test_upload_and_verify(server_url)
        
        if not upload_ok:
            # 提供解决方案
            provide_solution()
        else:
            print("✅ 数据库状态正常，无需修复")
    else:
        print("✅ 数据库状态正常，无需修复")

if __name__ == '__main__':
    main()
