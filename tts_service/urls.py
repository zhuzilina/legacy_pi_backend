from django.urls import path
from . import views

app_name = 'tts_service'

urlpatterns = [
    # 流式TTS API
    path('stream/', views.tts_stream_api, name='tts_stream'),
    
    # 文件式TTS API
    path('file/', views.tts_file_api, name='tts_file'),
    
    # 获取可用语音列表
    path('voices/', views.get_voices_api, name='get_voices'),
    
    # 获取TTS请求状态
    path('status/<int:request_id>/', views.get_tts_status_api, name='get_tts_status'),
    
    # 下载音频文件
    path('download/<int:request_id>/', views.download_audio_api, name='download_audio'),
    
    # 音频文件重定向（处理绝对路径访问）
    path('audio/<int:request_id>/', views.audio_redirect_api, name='audio_redirect'),
]
