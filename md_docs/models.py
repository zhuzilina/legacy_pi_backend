from django.db import models
from django.utils import timezone
import uuid


class MDDocument(models.Model):
    """MD文档模型"""
    
    CATEGORY_CHOICES = [
        ('spirit', '精神'),
        ('person', '人物'),
        ('party_history', '党史'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='标题')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='类别')
    content = models.TextField(verbose_name='MD内容')
    summary = models.TextField(blank=True, null=True, verbose_name='摘要')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name='来源')
    publish_date = models.DateTimeField(blank=True, null=True, verbose_name='发布日期')
    word_count = models.IntegerField(default=0, verbose_name='字数')
    image_count = models.IntegerField(default=0, verbose_name='图片数量')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'md_documents'
        verbose_name = 'MD文档'
        verbose_name_plural = 'MD文档'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_published']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class MDImage(models.Model):
    """MD文档图片模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(MDDocument, on_delete=models.CASCADE, related_name='images', verbose_name='所属文档', null=True, blank=True)
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    stored_filename = models.CharField(max_length=255, verbose_name='存储文件名')
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    content_type = models.CharField(max_length=100, verbose_name='内容类型')
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='替代文本')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        db_table = 'md_images'
        verbose_name = 'MD图片'
        verbose_name_plural = 'MD图片'
        ordering = ['upload_time']
    
    def __str__(self):
        if self.document:
            return f"{self.document.title} - {self.original_filename}"
        else:
            return f"独立图片 - {self.original_filename}"


class MDCategory(models.Model):
    """MD文档分类模型"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='分类代码')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'md_categories'
        verbose_name = 'MD分类'
        verbose_name_plural = 'MD分类'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name