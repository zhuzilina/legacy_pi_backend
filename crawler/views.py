import json
import re
import logging
import threading
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator

from .redis_models import RedisNewsArticle, RedisCrawlTask, RedisStats
from .redis_service import redis_service
from .services import PeopleNetCrawler
from .image_service import image_cache_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def get_daily_articles(request):
    """
    获取当日文章ID列表
    首次请求时触发爬取，返回所有文章ID
    """
    try:
        today = timezone.now().date()
        
        # 检查是否是新的一天，如果是则清理昨天的数据
        deleted_count = RedisStats.clear_old_data(days_to_keep=1)
        if deleted_count > 0:
            logger.info(f"清理了 {deleted_count} 篇昨日文章")
        
        # 先看今日状态
        status = redis_service.get_daily_crawl_status()

        # 如果今天已有成功数据，直接返回
        today_article_ids = RedisNewsArticle.filter(crawl_status='success')
        today_article_ids = [article.id for article in today_article_ids]
        if today_article_ids:
            return JsonResponse({
                'msg': 'success',
                'crawl_date': today.strftime('%Y-%m-%d'),
                'total_articles': len(today_article_ids),
                'article_ids': today_article_ids,
                'status': 'cached'
            })

        # 无缓存数据，如果状态为running，避免重复开启
        if status == 'running':
            return JsonResponse({
                'msg': 'crawling_started',
                'crawl_date': today.strftime('%Y-%m-%d'),
                'status': 'crawling',
                'message': '爬取任务正在进行，请稍后再次请求获取结果'
            })

        # 竞争锁，确保同一时间只有一个请求能启动任务
        if not redis_service.acquire_daily_crawl_lock():
            return JsonResponse({
                'msg': 'crawling_started',
                'crawl_date': today.strftime('%Y-%m-%d'),
                'status': 'crawling',
                'message': '爬取任务正在进行，请稍后再次请求获取结果'
            })

        # 设置状态为running
        redis_service.set_daily_crawl_status('running')

        # 创建任务并后台运行
        task = RedisCrawlTask.create(
            task_name=f'每日爬取-{today.strftime("%Y-%m-%d")}',
            target_url='http://www.people.com.cn/GB/59476/index.html',
            task_type='full'
        )

        def run_daily_crawler():
            try:
                crawler = PeopleNetCrawler()
                result = crawler.crawl_today_news(task_id=task.id)
                logger.info(f"每日爬取任务完成: {result}")
                redis_service.set_daily_crawl_status('completed')
            except Exception as e:
                logger.error(f"每日爬取任务失败: {str(e)}")
                redis_service.set_daily_crawl_status('failed')
            finally:
                # 释放锁
                redis_service.release_daily_crawl_lock()

        thread = threading.Thread(target=run_daily_crawler)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'msg': 'crawling_started',
            'crawl_date': today.strftime('%Y-%m-%d'),
            'task_id': task.id if task else None,
            'status': 'crawling',
            'message': '爬取任务已启动，请稍后再次请求获取结果'
        })
            
    except Exception as e:
        logger.error(f"获取每日文章失败: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_article_markdown(request, article_id):
    """
    根据文章ID获取Markdown格式内容
    """
    try:
        article = RedisNewsArticle.get(article_id)
        
        if not article or article.crawl_status != 'success':
            return HttpResponse('文章不存在', status=404, content_type='text/plain; charset=utf-8')
        
        # 构建完整的Markdown内容
        publish_date_str = article.publish_date
        if isinstance(article.publish_date, str):
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(article.publish_date.replace('Z', '+00:00'))
                publish_date_str = dt.strftime('%Y年%m月%d日 %H:%M')
            except:
                publish_date_str = article.publish_date
        else:
            publish_date_str = article.publish_date.strftime('%Y年%m月%d日 %H:%M')
        
        created_at_str = article.created_at
        if isinstance(article.created_at, str):
            try:
                dt = datetime.fromisoformat(article.created_at.replace('Z', '+00:00'))
                created_at_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_at_str = article.created_at
        else:
            created_at_str = article.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # 渲染前过滤“关注公众号/二维码/扫码”等推广类内容（针对已缓存旧数据的兜底处理）
        def filter_promo_content(md_text: str) -> str:
            if not md_text:
                return md_text
            # 关键词列表（含常见变体）
            keywords = [
                '关注公众号', '关注 公众号', '公众号', '二维码', '扫码', '微信', '微博', '客户端', '订阅', '官微'
            ]
            # 逐行过滤：
            # - 含关键词的纯文本行
            # - 含关键词的Markdown图片行
            filtered_lines = []
            for line in md_text.split('\n'):
                normalized = line.strip()
                lower_line = normalized.lower()
                if not normalized:
                    filtered_lines.append(line)
                    continue
                # 命中关键词即过滤
                if any(k in normalized for k in keywords):
                    # 只有当是图片且包含关键词或者纯文本推广时，均跳过
                    if normalized.startswith('![') or True:
                        continue
                # 针对图片的额外兜底：凡是图片alt或链接中包含关键词，删除
                if normalized.startswith('![') and any(k in normalized for k in keywords):
                    continue
                filtered_lines.append(line)
            md_text = '\n'.join(filtered_lines)
            # 收敛多余空行
            md_text = re.sub(r"\n{3,}", "\n\n", md_text)
            return md_text.strip()

        markdown_content = f"""# {article.title}

**来源**: {article.source}  
**发布时间**: {publish_date_str}  
**分类**: {article.category}  
**字数**: {article.word_count}  
**原文链接**: [{article.url}]({article.url})

---

{article.markdown_content}

---

*本文由人民网爬虫系统自动采集整理*  
*采集时间: {created_at_str}*  
*阅读次数: {article.view_count}*
"""
        # 最后一步过滤（确保旧缓存中的推广内容被清理）
        markdown_content = filter_promo_content(markdown_content)

        # 返回纯文本的Markdown内容
        response = HttpResponse(markdown_content, content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'inline; filename="{article.title}.md"'
        return response
        

    except Exception as e:
        logger.error(f"获取文章Markdown失败: {str(e)}")
        return HttpResponse(f'获取文章失败: {str(e)}', status=500, content_type='text/plain; charset=utf-8')

@csrf_exempt
@require_http_methods(["GET"])
def get_crawl_status(request):
    """
    获取当前爬取状态（可选的辅助接口）
    """
    try:
        today = timezone.now().date()
        
        # 获取统计信息
        stats = RedisStats.get_crawler_stats()
        
        # 获取最近的任务
        recent_tasks = RedisCrawlTask.get_recent(1)
        today_task = recent_tasks[0] if recent_tasks else None
        
        # 获取今日文章数量
        today_articles_count = RedisNewsArticle.count(crawl_status='success')
        
        if today_task:
            def format_datetime(dt_str):
                if dt_str:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        return dt_str
                return None
            
            return JsonResponse({
                'msg': 'success',
                'date': today.strftime('%Y-%m-%d'),
                'task_status': today_task.status,
                'articles_count': today_articles_count,
                'task_id': today_task.id,
                'started_at': format_datetime(today_task.started_at),
                'completed_at': format_datetime(today_task.completed_at),
                'total_tasks': stats.get('total_tasks_count', 0)
            })
        else:
            return JsonResponse({
                'msg': 'success',
                'date': today.strftime('%Y-%m-%d'),
                'task_status': 'not_started',
                'articles_count': today_articles_count,
                'total_tasks': stats.get('total_tasks_count', 0)
            })
            
    except Exception as e:
        logger.error(f"获取爬取状态失败: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_cached_image(request, image_id):
    """
    获取缓存的图片
    """
    try:
        # 获取图片数据
        image_data, content_type = image_cache_service.get_image_data(image_id)
        
        if image_data is None:
            return HttpResponse('图片不存在', status=404, content_type='text/plain; charset=utf-8')
        
        # 返回图片数据
        response = HttpResponse(image_data, content_type=content_type)
        response['Cache-Control'] = 'public, max-age=86400'  # 缓存1天
        response['Content-Disposition'] = f'inline; filename="{image_id}"'
        
        return response
        
    except Exception as e:
        logger.error(f"获取缓存图片失败: {str(e)}")
        return HttpResponse(f'获取图片失败: {str(e)}', status=500, content_type='text/plain; charset=utf-8')

