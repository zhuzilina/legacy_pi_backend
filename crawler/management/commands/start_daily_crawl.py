# your_app/management/commands/start_daily_crawl.py

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone


from crawler.redis_service import redis_service  
from crawler.redis_models import RedisCrawlTask, RedisNewsArticle, RedisStats
from crawler.tasks import run_daily_crawler_task 

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the daily article crawling task and performs data cleanup.'

    def handle(self, *args, **options):
        self.stdout.write("开始执行每日爬取任务...")
        
        try:
            today = timezone.now().date()
            today_str = today.isoformat()
            
            # 1. 清理旧数据 (和原逻辑一样)
            deleted_count = RedisStats.clear_old_data(days_to_keep=1)
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 篇昨日文章")
                self.stdout.write(f"成功清理了 {deleted_count} 篇昨日文章。")

            yesterday = today - timedelta(days=1)
            yesterday_str = yesterday.isoformat()
            try:
                yesterday_status_key = f"crawl_status:{yesterday_str}"
                yesterday_lock_key = f"daily_crawl_lock:{yesterday_str}"
                redis_service.redis_client.delete(yesterday_status_key)
                redis_service.redis_client.delete(yesterday_lock_key)
                logger.info(f"清理了昨天的状态和锁: {yesterday_str}")
            except Exception as e:
                logger.warning(f"清理昨天状态失败: {e}")

            # 2. 检查今天的任务是否已成功或正在运行，避免重复执行
            status = redis_service.get_daily_crawl_status()
            if status == 'running':
                self.stdout.write(self.style.WARNING("今日爬取任务已在运行中，跳过本次执行。"))
                logger.warning("每日爬取任务已在运行，跳过。")
                return
            
            # 如果已有成功数据，也跳过
            if RedisNewsArticle.filter(crawl_status='success'):
                self.stdout.write(self.style.SUCCESS("今日文章已成功爬取，跳过本次执行。"))
                logger.info("今日文章已成功爬取，跳过。")
                return

            # 3. 获取锁，确保即使cron任务意外重叠，也只有一个实例运行
            if not redis_service.acquire_daily_crawl_lock():
                self.stdout.write(self.style.WARNING("未能获取爬取锁，可能已有另一个任务在启动。跳过本次执行。"))
                logger.warning("获取每日爬取锁失败，跳过。")
                return

            # 4. 设置状态并启动任务
            self.stdout.write("获取锁成功，准备启动爬取任务...")
            redis_service.set_daily_crawl_status('running')
            
            task = RedisCrawlTask.create(
                task_name=f'每日爬取-{today.strftime("%Y-%m-%d")}',
                target_url='http://www.people.com.cn/GB/59476/index.html',
                task_type='full'
            )
            
            # 异步执行爬虫
            run_daily_crawler_task.delay(task.id)
            
            logger.info(f"成功启动每日爬取任务，Task ID: {task.id}")
            self.stdout.write(self.style.SUCCESS(f"成功启动每日爬取任务，Task ID: {task.id}"))

        except Exception as e:
            logger.error(f"执行每日爬取命令失败: {str(e)}")
            self.stderr.write(self.style.ERROR(f"执行任务时发生错误: {e}"))
            # 考虑在这里设置状态为 'failed'
            redis_service.set_daily_crawl_status('failed')