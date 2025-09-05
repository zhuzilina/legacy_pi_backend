# AI解读API完整文档

## 🎯 概述

AI解读应用是一个独立的Django应用，专门提供基于大模型的文本解读服务。使用OpenAI SDK调用方舟大模型API，支持多种解读模式和批量处理。

**基础URL**: `http://127.0.0.1:8000/api/ai/`

## 🚀 快速开始

### 1. 启动服务
```bash
./start_server.sh
```

### 2. 健康检查
```bash
curl http://127.0.0.1:8000/api/ai/health/
```

### 3. 快速测试
```bash
python quick_test_ai.py
```

## 📚 API端点

### 1. 文本解读 API

**端点**: `POST /api/ai/interpret/`

**描述**: 解读单个文本内容，支持多种解读模式和自定义提示词。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | ✅ | - | 要解读的文本内容 |
| `prompt_type` | string | ❌ | `default` | 提示词类型 |
| `custom_prompt` | string | ❌ | - | 自定义提示词 |
| `max_tokens` | integer | ❌ | `1000` | 最大输出token数 |

#### 提示词类型

- `default`: 详细解读模式 - 多角度深入分析
- `summary`: 全面总结模式 - 结构化归纳总结
- `analysis`: 深度分析模式 - 批判性思考和评价
- `qa`: 详细问答模式 - 全面覆盖和深入回答
- `detailed_explanation`: 最详细讲解模式 - 逐段深入解读
- `educational`: 教学讲解模式 - 循序渐进的教育式解读
- `research`: 学术研究模式 - 研究水平的深度分析
- `key_points`: 重点提炼模式 - 金字塔原理式简洁提炼

#### 请求示例

```bash
curl -X POST "http://127.0.0.1:8000/api/ai/interpret/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工智能正在改变世界...",
    "prompt_type": "summary",
    "max_tokens": 500
  }'
```

#### 响应格式

```json
{
  "success": true,
  "data": {
    "interpretation": "解读结果内容...",
    "model_used": "doubao-seed-1-6-250615",
    "prompt_type": "summary",
    "tokens_used": 150,
    "original_text_length": 200
  }
}
```

### 2. 批量解读 API

**端点**: `POST /api/ai/batch/`

**描述**: 批量解读多个文本，提高处理效率。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `texts` | array | ✅ | - | 文本列表（最多10个） |
| `prompt_type` | string | ❌ | `default` | 提示词类型 |

#### 请求示例

```bash
curl -X POST "http://127.0.0.1:8000/api/ai/batch/" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "文本1内容...",
      "文本2内容...",
      "文本3内容..."
    ],
    "prompt_type": "analysis"
  }'
```

#### 响应格式

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "success": true,
        "interpretation": "解读结果1...",
        "text_index": 0
      },
      {
        "success": true,
        "interpretation": "解读结果2...",
        "text_index": 1
      }
    ],
    "total_texts": 2,
    "successful_count": 2
  }
}
```

### 3. 健康检查 API

**端点**: `GET /api/ai/health/`

**描述**: 检查AI解读服务的健康状态和连接状态。

#### 请求示例

```bash
curl http://127.0.0.1:8000/api/ai/health/
```

#### 响应格式

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "model": "doubao-seed-1-6-250615",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "response_time": "normal"
  }
}
```

### 4. 提示词类型 API

**端点**: `GET /api/ai/prompts/`

**描述**: 获取可用的提示词类型和说明。

#### 请求示例

```bash
curl http://127.0.0.1:8000/api/ai/prompts/
```

#### 响应格式

```json
{
  "success": true,
  "data": {
    "available_prompts": {
      "default": "请对以下Markdown文本进行详细解读和深入分析...",
      "summary": "请对以下文本进行全面的总结和归纳...",
      "analysis": "请对以下文本进行深度分析和批判性思考...",
      "qa": "请基于以下文本内容，提供详细、准确的回答...",
      "detailed_explanation": "请对以下文本进行最详细的讲解和解读...",
      "educational": "请以教育者的身份，对以下文本进行教学式的详细讲解...",
      "research": "请以研究者的身份，对以下文本进行学术研究式的深入分析...",
      "key_points": "请简要提炼以下文本中的重点内容..."
    },
    "description": "可用的提示词类型，用于指定解读风格和深度"
  }
}
```

### 5. 主视图 API

**端点**: `GET /api/ai/`

**描述**: 获取AI解读服务的基本信息和使用说明。

#### 请求示例

```bash
curl http://127.0.0.1:8000/api/ai/
```

#### 响应格式

```json
{
  "success": true,
  "message": "AI解读服务",
  "usage": {
    "POST": "发送文本进行解读",
    "GET": "获取服务信息"
  },
  "endpoints": {
    "interpret": "/api/ai/interpret/",
    "batch_interpret": "/api/ai/batch/",
    "health_check": "/api/ai/health/",
    "prompts": "/api/ai/prompts/"
  }
}
```

## 🔧 高级功能

### 1. 提示词类型选择

#### 预定义类型
- **default**: 详细解读模式 - 适合需要全面理解的场景
- **summary**: 全面总结模式 - 适合快速获取要点
- **analysis**: 深度分析模式 - 适合学术研究和批判性思考
- **qa**: 详细问答模式 - 适合问题解答和指导
- **detailed_explanation**: 最详细讲解模式 - 适合深度学习和研究
- **educational**: 教学讲解模式 - 适合教育和培训场景
- **research**: 学术研究模式 - 适合学术论文和研究报告
- **key_points**: 重点提炼模式 - 适合快速获取核心要点

#### 自定义提示词

除了使用预定义的提示词类型，还可以提供自定义提示词：

```json
{
  "text": "今天天气很好...",
  "custom_prompt": "请用诗意的语言描述这段文字：",
  "max_tokens": 200
}
```

### 2. Token控制

通过 `max_tokens` 参数控制输出长度：

```json
{
  "text": "长文本内容...",
  "max_tokens": 2000
}
```

### 3. 批量处理优化

- 单次最多处理10个文本
- 支持并发处理
- 错误隔离，单个失败不影响其他

## 📊 性能指标

### 1. 响应时间
- **健康检查**: 1-3秒
- **单文本解读**: 10-30秒
- **批量解读**: 30-90秒（取决于文本数量和长度）

### 2. 并发支持
- 支持多个并发请求
- 建议并发数不超过5个
- 自动队列管理

### 3. 资源使用
- 内存使用: 低
- CPU使用: 中等（主要在网络I/O）
- 网络带宽: 取决于文本长度

## 🔒 安全特性

### 1. 输入验证
- 文本长度限制
- 批量处理数量限制
- 参数类型验证

### 2. 错误处理
- 详细的错误信息
- 异常日志记录
- 优雅降级

### 3. 访问控制
- CORS支持
- 请求频率限制（建议）
- 日志审计

## 🧪 测试指南

### 1. 功能测试

```bash
# 完整功能测试
python test_ai_interpreter.py

# 快速测试
python quick_test_ai.py
```

### 2. 性能测试

```bash
# 并发测试
for i in {1..5}; do
  curl -X POST "http://127.0.0.1:8000/api/ai/interpret/" \
    -H "Content-Type: application/json" \
    -d '{"text": "测试文本'$i'"}' &
done
wait
```

### 3. 错误测试

```bash
# 空文本测试
curl -X POST "http://127.0.0.1:8000/api/ai/interpret/" \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'

# 无效JSON测试
curl -X POST "http://127.0.0.1:8000/api/ai/interpret/" \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

## 🚨 错误码说明

| HTTP状态码 | 说明 | 解决方案 |
|-----------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查参数格式和必填字段 |
| 500 | 服务器内部错误 | 查看服务器日志 |
| 503 | 服务不可用 | 检查AI模型API连接 |

## 🔮 后续规划

### 1. 功能增强
- [ ] 支持图片解读
- [ ] 多语言支持
- [ ] 实时流式输出
- [ ] 结果缓存机制

### 2. 性能优化
- [ ] 异步处理
- [ ] 连接池优化
- [ ] 智能重试机制
- [ ] 负载均衡

### 3. 监控告警
- [ ] API调用统计
- [ ] 性能指标监控
- [ ] 异常告警
- [ ] 使用量分析

## 📞 技术支持

### 1. 常见问题
- 查看项目日志: `tail -f server.log`
- 检查环境变量: `echo $ARK_API_KEY`
- 验证网络连接: `ping ark.cn-beijing.volces.com`

### 2. 联系方式
- 项目Issues: GitHub Issues
- 开发团队: 内部沟通渠道
- 文档更新: 定期维护

---

**版本**: v2.0  
**更新时间**: 2025-09-02  
**状态**: ✅ 已完成并优化
