from django.db import models
from django.utils import timezone
from knowledge_quiz.models import Knowledge, Question


class OpenQuestion(models.Model):
    """AI生成的开放性提问模型"""
    knowledge = models.ForeignKey(
        Knowledge, 
        on_delete=models.CASCADE, 
        related_name='open_questions',
        verbose_name='关联知识'
    )
    question_text = models.TextField(verbose_name='问题内容')
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('comprehension', '理解型'),
            ('application', '应用型'),
            ('analysis', '分析型'),
            ('evaluation', '评价型'),
            ('creation', '创造型'),
        ],
        default='comprehension',
        verbose_name='问题类型'
    )
    difficulty_level = models.CharField(
        max_length=10,
        choices=[
            ('easy', '简单'),
            ('medium', '中等'),
            ('hard', '困难'),
        ],
        default='medium',
        verbose_name='难度等级'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '开放性提问'
        verbose_name_plural = '开放性提问'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.knowledge.title[:30]}... - {self.question_text[:50]}..."


class UserAnswer(models.Model):
    """用户对开放性问题的回答模型"""
    open_question = models.ForeignKey(
        OpenQuestion,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='关联问题'
    )
    user_answer = models.TextField(verbose_name='用户回答')
    relevance_score = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name='相关度评分',
        help_text='0-100分，表示回答与知识点的相关度'
    )
    feedback_text = models.TextField(
        blank=True,
        verbose_name='反馈文本',
        help_text='AI生成的详细反馈'
    )
    analysis_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='分析元数据',
        help_text='存储分析过程中的额外信息'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='回答时间')
    
    class Meta:
        verbose_name = '用户回答'
        verbose_name_plural = '用户回答'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.open_question.question_text[:30]}... - 评分: {self.relevance_score}"


class QuestionAnalysis(models.Model):
    """题目AI分析记录模型"""
    ANALYSIS_TYPE_CHOICES = [
        ('choice_explanation', '选择题详细解答'),
        ('fill_explanation', '填空题详细解答'),
        ('open_question_generation', '开放性提问生成'),
        ('answer_relevance_analysis', '回答相关度分析'),
    ]
    
    # 关联题目
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='ai_analyses',
        verbose_name='题目'
    )
    open_question = models.ForeignKey(
        OpenQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_analyses',
        verbose_name='开放性问题'
    )
    
    analysis_type = models.CharField(
        max_length=30,
        choices=ANALYSIS_TYPE_CHOICES,
        verbose_name='分析类型'
    )
    analysis_content = models.TextField(verbose_name='分析内容')
    ai_model_used = models.CharField(max_length=100, verbose_name='使用的AI模型')
    tokens_used = models.IntegerField(null=True, blank=True, verbose_name='使用的Token数')
    processing_time = models.FloatField(null=True, blank=True, verbose_name='处理时间(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '题目AI分析'
        verbose_name_plural = '题目AI分析'
        ordering = ['-created_at']
    
    def __str__(self):
        question_info = ""
        if self.question:
            question_info = f"题目{self.question.id}"
        elif self.open_question:
            question_info = f"开放性问题{self.open_question.id}"
        
        return f"{question_info} - {self.get_analysis_type_display()}"
    
    def get_question(self):
        """获取关联的题目对象"""
        if self.question:
            return self.question
        elif self.open_question:
            return self.open_question
        return None
