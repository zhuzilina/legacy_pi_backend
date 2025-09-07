# 知识AI服务API使用说明

## 概述

知识AI服务为app客户端提供三个核心API功能：
1. 通过题目ID获取AI对题目的详细解答
2. 通过知识ID生成开放性提问
3. 分析用户回答与知识点的相关度并提供反馈

## 基础信息

- **基础URL**: `/api/knowledge-ai/`
- **认证方式**: 无需认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## API接口详情

### 1. 题目详细解答API

**接口地址**: `GET /api/knowledge-ai/question/{question_id}/explanation/`

**功能描述**: 通过题目ID获取AI对题目的详细解答，支持选择题和填空题。

**请求参数**:
- `question_id` (路径参数): 题目ID，必填

**响应示例**:
```json
{
    "success": true,
    "data": {
        "question_id": 123,
        "question_type": "choice",
        "explanation": "这是一道关于马克思主义基本原理的选择题...",
        "analysis_id": 456,
        "model_used": "doubao-seed-1-6-250615",
        "tokens_used": 1200,
        "processing_time": 2.5
    }
}
```

**错误响应**:
```json
{
    "success": false,
    "error": "题目不存在",
    "error_code": "QUESTION_NOT_FOUND"
}
```

### 2. 开放性提问生成API

**接口地址**: `POST /api/knowledge-ai/open-question/generate/`

**功能描述**: 基于知识内容生成高质量的开放性问题。

**请求体**:
```json
{
    "knowledge_id": 123,
    "question_type": "comprehension",
    "difficulty_level": "medium"
}
```

**参数说明**:
- `knowledge_id` (必填): 知识ID
- `question_type` (可选): 问题类型，默认"comprehension"
  - `comprehension`: 理解型
  - `application`: 应用型
  - `analysis`: 分析型
  - `evaluation`: 评价型
  - `creation`: 创造型
- `difficulty_level` (可选): 难度等级，默认"medium"
  - `easy`: 简单
  - `medium`: 中等
  - `hard`: 困难

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 789,
        "question_text": "请结合马克思主义基本原理，分析当前社会发展中面临的主要矛盾及其解决路径。",
        "question_type": "analysis",
        "difficulty_level": "medium",
        "knowledge_id": 123,
        "knowledge_title": "马克思主义基本原理"
    }
}
```

### 3. 回答相关度分析API

**接口地址**: `POST /api/knowledge-ai/answer/analyze/`

**功能描述**: 分析用户对开放性问题的回答与知识点的相关度，提供0-100分评分和详细反馈。

**请求体**:
```json
{
    "open_question_id": 789,
    "user_answer": "我认为当前社会的主要矛盾是..."
}
```

**参数说明**:
- `open_question_id` (必填): 开放性问题的ID
- `user_answer` (必填): 用户的回答内容

**响应示例**:
```json
{
    "success": true,
    "data": {
        "user_answer_id": 101,
        "relevance_score": 85,
        "feedback_text": "您的回答展现了良好的理论基础...",
        "analysis_id": 202,
        "model_used": "doubao-seed-1-6-250615",
        "tokens_used": 1500,
        "processing_time": 3.2
    }
}
```

## 辅助API接口

### 4. 开放性问题列表API

**接口地址**: `GET /api/knowledge-ai/open-questions/`

**功能描述**: 获取开放性问题列表，支持筛选和分页。

**查询参数**:
- `knowledge_id` (可选): 知识ID筛选
- `question_type` (可选): 问题类型筛选
- `difficulty_level` (可选): 难度等级筛选
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认10

**响应示例**:
```json
{
    "success": true,
    "data": {
        "questions": [
            {
                "id": 789,
                "question_text": "请结合马克思主义基本原理...",
                "question_type": "analysis",
                "difficulty_level": "medium",
                "knowledge_id": 123,
                "knowledge_title": "马克思主义基本原理",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "page": 1,
        "page_size": 10,
        "total_count": 25
    }
}
```

### 5. 用户回答列表API

**接口地址**: `GET /api/knowledge-ai/user-answers/`

**功能描述**: 获取用户回答列表，支持筛选和分页。

**查询参数**:
- `open_question_id` (可选): 开放性问题ID筛选
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认10

### 6. 健康检查API

**接口地址**: `GET /api/knowledge-ai/health/`

**功能描述**: 检查服务健康状态。

**响应示例**:
```json
{
    "status": "healthy",
    "model": "doubao-seed-1-6-250615",
    "api_key_configured": true,
    "response_time": "normal"
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| `QUESTION_NOT_FOUND` | 题目不存在 |
| `KNOWLEDGE_NOT_FOUND` | 知识不存在 |
| `OPEN_QUESTION_NOT_FOUND` | 开放性问题不存在 |
| `MISSING_PARAMETER` | 缺少必需参数 |
| `INVALID_PARAMETER` | 参数值无效 |
| `INVALID_JSON` | JSON格式无效 |
| `AI_SERVICE_ERROR` | AI服务错误 |
| `INTERNAL_ERROR` | 服务器内部错误 |

## 使用示例

### JavaScript示例

```javascript
// 1. 获取题目解答
async function getQuestionExplanation(questionId) {
    const response = await fetch(`/api/knowledge-ai/question/${questionId}/explanation/`);
    const data = await response.json();
    return data;
}

// 2. 生成开放性问题
async function generateOpenQuestion(knowledgeId, questionType = 'comprehension', difficultyLevel = 'medium') {
    const response = await fetch('/api/knowledge-ai/open-question/generate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            knowledge_id: knowledgeId,
            question_type: questionType,
            difficulty_level: difficultyLevel
        })
    });
    const data = await response.json();
    return data;
}

// 3. 分析回答相关度
async function analyzeAnswerRelevance(openQuestionId, userAnswer) {
    const response = await fetch('/api/knowledge-ai/answer/analyze/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            open_question_id: openQuestionId,
            user_answer: userAnswer
        })
    });
    const data = await response.json();
    return data;
}
```

### Python示例

```python
import requests
import json

# 1. 获取题目解答
def get_question_explanation(question_id):
    url = f"/api/knowledge-ai/question/{question_id}/explanation/"
    response = requests.get(url)
    return response.json()

# 2. 生成开放性问题
def generate_open_question(knowledge_id, question_type='comprehension', difficulty_level='medium'):
    url = "/api/knowledge-ai/open-question/generate/"
    data = {
        "knowledge_id": knowledge_id,
        "question_type": question_type,
        "difficulty_level": difficulty_level
    }
    response = requests.post(url, json=data)
    return response.json()

# 3. 分析回答相关度
def analyze_answer_relevance(open_question_id, user_answer):
    url = "/api/knowledge-ai/answer/analyze/"
    data = {
        "open_question_id": open_question_id,
        "user_answer": user_answer
    }
    response = requests.post(url, json=data)
    return response.json()
```

## 注意事项

1. **API限制**: 建议对API调用频率进行限制，避免过度使用AI服务
2. **错误处理**: 请妥善处理各种错误情况，特别是网络错误和AI服务错误
3. **数据验证**: 客户端应验证输入数据的有效性
4. **缓存策略**: 对于相同的问题，可以考虑缓存AI分析结果以提高性能
5. **用户体验**: AI分析可能需要几秒钟时间，建议显示加载状态
6. **题目ID设计**: 当前选择题和填空题使用独立的ID序列，虽然目前没有冲突，但建议客户端不要依赖ID来判断题目类型，应通过API返回的`question_type`字段来判断

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本，提供三个核心API功能
