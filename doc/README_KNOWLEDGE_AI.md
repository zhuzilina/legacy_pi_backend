# 知识AI服务应用

## 概述

知识AI服务是一个新创建的Django应用，为app客户端提供基于大模型的智能分析功能。该应用复用了`ai_interpreter`的大模型调用逻辑，专门针对知识问答场景进行了优化。

## 主要功能

### 1. 题目详细解答
- **API**: `GET /api/knowledge-ai/question/{question_id}/explanation/`
- **功能**: 通过题目ID获取AI对题目的详细解答
- **支持**: 选择题和填空题
- **特点**: 提供多角度分析、知识点梳理、解题思路等

### 2. 开放性提问生成
- **API**: `POST /api/knowledge-ai/open-question/generate/`
- **功能**: 基于知识内容生成高质量的开放性问题
- **支持**: 5种问题类型（理解型、应用型、分析型、评价型、创造型）
- **特点**: 3个难度等级，鼓励批判性思维

### 3. 回答相关度分析
- **API**: `POST /api/knowledge-ai/answer/analyze/`
- **功能**: 分析用户回答与知识点的相关度
- **评分**: 0-100分相关度评分
- **特点**: 提供详细反馈和改进建议

## 技术架构

### 数据模型
- `OpenQuestion`: 存储AI生成的开放性问题
- `UserAnswer`: 存储用户回答和AI分析结果
- `QuestionAnalysis`: 记录所有AI分析过程

### 服务层
- `KnowledgeAiService`: 核心服务类，封装大模型调用逻辑
- 复用`ai_interpreter`的配置和SDK
- 支持错误处理和性能监控

### API层
- RESTful API设计
- 统一的错误处理机制
- 完整的参数验证

## 文件结构

```
knowledge_ai/
├── __init__.py
├── admin.py              # Django管理后台配置
├── apps.py               # 应用配置
├── config.py             # AI模型配置和提示词
├── models.py             # 数据模型定义
├── services.py           # 核心服务逻辑
├── urls.py               # URL路由配置
├── views.py              # API视图函数
├── tests.py              # 测试文件
└── migrations/           # 数据库迁移文件
    └── 0001_initial.py
```

## 安装和配置

### 1. 应用已添加到Django设置
```python
# settings.py
INSTALLED_APPS = [
    # ... 其他应用
    'knowledge_ai',
]
```

### 2. URL路由已配置
```python
# urls.py
urlpatterns = [
    # ... 其他路由
    path('api/knowledge-ai/', include('knowledge_ai.urls')),
]
```

### 3. 数据库迁移已完成
```bash
python manage.py makemigrations knowledge_ai
python manage.py migrate
```

## 环境要求

### 依赖包
- `volcenginesdkarkruntime`: 火山引擎大模型SDK
- `django`: Django框架
- 其他依赖已在`requirements.txt`中定义

### 环境变量
```bash
ARK_API_KEY=你的API密钥  # 火山引擎API密钥
```

## 使用示例

### 1. 获取题目解答
```bash
curl -X GET "http://localhost:8000/api/knowledge-ai/question/1/explanation/"
```

### 2. 生成开放性问题
```bash
curl -X POST "http://localhost:8000/api/knowledge-ai/open-question/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": 1,
    "question_type": "analysis",
    "difficulty_level": "medium"
  }'
```

### 3. 分析回答相关度
```bash
curl -X POST "http://localhost:8000/api/knowledge-ai/answer/analyze/" \
  -H "Content-Type: application/json" \
  -d '{
    "open_question_id": 1,
    "user_answer": "用户的回答内容"
  }'
```

## 测试

运行测试脚本验证功能：
```bash
python test_knowledge_ai.py
```

## 管理后台

访问Django管理后台可以查看和管理：
- 开放性问题列表
- 用户回答记录
- AI分析历史

## 性能优化

### 1. 缓存策略
- 相同题目的解答可以缓存
- 相同知识的开放性问题可以复用

### 2. 异步处理
- 可以考虑将AI分析任务放入队列异步处理
- 提供实时状态查询接口

### 3. 批量操作
- 支持批量生成开放性问题
- 支持批量分析用户回答

## 扩展功能

### 1. 个性化推荐
- 基于用户历史回答推荐相关问题
- 根据用户水平调整问题难度

### 2. 学习路径
- 基于知识点关联生成学习路径
- 提供循序渐进的问题序列

### 3. 统计分析
- 用户学习进度统计
- 知识点掌握情况分析

## 注意事项

1. **API限制**: 注意大模型API的调用频率限制
2. **数据安全**: 用户回答数据需要妥善保护
3. **错误处理**: 完善的错误处理和用户提示
4. **性能监控**: 监控AI服务的响应时间和成功率

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本发布
  - 实现三个核心API功能
  - 完成数据模型设计
  - 添加管理后台支持
  - 编写完整的使用文档
