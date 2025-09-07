# 题目ID设计改进建议

## 问题分析

### 当前设计问题

1. **ID不唯一性风险**：
   - 选择题和填空题使用各自独立的ID序列
   - 当前数据：选择题ID [14, 12]，填空题ID [7, 6, 5, 4, 3, 2, 1]
   - 虽然目前没有冲突，但存在潜在的ID冲突风险

2. **API效率问题**：
   - 题目解答API需要先查询选择题表，再查询填空题表
   - 每次都需要两次数据库查询，效率低下

3. **用户体验问题**：
   - 客户端无法通过ID直接判断题目类型
   - 需要额外的API调用来获取题目类型信息

## 改进方案

### 方案1：统一题目表（推荐）

**优点**：
- ID完全唯一
- 查询效率高
- 数据结构清晰
- 便于扩展

**实现**：
```python
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('choice_single', '单选题'),
        ('choice_multiple', '多选题'),
        ('fill', '填空题'),
    ]
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField(verbose_name='题目内容')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='party_history')
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 选择题特有字段
    options = models.JSONField(default=list, null=True, blank=True, verbose_name='选项')
    
    # 填空题特有字段
    correct_answer = models.TextField(null=True, blank=True, verbose_name='正确答案')
    
    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['-created_at']
```

### 方案2：ID前缀方案

**优点**：
- 保持现有表结构
- ID具有类型标识
- 实现简单

**实现**：
```python
# 在模型中添加方法
class ChoiceQuestion(BaseQuestion):
    def get_typed_id(self):
        return f"C{self.id}"
    
    @classmethod
    def get_by_typed_id(cls, typed_id):
        if typed_id.startswith('C'):
            return cls.objects.get(id=int(typed_id[1:]))
        return None

class FillQuestion(BaseQuestion):
    def get_typed_id(self):
        return f"F{self.id}"
    
    @classmethod
    def get_by_typed_id(cls, typed_id):
        if typed_id.startswith('F'):
            return cls.objects.get(id=int(typed_id[1:]))
        return None
```

### 方案3：复合ID方案

**优点**：
- 保持现有表结构
- ID包含类型信息
- 便于识别

**实现**：
```python
# 使用复合标识符
# 选择题：choice_1, choice_2, ...
# 填空题：fill_1, fill_2, ...

def get_question_by_composite_id(composite_id):
    if composite_id.startswith('choice_'):
        question_id = int(composite_id.split('_')[1])
        return ChoiceQuestion.objects.get(id=question_id), 'choice'
    elif composite_id.startswith('fill_'):
        question_id = int(composite_id.split('_')[1])
        return FillQuestion.objects.get(id=question_id), 'fill'
    return None, None
```

## 当前临时解决方案

如果不进行大规模重构，可以优化当前的实现：

### 1. 优化查询逻辑

```python
def get_question_by_id(question_id):
    """统一的题目查询函数"""
    # 先尝试选择题
    try:
        question = ChoiceQuestion.objects.get(id=question_id)
        return question, 'choice'
    except ChoiceQuestion.DoesNotExist:
        pass
    
    # 再尝试填空题
    try:
        question = FillQuestion.objects.get(id=question_id)
        return question, 'fill'
    except FillQuestion.DoesNotExist:
        pass
    
    return None, None
```

### 2. 添加题目类型查询API

```python
@csrf_exempt
@require_http_methods(["GET"])
def get_question_type(request, question_id):
    """获取题目类型"""
    question, question_type = get_question_by_id(question_id)
    
    if question is None:
        return JsonResponse({
            'success': False,
            'error': '题目不存在'
        }, status=404)
    
    return JsonResponse({
        'success': True,
        'data': {
            'question_id': question_id,
            'question_type': question_type
        }
    })
```

### 3. 数据库约束优化

```python
# 在settings.py中添加数据库约束检查
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'init_command': """
                CREATE TRIGGER IF NOT EXISTS check_question_id_conflict
                AFTER INSERT ON knowledge_quiz_choicequestion
                BEGIN
                    SELECT CASE
                        WHEN EXISTS(SELECT 1 FROM knowledge_quiz_fillquestion WHERE id = NEW.id)
                        THEN RAISE(ABORT, 'Question ID conflict detected')
                    END;
                END;
                
                CREATE TRIGGER IF NOT EXISTS check_fill_question_id_conflict
                AFTER INSERT ON knowledge_quiz_fillquestion
                BEGIN
                    SELECT CASE
                        WHEN EXISTS(SELECT 1 FROM knowledge_quiz_choicequestion WHERE id = NEW.id)
                        THEN RAISE(ABORT, 'Question ID conflict detected')
                    END;
                END;
            """
        }
    }
}
```

## 迁移建议

### 如果选择方案1（统一题目表）

1. **创建新模型**：创建统一的Question模型
2. **数据迁移**：编写数据迁移脚本，将现有数据迁移到新表
3. **API更新**：更新所有相关API
4. **测试验证**：全面测试确保功能正常
5. **清理旧表**：删除旧的ChoiceQuestion和FillQuestion表

### 如果选择方案2或3（保持现有结构）

1. **添加辅助方法**：在现有模型中添加ID处理方法
2. **API优化**：优化查询逻辑，减少数据库访问
3. **文档更新**：更新API文档，说明ID使用方式
4. **客户端适配**：指导客户端正确使用新的ID格式

## 推荐实施步骤

1. **短期**：实施当前临时解决方案，优化查询逻辑
2. **中期**：评估业务需求，选择合适的改进方案
3. **长期**：如果数据量增长，建议采用方案1进行重构

## 风险评估

- **方案1**：重构风险高，但长期收益大
- **方案2/3**：风险较低，但需要客户端适配
- **当前方案**：风险中等，需要添加约束检查

建议根据项目的实际情况和未来发展规划选择合适的方案。
