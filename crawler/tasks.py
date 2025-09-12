import logging
from celery import shared_task
from .services import PeopleNetCrawler
from .redis_service import redis_service

logger = logging.getLogger(__name__)

@shared_task
def run_daily_crawler_task(task_id):
    """
    这是一个 Celery 任务，它将在 Celery worker 中安全地运行。
    """
    try:
        logger.info(f"Celery worker 开始执行每日爬取任务，任务ID: {task_id}")
        crawler = PeopleNetCrawler()
        result = crawler.crawl_today_news(task_id=task_id)
        logger.info(f"每日爬取任务完成: {result}")
        redis_service.set_daily_crawl_status('success')
    except Exception as e:
        logger.error(f"每日爬取任务失败: {str(e)}", exc_info=True) # exc_info=True 会记录完整的堆栈跟踪
        redis_service.set_daily_crawl_status('failed')
    finally:
        # 释放锁
        redis_service.release_daily_crawl_lock()
        logger.info(f"Task {task_id} 执行完毕，释放锁。")
    return "Task finished."