#!/usr/bin/env python3
"""
云端服务器诊断脚本
用于检查云端服务器的数据库状态和API功能
"""

import requests
import json
import sys

def check_server_status(server_url):
    """检查服务器状态"""
    print(f"🔍 检查服务器状态: {server_url}")
    
    try:
        # 检查API健康状态
        health_response = requests.get(f"{server_url}/api/ai-chat/health/", timeout=10)
        if health_response.status_code == 200:
            print("✅ API服务正常")
            health_data = health_response.json()
            print(f"   模型: {health_data.get('data', {}).get('model', 'N/A')}")
        else:
            print(f"❌ API服务异常: {health_response.status_code}")
    except Exception as e:
        print(f"❌ API服务连接失败: {e}")
    
    try:
        # 检查文档列表
        docs_response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            print(f"📄 文档列表: {docs_data.get('total_articles', 0)} 个文档")
            article_ids = docs_data.get('article_ids', [])
            if article_ids:
                print(f"   文档ID: {article_ids[:3]}{'...' if len(article_ids) > 3 else ''}")
            else:
                print("   没有文档")
        else:
            print(f"❌ 文档列表获取失败: {docs_response.status_code}")
    except Exception as e:
        print(f"❌ 文档列表连接失败: {e}")
    
    try:
        # 检查特定文档
        test_doc_id = "107eb2b4-e86b-48d1-b68c-4b5c77663153"
        doc_response = requests.get(f"{server_url}/api/md-docs/document/{test_doc_id}/", timeout=10)
        if doc_response.status_code == 200:
            print(f"✅ 测试文档可访问: {test_doc_id}")
            content = doc_response.text[:100] + "..." if len(doc_response.text) > 100 else doc_response.text
            print(f"   内容预览: {content}")
        else:
            print(f"❌ 测试文档不可访问: {doc_response.status_code}")
    except Exception as e:
        print(f"❌ 测试文档连接失败: {e}")
    
    try:
        # 检查管理后台
        admin_response = requests.get(f"{server_url}/admin/login/", timeout=10)
        if admin_response.status_code == 200:
            print("✅ 管理后台可访问")
            if "Django 站点管理员" in admin_response.text:
                print("   中文化界面正常")
            else:
                print("   中文化界面可能有问题")
        else:
            print(f"❌ 管理后台不可访问: {admin_response.status_code}")
    except Exception as e:
        print(f"❌ 管理后台连接失败: {e}")

def test_upload(server_url):
    """测试上传功能"""
    print(f"\n🧪 测试上传功能: {server_url}")
    
    # 创建测试文档
    test_content = """# 测试文档

## 摘要
这是一个用于测试云端服务器上传功能的文档。

## 内容
测试内容...

## 结论
测试完成。
"""
    
    upload_data = {
        'title': '云端服务器测试文档',
        'category': 'spirit',
        'content': test_content,
        'summary': '这是一个用于测试云端服务器上传功能的文档。',
        'author': '测试用户',
        'source': '测试来源',
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
            print("✅ 测试文档上传成功")
            print(f"   文档ID: {result.get('document_id')}")
            
            # 验证文档是否在列表中
            docs_response = requests.get(f"{server_url}/api/md-docs/category/", timeout=10)
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                total_articles = docs_data.get('total_articles', 0)
                print(f"   当前文档总数: {total_articles}")
                
                if total_articles > 0:
                    print("✅ 文档已出现在列表中")
                else:
                    print("❌ 文档未出现在列表中")
        else:
            print(f"❌ 测试文档上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 测试上传失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 diagnose_cloud_server.py <服务器URL>")
        print("示例: python3 diagnose_cloud_server.py http://121.36.87.174")
        sys.exit(1)
    
    server_url = sys.argv[1].rstrip('/')
    
    print("🔧 云端服务器诊断工具")
    print("=" * 50)
    
    # 检查服务器状态
    check_server_status(server_url)
    
    # 测试上传功能
    test_upload(server_url)
    
    print("\n" + "=" * 50)
    print("🎯 诊断建议:")
    print("1. 如果API服务正常但文档列表为空，可能是数据库迁移问题")
    print("2. 如果上传成功但文档不出现，可能是数据库同步问题")
    print("3. 如果管理后台不可访问，可能是静态文件或权限问题")
    print("4. 建议在云端服务器上运行数据库迁移命令")

if __name__ == '__main__':
    main()
