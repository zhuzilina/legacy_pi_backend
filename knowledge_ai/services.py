"""
知识AI服务
使用方舟 SDK调用大模型API进行知识相关的AI分析
"""

import logging
import time
from typing import Dict, Any, Optional, Union
from volcenginesdkarkruntime import Ark
from .config import AI_MODEL_CONFIG, KNOWLEDGE_AI_PROMPTS
from .models import QuestionAnalysis
from knowledge_quiz.models import Knowledge, Question

logger = logging.getLogger(__name__)

class KnowledgeAiService:
    """知识AI服务类"""
    
    def __init__(self):
        """初始化知识AI服务"""
        self.client = Ark(api_key=AI_MODEL_CONFIG['api_key'])
        self.model = AI_MODEL_CONFIG['model']
    
    def explain_question(self, 
                        question: Question,
                        max_tokens: int = 2000) -> Dict[str, Any]:
        """
        对题目进行详细解答
        
        Args:
            question: 题目对象（选择题或填空题）
            max_tokens: 最大输出token数
            
        Returns:
            解答结果字典
        """
        start_time = time.time()
        
        try:
            # 构建题目内容
            if question.is_choice_question():
                question_content = self._build_choice_question_content(question)
                analysis_type = 'choice_explanation'
            else:  # FillQuestion
                question_content = self._build_fill_question_content(question)
                analysis_type = 'fill_explanation'
            
            # 获取提示词
            prompt = KNOWLEDGE_AI_PROMPTS['question_explanation']
            full_prompt = f"{prompt}\n\n{question_content}"
            
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
            explanation = completion.choices[0].message.content
            processing_time = time.time() - start_time
            
            # 保存分析记录
            analysis_record = QuestionAnalysis.objects.create(
                question=question,
                analysis_type=analysis_type,
                analysis_content=explanation,
                ai_model_used=self.model,
                tokens_used=completion.usage.total_tokens if completion.usage else None,
                processing_time=processing_time
            )
            
            return {
                'success': True,
                'explanation': explanation,
                'analysis_id': analysis_record.id,
                'model_used': self.model,
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"题目解答失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.model
            }
    
    def generate_open_question(self, 
                              knowledge: Knowledge,
                              question_type: str = 'comprehension',
                              difficulty_level: str = 'medium',
                              max_tokens: int = 1000) -> Dict[str, Any]:
        """
        基于知识内容生成开放性问题
        
        Args:
            knowledge: 知识对象
            question_type: 问题类型 (comprehension, application, analysis, evaluation, creation)
            difficulty_level: 难度等级 (easy, medium, hard)
            max_tokens: 最大输出token数
            
        Returns:
            生成结果字典
        """
        start_time = time.time()
        
        try:
            # 构建知识内容
            knowledge_content = f"知识标题：{knowledge.title}\n\n知识内容：{knowledge.content}"
            
            # 获取提示词并格式化
            prompt_template = KNOWLEDGE_AI_PROMPTS['open_question_generation']
            prompt = prompt_template.format(
                question_type=question_type,
                difficulty_level=difficulty_level
            )
            full_prompt = f"{prompt}\n\n{knowledge_content}"
            
            # 调用大模型API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.8  # 稍高的温度以增加创造性
            )
            
            # 提取结果
            question_text = completion.choices[0].message.content.strip()
            processing_time = time.time() - start_time
            
            # 创建开放性问题记录
            from .models import OpenQuestion
            open_question = OpenQuestion.objects.create(
                knowledge=knowledge,
                question_text=question_text,
                question_type=question_type,
                difficulty_level=difficulty_level
            )
            
            # 保存分析记录
            analysis_record = QuestionAnalysis.objects.create(
                open_question=open_question,
                analysis_type='open_question_generation',
                analysis_content=question_text,
                ai_model_used=self.model,
                tokens_used=completion.usage.total_tokens if completion.usage else None,
                processing_time=processing_time
            )
            
            return {
                'success': True,
                'open_question': {
                    'id': open_question.id,
                    'question_text': question_text,
                    'question_type': question_type,
                    'difficulty_level': difficulty_level,
                    'knowledge_id': knowledge.id,
                    'knowledge_title': knowledge.title
                },
                'analysis_id': analysis_record.id,
                'model_used': self.model,
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"开放性问题生成失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.model
            }
    
    def analyze_answer_relevance(self, 
                                open_question_id: int,
                                user_answer: str,
                                max_tokens: int = 1500) -> Dict[str, Any]:
        """
        分析用户回答与知识点的相关度
        
        Args:
            open_question_id: 开放性问题的ID
            user_answer: 用户的回答
            max_tokens: 最大输出token数
            
        Returns:
            分析结果字典
        """
        start_time = time.time()
        
        try:
            # 获取开放性问题
            from .models import OpenQuestion
            open_question = OpenQuestion.objects.get(id=open_question_id)
            knowledge = open_question.knowledge
            
            # 构建分析内容
            analysis_content = f"""
知识内容：
标题：{knowledge.title}
内容：{knowledge.content}

开放性问题：
{open_question.question_text}

用户回答：
{user_answer}
"""
            
            # 获取提示词
            prompt = KNOWLEDGE_AI_PROMPTS['answer_relevance_analysis']
            full_prompt = f"{prompt}\n\n{analysis_content}"
            
            # 调用大模型API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.6
            )
            
            # 提取结果
            analysis_result = completion.choices[0].message.content
            processing_time = time.time() - start_time
            
            # 解析评分（尝试从结果中提取数字）
            relevance_score = self._extract_relevance_score(analysis_result)
            
            # 创建用户回答记录
            from .models import UserAnswer
            user_answer_record = UserAnswer.objects.create(
                open_question=open_question,
                user_answer=user_answer,
                relevance_score=relevance_score,
                feedback_text=analysis_result,
                analysis_metadata={
                    'model_used': self.model,
                    'tokens_used': completion.usage.total_tokens if completion.usage else None,
                    'processing_time': processing_time
                }
            )
            
            # 保存分析记录
            analysis_record = QuestionAnalysis.objects.create(
                open_question=open_question,
                analysis_type='answer_relevance_analysis',
                analysis_content=analysis_result,
                ai_model_used=self.model,
                tokens_used=completion.usage.total_tokens if completion.usage else None,
                processing_time=processing_time
            )
            
            return {
                'success': True,
                'user_answer_id': user_answer_record.id,
                'relevance_score': relevance_score,
                'feedback_text': analysis_result,
                'analysis_id': analysis_record.id,
                'model_used': self.model,
                'tokens_used': completion.usage.total_tokens if completion.usage else None,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"回答相关度分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.model
            }
    
    def _build_choice_question_content(self, question: Question) -> str:
        """构建选择题内容"""
        content = f"题目：{question.question_text}\n\n"
        content += f"题目类型：{question.get_question_type_display()}\n"
        content += f"难度：{question.get_difficulty_display()}\n"
        content += f"分类：{question.get_category_display()}\n\n"
        
        if question.options:
            content += "选项：\n"
            for i, option in enumerate(question.options, 1):
                content += f"{chr(64+i)}. {option['text']}\n"
        
        if question.explanation:
            content += f"\n原解析：{question.explanation}\n"
        
        return content
    
    def _build_fill_question_content(self, question: Question) -> str:
        """构建填空题内容"""
        content = f"题目：{question.question_text}\n\n"
        content += f"难度：{question.get_difficulty_display()}\n"
        content += f"分类：{question.get_category_display()}\n"
        content += f"正确答案：{question.correct_answer}\n"
        
        if question.explanation:
            content += f"\n原解析：{question.explanation}\n"
        
        return content
    
    def _extract_relevance_score(self, analysis_text: str) -> Optional[int]:
        """从分析文本中提取相关度评分"""
        import re
        
        # 尝试多种模式匹配评分
        patterns = [
            r'相关度评分[：:]\s*(\d+)',
            r'评分[：:]\s*(\d+)',
            r'(\d+)\s*分',
            r'相关度[：:]\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, analysis_text)
            if match:
                score = int(match.group(1))
                # 确保评分在0-100范围内
                return max(0, min(100, score))
        
        # 如果没有找到明确的评分，返回None
        return None
    
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
                'api_key_configured': bool(AI_MODEL_CONFIG['api_key']),
                'response_time': 'normal'
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'model': self.model,
                'api_key_configured': bool(AI_MODEL_CONFIG['api_key'])
            }

# 创建全局服务实例
knowledge_ai_service = KnowledgeAiService()
