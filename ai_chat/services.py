"""
AI对话服务
使用方舟 SDK调用大模型API进行多轮对话
对话记录由客户端维护
"""

import logging
from typing import Dict, Any, List, Optional
from volcenginesdkarkruntime import Ark
from .config import AI_MODEL_CONFIG, CHAT_SYSTEM_PROMPTS, CHAT_CONFIG, IMAGE_PROMPTS
from .image_service import ai_image_service

logger = logging.getLogger(__name__)

class AIChatService:
    """AI对话服务类"""
    
    def __init__(self):
        """初始化AI对话服务"""
        self.client = Ark(api_key=AI_MODEL_CONFIG['api_key'])
        self.model = AI_MODEL_CONFIG['model']
        self.vision_model = AI_MODEL_CONFIG['vision_model']
        self.default_max_tokens = CHAT_CONFIG['max_tokens']
        self.default_temperature = CHAT_CONFIG['temperature']
    
    def chat(self, 
             user_message: str,
             conversation_history: Optional[List[Dict[str, str]]] = None,
             system_prompt_type: str = 'default',
             custom_system_prompt: Optional[str] = None,
             max_tokens: Optional[int] = None,
             temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        进行AI对话
        
        Args:
            user_message: 用户输入的消息
            conversation_history: 对话历史记录，格式为[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            system_prompt_type: 系统提示词类型
            custom_system_prompt: 自定义系统提示词
            max_tokens: 最大输出token数
            temperature: 温度参数
            
        Returns:
            对话结果字典
        """
        try:
            # 设置默认参数
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # 选择系统提示词
            if custom_system_prompt:
                system_prompt = custom_system_prompt
            else:
                system_prompt = CHAT_SYSTEM_PROMPTS.get(
                    system_prompt_type, 
                    CHAT_SYSTEM_PROMPTS['default']
                )
            
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史
            if conversation_history:
                # 验证对话历史格式
                valid_history = self._validate_conversation_history(conversation_history)
                if valid_history:
                    messages.extend(valid_history)
                else:
                    logger.warning("对话历史格式无效，将忽略历史记录")
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用大模型API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 提取AI回复
            ai_response = completion.choices[0].message.content
            
            
            return {
                'success': True,
                'response': ai_response,
                'model_used': self.model,
                'system_prompt_type': system_prompt_type,
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'conversation_length': len(messages) - 1,  # 减去system message
                'suggested_next_history': self._build_suggested_history(
                    conversation_history, user_message, ai_response
                )
            }
            
        except Exception as e:
            logger.error(f"AI对话失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.model
            }
    
    
    def _validate_conversation_history(self, history: List[Dict[str, str]]) -> Optional[List[Dict[str, str]]]:
        """
        验证对话历史格式
        
        Args:
            history: 对话历史列表
            
        Returns:
            验证后的历史记录或None（如果格式无效）
        """
        if not isinstance(history, list):
            return None
        
        valid_history = []
        for i, message in enumerate(history):
            if not isinstance(message, dict):
                continue
            
            role = message.get('role')
            content = message.get('content')
            
            if role in ['user', 'assistant'] and content and isinstance(content, str):
                valid_history.append({
                    'role': role,
                    'content': content.strip()
                })
            else:
                logger.warning(f"跳过无效的消息格式: {message}")
        
        return valid_history if valid_history else None
    
    def _build_suggested_history(self, 
                                current_history: Optional[List[Dict[str, str]]],
                                user_message: str,
                                ai_response: str) -> List[Dict[str, str]]:
        """
        构建建议的对话历史（供客户端参考）
        
        Args:
            current_history: 当前对话历史
            user_message: 用户消息
            ai_response: AI回复
            
        Returns:
            建议的完整对话历史
        """
        suggested_history = current_history or []
        
        # 添加当前对话轮次
        suggested_history.append({"role": "user", "content": user_message})
        suggested_history.append({"role": "assistant", "content": ai_response})
        
        # 限制历史长度
        max_length = CHAT_CONFIG['max_history_length']
        if len(suggested_history) > max_length:
            # 保留最近的对话，优先保留assistant的回复
            suggested_history = suggested_history[-max_length:]
        
        return suggested_history
    
    def chat_with_images(self, 
                        user_message: str,
                        image_ids: List[str],
                        conversation_history: Optional[List[Dict[str, str]]] = None,
                        image_prompt_type: str = 'default',
                        custom_image_prompt: Optional[str] = None,
                        max_tokens: Optional[int] = None,
                        temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        带图片的AI对话
        
        Args:
            user_message: 用户输入的消息
            image_ids: 图片ID列表
            conversation_history: 对话历史记录
            image_prompt_type: 图片理解提示词类型
            custom_image_prompt: 自定义图片理解提示词
            max_tokens: 最大输出token数
            temperature: 温度参数
            
        Returns:
            对话结果字典
        """
        try:
            # 设置默认参数
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # 验证图片ID
            if not image_ids:
                return {
                    'success': False,
                    'error': '图片ID列表不能为空'
                }
            
            # 获取图片信息
            image_data_urls = []
            for image_id in image_ids:
                data_url = ai_image_service.get_image_data_url(image_id)
                if data_url:
                    image_data_urls.append(data_url)
                else:
                    logger.warning(f"图片ID不存在或已过期: {image_id}")
            
            if not image_data_urls:
                return {
                    'success': False,
                    'error': '所有图片ID都无效或已过期'
                }
            
            # 选择图片理解提示词
            if custom_image_prompt:
                image_prompt = custom_image_prompt
            else:
                image_prompt = IMAGE_PROMPTS.get(
                    image_prompt_type, 
                    IMAGE_PROMPTS['default']
                )
            
            # 构建消息内容
            content = []
            
            # 添加图片
            for data_url in image_data_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": data_url}
                })
            
            # 添加文本
            if user_message:
                content.append({
                    "type": "text",
                    "text": user_message
                })
            else:
                content.append({
                    "type": "text",
                    "text": image_prompt
                })
            
            # 构建消息列表
            messages = []
            
            # 添加对话历史
            if conversation_history:
                valid_history = self._validate_conversation_history(conversation_history)
                if valid_history:
                    messages.extend(valid_history)
                else:
                    logger.warning("对话历史格式无效，将忽略历史记录")
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": content
            })
            
            # 调用图片理解模型
            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 提取AI回复
            ai_response = completion.choices[0].message.content
            
            return {
                'success': True,
                'response': ai_response,
                'model_used': self.vision_model,
                'image_prompt_type': image_prompt_type,
                'images_processed': len(image_data_urls),
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'conversation_length': len(messages),
                'suggested_next_history': self._build_suggested_history(
                    conversation_history, user_message, ai_response
                )
            }
            
        except Exception as e:
            logger.error(f"图片对话失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.vision_model
            }
    
    def get_available_system_prompts(self) -> Dict[str, str]:
        """
        获取可用的系统提示词类型
        
        Returns:
            提示词类型和描述的字典
        """
        return CHAT_SYSTEM_PROMPTS
    
    def get_available_image_prompts(self) -> Dict[str, str]:
        """
        获取可用的图片理解提示词类型
        
        Returns:
            图片提示词类型和描述的字典
        """
        return IMAGE_PROMPTS
    
    def stream_chat(self, 
                   user_message: str,
                   conversation_history: Optional[List[Dict[str, str]]] = None,
                   system_prompt_type: str = 'default',
                   custom_system_prompt: Optional[str] = None,
                   max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None):
        """
        流式AI对话
        
        Args:
            user_message: 用户输入的消息
            conversation_history: 对话历史记录
            system_prompt_type: 系统提示词类型
            custom_system_prompt: 自定义系统提示词
            max_tokens: 最大输出token数
            temperature: 温度参数
            
        Yields:
            流式响应数据块
        """
        try:
            # 设置默认参数
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # 选择系统提示词
            if custom_system_prompt:
                system_prompt = custom_system_prompt
            else:
                system_prompt = CHAT_SYSTEM_PROMPTS.get(
                    system_prompt_type, 
                    CHAT_SYSTEM_PROMPTS['default']
                )
            
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史
            if conversation_history:
                valid_history = self._validate_conversation_history(conversation_history)
                if valid_history:
                    messages.extend(valid_history)
                else:
                    logger.warning("对话历史格式无效，将忽略历史记录")
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用流式大模型API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            # 流式返回响应
            for chunk in completion:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield {
                        'type': 'content',
                        'content': delta.content,
                        'model': self.model,
                        'system_prompt_type': system_prompt_type
                    }
                elif hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                    yield {
                        'type': 'done',
                        'finish_reason': chunk.choices[0].finish_reason,
                        'model': self.model,
                        'tokens_used': chunk.usage.total_tokens if chunk.usage else None
                    }
            
        except Exception as e:
            logger.error(f"流式AI对话失败: {str(e)}")
            yield {
                'type': 'error',
                'error': str(e),
                'model': self.model
            }
    
    def stream_chat_with_images(self, 
                               user_message: str,
                               image_ids: List[str],
                               conversation_history: Optional[List[Dict[str, str]]] = None,
                               image_prompt_type: str = 'default',
                               custom_image_prompt: Optional[str] = None,
                               max_tokens: Optional[int] = None,
                               temperature: Optional[float] = None):
        """
        流式带图片的AI对话
        
        Args:
            user_message: 用户输入的消息
            image_ids: 图片ID列表
            conversation_history: 对话历史记录
            image_prompt_type: 图片理解提示词类型
            custom_image_prompt: 自定义图片理解提示词
            max_tokens: 最大输出token数
            temperature: 温度参数
            
        Yields:
            流式响应数据块
        """
        try:
            # 设置默认参数
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # 验证图片ID
            if not image_ids:
                yield {
                    'type': 'error',
                    'error': '图片ID列表不能为空',
                    'model': self.vision_model
                }
                return
            
            # 获取图片信息
            image_data_urls = []
            for image_id in image_ids:
                data_url = ai_image_service.get_image_data_url(image_id)
                if data_url:
                    image_data_urls.append(data_url)
                else:
                    logger.warning(f"图片ID不存在或已过期: {image_id}")
            
            if not image_data_urls:
                yield {
                    'type': 'error',
                    'error': '所有图片ID都无效或已过期',
                    'model': self.vision_model
                }
                return
            
            # 选择图片理解提示词
            if custom_image_prompt:
                image_prompt = custom_image_prompt
            else:
                image_prompt = IMAGE_PROMPTS.get(
                    image_prompt_type, 
                    IMAGE_PROMPTS['default']
                )
            
            # 构建消息内容
            content = []
            
            # 添加图片
            for data_url in image_data_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": data_url}
                })
            
            # 添加文本
            if user_message:
                content.append({
                    "type": "text",
                    "text": user_message
                })
            else:
                content.append({
                    "type": "text",
                    "text": image_prompt
                })
            
            # 构建消息列表
            messages = []
            
            # 添加对话历史
            if conversation_history:
                valid_history = self._validate_conversation_history(conversation_history)
                if valid_history:
                    messages.extend(valid_history)
                else:
                    logger.warning("对话历史格式无效，将忽略历史记录")
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": content
            })
            
            # 调用流式图片理解模型
            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            # 流式返回响应
            for chunk in completion:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield {
                        'type': 'content',
                        'content': delta.content,
                        'model': self.vision_model,
                        'image_prompt_type': image_prompt_type,
                        'images_processed': len(image_data_urls)
                    }
                elif hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                    yield {
                        'type': 'done',
                        'finish_reason': chunk.choices[0].finish_reason,
                        'model': self.vision_model,
                        'tokens_used': chunk.usage.total_tokens if chunk.usage else None
                    }
            
        except Exception as e:
            logger.error(f"流式图片对话失败: {str(e)}")
            yield {
                'type': 'error',
                'error': str(e),
                'model': self.vision_model
            }

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查，测试API连接
        
        Returns:
            健康状态信息
        """
        try:
            # 发送一个简单的测试请求
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个测试助手"},
                    {"role": "user", "content": "你好"}
                ],
                max_tokens=10
            )
            
            return {
                'status': 'healthy',
                'model': self.model,
                'vision_model': self.vision_model,
                'api_key_configured': bool(AI_MODEL_CONFIG['api_key']),
                'response_time': 'normal'
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'model': self.model,
                'vision_model': self.vision_model,
                'api_key_configured': bool(AI_MODEL_CONFIG['api_key'])
            }


# 创建全局服务实例
ai_chat_service = AIChatService()
