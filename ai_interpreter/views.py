"""
AI解读应用视图
提供文本解读相关的API接口
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View

from .services import ai_interpreter_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def interpret_text(request):
    """
    解读文本API
    支持多种解读模式和自定义提示词
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'text字段不能为空'
            }, status=400)
        
        # 获取可选参数
        prompt_type = data.get('prompt_type', 'default')
        custom_prompt = data.get('custom_prompt', None)
        max_tokens = data.get('max_tokens', 1000)
        
        # 调用AI解读服务
        result = ai_interpreter_service.interpret_text(
            text=text,
            prompt_type=prompt_type,
            custom_prompt=custom_prompt,
            max_tokens=max_tokens
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '解读失败'),
                'model_used': result.get('model_used')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"解读文本失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'解读失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def batch_interpret(request):
    """
    批量解读文本API
    支持一次解读多个文本
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return JsonResponse({
                'success': False,
                'error': 'texts字段必须是包含文本的列表'
            }, status=400)
        
        if len(texts) > 10:  # 限制批量处理数量
            return JsonResponse({
                'success': False,
                'error': '单次最多处理10个文本'
            }, status=400)
        
        # 获取可选参数
        prompt_type = data.get('prompt_type', 'default')
        
        # 调用批量解读服务
        results = ai_interpreter_service.batch_interpret(
            texts=texts,
            prompt_type=prompt_type
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'results': results,
                'total_texts': len(texts),
                'successful_count': sum(1 for r in results if r['success'])
            }
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误，请提供有效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"批量解读失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'批量解读失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查API
    检查AI解读服务是否正常运行
    """
    try:
        health_status = ai_interpreter_service.health_check()
        
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
def get_prompts(request):
    """
    获取可用的提示词类型
    """
    from .config import INTERPRETATION_PROMPTS
    
    return JsonResponse({
        'success': True,
        'data': {
            'available_prompts': INTERPRETATION_PROMPTS,
            'description': '可用的提示词类型，用于指定解读风格'
        }
    })

@method_decorator(csrf_exempt, name='dispatch')
class InterpretView(View):
    """
    基于类的文本解读视图
    支持GET和POST方法
    """
    
    def get(self, request):
        """GET方法：返回使用说明"""
        return JsonResponse({
            'success': True,
            'message': 'AI解读服务',
            'usage': {
                'POST': '发送文本进行解读',
                'GET': '获取服务信息'
            },
            'endpoints': {
                'interpret': '/api/ai/interpret/',
                'batch_interpret': '/api/ai/batch/',
                'stream_interpret': '/api/ai/stream/',
                'health_check': '/api/ai/health/',
                'prompts': '/api/ai/prompts/'
            },
            'features': [
                '文本解读和分析',
                '多种解读模式',
                '批量文本处理',
                '自定义提示词',
                '⚡ 流式解读支持（Server-Sent Events）',
                '🔄 实时流式响应'
            ]
        })
    
    def post(self, request):
        """POST方法：调用文本解读"""
        return interpret_text(request)

@csrf_exempt
@require_http_methods(["POST"])
def stream_interpret_text(request):
    """
    流式解读文本API
    支持实时流式响应，使用Server-Sent Events
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'text字段不能为空'
            }, status=400)
        
        # 获取可选参数
        prompt_type = data.get('prompt_type', 'default')
        custom_prompt = data.get('custom_prompt', None)
        max_tokens = data.get('max_tokens', 1000)
        
        # 创建流式响应
        from django.http import StreamingHttpResponse
        
        def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'message': '开始流式解读'}, ensure_ascii=False)}\n\n"
                
                # 调用流式解读服务
                for chunk in ai_interpreter_service.stream_interpret_text(
                    text=text,
                    prompt_type=prompt_type,
                    custom_prompt=custom_prompt,
                    max_tokens=max_tokens
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
                # 发送结束信号
                yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"流式解读生成失败: {str(e)}")
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
        logger.error(f"流式解读失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'流式解读失败: {str(e)}'
        }, status=500)
