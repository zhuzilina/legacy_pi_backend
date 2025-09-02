#!/usr/bin/env python3
"""
检查所有文章的图片情况
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from crawler.redis_models import RedisNewsArticle

def check_all_images():
    print("=== 检查所有文章图片情况 ===")
    
    articles = RedisNewsArticle.filter(crawl_status='success')
    
    total_articles = len(articles)
    articles_with_images = 0
    total_images = 0
    
    print(f"总文章数: {total_articles}\n")
    
    for i, article in enumerate(articles, 1):
        image_count = article.image_count
        image_mapping_count = len(article.image_mapping) if hasattr(article, 'image_mapping') and article.image_mapping else 0
        
        print(f"{i:2d}. {article.title[:50]}")
        print(f"    ID: {article.id}")
        print(f"    图片数量: {image_count}")
        print(f"    图片映射: {image_mapping_count}")
        
        if image_count > 0 or image_mapping_count > 0:
            articles_with_images += 1
            total_images += max(image_count, image_mapping_count)
            
            # 显示图片映射详情
            if hasattr(article, 'image_mapping') and article.image_mapping:
                print("    图片详情:")
                for orig_url, mapping in list(article.image_mapping.items())[:2]:  # 只显示前2个
                    print(f"      原链接: {orig_url[:80]}...")
                    print(f"      缓存ID: {mapping.get('image_id', 'None')}")
            
            # 检查markdown中是否包含图片
            if hasattr(article, 'markdown_content') and article.markdown_content:
                api_image_count = article.markdown_content.count('/api/crawler/image/')
                print(f"    Markdown中图片: {api_image_count}")
        
        print()
    
    print(f"=== 统计结果 ===")
    print(f"总文章数: {total_articles}")
    print(f"包含图片的文章: {articles_with_images}")
    print(f"总图片数: {total_images}")
    print(f"图片覆盖率: {articles_with_images/total_articles*100:.1f}%")

if __name__ == '__main__':
    check_all_images()
