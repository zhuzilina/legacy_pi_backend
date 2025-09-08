from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
import json
import random
from .models import Knowledge, Question, Answer, QuizSession, DailyQuestion


@csrf_exempt
@require_http_methods(["GET"])
def get_knowledge_list(request):
    """获取知识列表"""
    try:
        # 获取查询参数
        category = request.GET.get('category', '')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 构建查询
        queryset = Knowledge.objects.all()
        
        # 优化分类逻辑：只支持新思想和理论知识两个类别
        if category == 'new_thought':
            # 新思想类别：只返回习近平新时代中国特色社会主义思想
            queryset = queryset.filter(category='xi_jinping_thought')
        elif category == 'theory':
            # 理论知识类别：返回除习近平新时代中国特色社会主义思想外的所有其他分类
            queryset = queryset.exclude(category='xi_jinping_thought')
        elif category:
            # 如果传入了其他分类参数，返回空结果
            queryset = queryset.none()
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 构建响应数据
        knowledge_list = []
        for knowledge in page_obj:
            # 根据实际分类返回对应的显示名称
            if knowledge.category == 'xi_jinping_thought':
                category_display = '新思想'
            else:
                category_display = '理论知识'
            
            knowledge_list.append({
                'id': knowledge.id,
                'title': knowledge.title,
                'content': knowledge.content,
                'category': 'new_thought' if knowledge.category == 'xi_jinping_thought' else 'theory',
                'category_display': category_display,
                'source': knowledge.source,
                'tags': knowledge.get_tags_list(),
                'created_at': knowledge.created_at.isoformat(),
                'updated_at': knowledge.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'knowledge_list': knowledge_list,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_knowledge_detail(request, knowledge_id):
    """获取知识详情"""
    try:
        knowledge = Knowledge.objects.get(id=knowledge_id)
        
        # 根据实际分类返回对应的显示名称
        if knowledge.category == 'xi_jinping_thought':
            category_display = '新思想'
            category = 'new_thought'
        else:
            category_display = '理论知识'
            category = 'theory'
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': knowledge.id,
                'title': knowledge.title,
                'content': knowledge.content,
                'category': category,
                'category_display': category_display,
                'source': knowledge.source,
                'tags': knowledge.get_tags_list(),
                'created_at': knowledge.created_at.isoformat(),
                'updated_at': knowledge.updated_at.isoformat(),
            }
        })
    
    except Knowledge.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '知识条目不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




@csrf_exempt
@require_http_methods(["GET"])
def get_daily_question(request):
    """获取每日一题"""
    try:
        from django.utils import timezone
        from django.utils.dateparse import parse_date
        
        # 获取客户端IP
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1'))
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        today = timezone.now().date()
        
        # 检查今天是否已经有题目
        try:
            daily_record = DailyQuestion.objects.get(client_ip=client_ip, date=today)
            # 如果今天已经有题目，直接返回
            return JsonResponse({
                'success': True,
                'data': daily_record.question_data
            })
        except DailyQuestion.DoesNotExist:
            # 今天还没有题目，需要生成新的
            pass
        
        # 获取所有题目
        all_questions = list(Question.objects.all())
        
        if not all_questions:
            return JsonResponse({
                'success': False,
                'error': '暂无可用题目'
            }, status=404)
        
        # 随机选择一道题目
        question = random.choice(all_questions)
        
        # 确定题目类型
        if question.is_choice_question():
            question_type = 'choice'
        elif question.is_fill_question():
            question_type = 'fill'
        else:
            question_type = 'unknown'
        
        # 构建题目数据（包含正确答案）
        question_data = {
            'id': question.id,
            'question_type': question_type,
            'question_text': question.question_text,
            'difficulty': question.difficulty,
            'category': question.category,
            'category_display': question.get_category_display(),
            'tags': question.get_tags_list(),
            'explanation': question.explanation,
        }
        
        if question_type == 'choice':
            # 选择题：包含选项和正确答案
            question_data.update({
                'choice_type': question.question_type,  # choice_single or choice_multiple
                'options': question.get_options_display(),
                'correct_options': question.get_correct_options(),
            })
        elif question_type == 'fill':
            # 填空题：包含正确答案
            question_data.update({
                'correct_answer': question.correct_answer,
            })
        
        # 保存每日一题记录
        DailyQuestion.objects.create(
            client_ip=client_ip,
            question=question,
            question_data=question_data
        )
        
        return JsonResponse({
            'success': True,
            'data': question_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_question(request):
    """上传单个题目"""
    try:
        data = json.loads(request.body)
        
        # 验证必填字段
        required_fields = ['question_text', 'question_type', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }, status=400)
        
        # 验证题目类型
        valid_question_types = ['choice_single', 'choice_multiple', 'fill']
        if data['question_type'] not in valid_question_types:
            return JsonResponse({
                'success': False,
                'error': f'无效的题目类型: {data["question_type"]}'
            }, status=400)
        
        # 验证分类
        valid_categories = ['party_history', 'theory']
        if data['category'] not in valid_categories:
            return JsonResponse({
                'success': False,
                'error': f'无效的分类: {data["category"]}'
            }, status=400)
        
        # 验证难度
        valid_difficulties = ['easy', 'medium', 'hard']
        difficulty = data.get('difficulty', 'medium')
        if difficulty not in valid_difficulties:
            return JsonResponse({
                'success': False,
                'error': f'无效的难度: {difficulty}'
            }, status=400)
        
        # 创建题目
        with transaction.atomic():
            question = Question.objects.create(
                question_text=data['question_text'],
                question_type=data['question_type'],
                category=data['category'],
                difficulty=difficulty,
                explanation=data.get('explanation', ''),
                tags=data.get('tags', '')
            )
            
            # 处理选择题选项
            if data['question_type'] in ['choice_single', 'choice_multiple']:
                options = data.get('options', [])
                if not options:
                    return JsonResponse({
                        'success': False,
                        'error': '选择题必须提供选项'
                    }, status=400)
                
                # 验证选项格式
                for i, option in enumerate(options):
                    if not isinstance(option, dict) or 'text' not in option:
                        return JsonResponse({
                            'success': False,
                            'error': f'选项 {i+1} 格式错误'
                        }, status=400)
                
                question.options = options
                question.save()
            
            # 处理填空题答案
            elif data['question_type'] == 'fill':
                correct_answer = data.get('correct_answer', '')
                if not correct_answer:
                    return JsonResponse({
                        'success': False,
                        'error': '填空题必须提供正确答案'
                    }, status=400)
                
                question.correct_answer = correct_answer
                question.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'question_id': question.id,
                'message': '题目上传成功'
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def batch_upload_questions(request):
    """批量上传题目"""
    try:
        data = json.loads(request.body)
        questions_data = data.get('questions', [])
        
        if not questions_data:
            return JsonResponse({
                'success': False,
                'error': '没有提供题目数据'
            }, status=400)
        
        success_count = 0
        failed_count = 0
        errors = []
        
        with transaction.atomic():
            for i, question_data in enumerate(questions_data):
                try:
                    # 验证必填字段
                    required_fields = ['question_text', 'question_type', 'category']
                    for field in required_fields:
                        if field not in question_data or not question_data[field]:
                            raise ValueError(f'缺少必填字段: {field}')
                    
                    # 验证题目类型
                    valid_question_types = ['choice_single', 'choice_multiple', 'fill']
                    if question_data['question_type'] not in valid_question_types:
                        raise ValueError(f'无效的题目类型: {question_data["question_type"]}')
                    
                    # 验证分类
                    valid_categories = ['party_history', 'theory']
                    if question_data['category'] not in valid_categories:
                        raise ValueError(f'无效的分类: {question_data["category"]}')
                    
                    # 验证难度
                    valid_difficulties = ['easy', 'medium', 'hard']
                    difficulty = question_data.get('difficulty', 'medium')
                    if difficulty not in valid_difficulties:
                        raise ValueError(f'无效的难度: {difficulty}')
                    
                    # 创建题目
                    question = Question.objects.create(
                        question_text=question_data['question_text'],
                        question_type=question_data['question_type'],
                        category=question_data['category'],
                        difficulty=difficulty,
                        explanation=question_data.get('explanation', ''),
                        tags=question_data.get('tags', '')
                    )
                    
                    # 处理选择题选项
                    if question_data['question_type'] in ['choice_single', 'choice_multiple']:
                        options = question_data.get('options', [])
                        if not options:
                            raise ValueError('选择题必须提供选项')
                        
                        # 验证选项格式
                        for j, option in enumerate(options):
                            if not isinstance(option, dict) or 'text' not in option:
                                raise ValueError(f'选项 {j+1} 格式错误')
                        
                        question.options = options
                        question.save()
                    
                    # 处理填空题答案
                    elif question_data['question_type'] == 'fill':
                        correct_answer = question_data.get('correct_answer', '')
                        if not correct_answer:
                            raise ValueError('填空题必须提供正确答案')
                        
                        question.correct_answer = correct_answer
                        question.save()
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    errors.append(f'题目 {i+1}: {str(e)}')
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': len(questions_data),
                'success_count': success_count,
                'failed_count': failed_count,
                'errors': errors
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
