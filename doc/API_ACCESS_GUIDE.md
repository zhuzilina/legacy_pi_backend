# Legacy PI Backend API 访问指南

## 🌐 基础访问地址

**主服务器**: `http://localhost` (通过Nginx代理)

## 📋 完整API列表

### 1. 🤖 AI对话服务 (`/api/ai-chat/`)

#### 基础对话API
```bash
# 普通对话
POST http://localhost/api/ai-chat/chat/
Content-Type: application/json
{
  "message": "你好，请介绍一下人工智能"
}

# 带图片的对话
POST http://localhost/api/ai-chat/chat-with-images/
Content-Type: application/json
{
  "message": "请分析这张图片",
  "image_urls": ["http://example.com/image.jpg"]
}
```

#### 流式对话API
```bash
# 流式对话
POST http://localhost/api/ai-chat/stream/
Content-Type: application/json
{
  "message": "请详细解释量子计算"
}

# 流式图片对话
POST http://localhost/api/ai-chat/stream-with-images/
Content-Type: application/json
{
  "message": "分析这些图片",
  "image_urls": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
}
```

#### 图片上传API
```bash
# 单张图片上传
POST http://localhost/api/ai-chat/upload-image/
Content-Type: multipart/form-data
file: [图片文件]

# 批量图片上传
POST http://localhost/api/ai-chat/upload-images-batch/
Content-Type: multipart/form-data
files: [图片文件1, 图片文件2, ...]
```

#### 配置和状态API
```bash
# 健康检查
GET http://localhost/api/ai-chat/health/

# 获取系统提示词类型
GET http://localhost/api/ai-chat/prompts/

# 获取图片理解提示词类型
GET http://localhost/api/ai-chat/image-prompts/

# 获取图片缓存统计
GET http://localhost/api/ai-chat/image-cache-stats/

# 获取对话配置
GET http://localhost/api/ai-chat/config/
```

### 2. 📖 AI解读服务 (`/api/ai/`)

#### 文本解读API
```bash
# 普通文本解读
POST http://localhost/api/ai/interpret/
Content-Type: application/json
{
  "text": "这是一段需要解读的文本",
  "prompt_type": "summary"
}

# 批量文本解读
POST http://localhost/api/ai/batch/
Content-Type: application/json
{
  "texts": ["文本1", "文本2", "文本3"],
  "prompt_type": "summary"
}

# 流式文本解读
POST http://localhost/api/ai/stream/
Content-Type: application/json
{
  "text": "这是一段很长的文本，需要流式解读",
  "prompt_type": "summary"
}
```

#### 配置API
```bash
# 健康检查
GET http://localhost/api/ai/health/

# 获取提示词类型
GET http://localhost/api/ai/prompts/
```

### 3. 🔊 TTS语音服务 (`/api/tts/`)

#### 语音合成API
```bash
# 流式TTS
POST http://localhost/api/tts/stream/
Content-Type: application/json
{
  "text": "你好，这是语音合成测试",
  "voice": "zh-CN-XiaoxiaoNeural"
}

# 文件式TTS
POST http://localhost/api/tts/file/
Content-Type: application/json
{
  "text": "你好，这是语音合成测试",
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

#### 语音管理API
```bash
# 获取可用语音列表
GET http://localhost/api/tts/voices/

# 获取TTS请求状态
GET http://localhost/api/tts/status/{request_id}/

# 下载音频文件
GET http://localhost/api/tts/download/{request_id}/

# 音频文件重定向
GET http://localhost/api/tts/audio/{request_id}/
```

### 4. 📚 知识问答服务 (`/api/knowledge-quiz/`)

#### 知识库API
```bash
# 获取知识列表
GET http://localhost/api/knowledge-quiz/knowledge/

# 获取知识详情
GET http://localhost/api/knowledge-quiz/knowledge/{knowledge_id}/

# 获取每日一题
GET http://localhost/api/knowledge-quiz/daily-question/
```

### 5. 🧠 知识AI服务 (`/api/knowledge-ai/`)

#### 智能问答API
```bash
# 题目详细解答
GET http://localhost/api/knowledge-ai/question/{question_id}/explanation/

# 开放性提问生成
POST http://localhost/api/knowledge-ai/open-question/generate/
Content-Type: application/json
{
  "topic": "人工智能",
  "difficulty": "medium"
}

# 回答相关度分析
POST http://localhost/api/knowledge-ai/answer/analyze/
Content-Type: application/json
{
  "question": "什么是人工智能？",
  "answer": "人工智能是计算机科学的一个分支..."
}
```

#### 数据管理API
```bash
# 开放性问题列表
GET http://localhost/api/knowledge-ai/open-questions/

# 用户回答列表
GET http://localhost/api/knowledge-ai/user-answers/

# 健康检查
GET http://localhost/api/knowledge-ai/health/
```

### 6. 🕷️ 爬虫服务 (`/api/crawler/`)

#### 内容爬取API
```bash
# 获取每日文章ID列表
GET http://localhost/api/crawler/daily/

# 根据文章ID获取Markdown内容
GET http://localhost/api/crawler/article/{article_id}/

# 获取爬取状态
GET http://localhost/api/crawler/status/

# 获取缓存的图片
GET http://localhost/api/crawler/image/{image_id}/
```

### 7. 📄 文档服务 (`/api/md-docs/`)

#### 文档管理API
```bash
# 根据类别获取文档列表
GET http://localhost/api/md-docs/category/

# 根据文档ID获取Markdown内容
GET http://localhost/api/md-docs/document/{document_id}/

# 获取文档系统状态
GET http://localhost/api/md-docs/status/

# 获取文档图片
GET http://localhost/api/md-docs/image/{image_id}/

# 上传文档
POST http://localhost/api/md-docs/upload/
Content-Type: multipart/form-data
file: [文档文件]

# 上传图片
POST http://localhost/api/md-docs/upload-image/
Content-Type: multipart/form-data
file: [图片文件]
```

### 8. 🔧 管理后台

```bash
# Django管理后台
http://localhost/admin/

# MongoDB管理界面
http://localhost:8081
```

## 🧪 快速测试命令

### 使用curl测试API

```bash
# 测试AI对话
curl -X POST "http://localhost/api/ai-chat/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，测试API"}'

# 测试健康检查
curl http://localhost/api/ai-chat/health/

# 测试TTS语音列表
curl http://localhost/api/tts/voices/

# 测试知识问答
curl http://localhost/api/knowledge-quiz/knowledge/

# 测试AI解读
curl -X POST "http://localhost/api/ai/interpret/" \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本", "prompt_type": "summary"}'
```

### 使用测试脚本

```bash
# 完整API测试
./test_nginx_deployment.sh

# 性能优化测试
./test_performance_optimization.sh

# 性能监控
./monitor_performance.sh
```

## 📊 API响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据内容
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误信息描述"
}
```

## 🔐 认证和权限

- 大部分API无需认证
- 管理后台需要Django超级用户权限
- MongoDB管理界面需要用户名密码认证

## 📝 注意事项

1. **请求头**: 大部分API需要 `Content-Type: application/json`
2. **文件上传**: 使用 `multipart/form-data` 格式
3. **响应时间**: AI相关API响应时间较长（3-5秒）
4. **并发限制**: 系统支持8个并发请求
5. **缓存**: 部分API响应会被缓存以提高性能

## 🚀 开始使用

1. **确保服务运行**: `docker-compose ps`
2. **测试基础连接**: `curl http://localhost/api/ai-chat/health/`
3. **选择需要的API**: 参考上面的API列表
4. **发送请求**: 使用curl、Postman或其他HTTP客户端
5. **查看响应**: 检查返回的JSON数据

---

**API文档版本**: v1.0  
**最后更新**: 2025年9月7日  
**服务状态**: 全部正常运行 ✅
