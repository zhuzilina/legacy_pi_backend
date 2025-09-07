"""
AI对话应用URL配置
"""

from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    # 主要对话API
    path('chat/', views.chat, name='chat'),
    
    # 图片对话API
    path('chat-with-images/', views.chat_with_images, name='chat_with_images'),
    
    # 图片上传API
    path('upload-image/', views.upload_image, name='upload_image'),
    path('upload-images-batch/', views.upload_images_batch, name='upload_images_batch'),
    
    # 流式对话API
    path('stream/', views.stream_chat, name='stream_chat'),
    path('stream-with-images/', views.stream_chat_with_images, name='stream_chat_with_images'),
    
    # 获取系统提示词类型
    path('prompts/', views.get_system_prompts, name='get_system_prompts'),
    
    # 获取图片理解提示词类型
    path('image-prompts/', views.get_image_prompts, name='get_image_prompts'),
    
    # 获取图片缓存统计
    path('image-cache-stats/', views.get_image_cache_stats, name='get_image_cache_stats'),
    
    # 健康检查API
    path('health/', views.health_check, name='health_check'),
    
    # 获取对话配置
    path('config/', views.get_chat_config, name='get_chat_config'),
    
    # 基于类的视图（支持GET和POST）
    path('', views.ChatView.as_view(), name='chat_view'),
]
