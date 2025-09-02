import requests
import base64
import hashlib
import logging
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin, urlparse
from django.conf import settings
from .redis_service import redis_service

logger = logging.getLogger(__name__)

class ImageCacheService:
    """图片缓存服务"""
    
    def __init__(self):
        self.max_image_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)  # 5MB
        self.supported_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        self.cache_expire_time = 86400 * 7  # 7天过期
    
    def download_and_cache_image(self, image_url, base_url=None):
        """下载并缓存图片到Redis"""
        try:
            # 处理相对URL
            if base_url and not image_url.startswith('http'):
                image_url = urljoin(base_url, image_url)
            
            # 生成图片的唯一标识
            image_id = self._generate_image_id(image_url)
            
            # 检查是否已缓存
            cached_image = self.get_cached_image(image_id)
            if cached_image:
                logger.debug(f"图片已缓存: {image_id}")
                return image_id, cached_image['content_type']
            
            # 下载图片
            logger.info(f"开始下载图片: {image_url}")
            response = requests.get(
                image_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': base_url or 'http://www.people.com.cn/'
                },
                timeout=30,
                stream=True
            )
            
            if response.status_code != 200:
                logger.warning(f"图片下载失败，状态码: {response.status_code} - {image_url}")
                return None, None
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                logger.warning(f"不是有效的图片类型: {content_type} - {image_url}")
                return None, None
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_image_size:
                logger.warning(f"图片文件过大: {content_length} bytes - {image_url}")
                return None, None
            
            # 读取图片数据
            image_data = BytesIO()
            total_size = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)
                if total_size > self.max_image_size:
                    logger.warning(f"图片文件过大: {total_size} bytes - {image_url}")
                    return None, None
                image_data.write(chunk)
            
            image_data.seek(0)
            
            # 验证图片格式
            try:
                with Image.open(image_data) as img:
                    format_name = img.format
                    if format_name not in self.supported_formats:
                        logger.warning(f"不支持的图片格式: {format_name} - {image_url}")
                        return None, None
                    
                    # 获取图片信息
                    width, height = img.size
                    logger.debug(f"图片信息: {width}x{height}, {format_name} - {image_url}")
                    
            except Exception as e:
                logger.warning(f"图片格式验证失败: {str(e)} - {image_url}")
                return None, None
            
            # 重置数据流位置
            image_data.seek(0)
            
            # 编码为base64
            image_base64 = base64.b64encode(image_data.getvalue()).decode('utf-8')
            
            # 缓存到Redis
            image_cache_data = {
                'url': image_url,
                'content_type': content_type,
                'data': image_base64,
                'size': total_size,
                'width': width,
                'height': height,
                'format': format_name
            }
            
            cache_key = f"image:{image_id}"
            import json
            redis_service.redis_client.setex(
                cache_key, 
                self.cache_expire_time, 
                json.dumps(image_cache_data, ensure_ascii=False)
            )
            
            logger.info(f"图片缓存成功: {image_id} ({total_size} bytes)")
            return image_id, content_type
            
        except requests.RequestException as e:
            logger.error(f"下载图片时网络错误: {str(e)} - {image_url}")
            return None, None
        except Exception as e:
            logger.error(f"缓存图片时出错: {str(e)} - {image_url}")
            return None, None
    
    def get_cached_image(self, image_id):
        """获取缓存的图片"""
        try:
            cache_key = f"image:{image_id}"
            cached_data = redis_service.redis_client.get(cache_key)
            
            if cached_data:
                import json
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"获取缓存图片失败: {str(e)} - {image_id}")
            return None
    
    def get_image_data(self, image_id):
        """获取图片的二进制数据"""
        try:
            cached_image = self.get_cached_image(image_id)
            if cached_image:
                image_data = base64.b64decode(cached_image['data'])
                return image_data, cached_image['content_type']
            return None, None
            
        except Exception as e:
            logger.error(f"获取图片数据失败: {str(e)} - {image_id}")
            return None, None
    
    def process_article_images(self, content, base_url):
        """处理文章中的所有图片，下载并替换为缓存链接"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            images = soup.find_all('img')
            
            image_mapping = {}  # 原链接 -> 缓存ID的映射
            
            for img in images:
                src = img.get('src')
                if not src:
                    continue
                
                # 下载并缓存图片
                image_id, content_type = self.download_and_cache_image(src, base_url)
                
                if image_id:
                    # 记录映射关系
                    image_mapping[src] = {
                        'image_id': image_id,
                        'content_type': content_type,
                        'alt': img.get('alt', ''),
                        'original_url': src
                    }
                    logger.info(f"图片处理成功: {src} -> {image_id}")
                else:
                    logger.warning(f"图片处理失败: {src}")
            
            return image_mapping
            
        except Exception as e:
            logger.error(f"处理文章图片时出错: {str(e)}")
            return {}
    
    def _generate_image_id(self, image_url):
        """生成图片的唯一ID"""
        # 使用URL的MD5哈希作为ID
        return hashlib.md5(image_url.encode('utf-8')).hexdigest()
    
    def get_cache_stats(self):
        """获取图片缓存统计信息"""
        try:
            # 获取所有图片缓存键
            pattern = "image:*"
            keys = redis_service.redis_client.keys(pattern)
            
            total_images = len(keys)
            total_size = 0
            
            # 计算总大小（采样方式，避免性能问题）
            sample_keys = keys[:min(100, len(keys))]
            for key in sample_keys:
                try:
                    cached_data = redis_service.redis_client.get(key)
                    if cached_data:
                        import json
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
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {
                'total_images': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
    
    def clear_image_cache(self, older_than_days=7):
        """清理过期的图片缓存"""
        try:
            pattern = "image:*"
            keys = redis_service.redis_client.keys(pattern)
            
            deleted_count = 0
            for key in keys:
                # Redis会自动清理过期的键，这里主要是手动清理
                if not redis_service.redis_client.exists(key):
                    deleted_count += 1
            
            logger.info(f"清理了 {deleted_count} 个过期图片缓存")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理图片缓存失败: {str(e)}")
            return 0

# 全局图片缓存服务实例
image_cache_service = ImageCacheService()
