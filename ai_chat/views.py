"""
AI对话应用视图
提供多轮对话相关的API接口
对话记录由客户端维护
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.storage import default_storage

from .services import ai_chat_service
from .image_service import ai_image_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    AI对话API
    支持多轮对话，对话记录由客户端维护
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'message字段不能为空'
            }, status=400)
        
        # 获取可选参数
        conversation_history = data.get('conversation_history', [])
        system_prompt_type = data.get('system_prompt_type', 'default')
        custom_system_prompt = data.get('custom_system_prompt', None)
        max_tokens = data.get('max_tokens', None)
        temperature = data.get('temperature', None)
        
        # 验证对话历史格式
        if conversation_history and not isinstance(conversation_history, list):
            return JsonResponse({
                'success': False,
                'error': 'conversation_history必须是列表格式'
            }, status=400)
        
        
        # 调用AI对话服务
        result = ai_chat_service.chat(
            user_message=user_message,
            conversation_history=conversation_history,
            system_prompt_type=system_prompt_type,
            custom_system_prompt=custom_system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '对话失败'),
                'model_used': result.get('model_used')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"AI对话失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'对话失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    """
    上传图片到Redis缓存
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请提供图片文件'
            }, status=400)
        
        uploaded_file = request.FILES['image']
        
        # 上传并缓存图片
        result = ai_image_service.upload_and_cache_image(uploaded_file)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '上传失败')
            }, status=400)
            
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'图片上传失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_images_batch(request):
    """
    批量上传图片到Redis缓存
    """
    try:
        if 'images' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请提供图片文件列表'
            }, status=400)
        
        uploaded_files = request.FILES.getlist('images')
        
        if not uploaded_files:
            return JsonResponse({
                'success': False,
                'error': '图片文件列表不能为空'
            }, status=400)
        
        # 批量上传并缓存图片
        result = ai_image_service.batch_upload_images(uploaded_files)
        
        return JsonResponse({
            'success': result['success'],
            'data': result
        })
            
    except Exception as e:
        logger.error(f"批量图片上传失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'批量图片上传失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_images(request):
    """
    带图片的AI对话API
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        image_ids = data.get('image_ids', [])
        
        if not image_ids:
            return JsonResponse({
                'success': False,
                'error': 'image_ids字段不能为空'
            }, status=400)
        
        if not isinstance(image_ids, list):
            return JsonResponse({
                'success': False,
                'error': 'image_ids必须是列表格式'
            }, status=400)
        
        # 获取可选参数
        conversation_history = data.get('conversation_history', [])
        image_prompt_type = data.get('image_prompt_type', 'default')
        custom_image_prompt = data.get('custom_image_prompt', None)
        max_tokens = data.get('max_tokens', None)
        temperature = data.get('temperature', None)
        
        # 验证对话历史格式
        if conversation_history and not isinstance(conversation_history, list):
            return JsonResponse({
                'success': False,
                'error': 'conversation_history必须是列表格式'
            }, status=400)
        
        # 调用AI图片对话服务
        result = ai_chat_service.chat_with_images(
            user_message=user_message,
            image_ids=image_ids,
            conversation_history=conversation_history,
            image_prompt_type=image_prompt_type,
            custom_image_prompt=custom_image_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '图片对话失败'),
                'model_used': result.get('model_used')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"图片对话失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'图片对话失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_image_prompts(request):
    """
    获取可用的图片理解提示词类型
    """
    try:
        prompts = ai_chat_service.get_available_image_prompts()
        
        return JsonResponse({
            'success': True,
            'data': {
                'available_prompts': prompts,
                'description': '可用的图片理解提示词类型，用于指定AI如何分析图片',
                'usage': '在图片对话API中使用image_prompt_type参数指定提示词类型'
            }
        })
        
    except Exception as e:
        logger.error(f"获取图片提示词失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取图片提示词失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_image_cache_stats(request):
    """
    获取图片缓存统计信息
    """
    try:
        stats = ai_image_service.get_cache_stats()
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取图片缓存统计失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取图片缓存统计失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_system_prompts(request):
    """
    获取可用的系统提示词类型
    """
    try:
        prompts = ai_chat_service.get_available_system_prompts()
        
        return JsonResponse({
            'success': True,
            'data': {
                'available_prompts': prompts,
                'description': '可用的系统提示词类型，用于指定AI助手的角色和风格'
            }
        })
        
    except Exception as e:
        logger.error(f"获取系统提示词失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取系统提示词失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查API
    检查AI对话服务是否正常运行
    """
    try:
        health_status = ai_chat_service.health_check()
        
        if health_status['status'] == 'healthy':
            return JsonResponse({
                'success': True,
                'data': health_status
            })
        else:
            return JsonResponse({
                'success': False,
                'data': health_status
            }, status=503)
            
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'健康检查失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_chat_config(request):
    """
    获取对话配置信息
    """
    from .config import CHAT_CONFIG
    
    return JsonResponse({
        'success': True,
        'data': {
            'config': CHAT_CONFIG,
            'description': 'AI对话服务的配置参数'
        }
    })

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    """
    基于类的AI对话视图
    支持GET和POST方法
    """
    
    def get(self, request):
        """GET方法：返回使用说明"""
        return JsonResponse({
            'success': True,
            'message': 'AI对话服务',
            'description': '支持多轮对话的AI聊天API，对话记录由客户端维护',
            'usage': {
                'POST': '发送消息进行对话',
                'GET': '获取服务信息'
            },
            'endpoints': {
                'chat': '/api/ai-chat/chat/',
                'chat_with_images': '/api/ai-chat/chat-with-images/',
                'stream_chat': '/api/ai-chat/stream/',
                'stream_chat_with_images': '/api/ai-chat/stream-with-images/',
                'upload_image': '/api/ai-chat/upload-image/',
                'upload_images_batch': '/api/ai-chat/upload-images-batch/',
                'system_prompts': '/api/ai-chat/prompts/',
                'image_prompts': '/api/ai-chat/image-prompts/',
                'image_cache_stats': '/api/ai-chat/image-cache-stats/',
                'health_check': '/api/ai-chat/health/',
                'config': '/api/ai-chat/config/'
            },
            'features': [
                '支持多轮对话',
                '客户端维护对话历史',
                '专业的知识助手角色',
                '自定义系统提示词',
                '可调节的对话参数',
                '🖼️ 图片理解功能（支持多图片对话）',
                '📤 图片上传到Redis缓存',
                '🎨 多种图片理解提示词风格',
                '⚡ 流式对话支持（Server-Sent Events）',
                '🔄 实时流式响应'
            ]
        })
    
    def post(self, request):
        """POST方法：调用AI对话"""
        return chat(request)

@csrf_exempt
@require_http_methods(["POST"])
def stream_chat(request):
    """
    流式AI对话API
    支持实时流式响应，使用Server-Sent Events
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'message字段不能为空'
            }, status=400)
        
        # 获取可选参数
        conversation_history = data.get('conversation_history', [])
        system_prompt_type = data.get('system_prompt_type', 'default')
        custom_system_prompt = data.get('custom_system_prompt', None)
        max_tokens = data.get('max_tokens', None)
        temperature = data.get('temperature', None)
        
        # 创建流式响应
        from django.http import StreamingHttpResponse
        
        def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'message': '开始流式对话'}, ensure_ascii=False)}\n\n"
                
                # 调用流式对话服务
                for chunk in ai_chat_service.stream_chat(
                    user_message=user_message,
                    conversation_history=conversation_history,
                    system_prompt_type=system_prompt_type,
                    custom_system_prompt=custom_system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
                # 发送结束信号
                yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"流式对话生成失败: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
        
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        
        return response
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"流式AI对话失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'流式对话失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def stream_chat_with_images(request):
    """
    流式带图片的AI对话API
    支持实时流式响应，使用Server-Sent Events
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        image_ids = data.get('image_ids', [])
        
        if not image_ids:
            return JsonResponse({
                'success': False,
                'error': 'image_ids字段不能为空'
            }, status=400)
        
        if not isinstance(image_ids, list):
            return JsonResponse({
                'success': False,
                'error': 'image_ids必须是列表格式'
            }, status=400)
        
        # 获取可选参数
        conversation_history = data.get('conversation_history', [])
        image_prompt_type = data.get('image_prompt_type', 'default')
        custom_image_prompt = data.get('custom_image_prompt', None)
        max_tokens = data.get('max_tokens', None)
        temperature = data.get('temperature', None)
        
        # 创建流式响应
        from django.http import StreamingHttpResponse
        
        def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'message': '开始流式图片对话'}, ensure_ascii=False)}\n\n"
                
                # 调用流式图片对话服务
                for chunk in ai_chat_service.stream_chat_with_images(
                    user_message=user_message,
                    image_ids=image_ids,
                    conversation_history=conversation_history,
                    image_prompt_type=image_prompt_type,
                    custom_image_prompt=custom_image_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
                # 发送结束信号
                yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"流式图片对话生成失败: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
        
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        
        return response
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"流式图片对话失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'流式图片对话失败: {str(e)}'
        }, status=500)
