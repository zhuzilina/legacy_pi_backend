from django.contrib import admin
from .models import Knowledge, ChoiceQuestion, FillQuestion, Answer, QuizSession, DailyQuestion
from .forms import ChoiceQuestionForm


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_category_display', 'source', 'created_at', 'updated_at']
    list_filter = ['category', 'source', 'created_at']
    search_fields = ['title', 'content', 'source']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'category', 'source', 'tags')
        }),
        ('内容', {
            'fields': ('content',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_display(self, obj):
        """显示分类的中文名称"""
        return obj.get_category_display()
    get_category_display.short_description = '分类'


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    form = ChoiceQuestionForm
    list_display = ['question_text', 'get_category_display', 'question_type', 'difficulty', 'created_at']
    list_filter = ['question_type', 'difficulty', 'category', 'created_at']
    search_fields = ['question_text', 'explanation', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('question_text', 'question_type', 'difficulty', 'category', 'tags')
        }),
        ('选项和答案', {
            'fields': ('options', 'explanation'),
            'description': '使用下方的选项管理工具来添加和管理选择题选项'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_display(self, obj):
        """显示分类的中文名称"""
        return obj.get_category_display()
    get_category_display.short_description = '分类'


@admin.register(FillQuestion)
class FillQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'get_category_display', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'category', 'created_at']
    search_fields = ['question_text', 'explanation', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('question_text', 'difficulty', 'category', 'tags')
        }),
        ('答案和解析', {
            'fields': ('correct_answer', 'explanation'),
            'description': '正确答案：多个答案用分号(;)分隔'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_display(self, obj):
        """显示分类的中文名称"""
        return obj.get_category_display()
    get_category_display.short_description = '分类'
    


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['get_question_text', 'answer_type', 'user_answer', 'is_correct', 'answered_at']
    list_filter = ['answer_type', 'is_correct', 'answered_at']
    search_fields = ['choice_question__question_text', 'fill_question__question_text', 'user_answer']
    readonly_fields = ['answered_at']
    fieldsets = (
        ('题目信息', {
            'fields': ('answer_type', 'choice_question', 'fill_question')
        }),
        ('答案信息', {
            'fields': ('user_answer', 'is_correct', 'answered_at')
        }),
    )
    
    def get_question_text(self, obj):
        """显示题目文本"""
        question = obj.get_question()
        if question:
            return question.question_text[:50] + "..." if len(question.question_text) > 50 else question.question_text
        return "无题目"
    get_question_text.short_description = '题目'


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'total_questions', 'correct_answers', 'score', 'started_at', 'completed_at']
    list_filter = ['started_at', 'completed_at']
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'started_at', 'completed_at']
    fieldsets = (
        ('会话信息', {
            'fields': ('session_id', 'total_questions', 'correct_answers', 'score')
        }),
        ('时间信息', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyQuestion)
class DailyQuestionAdmin(admin.ModelAdmin):
    list_display = ['client_ip', 'date', 'get_question_type_display', 'question_id', 'created_at']
    list_filter = ['question_type', 'date', 'created_at']
    search_fields = ['client_ip', 'question_id']
    readonly_fields = ['date', 'created_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('client_ip', 'date', 'question_type', 'question_id')
        }),
        ('题目数据', {
            'fields': ('question_data',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
