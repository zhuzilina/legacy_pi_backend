import json
import logging
from datetime import datetime
from django.utils import timezone
from .redis_service import redis_service

logger = logging.getLogger(__name__)

class RedisNewsArticle:
    """新闻文章Redis模型"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title', '')
        self.url = kwargs.get('url', '')
        self.source = kwargs.get('source', '')
        self.publish_date = kwargs.get('publish_date')
        self.content = kwargs.get('content', '')
        self.markdown_content = kwargs.get('markdown_content', '')
        self.summary = kwargs.get('summary', '')
        self.category = kwargs.get('category', '')
        self.tags = kwargs.get('tags', '')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.crawl_status = kwargs.get('crawl_status', 'pending')
        self.view_count = kwargs.get('view_count', 0)
        self.word_count = kwargs.get('word_count', 0)
        self.image_count = kwargs.get('image_count', 0)
        self.image_mapping = kwargs.get('image_mapping', {})  # 图片映射关系
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'publish_date': self.publish_date.isoformat() if isinstance(self.publish_date, datetime) else self.publish_date,
            'content': self.content,
            'markdown_content': self.markdown_content,
            'summary': self.summary,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'crawl_status': self.crawl_status,
            'view_count': self.view_count,
            'word_count': self.word_count,
            'image_count': self.image_count,
            'image_mapping': self.image_mapping
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(**data)
    
    def save(self):
        """保存到Redis"""
        try:
            if not self.id:
                self.id = redis_service._generate_article_id()
            
            if not self.created_at:
                self.created_at = datetime.now()
            
            self.updated_at = datetime.now()
            
            article_id = redis_service.save_article(self.to_dict())
            if article_id:
                self.id = article_id
                return True
            return False
            
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False
    
    @classmethod
    def get(cls, article_id):
        """根据ID获取文章"""
        try:
            article_data = redis_service.get_article(article_id)
            if article_data:
                return cls.from_dict(article_data)
            return None
            
        except Exception as e:
            logger.error(f"获取文章失败: {str(e)}")
            return None
    
    @classmethod
    def filter(cls, **kwargs):
        """过滤文章"""
        try:
            # 支持的过滤条件
            category = kwargs.get('category')
            crawl_status = kwargs.get('crawl_status')
            date = kwargs.get('date')
            
            if category:
                article_ids = redis_service.get_articles_by_category(category)
            elif date:
                article_ids = redis_service.get_daily_articles(date)
            else:
                # 默认获取今日文章
                article_ids = redis_service.get_daily_articles()
            
            articles = []
            for article_id in article_ids:
                article_data = redis_service.get_article(article_id)
                if article_data:
                    # 应用额外的过滤条件
                    if crawl_status and article_data.get('crawl_status') != crawl_status:
                        continue
                    articles.append(cls.from_dict(article_data))
            
            return articles
            
        except Exception as e:
            logger.error(f"过滤文章失败: {str(e)}")
            return []
    
    @classmethod
    def search(cls, keyword):
        """搜索文章"""
        try:
            article_ids = redis_service.search_articles(keyword)
            articles = []
            
            for article_id in article_ids:
                article_data = redis_service.get_article(article_id)
                if article_data:
                    articles.append(cls.from_dict(article_data))
            
            return articles
            
        except Exception as e:
            logger.error(f"搜索文章失败: {str(e)}")
            return []
    
    @classmethod
    def count(cls, **kwargs):
        """统计文章数量"""
        try:
            articles = cls.filter(**kwargs)
            return len(articles)
            
        except Exception as e:
            logger.error(f"统计文章数量失败: {str(e)}")
            return 0
    
    def __str__(self):
        return self.title


class RedisCrawlTask:
    """爬取任务Redis模型"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_name = kwargs.get('task_name', '')
        self.target_url = kwargs.get('target_url', '')
        self.task_type = kwargs.get('task_type', 'full')
        self.status = kwargs.get('status', 'pending')
        self.created_at = kwargs.get('created_at')
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')
        self.total_links = kwargs.get('total_links', 0)
        self.success_count = kwargs.get('success_count', 0)
        self.failed_count = kwargs.get('failed_count', 0)
        self.error_message = kwargs.get('error_message', '')
    
    def to_dict(self):
        """转换为字典"""
        def format_datetime(dt):
            if isinstance(dt, datetime):
                return dt.isoformat()
            return dt
        
        return {
            'id': self.id,
            'task_name': self.task_name,
            'target_url': self.target_url,
            'task_type': self.task_type,
            'status': self.status,
            'created_at': format_datetime(self.created_at),
            'started_at': format_datetime(self.started_at),
            'completed_at': format_datetime(self.completed_at),
            'total_links': self.total_links,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(**data)
    
    def save(self):
        """保存到Redis"""
        try:
            if not self.id:
                self.id = redis_service._generate_task_id()
            
            if not self.created_at:
                self.created_at = datetime.now()
            
            task_id = redis_service.save_task(self.to_dict())
            if task_id:
                self.id = task_id
                return True
            return False
            
        except Exception as e:
            logger.error(f"保存任务失败: {str(e)}")
            return False
    
    def update(self, **kwargs):
        """更新任务"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            return redis_service.update_task(self.id, kwargs)
            
        except Exception as e:
            logger.error(f"更新任务失败: {str(e)}")
            return False
    
    @classmethod
    def get(cls, task_id):
        """根据ID获取任务"""
        try:
            task_data = redis_service.get_task(task_id)
            if task_data:
                return cls.from_dict(task_data)
            return None
            
        except Exception as e:
            logger.error(f"获取任务失败: {str(e)}")
            return None
    
    @classmethod
    def create(cls, **kwargs):
        """创建新任务"""
        task = cls(**kwargs)
        if task.save():
            return task
        return None
    
    @classmethod
    def get_recent(cls, limit=10):
        """获取最近的任务"""
        try:
            tasks_data = redis_service.get_recent_tasks(limit)
            tasks = []
            
            for task_data in tasks_data:
                tasks.append(cls.from_dict(task_data))
            
            return tasks
            
        except Exception as e:
            logger.error(f"获取最近任务失败: {str(e)}")
            return []
    
    def __str__(self):
        return f"{self.task_name} - {self.status}"


class RedisStats:
    """统计信息Redis模型"""
    
    @staticmethod
    def get_crawler_stats():
        """获取爬虫统计信息"""
        try:
            return redis_service.get_stats()
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def clear_old_data(days_to_keep=1):
        """清理旧数据"""
        try:
            return redis_service.clear_old_articles(days_to_keep)
        except Exception as e:
            logger.error(f"清理旧数据失败: {str(e)}")
            return 0
