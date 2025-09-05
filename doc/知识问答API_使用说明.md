# 知识问答API使用说明

## 概述

知识问答系统提供了简化的知识管理和每日一题功能，专注于党政理论知识的学习和测试。

## 系统架构

系统采用简化的设计：
- **知识管理**: 支持新思想和理论知识两个分类
- **每日一题**: 每个客户端IP每天只能获取一道题目，包含完整答案

## API端点

### 1. 知识管理API

#### 1.1 获取知识列表
- **URL**: `/api/knowledge-quiz/knowledge/`
- **方法**: `GET`
- **参数**:
  - `category` (可选): 知识分类筛选，支持 `new_thought`（新思想）和 `theory`（理论知识）
  - `search` (可选): 搜索关键词
  - `page` (可选): 页码，默认1
  - `page_size` (可选): 每页数量，默认10

**分类说明**:
- `new_thought`: 新思想类别，返回习近平新时代中国特色社会主义思想相关内容
- `theory`: 理论知识类别，返回除习近平新时代中国特色社会主义思想外的所有其他理论内容

**响应示例**:
```json
{
  "success": true,
  "data": {
    "knowledge_list": [
      {
        "id": 1,
        "title": "习近平新时代中国特色社会主义思想的核心要义",
        "content": "习近平新时代中国特色社会主义思想是当代中国马克思主义、二十一世纪马克思主义...",
        "category": "new_thought",
        "category_display": "新思想",
        "source": "共产党员网",
        "tags": ["新思想", "核心要义", "马克思主义"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_count": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

#### 1.2 获取知识详情
- **URL**: `/api/knowledge-quiz/knowledge/{knowledge_id}/`
- **方法**: `GET`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "习近平新时代中国特色社会主义思想的核心要义",
    "content": "习近平新时代中国特色社会主义思想是当代中国马克思主义、二十一世纪马克思主义...",
    "category": "new_thought",
    "category_display": "新思想",
    "source": "共产党员网",
    "tags": ["新思想", "核心要义", "马克思主义"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 每日一题API

#### 2.1 获取每日一题
- **URL**: `/api/knowledge-quiz/daily-question/`
- **方法**: `GET`
- **功能**: 每个客户端IP每天只能获取一道题目，包含题目、选项和正确答案
- **限制**: 基于客户端IP地址，每天只能请求一次

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question_type": "choice",
    "question_text": "标志着中国共产党开始独立领导革命战争和创建人民军队的事件是（ ）。",
    "difficulty": "easy",
    "category": "party_history",
    "category_display": "党史",
    "tags": ["党史", "重要事件"],
    "explanation": "南昌起义是中国共产党独立领导革命战争和创建人民军队的开始。",
    "choice_type": "single",
    "options": [
      {"text": "A.南昌起义", "is_correct": true},
      {"text": "B.广州起义", "is_correct": false},
      {"text": "C.秋收起义", "is_correct": false}
    ],
    "correct_options": [
      {"text": "A.南昌起义", "is_correct": true}
    ]
  }
}
```

**填空题响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "question_type": "fill",
    "question_text": "中国共产党的根本宗旨是（ ）。",
    "difficulty": "easy",
    "category": "theory",
    "category_display": "理论",
    "tags": ["理论", "宗旨"],
    "explanation": "全心全意为人民服务是中国共产党的根本宗旨。",
    "correct_answer": "全心全意为人民服务"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "暂无可用题目"
}
```

**特点**:
- ✅ **每日限制**: 每个IP每天只能获取一道题目
- ✅ **随机抽取**: 从所有可用题目中随机选择
- ✅ **完整数据**: 直接返回题目、选项和正确答案
- ✅ **类型支持**: 支持选择题和填空题
- ✅ **自动记录**: 自动记录每日答题情况

## 使用示例

### 1. 获取新思想知识
```bash
curl "http://10.0.2.2:8000/api/knowledge-quiz/knowledge/?category=new_thought"
```

### 2. 获取理论知识
```bash
curl "http://10.0.2.2:8000/api/knowledge-quiz/knowledge/?category=theory"
```

### 3. 搜索知识
```bash
curl "http://10.0.2.2:8000/api/knowledge-quiz/knowledge/?search=马克思主义"
```

### 4. 获取每日一题
```bash
curl "http://10.0.2.2:8000/api/knowledge-quiz/daily-question/"
```

## 管理后台

### 1. 知识录入
访问 `http://10.0.2.2:8000/admin/knowledge_quiz/knowledge/` 进行知识条目的录入和管理。

### 2. 题目录入
访问 `http://10.0.2.2:8000/admin/knowledge_quiz/` 进行选择题和填空题的录入和管理。

### 3. 每日一题记录
访问 `http://10.0.2.2:8000/admin/knowledge_quiz/dailyquestion/` 查看每日一题的答题记录。

## 系统特点

- ✅ **简化设计**: 只保留核心功能，易于使用和维护
- ✅ **分类清晰**: 新思想和理论知识两个主要分类
- ✅ **每日一题**: 防止刷题，确保学习效果
- ✅ **完整答案**: 直接提供正确答案，便于学习
- ✅ **管理便捷**: 提供完整的管理后台界面
- ✅ **数据统计**: 自动记录每日答题情况

## 部署说明

1. **启动服务器**:
   ```bash
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

2. **访问管理后台**:
   - 地址：`http://10.0.2.2:8000/admin/`
   - 使用admin账户登录

3. **API测试**:
   - 知识API：`http://10.0.2.2:8000/api/knowledge-quiz/knowledge/`
   - 每日一题API：`http://10.0.2.2:8000/api/knowledge-quiz/daily-question/`