from django.urls import path
from . import views

urlpatterns = [
    # 知识相关API
    path('knowledge/', views.get_knowledge_list, name='knowledge_list'),
    path('knowledge/<int:knowledge_id>/', views.get_knowledge_detail, name='knowledge_detail'),
    
    # 每日一题API
    path('daily-question/', views.get_daily_question, name='daily_question'),
]
