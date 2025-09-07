from django.db import models
from django.utils import timezone
import uuid


class Knowledge(models.Model):
    """知识库模型"""
    CATEGORY_CHOICES = [
        ('marxism_leninism', '马克思列宁主义'),
        ('mao_zedong_thought', '毛泽东思想'),
        ('deng_xiaoping_theory', '邓小平理论'),
        ('three_represents', '"三个代表"重要思想'),
        ('scientific_development', '科学发展观'),
        ('xi_jinping_thought', '习近平新时代中国特色社会主义思想'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='marxism_leninism', verbose_name='分类')
    source = models.CharField(max_length=100, default='共产党员网', verbose_name='数据来源', help_text='知识条目的来源网站或机构')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签', help_text='用逗号分隔多个标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '知识条目'
        verbose_name_plural = '知识条目'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class Question(models.Model):
    """统一题目模型"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    CATEGORY_CHOICES = [
        ('party_history', '党史'),
        ('theory', '理论'),
    ]
    
    QUESTION_TYPE_CHOICES = [
        ('choice_single', '单选题'),
        ('choice_multiple', '多选题'),
        ('fill', '填空题'),
    ]
    
    question_text = models.TextField(verbose_name='题目内容')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='题目类型')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='难度')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='party_history', verbose_name='分类')
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签', help_text='用逗号分隔多个标签')
    
    # 选择题特有字段
    options = models.JSONField(default=list, null=True, blank=True, verbose_name='选项', 
                              help_text='选择题的选项列表，格式：[{"text": "选项内容", "is_correct": true}]')
    
    # 填空题特有字段
    correct_answer = models.TextField(null=True, blank=True, verbose_name='正确答案', 
                                     help_text='填空题的正确答案，多个答案用分号分隔')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def get_category_display(self):
        """获取分类的中文显示"""
        for choice in self.CATEGORY_CHOICES:
            if choice[0] == self.category:
                return choice[1]
        return self.category
    
    def is_choice_question(self):
        """判断是否为选择题"""
        return self.question_type in ['choice_single', 'choice_multiple']
    
    def is_fill_question(self):
        """判断是否为填空题"""
        return self.question_type == 'fill'
    
    def get_options_display(self):
        """获取格式化的选项显示（仅选择题）"""
        if not self.is_choice_question() or not self.options:
            return []
        return self.options
    
    def get_correct_options(self):
        """获取正确答案选项（仅选择题）"""
        if not self.is_choice_question() or not self.options:
            return []
        return [opt for opt in self.options if opt.get('is_correct', False)]
    
    def get_correct_answer_text(self):
        """获取正确答案的文本表示"""
        if self.is_choice_question():
            correct_options = self.get_correct_options()
            if self.question_type == 'choice_single':
                return correct_options[0]['text'] if correct_options else ''
            else:  # choice_multiple
                return ', '.join([opt['text'] for opt in correct_options])
        elif self.is_fill_question():
            return self.correct_answer
        return ''
    
    def get_correct_answers_list(self):
        """获取正确答案列表（仅填空题）"""
        if not self.is_fill_question() or not self.correct_answer:
            return []
        return [answer.strip() for answer in self.correct_answer.split(';') if answer.strip()]
    
    def check_answer(self, user_answer):
        """检查用户答案是否正确"""
        if self.is_fill_question():
            correct_answers = self.get_correct_answers_list()
            user_answer = user_answer.strip()
            return user_answer in correct_answers
        # 选择题的答案检查逻辑可以在这里添加
        return False


class BaseQuestion(models.Model):
    """题目基类模型（已废弃，保留用于向后兼容）"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    CATEGORY_CHOICES = [
        ('party_history', '党史'),
        ('theory', '理论'),
    ]
    
    question_text = models.TextField(verbose_name='题目内容')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='难度')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='party_history', verbose_name='分类')
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签', help_text='用逗号分隔多个标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        abstract = True
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def get_category_display(self):
        """获取分类的中文显示"""
        for choice in self.CATEGORY_CHOICES:
            if choice[0] == self.category:
                return choice[1]
        return self.category


# 旧的ChoiceQuestion和FillQuestion模型已被统一的Question模型替代
# 保留BaseQuestion类用于向后兼容，但不再使用


class Answer(models.Model):
    """答题记录模型"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='题目')
    user_answer = models.TextField(verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='答题时间')
    
    class Meta:
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        ordering = ['-answered_at']
    
    def __str__(self):
        question_text = self.question.question_text[:30] if self.question else "未知题目"
        return f"{question_text}... - {'正确' if self.is_correct else '错误'}"
    
    def get_question(self):
        """获取关联的题目对象"""
        return self.question
    
    def get_question_type(self):
        """获取题目类型"""
        if self.question:
            if self.question.is_choice_question():
                return 'choice'
            elif self.question.is_fill_question():
                return 'fill'
        return 'unknown'


class QuizSession(models.Model):
    """答题会话模型"""
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='会话ID')
    total_questions = models.IntegerField(default=0, verbose_name='总题数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确题数')
    score = models.FloatField(default=0.0, verbose_name='得分')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '答题会话'
        verbose_name_plural = '答题会话'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"会话 {self.session_id} - 得分: {self.score}"
    
    def calculate_score(self):
        """计算得分"""
        if self.total_questions > 0:
            self.score = (self.correct_answers / self.total_questions) * 100
        else:
            self.score = 0.0
        return self.score
    
    def complete_session(self):
        """完成会话"""
        self.completed_at = timezone.now()
        self.calculate_score()
        self.save()


class DailyQuestion(models.Model):
    """每日一题记录模型"""
    client_ip = models.GenericIPAddressField(verbose_name='客户端IP')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    question_data = models.JSONField(verbose_name='题目数据', help_text='包含题目、选项和正确答案的完整数据')
    date = models.DateField(auto_now_add=True, verbose_name='日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '每日一题记录'
        verbose_name_plural = '每日一题记录'
        ordering = ['-created_at']
        unique_together = ['client_ip', 'date']  # 每个IP每天只能有一条记录
    
    def __str__(self):
        return f"{self.client_ip} - {self.date} - {self.question.get_question_type_display()}"
    
    def get_question_type(self):
        """获取题目类型"""
        if self.question.is_choice_question():
            return 'choice'
        elif self.question.is_fill_question():
            return 'fill'
        return 'unknown'
