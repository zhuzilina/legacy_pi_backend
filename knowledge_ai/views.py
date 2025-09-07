"""
知识AI服务API视图
提供题目解答、开放性提问生成、回答相关度分析等功能
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import json

from .services import knowledge_ai_service
from .models import OpenQuestion, UserAnswer
from knowledge_quiz.models import Knowledge, Question

logger = logging.getLogger(__name__)

def get_question_by_id(question_id):
    """
    根据题目ID获取题目对象和类型
    
    Args:
        question_id: 题目ID
        
    Returns:
        tuple: (question_object, question_type) 或 (None, None)
    """
    try:
        question = Question.objects.get(id=question_id)
        if question.is_choice_question():
            return question, 'choice'
        elif question.is_fill_question():
            return question, 'fill'
        return question, 'unknown'
    except Question.DoesNotExist:
        return None, None

@method_decorator(csrf_exempt, name='dispatch')
class QuestionExplanationView(View):
    """题目详细解答API"""
    
    def get(self, request, question_id):
        """
        通过题目ID获取AI对题目的详细解答
        
        Args:
            question_id: 题目ID
            
        Returns:
            JSON响应包含详细解答
        """
        try:
            # 使用辅助函数获取题目
            question, question_type = get_question_by_id(question_id)
            
            if question is None:
                return JsonResponse({
                    'success': False,
                    'error': '题目不存在',
                    'error_code': 'QUESTION_NOT_FOUND'
                }, status=404)
            
            # 调用AI服务进行解答
            result = knowledge_ai_service.explain_question(question)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'question_id': question_id,
                        'question_type': question_type,
                        'explanation': result['explanation'],
                        'analysis_id': result['analysis_id'],
                        'model_used': result['model_used'],
                        'tokens_used': result['tokens_used'],
                        'processing_time': result['processing_time']
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error'],
                    'error_code': 'AI_SERVICE_ERROR'
                }, status=500)
                
        except Exception as e:
            logger.error(f"题目解答API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class OpenQuestionGenerationView(View):
    """开放性提问生成API"""
    
    def post(self, request):
        """
        通过知识ID生成开放性提问
        
        Request Body:
        {
            "knowledge_id": 123,
            "question_type": "comprehension",  # 可选
            "difficulty_level": "medium"       # 可选
        }
        
        Returns:
            JSON响应包含生成的开放性问题
        """
        try:
            # 解析请求数据
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': '无效的JSON格式',
                    'error_code': 'INVALID_JSON'
                }, status=400)
            
            # 验证必需参数
            knowledge_id = data.get('knowledge_id')
            if not knowledge_id:
                return JsonResponse({
                    'success': False,
                    'error': '缺少必需参数: knowledge_id',
                    'error_code': 'MISSING_PARAMETER'
                }, status=400)
            
            # 获取知识对象
            try:
                knowledge = Knowledge.objects.get(id=knowledge_id)
            except Knowledge.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '知识不存在',
                    'error_code': 'KNOWLEDGE_NOT_FOUND'
                }, status=404)
            
            # 获取可选参数
            question_type = data.get('question_type', 'comprehension')
            difficulty_level = data.get('difficulty_level', 'medium')
            
            # 验证参数值
            valid_question_types = ['comprehension', 'application', 'analysis', 'evaluation', 'creation']
            valid_difficulty_levels = ['easy', 'medium', 'hard']
            
            if question_type not in valid_question_types:
                return JsonResponse({
                    'success': False,
                    'error': f'无效的问题类型，可选值: {", ".join(valid_question_types)}',
                    'error_code': 'INVALID_PARAMETER'
                }, status=400)
            
            if difficulty_level not in valid_difficulty_levels:
                return JsonResponse({
                    'success': False,
                    'error': f'无效的难度等级，可选值: {", ".join(valid_difficulty_levels)}',
                    'error_code': 'INVALID_PARAMETER'
                }, status=400)
            
            # 调用AI服务生成开放性问题
            result = knowledge_ai_service.generate_open_question(
                knowledge=knowledge,
                question_type=question_type,
                difficulty_level=difficulty_level
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'data': result['open_question']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error'],
                    'error_code': 'AI_SERVICE_ERROR'
                }, status=500)
                
        except Exception as e:
            logger.error(f"开放性问题生成API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AnswerRelevanceAnalysisView(View):
    """回答相关度分析API"""
    
    def post(self, request):
        """
        分析用户对开放性问题的回答与知识点的相关度
        
        Request Body:
        {
            "open_question_id": 123,
            "user_answer": "用户的回答内容"
        }
        
        Returns:
            JSON响应包含相关度评分和详细反馈
        """
        try:
            # 解析请求数据
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': '无效的JSON格式',
                    'error_code': 'INVALID_JSON'
                }, status=400)
            
            # 验证必需参数
            open_question_id = data.get('open_question_id')
            user_answer = data.get('user_answer')
            
            if not open_question_id:
                return JsonResponse({
                    'success': False,
                    'error': '缺少必需参数: open_question_id',
                    'error_code': 'MISSING_PARAMETER'
                }, status=400)
            
            if not user_answer:
                return JsonResponse({
                    'success': False,
                    'error': '缺少必需参数: user_answer',
                    'error_code': 'MISSING_PARAMETER'
                }, status=400)
            
            # 验证开放性问题是否存在
            try:
                open_question = OpenQuestion.objects.get(id=open_question_id)
            except OpenQuestion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '开放性问题不存在',
                    'error_code': 'OPEN_QUESTION_NOT_FOUND'
                }, status=404)
            
            # 调用AI服务分析回答相关度
            result = knowledge_ai_service.analyze_answer_relevance(
                open_question_id=open_question_id,
                user_answer=user_answer
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'user_answer_id': result['user_answer_id'],
                        'relevance_score': result['relevance_score'],
                        'feedback_text': result['feedback_text'],
                        'analysis_id': result['analysis_id'],
                        'model_used': result['model_used'],
                        'tokens_used': result['tokens_used'],
                        'processing_time': result['processing_time']
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error'],
                    'error_code': 'AI_SERVICE_ERROR'
                }, status=500)
                
        except Exception as e:
            logger.error(f"回答相关度分析API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """健康检查API"""
    
    def get(self, request):
        """检查服务健康状态"""
        try:
            result = knowledge_ai_service.health_check()
            status_code = 200 if result['status'] == 'healthy' else 503
            return JsonResponse(result, status=status_code)
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=503)


@method_decorator(csrf_exempt, name='dispatch')
class OpenQuestionListView(View):
    """开放性问题列表API"""
    
    def get(self, request):
        """
        获取开放性问题列表
        
        Query Parameters:
        - knowledge_id: 知识ID（可选）
        - question_type: 问题类型（可选）
        - difficulty_level: 难度等级（可选）
        - page: 页码（可选，默认1）
        - page_size: 每页数量（可选，默认10）
        """
        try:
            # 获取查询参数
            knowledge_id = request.GET.get('knowledge_id')
            question_type = request.GET.get('question_type')
            difficulty_level = request.GET.get('difficulty_level')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 构建查询
            queryset = OpenQuestion.objects.all()
            
            if knowledge_id:
                queryset = queryset.filter(knowledge_id=knowledge_id)
            if question_type:
                queryset = queryset.filter(question_type=question_type)
            if difficulty_level:
                queryset = queryset.filter(difficulty_level=difficulty_level)
            
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            questions = queryset[start:end]
            
            # 构建响应数据
            data = []
            for question in questions:
                data.append({
                    'id': question.id,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'difficulty_level': question.difficulty_level,
                    'knowledge_id': question.knowledge.id,
                    'knowledge_title': question.knowledge.title,
                    'created_at': question.created_at.isoformat()
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'questions': data,
                    'page': page,
                    'page_size': page_size,
                    'total_count': queryset.count()
                }
            })
            
        except Exception as e:
            logger.error(f"开放性问题列表API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserAnswerListView(View):
    """用户回答列表API"""
    
    def get(self, request):
        """
        获取用户回答列表
        
        Query Parameters:
        - open_question_id: 开放性问题ID（可选）
        - page: 页码（可选，默认1）
        - page_size: 每页数量（可选，默认10）
        """
        try:
            # 获取查询参数
            open_question_id = request.GET.get('open_question_id')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 构建查询
            queryset = UserAnswer.objects.all()
            
            if open_question_id:
                queryset = queryset.filter(open_question_id=open_question_id)
            
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            answers = queryset[start:end]
            
            # 构建响应数据
            data = []
            for answer in answers:
                data.append({
                    'id': answer.id,
                    'open_question_id': answer.open_question.id,
                    'question_text': answer.open_question.question_text,
                    'user_answer': answer.user_answer,
                    'relevance_score': answer.relevance_score,
                    'feedback_text': answer.feedback_text,
                    'created_at': answer.created_at.isoformat()
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'answers': data,
                    'page': page,
                    'page_size': page_size,
                    'total_count': queryset.count()
                }
            })
            
        except Exception as e:
            logger.error(f"用户回答列表API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)
