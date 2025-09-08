#!/usr/bin/env python3
"""
诊断crawler爬取问题
"""

import os
import sys
import django
import requests
import time
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from crawler.services import PeopleNetCrawler
from crawler.redis_service import redis_service
from crawler.redis_models import RedisNewsArticle, RedisCrawlTask


def test_network_connectivity():
    """测试网络连接"""
    print("🌐 测试网络连接...")
    print("=" * 50)
    
    test_urls = [
        "http://www.people.com.cn",
        "http://www.people.com.cn/GB/59476/",
        "http://www.people.com.cn/GB/",
    ]
    
    for url in test_urls:
        try:
            print(f"测试 {url}...")
            response = requests.get(url, timeout=10)
            print(f"   状态码: {response.status_code}")
            print(f"   内容长度: {len(response.text)}")
            print(f"   编码: {response.encoding}")
            
            if response.status_code == 200:
                print("   ✅ 连接成功")
            else:
                print(f"   ❌ 连接失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 连接异常: {e}")
        print()


def test_crawler_service():
    """测试爬虫服务"""
    print("🕷️ 测试爬虫服务...")
    print("=" * 50)
    
    try:
        crawler = PeopleNetCrawler()
        print("✅ 爬虫服务初始化成功")
        
        # 测试获取新闻链接
        print("测试获取新闻链接...")
        news_links = crawler._get_news_from_homepage()
        print(f"   首页获取结果: {len(news_links)} 条链接")
        
        if not news_links:
            print("   尝试直接页面获取...")
            news_links = crawler._get_news_from_direct_page()
            print(f"   直接页面获取结果: {len(news_links)} 条链接")
        
        if news_links:
            print("   ✅ 成功获取新闻链接")
            print(f"   前3条链接:")
            for i, link in enumerate(news_links[:3]):
                print(f"     {i+1}. {link.get('title', 'No title')[:50]}...")
        else:
            print("   ❌ 无法获取新闻链接")
            
    except Exception as e:
        print(f"❌ 爬虫服务测试失败: {e}")
    print()


def test_redis_connection():
    """测试Redis连接"""
    print("🔴 测试Redis连接...")
    print("=" * 50)
    
    try:
        if redis_service.test_connection():
            print("✅ Redis连接正常")
            
            # 测试基本操作
            test_key = "test_crawler_diagnosis"
            redis_service.redis_client.set(test_key, "test_value", ex=60)
            value = redis_service.redis_client.get(test_key)
            if value == "test_value":
                print("✅ Redis读写正常")
                redis_service.redis_client.delete(test_key)
            else:
                print("❌ Redis读写异常")
        else:
            print("❌ Redis连接失败")
            
    except Exception as e:
        print(f"❌ Redis测试失败: {e}")
    print()


def test_crawler_api():
    """测试爬虫API"""
    print("🔌 测试爬虫API...")
    print("=" * 50)
    
    base_url = "http://localhost"
    
    # 1. 测试重置API
    print("1. 测试重置API:")
    try:
        response = requests.post(f"{base_url}/api/crawler/reset/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data.get('message', 'No message')}")
            print("   ✅ 重置API正常")
        else:
            print(f"   ❌ 重置API失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 重置API异常: {e}")
    print()
    
    # 2. 测试每日文章API
    print("2. 测试每日文章API:")
    try:
        response = requests.get(f"{base_url}/api/crawler/daily/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   状态: {data.get('status', 'Unknown')}")
            print(f"   消息: {data.get('message', 'No message')}")
            
            if data.get('status') == 'crawling':
                print("   ✅ 爬取任务已启动")
                
                # 等待一段时间后检查结果
                print("   等待30秒后检查结果...")
                time.sleep(30)
                
                response2 = requests.get(f"{base_url}/api/crawler/daily/")
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"   第二次状态: {data2.get('status', 'Unknown')}")
                    print(f"   文章数量: {data2.get('total_articles', 0)}")
                    
                    if data2.get('status') == 'cached' and data2.get('total_articles', 0) > 0:
                        print("   ✅ 爬取成功，有数据返回")
                    elif data2.get('status') == 'crawling':
                        print("   ⏳ 爬取仍在进行中")
                    else:
                        print(f"   ⚠️ 爬取可能失败: {data2}")
                        
            elif data.get('status') == 'cached':
                print("   ✅ 返回缓存数据")
            else:
                print(f"   ⚠️ 未知状态: {data.get('status')}")
        else:
            print(f"   ❌ 每日文章API失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 每日文章API异常: {e}")
    print()


def test_article_crawling():
    """测试文章爬取"""
    print("📰 测试文章爬取...")
    print("=" * 50)
    
    try:
        crawler = PeopleNetCrawler()
        
        # 创建一个测试链接
        test_link = {
            'title': '测试文章',
            'url': 'http://www.people.com.cn/GB/59476/',
            'source': '人民网'
        }
        
        print("测试爬取文章详情...")
        article_data = crawler._crawl_article_detail(test_link)
        
        if article_data:
            print("   ✅ 文章爬取成功")
            print(f"   标题: {article_data.get('title', 'No title')}")
            print(f"   内容长度: {len(article_data.get('content', ''))}")
            print(f"   字数: {article_data.get('word_count', 0)}")
        else:
            print("   ❌ 文章爬取失败")
            
    except Exception as e:
        print(f"❌ 文章爬取测试失败: {e}")
    print()


def check_existing_data():
    """检查现有数据"""
    print("📊 检查现有数据...")
    print("=" * 50)
    
    try:
        # 检查文章数据
        articles = RedisNewsArticle.filter()
        print(f"总文章数量: {len(articles)}")
        
        if articles:
            # 按状态分组
            status_count = {}
            for article in articles:
                status = article.crawl_status
                status_count[status] = status_count.get(status, 0) + 1
            
            print("按状态分组:")
            for status, count in status_count.items():
                print(f"  {status}: {count}")
            
            # 显示最近的文章
            print("最近的文章:")
            for i, article in enumerate(articles[:3]):
                print(f"  {i+1}. {article.title[:50]}... ({article.crawl_status})")
        else:
            print("❌ 没有找到任何文章数据")
            
        # 检查任务数据
        tasks = RedisCrawlTask.filter()
        print(f"总任务数量: {len(tasks)}")
        
        if tasks:
            recent_task = tasks[0]
            print(f"最近任务: {recent_task.task_name}")
            print(f"任务状态: {recent_task.status}")
            print(f"创建时间: {recent_task.created_at}")
            
    except Exception as e:
        print(f"❌ 检查数据失败: {e}")
    print()


def main():
    """主函数"""
    print("🚀 开始诊断crawler爬取问题...")
    print("=" * 60)
    
    # 1. 测试网络连接
    test_network_connectivity()
    
    # 2. 测试Redis连接
    test_redis_connection()
    
    # 3. 测试爬虫服务
    test_crawler_service()
    
    # 4. 测试文章爬取
    test_article_crawling()
    
    # 5. 检查现有数据
    check_existing_data()
    
    # 6. 测试API
    test_crawler_api()
    
    print("✅ 诊断完成！")
    print("=" * 60)
    print("📋 诊断总结:")
    print("   - 如果网络连接失败，检查网络和防火墙设置")
    print("   - 如果Redis连接失败，检查Redis服务状态")
    print("   - 如果爬虫服务失败，检查目标网站是否可访问")
    print("   - 如果API测试失败，检查Django服务状态")
    print()
    print("💡 常见问题解决方案:")
    print("   1. 网络问题: 检查防火墙和代理设置")
    print("   2. Redis问题: 重启Redis服务")
    print("   3. 爬虫问题: 检查目标网站结构变化")
    print("   4. API问题: 重启Django服务")


if __name__ == '__main__':
    main()
