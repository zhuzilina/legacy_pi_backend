from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
import random
from .models import Knowledge, ChoiceQuestion, FillQuestion, Answer, QuizSession, DailyQuestion


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
        all_questions = []
        
        # 获取选择题
        choice_questions = list(ChoiceQuestion.objects.all())
        for q in choice_questions:
            all_questions.append({
                'type': 'choice',
                'question': q,
                'id': q.id
            })
        
        # 获取填空题
        fill_questions = list(FillQuestion.objects.all())
        for q in fill_questions:
            all_questions.append({
                'type': 'fill',
                'question': q,
                'id': q.id
            })
        
        if not all_questions:
            return JsonResponse({
                'success': False,
                'error': '暂无可用题目'
            }, status=404)
        
        # 随机选择一道题目
        selected = random.choice(all_questions)
        question = selected['question']
        question_type = selected['type']
        
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
                'choice_type': question.question_type,  # single or multiple
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
            question_type=question_type,
            question_id=question.id,
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
