import json
import logging
import uuid
import os
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import MDDocument, MDImage, MDCategory

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_documents_by_category(request):
    """
    根据类别获取MD文档ID列表
    接口格式与crawler应用保持一致，只返回文档ID列表
    """
    try:
        category = request.GET.get('category', '')
        
        # 验证类别
        valid_categories = ['spirit', 'person', 'party_history']
        if category and category not in valid_categories:
            return JsonResponse({
                'msg': 'error',
                'error': f'无效的类别: {category}。有效类别: {", ".join(valid_categories)}'
            }, status=400)
        
        # 构建查询
        query = Q(is_published=True)
        if category:
            query &= Q(category=category)
        
        # 获取文档列表
        documents = MDDocument.objects.filter(query).order_by('-created_at')
        
        # 构建文档ID列表
        document_ids = [str(doc.id) for doc in documents]
        
        # 获取当前日期
        from datetime import date
        current_date = date.today().strftime('%Y-%m-%d')
        
        return JsonResponse({
            'msg': 'success',
            'crawl_date': current_date,
            'total_articles': len(document_ids),
            'article_ids': document_ids,
            'status': 'cached'
        })
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        return JsonResponse({
            'msg': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_document_markdown(request, document_id):
    """
    根据文档ID获取Markdown格式内容
    直接返回用户上传的原始MD内容，包含用户手动编写的元数据
    """
    try:
        try:
            document = MDDocument.objects.get(id=document_id, is_published=True)
        except MDDocument.DoesNotExist:
            return HttpResponse('文档不存在', status=404, content_type='text/plain; charset=utf-8')
        
        # 直接返回用户上传的原始MD内容
        # 图片路径已经在上传时处理过了
        markdown_content = document.content
        
        # 返回纯文本的Markdown内容
        response = HttpResponse(markdown_content, content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'inline; filename="{document.title}.md"'
        return response
        
    except Exception as e:
        logger.error(f"获取文档Markdown失败: {str(e)}")
        return HttpResponse(f'获取文档失败: {str(e)}', status=500, content_type='text/plain; charset=utf-8')


@csrf_exempt
@require_http_methods(["GET"])
def get_document_status(request):
    """
    获取文档系统状态（可选的辅助接口）
    """
    try:
        # 获取统计信息
        total_documents = MDDocument.objects.filter(is_published=True).count()
        spirit_count = MDDocument.objects.filter(category='spirit', is_published=True).count()
        person_count = MDDocument.objects.filter(category='person', is_published=True).count()
        party_history_count = MDDocument.objects.filter(category='party_history', is_published=True).count()
        
        # 获取最近更新的文档
        recent_document = MDDocument.objects.filter(is_published=True).order_by('-updated_at').first()
        
        return JsonResponse({
            'msg': 'success',
            'total_documents': total_documents,
            'category_stats': {
                'spirit': spirit_count,
                'person': person_count,
                'party_history': party_history_count
            },
            'recent_update': recent_document.updated_at.isoformat() if recent_document else None,
            'system_status': 'running'
        })
        
    except Exception as e:
        logger.error(f"获取文档状态失败: {str(e)}")
        return JsonResponse({
            'msg': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_document_image(request, image_id):
    """
    获取文档图片
    """
    try:
        try:
            image = MDImage.objects.get(id=image_id)
        except MDImage.DoesNotExist:
            return HttpResponse('图片不存在', status=404, content_type='text/plain; charset=utf-8')
        
        # 构建图片文件路径
        image_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
        
        if not os.path.exists(image_path):
            return HttpResponse('图片文件不存在', status=404, content_type='text/plain; charset=utf-8')
        
        # 读取图片数据
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 返回图片数据
        response = HttpResponse(image_data, content_type=image.content_type)
        response['Cache-Control'] = 'public, max-age=86400'  # 缓存1天
        response['Content-Disposition'] = f'inline; filename="{image.original_filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"获取文档图片失败: {str(e)}")
        return HttpResponse(f'获取图片失败: {str(e)}', status=500, content_type='text/plain; charset=utf-8')


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request):
    """
    上传MD文档（管理员接口）
    """
    try:
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['title', 'category', 'content']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'msg': 'error',
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 验证类别
        valid_categories = ['spirit', 'person', 'party_history']
        if data['category'] not in valid_categories:
            return JsonResponse({
                'msg': 'error',
                'error': f'无效的类别: {data["category"]}。有效类别: {", ".join(valid_categories)}'
            }, status=400)
        
        # 创建文档
        document = MDDocument(
            title=data['title'],
            category=data['category'],
            content=data['content'],
            summary=data.get('summary', ''),
            author=data.get('author', ''),
            source=data.get('source', ''),
            publish_date=datetime.fromisoformat(data['publish_date']) if data.get('publish_date') else None,
            word_count=len(data['content']),
            image_count=data.get('image_count', 0),
            is_published=data.get('is_published', True)
        )
        
        document.save()
        
        return JsonResponse({
            'msg': 'success',
            'document_id': str(document.id),
            'message': '文档上传成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'msg': 'error',
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"上传文档失败: {str(e)}")
        return JsonResponse({
            'msg': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    """
    上传图片文件
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'msg': 'error',
                'error': '没有找到图片文件'
            }, status=400)
        
        image_file = request.FILES['image']
        alt_text = request.POST.get('alt_text', '')
        original_filename = request.POST.get('original_filename', image_file.name)
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'msg': 'error',
                'error': f'不支持的文件类型: {image_file.content_type}'
            }, status=400)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 构建存储路径
        file_path = f"md_docs/images/{unique_filename}"
        
        # 保存文件
        saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
        
        # 创建图片记录
        image = MDImage(
            original_filename=original_filename,
            stored_filename=unique_filename,
            file_path=saved_path,
            file_size=image_file.size,
            content_type=image_file.content_type,
            alt_text=alt_text
        )
        image.save()
        
        return JsonResponse({
            'msg': 'success',
            'image_id': str(image.id),
            'filename': unique_filename,
            'file_path': saved_path
        })
        
    except Exception as e:
        logger.error(f"上传图片失败: {str(e)}")
        return JsonResponse({
            'msg': 'error',
            'error': str(e)
        }, status=500)