import asyncio
import edge_tts
import os
import tempfile
import time
from typing import AsyncGenerator, Optional
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """TTS文本转语音服务"""
    
    def __init__(self):
        self.available_voices = {
            'zh-CN-XiaoxiaoNeural': '晓晓(女声)',
            'zh-CN-YunxiNeural': '云希(男声)',
            'zh-CN-YunyangNeural': '云扬(男声)',
            'zh-CN-XiaoyiNeural': '晓伊(女声)',
            'zh-CN-YunfengNeural': '云枫(男声)',
            'zh-CN-XiaohanNeural': '晓涵(女声)',
            'zh-CN-XiaomoNeural': '晓墨(女声)',
            'zh-CN-XiaoxuanNeural': '晓萱(女声)',
            'zh-CN-XiaoyanNeural': '晓颜(女声)',
            'zh-CN-YunxiNeural': '云希(男声)',
        }
        
        self.default_voice = 'zh-CN-XiaoxiaoNeural'
        self.default_language = 'zh-CN'
    
    async def get_available_voices(self) -> dict:
        """获取可用的语音列表"""
        try:
            voices = await edge_tts.list_voices()
            # 过滤中文语音
            chinese_voices = {}
            for voice in voices:
                if voice['Locale'].startswith('zh'):
                    chinese_voices[voice['ShortName']] = voice['LocalName']
            
            return chinese_voices
        except Exception as e:
            logger.error(f"获取语音列表失败: {str(e)}")
            return self.available_voices
    
    async def text_to_speech_stream(self, text: str, voice: str = None, 
                                   language: str = None) -> AsyncGenerator[bytes, None]:
        """
        流式文本转语音
        
        Args:
            text: 要转换的文本
            voice: 语音类型
            language: 语言
            
        Yields:
            bytes: 音频数据块
        """
        if not voice:
            voice = self.default_voice
        if not language:
            language = self.default_language
            
        try:
            logger.info(f"开始TTS转换: {text[:50]}... 使用语音: {voice}")
            
            # 分段处理长文本
            segments = self._split_text(text)
            
            for i, segment in enumerate(segments):
                logger.info(f"处理第 {i+1}/{len(segments)} 段文本: {segment[:30]}...")
                
                # 使用edge-tts进行转换
                communicate = edge_tts.Communicate(segment, voice)
                
                # 流式获取音频数据
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        yield chunk["data"]
                    elif chunk["type"] == "WordBoundary":
                        # 可以在这里处理单词边界信息
                        pass
                
                # 段落间短暂停顿
                if i < len(segments) - 1:
                    await asyncio.sleep(0.1)
                    
            logger.info("TTS转换完成")
            
        except Exception as e:
            error_msg = f"TTS转换失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def text_to_speech_file(self, text: str, output_path: str, 
                                 voice: str = None, language: str = None) -> dict:
        """
        文本转语音并保存到文件
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            voice: 语音类型
            language: 语言
            
        Returns:
            dict: 包含文件路径和时长的信息
        """
        if not voice:
            voice = self.default_voice
        if not language:
            language = self.default_language
            
        try:
            logger.info(f"开始TTS转换到文件: {text[:50]}...")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 使用edge-tts进行转换
            communicate = edge_tts.Communicate(text, voice)
            
            # 保存到文件
            await communicate.save(output_path)
            
            # 获取文件信息
            file_size = os.path.getsize(output_path)
            
            logger.info(f"TTS转换完成，文件保存到: {output_path}, 大小: {file_size} bytes")
            
            return {
                'file_path': output_path,
                'file_size': file_size,
                'voice': voice,
                'language': language,
                'text_length': len(text)
            }
            
        except Exception as e:
            error_msg = f"TTS转换到文件失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _split_text(self, text: str, max_length: int = 200) -> list:
        """
        将长文本分段
        
        Args:
            text: 输入文本
            max_length: 每段最大长度
            
        Returns:
            list: 分段后的文本列表
        """
        if len(text) <= max_length:
            return [text]
        
        segments = []
        current_segment = ""
        
        # 按句子分割
        sentences = text.split('。')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果当前段落加上新句子不超过最大长度，则添加
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence + "。"
            else:
                # 如果当前段落不为空，保存它
                if current_segment:
                    segments.append(current_segment)
                
                # 开始新段落
                current_segment = sentence + "。"
        
        # 添加最后一个段落
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    async def get_voice_info(self, voice: str) -> Optional[dict]:
        """获取指定语音的详细信息"""
        try:
            voices = await edge_tts.list_voices()
            for v in voices:
                if v['ShortName'] == voice:
                    return v
            return None
        except Exception as e:
            logger.error(f"获取语音信息失败: {str(e)}")
            return None
    
    def validate_text(self, text: str) -> tuple[bool, str]:
        """
        验证输入文本
        
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not text or not text.strip():
            return False, "文本不能为空"
        
        if len(text) > 5000:
            return False, "文本长度不能超过5000字符"
        
        # 检查是否包含有效的中文字符
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if chinese_chars == 0:
            return False, "文本应包含中文字符"
        
        return True, ""


# 创建全局TTS服务实例
tts_service = TTSService()


