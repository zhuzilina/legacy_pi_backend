from django.urls import path
from . import views

app_name = 'crawler'

urlpatterns = [
    # 核心API：获取每日文章ID列表（被动触发爬取）
    path('daily/', views.get_daily_articles, name='daily_articles'),
    
    # 核心API：根据文章ID获取Markdown内容
    path('article/<str:article_id>/', views.get_article_markdown, name='article_markdown'),
    
    # 辅助API：获取爬取状态
    path('status/', views.get_crawl_status, name='crawl_status'),
    
    # 图片API：获取缓存的图片
    path('image/<str:image_id>/', views.get_cached_image, name='cached_image'),
]
