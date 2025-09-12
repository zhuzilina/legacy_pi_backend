import os
from celery import Celery

# 设置 Django 的 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')

app = Celery('legacy_pi_backend')

# 使用字符串，这样 worker 就不需要序列化配置对象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 Django app 下的 tasks.py 文件
app.autodiscover_tasks()