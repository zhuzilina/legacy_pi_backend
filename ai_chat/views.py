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
from .error_handlers import (
    RequestValidator, ErrorResponse, handle_service_exception, ErrorCode
)

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
    提供增强的错误处理和输入验证
    """
    try:
        # 验证请求头
        content_type = request.content_type or ''
        if not content_type.startswith('multipart/form-data'):
            return ErrorResponse.create_error_response(
                error_code=ErrorCode.INVALID_REQUEST_FORMAT,
                error_message='Content-Type必须是multipart/form-data',
                status_code=400,
                details={
                    'received_content_type': content_type,
                    'expected_content_type': 'multipart/form-data'
                },
                suggestion='请使用form-data格式上传图片文件'
            )

        if 'image' not in request.FILES:
            return ErrorResponse.missing_field_error(
                field_name='image',
                expected_type='file',
                suggestion='请提供图片文件，支持的格式：jpg, jpeg, png, gif, bmp, webp'
            )

        uploaded_file = request.FILES['image']

        # 验证文件基本属性
        if not uploaded_file.name:
            return ErrorResponse.validation_error(
                message='文件名不能为空',
                field_name='filename',
                suggestion='请确保上传的文件有有效的文件名'
            )

        # 验证文件大小（在服务层也有限制，但这里提供早期反馈）
        max_size_mb = 10  # 10MB
        if uploaded_file.size > max_size_mb * 1024 * 1024:
            return ErrorResponse.create_error_response(
                error_code=ErrorCode.IMAGE_SIZE_TOO_LARGE,
                error_message='图片文件过大',
                status_code=400,
                details={
                    'max_size_mb': max_size_mb,
                    'actual_size_mb': round(uploaded_file.size / (1024 * 1024), 2),
                    'actual_size_bytes': uploaded_file.size
                },
                suggestion=f'请选择小于{max_size_mb}MB的图片文件'
            )

        # 上传并缓存图片
        result = ai_image_service.upload_and_cache_image(uploaded_file)

        if result['success']:
            return JsonResponse({
                'success': True,
                'data': {
                    'image_id': result.get('image_id'),
                    'image_info': result.get('image_info', {}),
                    'message': result.get('message', '上传成功'),
                    'upload_status': 'completed'
                }
            })
        else:
            error_details = result.get('error', '上传失败')
            logger.warning(f"图片上传服务错误: {error_details}")

            # 分析服务层错误类型
            error_code = ErrorCode.IMAGE_UPLOAD_FAILED
            suggestion = None

            if '不支持的图片格式' in error_details:
                error_code = ErrorCode.IMAGE_FORMAT_UNSUPPORTED
                suggestion = '请使用支持的图片格式：jpg, jpeg, png, gif, bmp, webp'
            elif '图片文件过大' in error_details:
                error_code = ErrorCode.IMAGE_SIZE_TOO_LARGE
                suggestion = '请选择较小的图片文件'
            elif '无效的图片文件' in error_details:
                error_code = ErrorCode.IMAGE_PROCESSING_ERROR
                suggestion = '请确保文件是有效的图片格式'

            return ErrorResponse.image_upload_error(
                message=error_details,
                details={'service_error': error_details},
                suggestion=suggestion
            )

    except Exception as e:
        return handle_service_exception(
            'upload_image',
            e,
            {
                'filename': getattr(request.FILES.get('image'), 'name', 'unknown') if request.FILES else None,
                'file_size': getattr(request.FILES.get('image'), 'size', 0) if request.FILES else None
            }
        )

@csrf_exempt
@require_http_methods(["POST"])
def upload_images_batch(request):
    """
    批量上传图片到Redis缓存
    """
    try:
        # 验证请求头
        content_type = request.content_type
        if not content_type.startswith('multipart/form-data'):
            return JsonResponse({
                'success': False,
                'error': 'Content-Type必须是multipart/form-data',
                'details': '请使用form-data格式上传图片文件'
            }, status=400)

        if 'images' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请提供图片文件列表',
                'field_required': 'images',
                'expected_type': 'file_list'
            }, status=400)

        uploaded_files = request.FILES.getlist('images')

        if not uploaded_files:
            return JsonResponse({
                'success': False,
                'error': '图片文件列表不能为空',
                'field_name': 'images',
                'received_count': 0
            }, status=400)

        # 验证文件数量限制
        max_batch_size = 10  # 最多同时上传10张图片
        if len(uploaded_files) > max_batch_size:
            return JsonResponse({
                'success': False,
                'error': f'一次最多只能上传{max_batch_size}张图片',
                'provided_count': len(uploaded_files),
                'max_allowed': max_batch_size
            }, status=400)

        # 预验证文件基本信息
        file_validation_errors = []
        for i, uploaded_file in enumerate(uploaded_files):
            if not uploaded_file.name:
                file_validation_errors.append({
                    'index': i,
                    'filename': 'unknown',
                    'error': '文件名不能为空'
                })
                continue

            # 验证文件大小
            max_size_mb = 10  # 10MB
            if uploaded_file.size > max_size_mb * 1024 * 1024:
                file_validation_errors.append({
                    'index': i,
                    'filename': uploaded_file.name,
                    'error': f'文件过大 ({round(uploaded_file.size / (1024 * 1024), 2)}MB > {max_size_mb}MB)',
                    'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
                    'max_size_mb': max_size_mb
                })

        if file_validation_errors:
            return JsonResponse({
                'success': False,
                'error': '文件验证失败',
                'validation_errors': file_validation_errors,
                'valid_files_count': len(uploaded_files) - len(file_validation_errors)
            }, status=400)

        # 批量上传并缓存图片
        result = ai_image_service.batch_upload_images(uploaded_files)

        # 增强返回信息
        response_data = {
            'success': result['success'],
            'data': {
                'total_count': result.get('total_count', 0),
                'success_count': result.get('success_count', 0),
                'failed_count': result.get('total_count', 0) - result.get('success_count', 0),
                'results': result.get('results', []),
                'processing_summary': {
                    'total_files_processed': len(uploaded_files),
                    'successful_uploads': result.get('success_count', 0),
                    'failed_uploads': result.get('total_count', 0) - result.get('success_count', 0)
                }
            }
        }

        if not result['success']:
            response_data['error'] = result.get('error', '批量上传失败')
            response_data['error_type'] = 'batch_upload_error'

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"批量图片上传异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '批量图片上传处理失败',
            'error_details': str(e) if str(e) else '未知服务器错误',
            'error_type': 'server_error',
            'timestamp': str(request.timestamp)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_images(request):
    """
    带图片的AI对话API
    提供增强的错误处理和输入验证
    """
    try:
        # 验证JSON请求
        is_valid, data, error_response = RequestValidator.validate_json_request(request)
        if not is_valid:
            return error_response

        # 验证必填字段
        required_fields = [
            ('message', 'str', '用户消息'),
            ('image_ids', 'list', '图片ID列表')
        ]

        # DEBUG: Print the data we're validating
        logger.info(f"DEBUG: Validating data: {data}")
        logger.info(f"DEBUG: message type: {type(data.get('message'))}")
        logger.info(f"DEBUG: image_ids type: {type(data.get('image_ids'))}")

        validation_error = RequestValidator.validate_required_fields(data, required_fields)
        if validation_error:
            logger.info(f"DEBUG: Validation error returned: {validation_error}")
            return validation_error
        else:
            logger.info("DEBUG: No validation error - proceeding")

        # 验证图片ID列表
        image_ids = data['image_ids']  # 已经验证过存在且是列表
        is_valid_ids, valid_image_ids, id_error = RequestValidator.validate_image_ids(image_ids)
        if not is_valid_ids:
            return id_error

        # 验证数值参数
        param_error = RequestValidator.validate_numeric_parameters(data)
        if param_error:
            return param_error

        # 验证对话历史格式
        conversation_history = data.get('conversation_history', [])
        if conversation_history and not isinstance(conversation_history, list):
            return ErrorResponse.validation_error(
                message='conversation_history必须是列表格式',
                field_name='conversation_history',
                expected_type='list',
                received_type=type(conversation_history).__name__
            )

        # 验证图片是否存在（提前验证，避免后续处理中的错误）
        existing_image_ids = []
        missing_image_ids = []

        for image_id in valid_image_ids:
            cached_image = ai_image_service.get_cached_image(image_id)
            if cached_image:
                existing_image_ids.append(image_id)
            else:
                missing_image_ids.append(image_id)
                logger.warning(f"图片ID不存在或已过期: {image_id}")

        if not existing_image_ids:
            return ErrorResponse.create_error_response(
                error_code=ErrorCode.IMAGE_NOT_FOUND,
                error_message='所有指定的图片ID都无效或已过期',
                status_code=400,
                details={
                    'provided_ids': image_ids,
                    'missing_ids': missing_image_ids
                },
                suggestion='请重新上传图片或使用有效的图片ID'
            )

        if len(existing_image_ids) != len(valid_image_ids):
            logger.info(f"部分图片ID无效，将使用有效的图片进行对话: {len(existing_image_ids)}/{len(valid_image_ids)}")

        # 提取其他参数（使用验证后的数据）
        user_message = data['message'].strip()  # 已经验证过存在且是字符串
        image_prompt_type = data.get('image_prompt_type', 'default')
        custom_image_prompt = data.get('custom_image_prompt', None)
        max_tokens = data.get('max_tokens', None)
        temperature = data.get('temperature', None)

        # 调用AI图片对话服务
        try:
            result = ai_chat_service.chat_with_images(
                user_message=user_message,
                image_ids=existing_image_ids,
                conversation_history=conversation_history,
                image_prompt_type=image_prompt_type,
                custom_image_prompt=custom_image_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except Exception as service_error:
            return handle_service_exception(
                'chat_with_images',
                service_error,
                {'image_ids_count': len(existing_image_ids), 'message_length': len(user_message)}
            )

        if result['success']:
            return JsonResponse({
                'success': True,
                'data': {
                    'response': result.get('response'),
                    'model_used': result.get('model_used'),
                    'tokens_used': result.get('tokens_used'),
                    'images_processed': len(existing_image_ids),
                    'original_image_count': len(image_ids),
                    'invalid_image_count': len(missing_image_ids),
                    'processing_status': 'completed'
                }
            })
        else:
            error_message = result.get('error', '图片对话失败')
            logger.error(f"AI图片对话服务错误: {error_message}")

            # 分析错误类型并提供相应的建议
            error_details = {'ai_error': error_message}
            suggestion = None
            error_code = ErrorCode.AI_SERVICE_ERROR

            if 'InvalidParameter' in error_message:
                suggestion = '请检查图片格式是否正确，或尝试重新上传图片'
                error_code = ErrorCode.AI_INVALID_PARAMETER
            elif 'image_url' in error_message or 'base64' in error_message:
                suggestion = '图片数据处理失败，请尝试重新上传图片'
                error_code = ErrorCode.IMAGE_PROCESSING_ERROR
            elif 'timeout' in error_message.lower():
                suggestion = 'AI服务响应超时，请稍后重试'
                error_code = ErrorCode.AI_TIMEOUT_ERROR

            return ErrorResponse.ai_service_error(
                message=error_message,
                details=error_details,
                suggestion=suggestion,
                model_used=result.get('model_used')
            )

    except Exception as e:
        return handle_service_exception(
            'chat_with_images',
            e,
            {'request_body_length': len(request.body) if hasattr(request, 'body') else 0}
        )

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
