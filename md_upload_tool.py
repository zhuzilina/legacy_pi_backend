#!/usr/bin/env python3
"""
MD文档上传工具
用于将本地编写的带图片的MD文档上传到服务器
"""

import os
import re
import json
import uuid
import shutil
import requests
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
import mimetypes


class MDUploadTool:
    """MD文档上传工具类"""
    
    def __init__(self, server_url=None, api_key=None):
        if not server_url:
            raise ValueError("必须提供服务器地址 (server_url)")
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MD-Upload-Tool/1.0'
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        self.session.headers.update(headers)
    
    def upload_md_document(self, md_file_path, category, title=None, author=None, source=None, publish_date=None):
        """
        上传MD文档
        
        Args:
            md_file_path: MD文件路径
            category: 文档类别 (spirit, person, party_history)
            title: 文档标题（如果不提供，从MD文件第一行提取）
            author: 作者
            source: 来源
            publish_date: 发布日期 (YYYY-MM-DD格式)
        
        Returns:
            dict: 上传结果
        """
        try:
            # 读取MD文件
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 处理图片
            processed_content, image_mappings = self._process_images(md_content, md_file_path)
            
            # 提取标题（如果未提供）
            if not title:
                title = self._extract_title_from_md(md_content)
            
            # 计算统计信息
            word_count = len(processed_content)
            image_count = len(image_mappings)
            
            # 构建上传数据
            upload_data = {
                'title': title,
                'category': category,
                'content': processed_content,
                'summary': self._extract_summary_from_md(processed_content),
                'author': author or '',
                'source': source or '',
                'publish_date': publish_date,
                'word_count': word_count,
                'image_count': image_count,
                'is_published': True
            }
            
            # 上传文档
            response = self.session.post(
                f"{self.server_url}/api/md-docs/upload/",
                json=upload_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文档上传成功: {title}")
                print(f"   文档ID: {result.get('document_id')}")
                print(f"   字数: {word_count}")
                print(f"   图片数量: {image_count}")
                return result
            else:
                error_msg = f"上传失败: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"上传过程中出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _process_images(self, md_content, md_file_path):
        """
        处理MD文档中的图片
        
        Args:
            md_content: MD文档内容
            md_file_path: MD文件路径
        
        Returns:
            tuple: (处理后的内容, 图片映射信息)
        """
        md_dir = Path(md_file_path).parent
        image_mappings = {}
        
        # 查找所有图片引用
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, md_content)
        
        processed_content = md_content
        
        for i, (alt_text, image_path) in enumerate(matches):
            # 处理相对路径
            if not image_path.startswith(('http://', 'https://', '/')):
                full_image_path = md_dir / image_path
            else:
                full_image_path = Path(image_path)
            
            if full_image_path.exists():
                # 上传图片到服务器
                image_result = self._upload_image(full_image_path, alt_text)
                if image_result['success']:
                    # 替换MD中的图片路径
                    new_image_path = f"/api/md-docs/image/{image_result['image_id']}/"
                    processed_content = processed_content.replace(
                        f"![{alt_text}]({image_path})",
                        f"![{alt_text}]({new_image_path})"
                    )
                    image_mappings[image_path] = image_result
                    print(f"  📷 图片上传成功: {full_image_path.name}")
                else:
                    print(f"  ⚠️  图片上传失败: {full_image_path.name} - {image_result.get('error')}")
            else:
                print(f"  ⚠️  图片文件不存在: {full_image_path}")
        
        return processed_content, image_mappings
    
    def _upload_image(self, image_path, alt_text):
        """
        上传图片到服务器
        
        Args:
            image_path: 图片文件路径
            alt_text: 图片替代文本
        
        Returns:
            dict: 上传结果
        """
        try:
            # 获取MIME类型
            content_type, _ = mimetypes.guess_type(str(image_path))
            if not content_type:
                content_type = 'application/octet-stream'
            
            # 构建上传数据 - 直接传递文件对象
            with open(image_path, 'rb') as f:
                files = {
                    'image': (Path(image_path).name, f, content_type)
                }
                
                data = {
                    'alt_text': alt_text,
                    'original_filename': Path(image_path).name
                }
                
                # 创建新的请求会话，不包含JSON Content-Type
                upload_session = requests.Session()
                upload_headers = {
                    'User-Agent': 'MD-Upload-Tool/1.0'
                }
                if self.api_key:
                    upload_headers['Authorization'] = f'Bearer {self.api_key}'
                upload_session.headers.update(upload_headers)
                
                # 上传图片到服务器
                response = upload_session.post(
                    f"{self.server_url}/api/md-docs/upload-image/",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'image_id': result.get('image_id'),
                    'filename': result.get('filename')
                }
            else:
                return {
                    'success': False,
                    'error': f"上传失败: {response.status_code} - {response.text}"
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_title_from_md(self, md_content):
        """从MD内容中提取标题"""
        lines = md_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "未命名文档"
    
    def _extract_summary_from_md(self, md_content):
        """从MD内容中提取手动添加的摘要"""
        lines = md_content.split('\n')
        summary_lines = []
        in_summary_section = False
        
        for line in lines:
            line = line.strip()
            
            # 查找摘要部分标记
            if line.startswith('## 摘要') or line.startswith('## 简介') or line.startswith('## 概述'):
                in_summary_section = True
                continue
            
            # 如果遇到下一个二级标题，结束摘要部分
            if in_summary_section and line.startswith('## ') and not line.startswith('## 摘要'):
                break
            
            # 如果在摘要部分，收集内容
            if in_summary_section:
                # 跳过空行
                if not line:
                    continue
                # 跳过图片行
                if line.startswith('!['):
                    continue
                # 跳过分隔线
                if line.startswith('---'):
                    continue
                
                summary_lines.append(line)
        
        # 如果没有找到摘要部分，返回空字符串
        if not summary_lines:
            return ''
        
        summary = ' '.join(summary_lines)
        # 限制摘要长度
        if len(summary) > 500:
            summary = summary[:500] + '...'
        
        return summary
    
    def batch_upload(self, directory_path, category, author=None, source=None):
        """
        批量上传目录中的所有MD文件
        
        Args:
            directory_path: 目录路径
            category: 文档类别
            author: 作者
            source: 来源
        """
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ 目录不存在: {directory_path}")
            return
        
        md_files = list(directory.glob('*.md'))
        if not md_files:
            print(f"❌ 目录中没有找到MD文件: {directory_path}")
            return
        
        print(f"📁 找到 {len(md_files)} 个MD文件")
        
        success_count = 0
        failed_count = 0
        
        for md_file in md_files:
            print(f"\n📄 处理文件: {md_file.name}")
            result = self.upload_md_document(
                md_file,
                category=category,
                author=author,
                source=source
            )
            
            if result.get('success', False):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\n📊 批量上传完成:")
        print(f"   成功: {success_count}")
        print(f"   失败: {failed_count}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MD文档上传工具')
    parser.add_argument('--server', required=True, help='服务器地址 (必填)')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--category', required=True, choices=['spirit', 'person', 'party_history'], help='文档类别')
    parser.add_argument('--author', help='作者')
    parser.add_argument('--source', help='来源')
    parser.add_argument('--publish-date', help='发布日期 (YYYY-MM-DD)')
    parser.add_argument('--batch', action='store_true', help='批量上传模式')
    parser.add_argument('path', help='MD文件路径或目录路径')
    
    args = parser.parse_args()
    
    # 创建上传工具实例
    uploader = MDUploadTool(server_url=args.server, api_key=args.api_key)
    
    if args.batch:
        # 批量上传模式
        uploader.batch_upload(
            directory_path=args.path,
            category=args.category,
            author=args.author,
            source=args.source
        )
    else:
        # 单文件上传模式
        uploader.upload_md_document(
            md_file_path=args.path,
            category=args.category,
            title=None,  # 从文件自动提取
            author=args.author,
            source=args.source,
            publish_date=args.publish_date
        )


if __name__ == '__main__':
    main()
