from django.contrib import admin
from .models import TTSRequest


@admin.register(TTSRequest)
class TTSRequestAdmin(admin.ModelAdmin):
    """TTS请求管理"""
    
    list_display = [
        'id', 'text_preview', 'voice', 'language', 'status', 
        'created_at', 'completed_at', 'duration'
    ]
    
    list_filter = [
        'status', 'voice', 'language', 'created_at', 'completed_at'
    ]
    
    search_fields = ['text', 'voice', 'language']
    
    readonly_fields = [
        'id', 'created_at', 'completed_at', 'audio_file', 
        'duration', 'error_message'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'text', 'voice', 'language', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'completed_at')
        }),
        ('结果信息', {
            'fields': ('audio_file', 'duration', 'error_message')
        }),
    )
    
    def text_preview(self, obj):
        """文本预览"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '文本预览'
    
    def has_add_permission(self, request):
        """禁止手动添加"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许查看"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """允许删除"""
        return True


