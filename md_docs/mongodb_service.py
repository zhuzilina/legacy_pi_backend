"""
MongoDB服务类
用于处理MD文档的MongoDB存储
"""

import pymongo
from pymongo import MongoClient
from django.conf import settings
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB服务类"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """连接到MongoDB"""
        try:
            # MongoDB连接配置
            mongo_config = {
                'host': getattr(settings, 'MONGODB_HOST', 'localhost'),
                'port': getattr(settings, 'MONGODB_PORT', 27017),
                'username': getattr(settings, 'MONGODB_USERNAME', 'md_docs_user'),
                'password': getattr(settings, 'MONGODB_PASSWORD', 'md_docs_password'),
                'authSource': getattr(settings, 'MONGODB_AUTH_SOURCE', 'md_docs'),
            }
            
            # 构建连接字符串
            if mongo_config['username'] and mongo_config['password']:
                connection_string = f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/{mongo_config['authSource']}"
            else:
                connection_string = f"mongodb://{mongo_config['host']}:{mongo_config['port']}"
            
            self.client = MongoClient(connection_string)
            self.db = self.client[getattr(settings, 'MONGODB_DATABASE', 'md_docs')]
            
            # 测试连接
            self.client.admin.command('ping')
            logger.info("MongoDB连接成功")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            raise
    
    def save_document(self, document_data):
        """保存文档到MongoDB"""
        try:
            collection = self.db.documents
            
            # 添加时间戳
            document_data['created_at'] = datetime.utcnow()
            document_data['updated_at'] = datetime.utcnow()
            
            # 生成ID
            if 'id' not in document_data:
                document_data['id'] = str(uuid.uuid4())
            
            result = collection.insert_one(document_data)
            logger.info(f"文档保存成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存文档失败: {str(e)}")
            raise
    
    def get_document(self, document_id):
        """获取文档"""
        try:
            collection = self.db.documents
            document = collection.find_one({'id': document_id})
            return document
            
        except Exception as e:
            logger.error(f"获取文档失败: {str(e)}")
            return None
    
    def get_documents_by_category(self, category=None, page=1, page_size=20):
        """根据类别获取文档列表"""
        try:
            collection = self.db.documents
            
            # 构建查询条件
            query = {'is_published': True}
            if category:
                query['category'] = category
            
            # 计算跳过的文档数
            skip = (page - 1) * page_size
            
            # 查询文档
            documents = list(collection.find(query).sort('created_at', -1).skip(skip).limit(page_size))
            total_count = collection.count_documents(query)
            
            return {
                'documents': documents,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"获取文档列表失败: {str(e)}")
            return {'documents': [], 'total_count': 0, 'page': 1, 'page_size': page_size, 'total_pages': 0}
    
    def save_image(self, image_data):
        """保存图片信息到MongoDB"""
        try:
            collection = self.db.images
            
            # 添加时间戳
            image_data['upload_time'] = datetime.utcnow()
            
            # 生成ID
            if 'id' not in image_data:
                image_data['id'] = str(uuid.uuid4())
            
            result = collection.insert_one(image_data)
            logger.info(f"图片信息保存成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存图片信息失败: {str(e)}")
            raise
    
    def get_image(self, image_id):
        """获取图片信息"""
        try:
            collection = self.db.images
            image = collection.find_one({'id': image_id})
            return image
            
        except Exception as e:
            logger.error(f"获取图片信息失败: {str(e)}")
            return None
    
    def update_document(self, document_id, update_data):
        """更新文档"""
        try:
            collection = self.db.documents
            
            # 添加更新时间
            update_data['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(
                {'id': document_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"文档更新成功: {document_id}")
                return True
            else:
                logger.warning(f"文档更新失败，未找到文档: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新文档失败: {str(e)}")
            return False
    
    def delete_document(self, document_id):
        """删除文档"""
        try:
            collection = self.db.documents
            result = collection.delete_one({'id': document_id})
            
            if result.deleted_count > 0:
                logger.info(f"文档删除成功: {document_id}")
                return True
            else:
                logger.warning(f"文档删除失败，未找到文档: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False
    
    def get_statistics(self):
        """获取统计信息"""
        try:
            collection = self.db.documents
            
            total_documents = collection.count_documents({'is_published': True})
            spirit_count = collection.count_documents({'category': 'spirit', 'is_published': True})
            person_count = collection.count_documents({'category': 'person', 'is_published': True})
            party_history_count = collection.count_documents({'category': 'party_history', 'is_published': True})
            
            return {
                'total_documents': total_documents,
                'category_stats': {
                    'spirit': spirit_count,
                    'person': person_count,
                    'party_history': party_history_count
                }
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {
                'total_documents': 0,
                'category_stats': {
                    'spirit': 0,
                    'person': 0,
                    'party_history': 0
                }
            }
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")


# 全局MongoDB服务实例
mongodb_service = MongoDBService()
