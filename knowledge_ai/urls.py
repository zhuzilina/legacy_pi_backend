"""
知识AI服务URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 题目详细解答API
    path('question/<int:question_id>/explanation/', 
         views.QuestionExplanationView.as_view(), 
         name='question_explanation'),
    
    # 开放性提问生成API
    path('open-question/generate/', 
         views.OpenQuestionGenerationView.as_view(), 
         name='open_question_generation'),
    
    # 回答相关度分析API
    path('answer/analyze/', 
         views.AnswerRelevanceAnalysisView.as_view(), 
         name='answer_relevance_analysis'),
    
    # 开放性问题列表API
    path('open-questions/', 
         views.OpenQuestionListView.as_view(), 
         name='open_question_list'),
    
    # 用户回答列表API
    path('user-answers/', 
         views.UserAnswerListView.as_view(), 
         name='user_answer_list'),
    
    # 健康检查API
    path('health/', 
         views.HealthCheckView.as_view(), 
         name='health_check'),
]
