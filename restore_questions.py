#!/usr/bin/env python3
"""
恢复题目数据脚本
从备份的JSON文件中恢复题目数据到新的统一Question模型
"""

import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacy_pi_backend.settings')
django.setup()

from knowledge_quiz.models import Question

def restore_questions():
    """恢复题目数据"""
    try:
        # 读取备份数据
        with open('question_data_backup.json', 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"开始恢复数据...")
        print(f"备份时间: {backup_data.get('backup_time', '未知')}")
        
        # 恢复选择题
        choice_questions = backup_data.get('choice_questions', [])
        print(f"恢复选择题: {len(choice_questions)} 道")
        
        for choice_data in choice_questions:
            # 转换题目类型
            question_type = 'choice_single' if choice_data['question_type'] == 'single' else 'choice_multiple'
            
            Question.objects.create(
                id=choice_data['id'],
                question_text=choice_data['question_text'],
                question_type=question_type,
                difficulty=choice_data['difficulty'],
                category=choice_data['category'],
                explanation=choice_data['explanation'],
                tags=choice_data['tags'],
                options=choice_data['options'],
                correct_answer=None,
                created_at=datetime.fromisoformat(choice_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(choice_data['updated_at'].replace('Z', '+00:00'))
            )
            print(f"  - 恢复选择题 ID: {choice_data['id']}")
        
        # 恢复填空题
        fill_questions = backup_data.get('fill_questions', [])
        print(f"恢复填空题: {len(fill_questions)} 道")
        
        for fill_data in fill_questions:
            Question.objects.create(
                id=fill_data['id'],
                question_text=fill_data['question_text'],
                question_type='fill',
                difficulty=fill_data['difficulty'],
                category=fill_data['category'],
                explanation=fill_data['explanation'],
                tags=fill_data['tags'],
                options=None,
                correct_answer=fill_data['correct_answer'],
                created_at=datetime.fromisoformat(fill_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(fill_data['updated_at'].replace('Z', '+00:00'))
            )
            print(f"  - 恢复填空题 ID: {fill_data['id']}")
        
        print(f"\n数据恢复完成!")
        print(f"总计恢复: {len(choice_questions) + len(fill_questions)} 道题目")
        
        # 验证数据
        total_questions = Question.objects.count()
        print(f"数据库中现有题目总数: {total_questions}")
        
        # 显示题目类型分布
        choice_count = Question.objects.filter(question_type__startswith='choice').count()
        fill_count = Question.objects.filter(question_type='fill').count()
        print(f"选择题: {choice_count} 道")
        print(f"填空题: {fill_count} 道")
        
    except FileNotFoundError:
        print("错误: 找不到备份文件 question_data_backup.json")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    restore_questions()
