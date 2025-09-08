#!/usr/bin/env python3
"""
Excel题目上传工具
用于解析Excel题目表格并上传到知识问答系统
"""

import os
import json
import requests
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class ExcelQuestionUploader:
    """Excel题目上传工具类"""
    
    def __init__(self, server_url=None, api_key=None):
        if not server_url:
            raise ValueError("必须提供服务器地址 (server_url)")
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Excel-Question-Uploader/1.0'
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        self.session.headers.update(headers)
        
        # 题目类型映射
        self.question_type_mapping = {
            '单选题': 'choice_single',
            '多选题': 'choice_multiple',
            '填空题': 'fill',
            'choice_single': 'choice_single',
            'choice_multiple': 'choice_multiple',
            'fill': 'fill'
        }
        
        # 分类映射
        self.category_mapping = {
            '党史': 'party_history',
            '理论': 'theory',
            'party_history': 'party_history',
            'theory': 'theory'
        }
        
        # 难度映射
        self.difficulty_mapping = {
            '简单': 'easy',
            '中等': 'medium',
            '困难': 'hard',
            'easy': 'easy',
            'medium': 'medium',
            'hard': 'hard'
        }
    
    def parse_excel_file(self, excel_file_path: str) -> List[Dict[str, Any]]:
        """
        解析Excel文件
        
        Args:
            excel_file_path: Excel文件路径
        
        Returns:
            List[Dict]: 解析后的题目数据列表
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_file_path)
            
            # 检查必要的列
            required_columns = ['题目内容', '题目类型', '分类']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Excel文件缺少必要的列: {missing_columns}")
            
            questions = []
            
            for index, row in df.iterrows():
                try:
                    question_data = self._parse_question_row(row, index + 1)
                    if question_data:
                        questions.append(question_data)
                except Exception as e:
                    print(f"⚠️  第 {index + 1} 行解析失败: {str(e)}")
                    continue
            
            return questions
            
        except Exception as e:
            raise Exception(f"解析Excel文件失败: {str(e)}")
    
    def _parse_question_row(self, row: pd.Series, row_number: int) -> Optional[Dict[str, Any]]:
        """
        解析单行题目数据
        
        Args:
            row: Excel行数据
            row_number: 行号
        
        Returns:
            Dict: 题目数据
        """
        # 基本字段
        question_text = str(row.get('题目内容', '')).strip()
        if not question_text or question_text == 'nan':
            raise ValueError("题目内容不能为空")
        
        question_type_raw = str(row.get('题目类型', '')).strip()
        question_type = self.question_type_mapping.get(question_type_raw)
        if not question_type:
            raise ValueError(f"无效的题目类型: {question_type_raw}")
        
        category_raw = str(row.get('分类', '')).strip()
        category = self.category_mapping.get(category_raw)
        if not category:
            raise ValueError(f"无效的分类: {category_raw}")
        
        # 可选字段
        difficulty_raw = str(row.get('难度', '中等')).strip()
        difficulty = self.difficulty_mapping.get(difficulty_raw, 'medium')
        
        explanation = str(row.get('答案解析', '')).strip()
        if explanation == 'nan':
            explanation = ''
        
        tags = str(row.get('标签', '')).strip()
        if tags == 'nan':
            tags = ''
        
        # 构建题目数据
        question_data = {
            'question_text': question_text,
            'question_type': question_type,
            'category': category,
            'difficulty': difficulty,
            'explanation': explanation,
            'tags': tags
        }
        
        # 处理选择题选项
        if question_type in ['choice_single', 'choice_multiple']:
            options = self._parse_choice_options(row)
            if not options:
                raise ValueError("选择题必须提供选项")
            question_data['options'] = options
        
        # 处理填空题答案
        elif question_type == 'fill':
            correct_answer = str(row.get('正确答案', '')).strip()
            if not correct_answer or correct_answer == 'nan':
                raise ValueError("填空题必须提供正确答案")
            question_data['correct_answer'] = correct_answer
        
        return question_data
    
    def _parse_choice_options(self, row: pd.Series) -> List[Dict[str, Any]]:
        """
        解析选择题选项
        
        Args:
            row: Excel行数据
        
        Returns:
            List[Dict]: 选项列表
        """
        options = []
        
        # 尝试解析选项列（选项A、选项B、选项C、选项D等）
        option_columns = [col for col in row.index if col.startswith('选项')]
        
        if option_columns:
            # 按列名排序
            option_columns.sort()
            
            for col in option_columns:
                option_text = str(row[col]).strip()
                if option_text and option_text != 'nan':
                    # 检查是否为正确答案
                    is_correct = self._check_correct_option(row, col)
                    
                    options.append({
                        'text': option_text,
                        'is_correct': is_correct
                    })
        
        # 如果没有找到选项列，尝试解析"选项"列（JSON格式）
        if not options:
            options_text = str(row.get('选项', '')).strip()
            if options_text and options_text != 'nan':
                try:
                    # 尝试解析JSON格式的选项
                    if options_text.startswith('[') and options_text.endswith(']'):
                        options = json.loads(options_text)
                    else:
                        # 尝试解析简单格式：A.选项1|B.选项2|C.选项3|D.选项4
                        options = self._parse_simple_options(options_text)
                except Exception as e:
                    raise ValueError(f"选项格式错误: {str(e)}")
        
        return options
    
    def _check_correct_option(self, row: pd.Series, option_column: str) -> bool:
        """
        检查选项是否为正确答案
        
        Args:
            row: Excel行数据
            option_column: 选项列名
        
        Returns:
            bool: 是否为正确答案
        """
        # 检查"正确答案"列
        correct_answer = str(row.get('正确答案', '')).strip()
        if correct_answer and correct_answer != 'nan':
            # 提取选项标识符（A、B、C、D等）
            option_letter = option_column.replace('选项', '').strip()
            return option_letter in correct_answer
        
        # 检查"正确选项"列
        correct_options = str(row.get('正确选项', '')).strip()
        if correct_options and correct_options != 'nan':
            option_letter = option_column.replace('选项', '').strip()
            return option_letter in correct_options
        
        return False
    
    def _parse_simple_options(self, options_text: str) -> List[Dict[str, Any]]:
        """
        解析简单格式的选项
        
        Args:
            options_text: 选项文本，格式如：A.选项1|B.选项2|C.选项3|D.选项4
        
        Returns:
            List[Dict]: 选项列表
        """
        options = []
        
        # 按|分割选项
        option_parts = options_text.split('|')
        
        for part in option_parts:
            part = part.strip()
            if not part:
                continue
            
            # 匹配格式：A.选项内容
            match = re.match(r'^([A-Z])\.(.+)$', part)
            if match:
                letter = match.group(1)
                text = match.group(2).strip()
                
                options.append({
                    'text': text,
                    'is_correct': False  # 需要单独指定正确答案
                })
        
        return options
    
    def upload_questions(self, questions: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, Any]:
        """
        上传题目到服务器
        
        Args:
            questions: 题目数据列表
            batch_size: 批量上传大小
        
        Returns:
            Dict: 上传结果
        """
        total_questions = len(questions)
        success_count = 0
        failed_count = 0
        all_errors = []
        
        print(f"📤 开始上传 {total_questions} 道题目...")
        
        # 分批上传
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_number = i // batch_size + 1
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            print(f"📦 上传第 {batch_number}/{total_batches} 批 ({len(batch)} 道题目)...")
            
            try:
                response = self.session.post(
                    f"{self.server_url}/api/knowledge-quiz/batch-upload-questions/",
                    json={'questions': batch}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        batch_success = result['data']['success_count']
                        batch_failed = result['data']['failed_count']
                        batch_errors = result['data']['errors']
                        
                        success_count += batch_success
                        failed_count += batch_failed
                        all_errors.extend(batch_errors)
                        
                        print(f"✅ 第 {batch_number} 批上传完成: 成功 {batch_success}, 失败 {batch_failed}")
                    else:
                        failed_count += len(batch)
                        all_errors.append(f"第 {batch_number} 批: {result.get('error', '未知错误')}")
                        print(f"❌ 第 {batch_number} 批上传失败: {result.get('error', '未知错误')}")
                else:
                    failed_count += len(batch)
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    all_errors.append(f"第 {batch_number} 批: {error_msg}")
                    print(f"❌ 第 {batch_number} 批上传失败: {error_msg}")
                    
            except Exception as e:
                failed_count += len(batch)
                error_msg = f"网络错误: {str(e)}"
                all_errors.append(f"第 {batch_number} 批: {error_msg}")
                print(f"❌ 第 {batch_number} 批上传失败: {error_msg}")
        
        # 输出最终结果
        print(f"\n📊 上传完成:")
        print(f"   总题目数: {total_questions}")
        print(f"   成功: {success_count}")
        print(f"   失败: {failed_count}")
        
        if all_errors:
            print(f"\n❌ 错误详情:")
            for error in all_errors:
                print(f"   - {error}")
        
        return {
            'total': total_questions,
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': all_errors
        }
    
    def validate_excel_template(self, excel_file_path: str) -> bool:
        """
        验证Excel模板格式
        
        Args:
            excel_file_path: Excel文件路径
        
        Returns:
            bool: 是否为有效模板
        """
        try:
            df = pd.read_excel(excel_file_path)
            
            # 检查必要的列
            required_columns = ['题目内容', '题目类型', '分类']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ 缺少必要的列: {missing_columns}")
                return False
            
            # 检查题目类型列的值
            question_types = df['题目类型'].dropna().unique()
            invalid_types = [t for t in question_types if t not in self.question_type_mapping]
            if invalid_types:
                print(f"❌ 无效的题目类型: {invalid_types}")
                print(f"   支持的题目类型: {list(self.question_type_mapping.keys())}")
                return False
            
            # 检查分类列的值
            categories = df['分类'].dropna().unique()
            invalid_categories = [c for c in categories if c not in self.category_mapping]
            if invalid_categories:
                print(f"❌ 无效的分类: {invalid_categories}")
                print(f"   支持的分类: {list(self.category_mapping.keys())}")
                return False
            
            print("✅ Excel模板格式验证通过")
            return True
            
        except Exception as e:
            print(f"❌ 验证Excel模板失败: {str(e)}")
            return False
    
    def create_excel_template(self, output_path: str):
        """
        创建Excel模板文件
        
        Args:
            output_path: 输出文件路径
        """
        # 创建示例数据
        sample_data = [
            {
                '题目内容': '中国共产党成立于哪一年？',
                '题目类型': '单选题',
                '分类': '党史',
                '难度': '简单',
                '选项A': '1921年',
                '选项B': '1922年',
                '选项C': '1923年',
                '选项D': '1924年',
                '正确答案': 'A',
                '答案解析': '中国共产党成立于1921年7月1日。',
                '标签': '党史,建党,基础知识'
            },
            {
                '题目内容': '以下哪些是中国特色社会主义理论体系的重要组成部分？',
                '题目类型': '多选题',
                '分类': '理论',
                '难度': '中等',
                '选项A': '邓小平理论',
                '选项B': '"三个代表"重要思想',
                '选项C': '科学发展观',
                '选项D': '习近平新时代中国特色社会主义思想',
                '正确答案': 'ABCD',
                '答案解析': '中国特色社会主义理论体系包括邓小平理论、"三个代表"重要思想、科学发展观和习近平新时代中国特色社会主义思想。',
                '标签': '理论,中国特色社会主义,理论体系'
            },
            {
                '题目内容': '马克思主义的三大组成部分是马克思主义哲学、马克思主义政治经济学和______。',
                '题目类型': '填空题',
                '分类': '理论',
                '难度': '中等',
                '正确答案': '科学社会主义',
                '答案解析': '马克思主义的三大组成部分是马克思主义哲学、马克思主义政治经济学和科学社会主义。',
                '标签': '理论,马克思主义,基础知识'
            }
        ]
        
        # 创建DataFrame
        df = pd.DataFrame(sample_data)
        
        # 保存为Excel文件
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        print(f"✅ Excel模板已创建: {output_path}")
        print("📋 模板包含以下列:")
        print("   - 题目内容 (必填): 题目的具体内容")
        print("   - 题目类型 (必填): 单选题/多选题/填空题")
        print("   - 分类 (必填): 党史/理论")
        print("   - 难度 (可选): 简单/中等/困难，默认为中等")
        print("   - 选项A/B/C/D (选择题必填): 选项内容")
        print("   - 正确答案 (必填): 正确答案标识")
        print("   - 答案解析 (可选): 题目的详细解析")
        print("   - 标签 (可选): 用逗号分隔的标签")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Excel题目上传工具')
    parser.add_argument('--server', help='服务器地址 (上传时必填)')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--batch-size', type=int, default=10, help='批量上传大小')
    parser.add_argument('--validate-only', action='store_true', help='仅验证Excel格式，不上传')
    parser.add_argument('--create-template', help='创建Excel模板文件')
    parser.add_argument('excel_file', nargs='?', help='Excel文件路径')
    
    args = parser.parse_args()
    
    # 创建模板功能（不需要服务器地址）
    if args.create_template:
        uploader = ExcelQuestionUploader.__new__(ExcelQuestionUploader)
        uploader.create_excel_template(args.create_template)
        return
    
    # 其他功能需要服务器地址
    if not args.server:
        print("❌ 必须提供服务器地址")
        print("💡 使用 --server 参数指定服务器地址")
        print("💡 使用 --create-template 参数创建模板文件（不需要服务器地址）")
        return
    
    # 创建上传工具实例
    uploader = ExcelQuestionUploader(server_url=args.server, api_key=args.api_key)
    
    # 检查Excel文件
    if not args.excel_file:
        print("❌ 请提供Excel文件路径")
        print("💡 使用 --create-template 参数创建模板文件")
        return
    
    excel_file = Path(args.excel_file)
    if not excel_file.exists():
        print(f"❌ Excel文件不存在: {excel_file}")
        return
    
    try:
        # 验证Excel格式
        if not uploader.validate_excel_template(str(excel_file)):
            return
        
        # 仅验证模式
        if args.validate_only:
            print("✅ Excel格式验证通过，未进行上传")
            return
        
        # 解析Excel文件
        print(f"📖 解析Excel文件: {excel_file}")
        questions = uploader.parse_excel_file(str(excel_file))
        
        if not questions:
            print("❌ 没有找到有效的题目数据")
            return
        
        print(f"✅ 解析完成，共找到 {len(questions)} 道题目")
        
        # 上传题目
        result = uploader.upload_questions(questions, batch_size=args.batch_size)
        
        # 输出最终结果
        if result['failed_count'] == 0:
            print(f"\n🎉 所有题目上传成功！")
        else:
            print(f"\n⚠️  上传完成，但有 {result['failed_count']} 道题目失败")
    
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")


if __name__ == '__main__':
    main()
