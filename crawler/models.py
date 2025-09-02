# 数据库模型已迁移到Redis
# 现在使用 redis_models.py 中的 RedisNewsArticle 和 RedisCrawlTask
# 保留此文件以避免Django报错，但所有模型已移除

from django.db import models

# 所有数据现在存储在Redis中
# 使用以下模型类：
# - RedisNewsArticle (来自 redis_models.py)
# - RedisCrawlTask (来自 redis_models.py)
# - RedisStats (来自 redis_models.py)