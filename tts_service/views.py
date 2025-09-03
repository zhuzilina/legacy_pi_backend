
import asyncio
import edge_tts
import json
import logging
import os
import tempfile
from datetime import datetime
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.shortcuts import redirect
import edge_tts

from .models import TTSRequest
from .services import tts_service

logger = logging.getLogger(__name__)


class TTSView(View):
    """TTS文本转语音视图"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    async def post(self, request):
        """流式文本转语音API"""
        try:
            # 解析请求数据
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            text = data.get('text', '').strip()
            voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
            language = data.get('language', 'zh-CN')
            
            # 验证输入
            is_valid, error_msg = tts_service.validate_text(text)
            if not is_valid:
                return JsonResponse({
                    'error': error_msg
                }, status=400)
            
            # 创建TTS请求记录
            tts_request = TTSRequest.objects.create(
                text=text,
                voice=voice,
                language=language,
                status='processing'
            )
            
            try:
                # 开始流式转换
                logger.info(f"开始TTS转换，请求ID: {tts_request.id}")
                
                # 创建流式响应
                response = StreamingHttpResponse(
                    streaming_content=self._stream_tts(text, voice, language, tts_request),
                    content_type='audio/wav'
                )
                
                # 设置响应头
                response['Content-Disposition'] = f'attachment; filename="tts_{tts_request.id}.wav"'
                response['X-TTS-Request-ID'] = str(tts_request.id)
                response['X-TTS-Voice'] = voice
                response['X-TTS-Language'] = language
                
                return response
                
            except Exception as e:
                # 标记失败
                tts_request.mark_failed(str(e))
                logger.error(f"TTS转换失败，请求ID: {tts_request.id}: {str(e)}")
                
                return JsonResponse({
                    'error': f'TTS转换失败: {str(e)}',
                    'request_id': tts_request.id
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': '无效的JSON格式'
            }, status=400)
        except Exception as e:
            logger.error(f"TTS API错误: {str(e)}")
            return JsonResponse({
                'error': f'服务器错误: {str(e)}'
            }, status=500)
    
    async def _stream_tts(self, text: str, voice: str, language: str, tts_request: TTSRequest):
        """流式TTS转换生成器"""
        try:
            # 分段处理文本
            segments = tts_service._split_text(text)
            
            # 创建临时文件来存储音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            try:
                # 使用edge-tts进行转换
                communicate = edge_tts.Communicate(text, voice)
                
                # 流式获取音频数据
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        yield chunk["data"]
                    elif chunk["type"] == "WordBoundary":
                        # 可以在这里处理单词边界信息
                        pass
                
                # 标记完成
                tts_request.mark_completed(
                    audio_file=temp_path,
                    duration=0.0  # 这里可以计算实际时长
                )
                
                logger.info(f"TTS转换完成，请求ID: {tts_request.id}")
                
            except Exception as e:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise e
                
        except Exception as e:
            logger.error(f"流式TTS转换失败: {str(e)}")
            raise e


@csrf_exempt
@require_http_methods(["POST"])
def tts_stream_api(request):
    """流式TTS API端点"""
    try:
        # 解析请求数据
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        text = data.get('text', '').strip()
        voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
        language = data.get('language', 'zh-CN')
        
        # 验证输入
        is_valid, error_msg = tts_service.validate_text(text)
        if not is_valid:
            return JsonResponse({
                'error': error_msg
            }, status=400)
        
        # 创建TTS请求记录
        tts_request = TTSRequest.objects.create(
            text=text,
            voice=voice,
            language=language,
            status='processing'
        )
        
        try:
            # 开始流式转换
            logger.info(f"开始TTS转换，请求ID: {tts_request.id}")
            
            # 使用同步方式创建流式响应
            def generate_audio_stream():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        async_gen = tts_service.text_to_speech_stream(text, voice, language)
                        while True:
                            try:
                                chunk = loop.run_until_complete(async_gen.__anext__())
                                yield chunk
                            except StopAsyncIteration:
                                break
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"流式TTS生成失败: {str(e)}")
                    raise e
            
            # 创建流式响应
            response = StreamingHttpResponse(
                streaming_content=generate_audio_stream(),
                content_type='audio/wav'
            )
            
            # 设置响应头
            response['Content-Disposition'] = f'attachment; filename="tts_{tts_request.id}.wav"'
            response['X-TTS-Request-ID'] = str(tts_request.id)
            response['X-TTS-Voice'] = voice
            response['X-TTS-Language'] = language
            
            # 标记完成
            tts_request.mark_completed()
            
            return response
            
        except Exception as e:
            # 标记失败
            tts_request.mark_failed(str(e))
            logger.error(f"TTS转换失败，请求ID: {tts_request.id}: {str(e)}")
            
            return JsonResponse({
                'error': f'TTS转换失败: {str(e)}',
                'request_id': tts_request.id
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        logger.error(f"TTS API错误: {str(e)}")
        return JsonResponse({
            'error': f'服务器错误: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def tts_file_api(request):
    """文件式TTS API端点"""
    try:
        # 解析请求数据
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        text = data.get('text', '').strip()
        voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
        language = data.get('language', 'zh-CN')
        
        # 验证输入
        is_valid, error_msg = tts_service.validate_text(text)
        if not is_valid:
            return JsonResponse({
                'error': error_msg
            }, status=400)
        
        # 创建TTS请求记录
        tts_request = TTSRequest.objects.create(
            text=text,
            voice=voice,
            language=language,
            status='processing'
        )
        
        try:
            # 生成输出文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tts_{tts_request.id}_{timestamp}.wav"
            output_path = os.path.join(settings.MEDIA_ROOT, 'tts', filename)
            
            # 使用同步方式转换到文件
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(tts_service.text_to_speech_file(text, output_path, voice, language))
            finally:
                loop.close()
            
            # 标记完成
            tts_request.mark_completed(
                audio_file=output_path,
                duration=0.0  # 这里可以计算实际时长
            )
            
            logger.info(f"TTS转换完成，请求ID: {tts_request.id}")
            
            # 构建音频文件的相对URL
            relative_path = output_path.replace(str(settings.MEDIA_ROOT), '').lstrip('/')
            audio_url = f"{settings.MEDIA_URL}{relative_path}"
            
            return JsonResponse({
                'success': True,
                'request_id': tts_request.id,
                'audio_file': output_path,      # 绝对路径，用于内部处理
                'audio_url': audio_url,         # 相对URL，用于客户端访问
                'file_size': result['file_size'],
                'voice': voice,
                'language': language,
                'message': 'TTS转换成功'
            })
            
        except Exception as e:
            # 标记失败
            tts_request.mark_failed(str(e))
            logger.error(f"TTS转换失败，请求ID: {tts_request.id}: {str(e)}")
            
            return JsonResponse({
                'error': f'TTS转换失败: {str(e)}',
                'message': str(e)
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        logger.error(f"TTS API错误: {str(e)}")
        return JsonResponse({
            'error': f'服务器错误: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_voices_api(request):
    """获取可用语音列表API"""
    try:
        # 使用同步方式获取语音列表
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            voices = loop.run_until_complete(tts_service.get_available_voices())
        finally:
            loop.close()
        
        return JsonResponse({
            'success': True,
            'voices': voices,
            'default_voice': tts_service.default_voice,
            'default_language': tts_service.default_language
        })
        
    except Exception as e:
        logger.error(f"获取语音列表失败: {str(e)}")
        return JsonResponse({
            'error': f'获取语音列表失败: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_tts_status_api(request, request_id):
    """获取TTS请求状态API"""
    try:
        tts_request = TTSRequest.objects.get(id=request_id)
        
        # 构建音频文件的相对URL
        audio_url = None
        if tts_request.audio_file:
            relative_path = tts_request.audio_file.replace(str(settings.MEDIA_ROOT), '').lstrip('/')
            audio_url = f"{settings.MEDIA_URL}{relative_path}"
        
        return JsonResponse({
            'success': True,
            'request_id': tts_request.id,
            'status': tts_request.status,
            'text': tts_request.text[:100] + '...' if len(tts_request.text) > 100 else tts_request.text,
            'voice': tts_request.voice,
            'language': tts_request.language,
            'audio_file': tts_request.audio_file,    # 绝对路径，用于内部处理
            'audio_url': audio_url,                  # 相对URL，用于客户端访问
            'duration': tts_request.duration,
            'error_message': tts_request.error_message,
            'created_at': tts_request.created_at.isoformat(),
            'completed_at': tts_request.completed_at.isoformat() if tts_request.completed_at else None
        })
        
    except TTSRequest.DoesNotExist:
        return JsonResponse({
            'error': 'TTS请求不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"获取TTS状态失败: {str(e)}")
        return JsonResponse({
            'error': f'获取TTS状态失败: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def download_audio_api(request, request_id):
    """下载音频文件API"""
    try:
        tts_request = TTSRequest.objects.get(id=request_id)
        
        if tts_request.status != 'completed' or not tts_request.audio_file:
            return JsonResponse({
                'error': '音频文件不存在或转换未完成'
            }, status=404)
        
        if not os.path.exists(tts_request.audio_file):
            return JsonResponse({
                'error': '音频文件不存在'
            }, status=404)
        
        # 返回音频文件
        with open(tts_request.audio_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/wav')
            response['Content-Disposition'] = f'attachment; filename="tts_{request_id}.wav"'
            return response
        
    except TTSRequest.DoesNotExist:
        return JsonResponse({
            'error': 'TTS请求不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"下载音频文件失败: {str(e)}")
        return JsonResponse({
            'error': f'下载音频文件失败: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def audio_redirect_api(request, request_id):
    """音频文件重定向API - 处理客户端直接访问音频文件的情况"""
    try:
        tts_request = TTSRequest.objects.get(id=request_id)
        
        if tts_request.status != 'completed' or not tts_request.audio_file:
            raise Http404("音频文件不存在或转换未完成")
        
        if not os.path.exists(tts_request.audio_file):
            raise Http404("音频文件不存在")
        
        # 构建音频文件的相对URL并重定向
        relative_path = tts_request.audio_file.replace(str(settings.MEDIA_ROOT), '').lstrip('/')
        audio_url = f"{settings.MEDIA_URL}{relative_path}"
        
        return redirect(audio_url)
        
    except TTSRequest.DoesNotExist:
        raise Http404("TTS请求不存在")
    except Exception as e:
        logger.error(f"音频重定向失败: {str(e)}")
        raise Http404("音频文件访问失败")

