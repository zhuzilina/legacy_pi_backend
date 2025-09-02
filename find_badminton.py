#!/usr/bin/env python3
"""
查找羽毛球文章并检查图片
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from crawler.redis_models import RedisNewsArticle

def find_badminton_article():
    print("=== 查找羽毛球文章 ===")
    
    articles = RedisNewsArticle.filter(crawl_status='success')
    
    badminton_article = None
    for article in articles:
        if "羽毛球" in article.title or "世锦赛" in article.title or "国羽" in article.title:
            badminton_article = article
            break
    
    if badminton_article:
        print(f"找到羽毛球文章: {badminton_article.title}")
        print(f"文章ID: {badminton_article.id}")
        print(f"图片数量: {badminton_article.image_count}")
        print(f"图片映射: {len(badminton_article.image_mapping) if hasattr(badminton_article, 'image_mapping') and badminton_article.image_mapping else 0}")
        
        # 显示图片映射详情
        if hasattr(badminton_article, 'image_mapping') and badminton_article.image_mapping:
            print("\n图片映射详情:")
            for orig_url, mapping in badminton_article.image_mapping.items():
                print(f"  原链接: {orig_url}")
                print(f"  缓存ID: {mapping.get('image_id', 'None')}")
                print()
        
        # 显示部分内容
        print("\n文章内容（前500字符）:")
        print(badminton_article.markdown_content[:500] + "...")
        
        return badminton_article.id
    else:
        print("未找到羽毛球文章")
        print("所有文章标题:")
        for article in articles:
            print(f"  - {article.title}")
        return None

if __name__ == '__main__':
    find_badminton_article()
