"""
AI对话应用图片服务
处理图片上传、缓存和图片理解功能
"""

import base64
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

# 导入 crawler 应用的 Redis 服务
from crawler.redis_service import redis_service
from .config import IMAGE_CONFIG

logger = logging.getLogger(__name__)

class AIImageService:
    """AI对话图片服务类"""
    
    def __init__(self):
        """初始化图片服务"""
        self.max_image_size = IMAGE_CONFIG['max_image_size']
        self.supported_formats = IMAGE_CONFIG['supported_formats']
        self.cache_expire_time = IMAGE_CONFIG['cache_expire_time']
        self.max_images_per_request = IMAGE_CONFIG['max_images_per_request']
    
    def upload_and_cache_image(self, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """
        上传并缓存图片到Redis
        
        Args:
            uploaded_file: Django上传的文件对象
            
        Returns:
            包含图片ID和信息的字典
        """
        try:
            # 验证文件大小
            if uploaded_file.size > self.max_image_size:
                return {
                    'success': False,
                    'error': f'图片文件过大，最大支持 {self.max_image_size // (1024*1024)}MB'
                }
            
            # 读取文件数据
            file_data = uploaded_file.read()
            uploaded_file.seek(0)  # 重置文件指针
            
            # 验证图片格式
            try:
                with Image.open(BytesIO(file_data)) as img:
                    format_name = img.format
                    if format_name not in self.supported_formats:
                        return {
                            'success': False,
                            'error': f'不支持的图片格式: {format_name}，支持的格式: {", ".join(self.supported_formats)}'
                        }
                    
                    # 获取图片信息
                    width, height = img.size
                    logger.info(f"图片信息: {width}x{height}, {format_name}, {len(file_data)} bytes")
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': f'无效的图片文件: {str(e)}'
                }
            
            # 生成图片ID
            image_id = self._generate_image_id(file_data)
            
            # 检查是否已缓存
            if self.get_cached_image(image_id):
                logger.info(f"图片已缓存: {image_id}")
                return {
                    'success': True,
                    'image_id': image_id,
                    'message': '图片已存在缓存中'
                }
            
            # 编码为base64
            image_base64 = base64.b64encode(file_data).decode('utf-8')
            
            # 构建缓存数据
            image_cache_data = {
                'filename': uploaded_file.name,
                'content_type': uploaded_file.content_type,
                'data': image_base64,
                'size': len(file_data),
                'width': width,
                'height': height,
                'format': format_name,
                'uploaded_at': datetime.now().isoformat()
            }
            
            # 缓存到Redis
            cache_key = f"ai_chat_image:{image_id}"
            redis_service.redis_client.setex(
                cache_key, 
                self.cache_expire_time, 
                json.dumps(image_cache_data, ensure_ascii=False)
            )
            
            logger.info(f"图片缓存成功: {image_id} ({len(file_data)} bytes)")
            
            return {
                'success': True,
                'image_id': image_id,
                'image_info': {
                    'filename': uploaded_file.name,
                    'size': len(file_data),
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'content_type': uploaded_file.content_type
                }
            }
            
        except Exception as e:
            logger.error(f"上传图片失败: {str(e)}")
            return {
                'success': False,
                'error': f'上传图片失败: {str(e)}'
            }
    
    def get_cached_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的图片信息
        
        Args:
            image_id: 图片ID
            
        Returns:
            图片信息字典或None
        """
        try:
            cache_key = f"ai_chat_image:{image_id}"
            cached_data = redis_service.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"获取缓存图片失败: {str(e)} - {image_id}")
            return None
    
    def get_image_data_url(self, image_id: str) -> Optional[str]:
        """
        获取图片的data URL格式
        
        Args:
            image_id: 图片ID
            
        Returns:
            data URL字符串或None
        """
        try:
            cached_image = self.get_cached_image(image_id)
            if cached_image:
                content_type = cached_image.get('content_type', 'image/jpeg')
                data = cached_image.get('data', '')
                return f"data:{content_type};base64,{data}"
            return None
            
        except Exception as e:
            logger.error(f"获取图片data URL失败: {str(e)} - {image_id}")
            return None
    
    def batch_upload_images(self, uploaded_files: List[UploadedFile]) -> Dict[str, Any]:
        """
        批量上传图片
        
        Args:
            uploaded_files: 上传的文件列表
            
        Returns:
            批量上传结果
        """
        try:
            if len(uploaded_files) > self.max_images_per_request:
                return {
                    'success': False,
                    'error': f'一次最多只能上传 {self.max_images_per_request} 张图片'
                }
            
            results = []
            success_count = 0
            
            for i, uploaded_file in enumerate(uploaded_files):
                result = self.upload_and_cache_image(uploaded_file)
                result['index'] = i
                results.append(result)
                
                if result['success']:
                    success_count += 1
            
            return {
                'success': success_count > 0,
                'total_count': len(uploaded_files),
                'success_count': success_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"批量上传图片失败: {str(e)}")
            return {
                'success': False,
                'error': f'批量上传图片失败: {str(e)}'
            }
    
    def delete_cached_image(self, image_id: str) -> bool:
        """
        删除缓存的图片
        
        Args:
            image_id: 图片ID
            
        Returns:
            是否删除成功
        """
        try:
            cache_key = f"ai_chat_image:{image_id}"
            result = redis_service.redis_client.delete(cache_key)
            logger.info(f"删除缓存图片: {image_id}, 结果: {bool(result)}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"删除缓存图片失败: {str(e)} - {image_id}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取图片缓存统计信息
        
        Returns:
            缓存统计信息
        """
        try:
            # 获取所有AI对话图片缓存键
            pattern = "ai_chat_image:*"
            keys = redis_service.redis_client.keys(pattern)
            
            total_images = len(keys)
            total_size = 0
            
            # 计算总大小（采样方式，避免性能问题）
            sample_keys = keys[:min(100, len(keys))]
            for key in sample_keys:
                try:
                    cached_data = redis_service.redis_client.get(key)
                    if cached_data:
                        image_info = json.loads(cached_data)
                        total_size += image_info.get('size', 0)
                except:
                    continue
            
            # 如果是采样，估算总大小
            if len(keys) > 100:
                total_size = int(total_size * (len(keys) / len(sample_keys)))
            
            return {
                'total_images': total_images,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_expire_time': self.cache_expire_time,
                'max_image_size': self.max_image_size,
                'supported_formats': self.supported_formats
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {
                'total_images': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'error': str(e)
            }
    
    def _generate_image_id(self, image_data: bytes) -> str:
        """
        生成图片的唯一ID
        
        Args:
            image_data: 图片二进制数据
            
        Returns:
            图片ID
        """
        # 使用图片数据的MD5哈希作为ID
        return hashlib.md5(image_data).hexdigest()

# 创建全局图片服务实例
ai_image_service = AIImageService()
