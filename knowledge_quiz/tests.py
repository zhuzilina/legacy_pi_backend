from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import json
from .models import Knowledge, Question, Answer, QuizSession


class KnowledgeQuizTestCase(TestCase):
    def setUp(self):
        """设置测试数据"""
        # 创建知识条目
        self.knowledge = Knowledge.objects.create(
            title="Python基础",
            content="Python是一种高级编程语言，具有简洁的语法和强大的功能。",
            category="technology",
            tags="python,编程,基础"
        )
        
        # 创建题目
        self.question = Question.objects.create(
            question_text="Python是什么类型的编程语言？",
            knowledge=self.knowledge,
            question_type="single",
            difficulty="easy",
            options=["编译型", "解释型", "汇编型", "机器型"],
            correct_answer="解释型",
            explanation="Python是解释型编程语言，代码在运行时由解释器逐行执行。"
        )
    
    def test_knowledge_list_api(self):
        """测试知识列表API"""
        response = self.client.get('/api/knowledge-quiz/knowledge/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['knowledge_list']), 1)
    
    def test_knowledge_detail_api(self):
        """测试知识详情API"""
        response = self.client.get(f'/api/knowledge-quiz/knowledge/{self.knowledge.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Python基础")
    
    def test_create_quiz_session(self):
        """测试创建答题会话"""
        data = {
            'category': 'technology',
            'difficulty': 'easy',
            'question_count': 1
        }
        
        response = self.client.post(
            '/api/knowledge-quiz/quiz/create/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['total_questions'], 1)
    
    def test_submit_answer(self):
        """测试提交答案"""
        # 先创建会话
        session = QuizSession.objects.create(total_questions=1)
        
        data = {
            'session_id': str(session.session_id),
            'question_id': self.question.id,
            'user_answer': '解释型'
        }
        
        response = self.client.post(
            '/api/knowledge-quiz/quiz/submit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['data']['is_correct'])
    
    def test_complete_quiz(self):
        """测试完成答题会话"""
        session = QuizSession.objects.create(total_questions=1, correct_answers=1)
        
        data = {
            'session_id': str(session.session_id)
        }
        
        response = self.client.post(
            '/api/knowledge-quiz/quiz/complete/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['score'], 100.0)
    
    def test_quiz_statistics(self):
        """测试答题统计API"""
        response = self.client.get('/api/knowledge-quiz/statistics/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['data']['total_knowledge'], 1)
        self.assertGreaterEqual(data['data']['total_questions'], 1)
