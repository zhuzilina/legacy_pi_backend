from django.apps import AppConfig


class TtsServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tts_service'
    verbose_name = 'TTS文本转语音服务'


