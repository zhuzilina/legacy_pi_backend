from django.db import models
from django.utils import timezone


class TTSRequest(models.Model):
    """TTS请求记录模型"""
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    text = models.TextField('输入文本', max_length=5000)
    voice = models.CharField('语音类型', max_length=50, default='zh-CN-XiaoxiaoNeural')
    language = models.CharField('语言', max_length=10, default='zh-CN')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    audio_file = models.CharField('音频文件路径', max_length=255, blank=True, null=True)
    duration = models.FloatField('音频时长(秒)', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    class Meta:
        db_table = 'tts_request'
        verbose_name = 'TTS请求'
        verbose_name_plural = 'TTS请求'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.text[:50]}... ({self.status})"
    
    def mark_completed(self, audio_file=None, duration=None):
        """标记为完成"""
        self.status = 'completed'
        self.audio_file = audio_file
        self.duration = duration
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """标记为失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()


