"""
AI解读服务
使用OpenAI SDK调用大模型API进行文本解读
"""

import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import AI_MODEL_CONFIG, INTERPRETATION_PROMPTS

logger = logging.getLogger(__name__)

class AIInterpreterService:
    """AI解读服务类"""
    
    def __init__(self):
        """初始化AI解读服务"""
        self.client = OpenAI(
            api_key=AI_MODEL_CONFIG['api_key'],
            base_url=AI_MODEL_CONFIG['base_url'],
        )
        self.model = AI_MODEL_CONFIG['model']
    
    def interpret_text(self, 
                      text: str, 
                      prompt_type: str = 'default',
                      custom_prompt: Optional[str] = None,
                      max_tokens: int = 1000) -> Dict[str, Any]:
        """
        解读文本内容
        
        Args:
            text: 要解读的文本内容
            prompt_type: 提示词类型 (default, summary, analysis, qa)
            custom_prompt: 自定义提示词
            max_tokens: 最大输出token数
            
        Returns:
            解读结果字典
        """
        try:
            # 选择提示词
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = INTERPRETATION_PROMPTS.get(prompt_type, INTERPRETATION_PROMPTS['default'])
            
            # 构建完整的提示词
            full_prompt = f"{prompt}\n\n{text}"
            
            # 调用大模型API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # 提取结果
            interpretation = completion.choices[0].message.content
            
            return {
                'success': True,
                'interpretation': interpretation,
                'model_used': self.model,
                'prompt_type': prompt_type,
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'original_text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"AI解读失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.model
            }
    
    def batch_interpret(self, 
                       texts: list, 
                       prompt_type: str = 'default') -> list:
        """
        批量解读多个文本
        
        Args:
            texts: 文本列表
            prompt_type: 提示词类型
            
        Returns:
            解读结果列表
        """
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.interpret_text(text, prompt_type)
                result['text_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"批量解读第{i}个文本失败: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'text_index': i
                })
        
        return results
    
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
                    {"role": "user", "content": "你好"}
                ],
                max_tokens=10
            )
            
            return {
                'status': 'healthy',
                'model': self.model,
                'base_url': AI_MODEL_CONFIG['base_url'],
                'response_time': 'normal'
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'model': self.model,
                'base_url': AI_MODEL_CONFIG['base_url']
            }

# 创建全局服务实例
ai_interpreter_service = AIInterpreterService()
