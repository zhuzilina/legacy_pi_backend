from django.contrib import admin
from .models import OpenQuestion, UserAnswer, QuestionAnalysis

@admin.register(OpenQuestion)
class OpenQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'knowledge', 'question_text', 'created_at']
    list_filter = ['created_at', 'knowledge__category']
    search_fields = ['question_text', 'knowledge__title']
    readonly_fields = ['created_at']

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'open_question', 'user_answer', 'relevance_score', 'created_at']
    list_filter = ['created_at', 'relevance_score']
    search_fields = ['user_answer', 'open_question__question_text']
    readonly_fields = ['created_at', 'relevance_score', 'feedback_text']

@admin.register(QuestionAnalysis)
class QuestionAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_question_info', 'analysis_type', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['analysis_content']
    readonly_fields = ['created_at']
    
    def get_question_info(self, obj):
        """获取题目信息"""
        if obj.question:
            return f"题目{obj.question.id}"
        elif obj.open_question:
            return f"开放性问题{obj.open_question.id}"
        return "未知"
    get_question_info.short_description = '题目信息'
