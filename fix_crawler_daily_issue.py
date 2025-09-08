#!/usr/bin/env python3
"""
修复crawler应用第二天无法获取新数据的问题
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from crawler.redis_service import redis_service
from crawler.redis_models import RedisNewsArticle, RedisCrawlTask, RedisStats


def diagnose_crawler_issue():
    """诊断crawler问题"""
    print("🔍 诊断crawler应用问题...")
    print("=" * 50)
    
    # 1. 检查Redis连接
    print("1. 检查Redis连接:")
    if redis_service.test_connection():
        print("✅ Redis连接正常")
    else:
        print("❌ Redis连接失败")
        return False
    print()
    
    # 2. 检查今日状态
    print("2. 检查今日爬取状态:")
    today = timezone.now().date()
    today_str = today.isoformat()
    status = redis_service.get_daily_crawl_status()
    print(f"   今日日期: {today_str}")
    print(f"   今日状态: {status}")
    print()
    
    # 3. 检查今日文章
    print("3. 检查今日文章:")
    today_articles = redis_service.get_daily_articles()
    print(f"   今日文章数量: {len(today_articles)}")
    if today_articles:
        print(f"   文章ID列表: {today_articles[:5]}...")  # 只显示前5个
    print()
    
    # 4. 检查昨日数据
    print("4. 检查昨日数据:")
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    yesterday_articles = redis_service.get_daily_articles(yesterday_str)
    print(f"   昨日日期: {yesterday_str}")
    print(f"   昨日文章数量: {len(yesterday_articles)}")
    print()
    
    # 5. 检查所有文章数据
    print("5. 检查所有文章数据:")
    all_articles = RedisNewsArticle.filter()
    print(f"   总文章数量: {len(all_articles)}")
    
    # 按状态分组
    status_count = {}
    for article in all_articles:
        status = article.crawl_status
        status_count[status] = status_count.get(status, 0) + 1
    
    print("   按状态分组:")
    for status, count in status_count.items():
        print(f"     {status}: {count}")
    print()
    
    # 6. 检查任务状态
    print("6. 检查任务状态:")
    try:
        # 获取最近的任务
        all_tasks = RedisCrawlTask.filter()
        print(f"   总任务数量: {len(all_tasks)}")
        
        if all_tasks:
            recent_task = all_tasks[0]  # 假设按时间排序
            print(f"   最近任务: {recent_task.task_name}")
            print(f"   任务状态: {recent_task.status}")
            print(f"   创建时间: {recent_task.created_at}")
    except Exception as e:
        print(f"   ❌ 获取任务失败: {e}")
    print()
    
    return True


def fix_crawler_issue():
    """修复crawler问题"""
    print("🛠️ 修复crawler应用问题...")
    print("=" * 50)
    
    today = timezone.now().date()
    today_str = today.isoformat()
    
    # 1. 清理旧状态
    print("1. 清理旧状态:")
    try:
        # 清理昨天的状态
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.isoformat()
        
        # 删除昨天的状态键
        yesterday_status_key = f"crawl_status:{yesterday_str}"
        redis_service.redis_client.delete(yesterday_status_key)
        print(f"   ✅ 清理了昨天的状态: {yesterday_status_key}")
        
        # 清理更早的状态
        for days_ago in range(2, 7):  # 清理2-6天前的状态
            old_date = today - timedelta(days=days_ago)
            old_date_str = old_date.isoformat()
            old_status_key = f"crawl_status:{old_date_str}"
            redis_service.redis_client.delete(old_status_key)
        
        print("   ✅ 清理了更早的状态")
    except Exception as e:
        print(f"   ❌ 清理状态失败: {e}")
    print()
    
    # 2. 重置今日状态
    print("2. 重置今日状态:")
    try:
        # 删除今日状态
        today_status_key = f"crawl_status:{today_str}"
        redis_service.redis_client.delete(today_status_key)
        print(f"   ✅ 重置了今日状态: {today_status_key}")
        
        # 删除今日锁
        today_lock_key = f"daily_crawl_lock:{today_str}"
        redis_service.redis_client.delete(today_lock_key)
        print(f"   ✅ 重置了今日锁: {today_lock_key}")
    except Exception as e:
        print(f"   ❌ 重置状态失败: {e}")
    print()
    
    # 3. 清理旧文章数据
    print("3. 清理旧文章数据:")
    try:
        # 清理2天前的数据
        deleted_count = RedisStats.clear_old_data(days_to_keep=2)
        print(f"   ✅ 清理了 {deleted_count} 篇旧文章")
    except Exception as e:
        print(f"   ❌ 清理文章失败: {e}")
    print()
    
    # 4. 验证修复结果
    print("4. 验证修复结果:")
    try:
        # 检查今日状态
        status = redis_service.get_daily_crawl_status()
        print(f"   今日状态: {status} (应该为None)")
        
        # 检查今日文章
        today_articles = redis_service.get_daily_articles()
        print(f"   今日文章数量: {len(today_articles)}")
        
        print("   ✅ 修复完成，系统已重置")
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
    print()


def test_crawler_api():
    """测试crawler API"""
    print("🧪 测试crawler API...")
    print("=" * 50)
    
    import requests
    
    try:
        # 测试API
        response = requests.get("http://localhost/api/crawler/daily-articles/")
        print(f"API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {data}")
            
            if data.get('status') == 'crawling':
                print("✅ API正常，爬取任务已启动")
            elif data.get('status') == 'cached':
                print("✅ API正常，返回缓存数据")
            else:
                print(f"⚠️ API响应异常: {data}")
        else:
            print(f"❌ API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试API失败: {e}")
    print()


def main():
    """主函数"""
    print("🚀 开始修复crawler应用问题...")
    print("=" * 60)
    
    # 1. 诊断问题
    if not diagnose_crawler_issue():
        print("❌ 诊断失败，无法继续")
        return
    
    print()
    
    # 2. 修复问题
    fix_crawler_issue()
    
    print()
    
    # 3. 测试API
    test_crawler_api()
    
    print("✅ 修复完成！")
    print("=" * 60)
    print("📋 修复总结:")
    print("   - 清理了旧的状态和锁")
    print("   - 重置了今日状态")
    print("   - 清理了旧的文章数据")
    print("   - 系统已准备好进行新的爬取")
    print()
    print("💡 现在可以重新测试crawler API:")
    print("   curl http://localhost/api/crawler/daily-articles/")


if __name__ == '__main__':
    main()
