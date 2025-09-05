from django.contrib import admin
from .models import MDDocument, MDImage, MDCategory


@admin.register(MDDocument)
class MDDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'word_count', 'image_count', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'author', 'source']
    readonly_fields = ['id', 'created_at', 'updated_at', 'word_count', 'image_count']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'category', 'author', 'source', 'publish_date')
        }),
        ('内容', {
            'fields': ('content', 'summary')
        }),
        ('统计信息', {
            'fields': ('word_count', 'image_count'),
            'classes': ('collapse',)
        }),
        ('状态', {
            'fields': ('is_published',)
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MDImage)
class MDImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'document', 'file_size', 'content_type', 'upload_time']
    list_filter = ['content_type', 'upload_time']
    search_fields = ['original_filename', 'document__title']
    readonly_fields = ['id', 'upload_time']


@admin.register(MDCategory)
class MDCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']