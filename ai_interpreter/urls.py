"""
AI解读应用URL配置
"""

from django.urls import path
from . import views

app_name = 'ai_interpreter'

urlpatterns = [
    # 主要解读API
    path('interpret/', views.interpret_text, name='interpret_text'),
    
    # 批量解读API
    path('batch/', views.batch_interpret, name='batch_interpret'),
    
    # 健康检查API
    path('health/', views.health_check, name='health_check'),
    
    # 获取提示词类型
    path('prompts/', views.get_prompts, name='get_prompts'),
    
    # 基于类的视图（支持GET和POST）
    path('', views.InterpretView.as_view(), name='interpret_view'),
]
