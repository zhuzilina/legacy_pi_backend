#!/usr/bin/env python3
"""
完整修复crawler问题
"""

import os
import sys
import django
import requests
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from crawler.services import PeopleNetCrawler
from crawler.redis_service import redis_service
from crawler.redis_models import RedisNewsArticle, RedisCrawlTask


def test_redis_connection():
    """测试Redis连接"""
    print("🔴 测试Redis连接...")
    try:
        if redis_service.test_connection():
            print("✅ Redis连接正常")
            return True
        else:
            print("❌ Redis连接失败")
            return False
    except Exception as e:
        print(f"❌ Redis连接异常: {e}")
        return False


def test_crawler_functionality():
    """测试爬虫功能"""
    print("\n🕷️ 测试爬虫功能...")
    try:
        crawler = PeopleNetCrawler()
        
        # 测试获取新闻链接
        print("1. 测试获取新闻链接:")
        news_links = crawler._get_news_from_direct_page()
        print(f"   获取到 {len(news_links)} 条新闻链接")
        
        if news_links:
            # 测试爬取第一篇文章
            print("2. 测试爬取第一篇文章:")
            first_link = news_links[0]
            print(f"   标题: {first_link.get('title', 'No title')}")
            
            article_data = crawler._crawl_article_detail(first_link)
            if article_data:
                print("   ✅ 文章爬取成功")
                print(f"   内容长度: {len(article_data.get('content', ''))}")
                print(f"   字数: {article_data.get('word_count', 0)}")
                return True
            else:
                print("   ❌ 文章爬取失败")
                return False
        else:
            print("   ❌ 无法获取新闻链接")
            return False
            
    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        return False


def test_save_article():
    """测试保存文章"""
    print("\n💾 测试保存文章...")
    try:
        # 创建测试文章数据
        test_article = {
            'title': '测试文章标题',
            'content': '这是一篇测试文章的内容。' * 50,  # 生成足够长的内容
            'url': 'http://test.example.com',
            'source': '测试来源',
            'category': 'test',
            'word_count': 1000,
            'image_count': 0,
            'image_mapping': {}
        }
        
        # 保存文章
        article = RedisNewsArticle(**test_article)
        article.save()
        
        print("   ✅ 文章保存成功")
        
        # 验证保存
        saved_article = RedisNewsArticle.get(article.id)
        if saved_article:
            print("   ✅ 文章读取成功")
            return True
        else:
            print("   ❌ 文章读取失败")
            return False
            
    except Exception as e:
        print(f"❌ 保存文章测试失败: {e}")
        return False


def test_full_crawling():
    """测试完整爬取流程"""
    print("\n🚀 测试完整爬取流程...")
    try:
        crawler = PeopleNetCrawler()
        
        # 创建测试任务
        task = RedisCrawlTask.create(
            task_name='测试爬取任务',
            target_url='http://www.people.com.cn/GB/59476/',
            task_type='test'
        )
        
        print(f"   创建任务: {task.id}")
        
        # 执行爬取
        result = crawler.crawl_today_news(task_id=task.id)
        
        if result and result.get('success'):
            print("   ✅ 完整爬取成功")
            print(f"   成功: {result.get('success_count', 0)} 篇")
            print(f"   失败: {result.get('failed_count', 0)} 篇")
            return True
        else:
            print("   ❌ 完整爬取失败")
            return False
            
    except Exception as e:
        print(f"❌ 完整爬取测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始完整修复crawler问题...")
    print("=" * 60)
    
    # 1. 测试Redis连接
    redis_ok = test_redis_connection()
    
    # 2. 测试爬虫功能
    crawler_ok = test_crawler_functionality()
    
    # 3. 测试保存文章
    save_ok = test_save_article()
    
    # 4. 测试完整爬取流程
    if redis_ok and crawler_ok and save_ok:
        full_ok = test_full_crawling()
    else:
        full_ok = False
    
    print("\n✅ 修复测试完成！")
    print("=" * 60)
    print("📋 测试结果:")
    print(f"   Redis连接: {'✅' if redis_ok else '❌'}")
    print(f"   爬虫功能: {'✅' if crawler_ok else '❌'}")
    print(f"   保存文章: {'✅' if save_ok else '❌'}")
    print(f"   完整流程: {'✅' if full_ok else '❌'}")
    
    if all([redis_ok, crawler_ok, save_ok, full_ok]):
        print("\n🎉 所有测试通过！crawler已修复")
    else:
        print("\n⚠️ 部分测试失败，需要进一步修复")
        
        if not redis_ok:
            print("   - 检查Redis配置和连接")
        if not crawler_ok:
            print("   - 检查爬虫选择器和网页结构")
        if not save_ok:
            print("   - 检查Redis模型和保存逻辑")
        if not full_ok:
            print("   - 检查完整爬取流程")


if __name__ == '__main__':
    main()
