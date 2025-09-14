import os
import redis
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Redis服务类，用于管理爬虫数据的缓存"""
    
    def __init__(self):
        redis_config = {
            'host': getattr(settings, 'REDIS_HOST', 'localhost'),
            'port': getattr(settings, 'REDIS_PORT', 6379),
            'db': getattr(settings, 'REDIS_DB', 0),
            'decode_responses': True
        }
        
        # 如果配置了密码，则添加密码认证
        redis_password = getattr(settings, 'REDIS_PASSWORD', None)
        if redis_password:
            redis_config['password'] = redis_password
        
        self.redis_client = redis.Redis(**redis_config)

        logger.info(
            f"RedisService Initialized in PID [{os.getpid()}]: "
            f"Connecting to DB [{self.redis_client.connection_pool.connection_kwargs.get('db')}]"
        )
        
    def test_connection(self):
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            return False
    
    # 文章相关操作
    def save_article(self, article_data):
        """保存文章 Hash，并为其创建索引。"""
        try:
            article_id = article_data.get('id')

            key = f"article:{article_id}"

            # 使用 pipeline 保证原子性
            with self.redis_client.pipeline() as pipe:
                # 1. 保存文章主体数据 (Hash)
                pipe.hset(key, mapping=article_data)
                
                # 2. (核心) 创建或更新索引 (Sets)
                crawl_date = article_data.get('crawl_date')
                crawl_status = article_data.get('crawl_status')
                
                if crawl_date:
                    # 按日期索引
                    pipe.sadd(f"index:crawl_date:{crawl_date}", article_id)
                if crawl_status:
                    # 按状态索引
                    pipe.sadd(f"index:crawl_status:{crawl_status}", article_id)
                if crawl_date and crawl_status:
                    # (最重要) 创建联合索引！
                    pipe.sadd(f"index:date_status:{crawl_date}:{crawl_status}", article_id)
                
                pipe.execute()
            
            logger.info(f"文章已保存到Redis: {article_id}")
            return article_id
        except Exception as e:
            logger.error(f"Redis 保存文章失败: {e}")
            return None
    
    def get_article(self, article_id):
        """根据ID获取文章"""
        try:
            key = f"article:{article_id}"
            article_json = self.redis_client.get(key)
            
            if article_json:
                article_data = json.loads(article_json)
                # 增加阅读量
                article_data['view_count'] = article_data.get('view_count', 0) + 1
                self.redis_client.set(key, json.dumps(article_data, ensure_ascii=False), ex=86400*2)
                return article_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取文章失败: {str(e)}")
            return None
    
    def get_daily_articles(self, date=None):
        """获取指定日期的文章ID列表"""
        try:
            if date is None:
                date = timezone.now().date().isoformat()
            
            article_ids = self.redis_client.smembers(f"daily_articles:{date}")
            return list(article_ids)
            
        except Exception as e:
            logger.error(f"获取每日文章列表失败: {str(e)}")
            return []
    
    def get_articles_by_category(self, category):
        """根据分类获取文章ID列表"""
        try:
            article_ids = self.redis_client.smembers(f"category:{category}")
            return list(article_ids)
            
        except Exception as e:
            logger.error(f"获取分类文章失败: {str(e)}")
            return []
    
    def search_articles(self, keyword):
        """搜索包含关键词的文章"""
        try:
            # 获取所有今日文章
            today = timezone.now().date().isoformat()
            article_ids = self.get_daily_articles(today)
            
            matching_articles = []
            for article_id in article_ids:
                article = self.get_article(article_id)
                if article:
                    title = article.get('title', '').lower()
                    content = article.get('content', '').lower()
                    if keyword.lower() in title or keyword.lower() in content:
                        matching_articles.append(article_id)
            
            return matching_articles
            
        except Exception as e:
            logger.error(f"搜索文章失败: {str(e)}")
            return []
    
    def clear_old_articles(self, days_to_keep=1):
        """清理旧文章"""
        try:
            cutoff_date = timezone.now().date() - timedelta(days=days_to_keep)
            cutoff_date_str = cutoff_date.isoformat()
            
            # 获取要删除的文章ID
            old_article_ids = self.redis_client.smembers(f"daily_articles:{cutoff_date_str}")
            
            deleted_count = 0
            for article_id in old_article_ids:
                # 删除文章数据
                self.redis_client.delete(f"article:{article_id}")
                deleted_count += 1
            
            # 删除日期索引
            self.redis_client.delete(f"daily_articles:{cutoff_date_str}")
            
            logger.info(f"清理了 {deleted_count} 篇 {cutoff_date_str} 的文章")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧文章失败: {str(e)}")
            return 0
    
    # 任务相关操作
    def save_task(self, task_data):
        """保存爬取任务"""
        try:
            task_id = task_data.get('id') or self._generate_task_id()
            task_data['id'] = task_id
            task_data['created_at'] = datetime.now().isoformat()
            task_data['updated_at'] = datetime.now().isoformat()
            
            task_json = json.dumps(task_data, ensure_ascii=False)
            
            # 保存任务数据
            key = f"task:{task_id}"
            self.redis_client.set(key, task_json, ex=86400*7)  # 7天过期
            
            # 添加到任务列表
            self.redis_client.lpush("tasks", task_id)
            self.redis_client.ltrim("tasks", 0, 99)  # 只保留最近100个任务
            
            logger.info(f"任务已保存到Redis: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"保存任务到Redis失败: {str(e)}")
            return None
    
    def get_task(self, task_id):
        """获取任务信息"""
        try:
            key = f"task:{task_id}"
            task_json = self.redis_client.get(key)
            
            if task_json:
                return json.loads(task_json)
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取任务失败: {str(e)}")
            return None
    
    def get_all_task_ids(self):
        """获取所有任务ID"""
        try:
            pattern = "task:*"
            keys = self.redis_client.keys(pattern)
            task_ids = [key.decode('utf-8').replace('task:', '') for key in keys]
            return task_ids
        except Exception as e:
            logger.error(f"获取任务ID列表失败: {str(e)}")
            return []
    
    def update_task(self, task_id, updates):
        """更新任务信息"""
        try:
            task_data = self.get_task(task_id)
            if task_data:
                task_data.update(updates)
                task_data['updated_at'] = datetime.now().isoformat()
                
                task_json = json.dumps(task_data, ensure_ascii=False)
                key = f"task:{task_id}"
                self.redis_client.set(key, task_json, ex=86400*7)
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"更新任务失败: {str(e)}")
            return False
    
    def get_recent_tasks(self, limit=10):
        """获取最近的任务列表"""
        try:
            task_ids = self.redis_client.lrange("tasks", 0, limit-1)
            tasks = []
            
            for task_id in task_ids:
                task = self.get_task(task_id)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"获取最近任务失败: {str(e)}")
            return []
    
    # 统计相关操作
    def get_stats(self):
        """获取统计信息"""
        try:
            today = timezone.now().date().isoformat()
            
            # 今日文章数量
            today_articles_count = self.redis_client.scard(f"daily_articles:{today}")
            
            # 总任务数量
            total_tasks_count = self.redis_client.llen("tasks")
            
            # 最近任务
            recent_tasks = self.get_recent_tasks(5)
            
            return {
                'today_articles_count': today_articles_count,
                'total_tasks_count': total_tasks_count,
                'recent_tasks': recent_tasks,
                'redis_info': self.redis_client.info('memory')
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    # 辅助方法
    def acquire_daily_crawl_lock(self, date_str=None, ttl_seconds=7200):
        """获取每日爬取分布式锁（避免并发重复触发）。返回True表示获取成功。"""
        try:
            if date_str is None:
                date_str = timezone.now().date().isoformat()
            key = f"crawl_lock:{date_str}"
            # NX: 不存在才设置; ex: 过期（两小时防止死锁）
            return bool(self.redis_client.set(key, "1", nx=True, ex=ttl_seconds))
        except Exception as e:
            logger.error(f"获取每日爬取锁失败: {str(e)}")
            return False

    def release_daily_crawl_lock(self, date_str=None):
        """释放每日爬取锁。"""
        try:
            if date_str is None:
                date_str = timezone.now().date().isoformat()
            key = f"crawl_lock:{date_str}"
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"释放每日爬取锁失败: {str(e)}")
            return False

    def set_daily_crawl_status(self, status, date_str=None, ttl_seconds=172800):
        """设置每日爬取状态: running/completed/failed。默认两天过期。"""
        try:
            if date_str is None:
                date_str = timezone.now().date().isoformat()
            key = f"crawl_status:{date_str}"
            self.redis_client.set(key, status, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"设置每日爬取状态失败: {str(e)}")
            return False

    def get_daily_crawl_status(self, date_str=None):
        """获取每日爬取状态。可能返回None/running/completed/failed。"""
        try:
            if date_str is None:
                date_str = timezone.now().date().isoformat()
            key = f"crawl_status:{date_str}"
            status = self.redis_client.get(key)
            return status
        except Exception as e:
            logger.error(f"获取每日爬取状态失败: {str(e)}")
            return None
    def _generate_article_id(self):
        """生成文章ID"""
        return f"article_{int(datetime.now().timestamp() * 1000)}"
    
    def _generate_task_id(self):
        """生成任务ID"""
        return f"task_{int(datetime.now().timestamp() * 1000)}"
    
    def flush_all(self):
        """清空所有数据（仅用于测试）"""
        try:
            self.redis_client.flushdb()
            logger.info("已清空Redis数据库")
            return True
        except Exception as e:
            logger.error(f"清空数据库失败: {str(e)}")
            return False
    
    def get_article_ids_by_filter(self, crawl_date=None, crawl_status=None):
        """根据索引高效地获取文章ID (带有详细的调试日志)"""
        try:
            if crawl_date and crawl_status:
                index_key = f"index:date_status:{crawl_date}:{crawl_status}"
                # --- 添加这条“黑匣子”日志 ---
                logger.info(f"SERVICE.get_ids: Querying index with key: '{index_key}'")
                
                raw_ids_set = self.redis_client.smembers(index_key)
                # --- 添加这条“黑匣子”日志 ---
                logger.info(f"SERVICE.get_ids: self.redis.smembers for key '{index_key}' returned {len(raw_ids_set)} raw items.")
                
                return list(raw_ids_set)
            
            # ... (其他分支保持不变) ...
            return []
        except Exception as e:
            logger.error(f"SERVICE.get_ids: An exception occurred: {repr(e)}", exc_info=True)
            return []
        
    def get_articles_batch(self, article_ids):
        """使用 pipeline 批量获取多个文章的 Hash 数据。"""
        try:
            with self.redis_client.pipeline() as pipe:
                for article_id in article_ids:
                    pipe.hgetall(f"article:{article_id}")
                results = pipe.execute()
            
            # 将 Redis 返回的字节字典解码为字符串字典
            articles_data = []
            for raw_data in results:
                if raw_data:
                    decoded_data = raw_data
                    image_mapping_field = decoded_data.get('image_mapping')
                    if image_mapping_field and isinstance(image_mapping_field, str):
                        try:
                            decoded_data['image_mapping'] = json.loads(image_mapping_field)
                        except (json.JSONDecodeError,TypeError):
                            decoded_data['image_mapping'] = {}
                    
                    articles_data.append(decoded_data)
            return [data for data in results if data]
        except Exception as e:
            logger.error(f"Redis 批量获取文章失败: {e}")
            return []

# 全局Redis服务实例
redis_service = RedisService()
