# AI对话API 使用说明

## 概述

AI对话API是一个支持多轮对话的智能聊天服务，基于大语言模型提供自然语言交互能力。该API采用客户端维护对话历史的架构，服务端专注于AI模型调用和响应生成。

## 主要特性

- 🗣️ **多轮对话支持**：支持连续的多轮对话交互
- 📝 **客户端维护历史**：对话记录完全由客户端管理，服务端无状态
- 🎭 **多种AI角色**：提供多种预设的系统提示词风格
- ⚙️ **灵活参数配置**：支持自定义提示词、温度、最大token数等参数
- 🔒 **安全可靠**：完善的错误处理和输入验证
- 📊 **详细响应信息**：返回模型信息、token使用量等详细信息
- 🌟 **红色文化主题**：专门用于红色文化和理论知识问答，具有严格的回答范围限制

## API端点

### 基础URL
```
http://your-domain/api/ai-chat/
```

### 可用端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/chat/` | POST | 主要对话API，支持多轮对话 |
| `/stream/` | POST | 流式对话API（实验性功能） |
| `/prompts/` | GET | 获取可用的系统提示词类型 |
| `/health/` | GET | 健康检查，测试服务状态 |
| `/config/` | GET | 获取对话配置参数 |
| `/` | GET/POST | 基于类的视图，支持GET和POST |

## 核心API详解

### 1. 对话API (`/chat/`)

#### 请求格式
```http
POST /api/ai-chat/chat/
Content-Type: application/json

{
    "message": "用户输入的消息",
    "conversation_history": [
        {"role": "user", "content": "之前的用户消息"},
        {"role": "assistant", "content": "之前的AI回复"}
    ],
    "system_prompt_type": "default",
    "custom_system_prompt": "自定义系统提示词（可选）",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `message` | string | ✅ | - | 用户输入的消息内容 |
| `conversation_history` | array | ❌ | [] | 对话历史记录 |
| `system_prompt_type` | string | ❌ | "default" | 系统提示词类型 |
| `custom_system_prompt` | string | ❌ | null | 自定义系统提示词 |
| `max_tokens` | integer | ❌ | 2000 | 最大输出token数 |
| `temperature` | float | ❌ | 0.7 | 温度参数（0.0-1.0） |

#### 对话历史格式

对话历史应该是一个包含消息对象的数组，每个消息对象包含：

```json
{
    "role": "user|assistant",
    "content": "消息内容"
}
```

- `role`: 消息角色，必须是 "user" 或 "assistant"
- `content`: 消息内容，字符串类型

#### 响应格式

```json
{
    "success": true,
    "data": {
        "response": "AI的回复内容",
        "model_used": "使用的模型名称",
        "system_prompt_type": "使用的系统提示词类型",
        "tokens_used": 1234,
        "conversation_length": 6,
        "suggested_next_history": [
            {"role": "user", "content": "用户消息"},
            {"role": "assistant", "content": "AI回复"}
        ]
    }
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `data.response` | string | AI的回复内容 |
| `data.model_used` | string | 使用的AI模型名称 |
| `data.system_prompt_type` | string | 使用的系统提示词类型 |
| `data.tokens_used` | integer | 本次对话使用的token总数 |
| `data.conversation_length` | integer | 当前对话的消息数量 |
| `data.suggested_next_history` | array | 建议的下一轮对话历史 |

### 2. 系统提示词类型

#### 预设提示词类型

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `default` | 智能、友好、有帮助的AI助手 | 通用对话 |
| `professional` | 专业、严谨的AI助手 | 工作、学习 |
| `creative` | 富有创造力和想象力的AI助手 | 创意、艺术 |
| `educational` | 耐心、细致的AI教育助手 | 教学、学习 |
| `casual` | 轻松、友好的AI助手 | 休闲聊天 |
| `technical` | 技术专家AI助手 | 技术问题 |
| 🌟 `red_culture` | **红色文化和理论知识专用AI助手** | **理论学习、政策宣传、教育培训、思想教育** |

#### 🌟 红色文化主题 (`red_culture`) 详细说明

红色文化主题是一个特殊的系统提示词类型，专门用于红色文化和理论知识问答，同时也关注教育、科技、新闻、生活等积极正面的话题。该主题具有以下特点：

##### 优先回答范围
AI优先回答与以下主题相关的问题：
- **马克思主义理论**：马克思主义哲学、政治经济学、科学社会主义
- **中国特色社会主义理论体系**：邓小平理论、"三个代表"重要思想、科学发展观、习近平新时代中国特色社会主义思想
- **中国共产党历史、理论、路线方针政策**：党的历史、理论创新、政策解读
- **中国革命历史、建设历史、改革历史**：重要历史事件、历史人物、历史经验
- **社会主义核心价值观、中华优秀传统文化**：价值观念、文化传承、道德建设
- **国家法律法规、政策文件**：法律条文、政策解读、制度说明
- **时事政治、国际关系中的相关理论问题**：政治理论、国际关系理论

##### 积极正面话题
AI也可以回答以下积极正面的内容：
- **教育话题**：学习方法、知识科普、技能培训、学术研究等
- **科技话题**：科技创新、技术发展、科学发现、工程应用等
- **新闻话题**：时事新闻、社会进步、经济发展、国际关系等
- **生活话题**：健康生活、环保理念、社会公益、文化传承等
- **职业发展**：职场技能、创业指导、职业规划、个人成长等

##### 严格禁止回答
对于以下内容，AI必须明确拒绝回答：
- 娱乐八卦、明星绯闻、娱乐圈内幕
- 商业广告、产品推销、营销推广
- 个人隐私、八卦消息、负面新闻
- 暴力、色情、赌博等不良内容
- 政治敏感、社会争议等敏感话题

##### 回答要求
- 基于权威理论、政策文件、科学事实和正面价值观
- 语言准确、严谨、有教育意义和启发性
- 引导用户树立正确的价值观和世界观
- 对于超出范围的问题，礼貌地说明专业领域
- 在回答其他话题时，也要体现积极正面的价值导向

##### 使用场景
- **理论学习**：马克思主义理论学习、政策理论学习
- **政策宣传**：党的路线方针政策宣传、国家政策解读
- **教育培训**：党校培训、干部教育、学生思想政治教育
- **思想教育**：价值观教育、理想信念教育、爱国主义教育
- **知识科普**：科学知识普及、技术发展介绍
- **生活指导**：健康生活指导、职业发展建议

##### 使用示例

```python
import requests

# 正常范围内的红色文化问题
response1 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请介绍一下马克思主义的基本原理",
    "system_prompt_type": "red_culture"
})

# 教育话题（积极正面）
response2 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "如何提高学习效率？",
    "system_prompt_type": "red_culture"
})

# 科技话题（积极正面）
response3 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "人工智能的发展前景如何？",
    "system_prompt_type": "red_culture"
})

# 超出范围的娱乐问题（AI会拒绝回答）
response4 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "最近有什么明星八卦新闻吗？",
    "system_prompt_type": "red_culture"
})
```

#### 自定义提示词

除了使用预设类型，还可以通过 `custom_system_prompt` 参数自定义AI助手的角色和行为。

### 3. 配置参数

#### 默认配置

```json
{
    "max_tokens": 2000,
    "temperature": 0.7,
    "max_history_length": 20,
    "default_system_prompt": "default"
}
```

#### 参数说明

- `max_tokens`: 控制AI回复的最大长度
- `temperature`: 控制回复的创造性（0.0=保守，1.0=创造性）
- `max_history_length`: 建议的最大对话历史长度

#### 🌟 红色文化主题特殊配置

当使用 `red_culture` 主题时，系统会自动调整以下参数：
- **温度参数**：自动降低到0.5以下，确保回答更加严谨
- **最大token数**：自动增加到2500，确保回答的完整性
- **内容验证**：自动验证用户问题是否在允许范围内

## 使用示例

### 基础对话

```python
import requests

# 单轮对话
response = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "你好，请介绍一下你自己",
    "system_prompt_type": "default"
})

print(response.json())
```

### 多轮对话

```python
import requests

# 第一轮对话
response1 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "我想学习Python编程",
    "system_prompt_type": "educational"
})

result1 = response1.json()
ai_response1 = result1['data']['response']

# 第二轮对话（带历史记录）
response2 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请给我一个具体的例子",
    "conversation_history": [
        {"role": "user", "content": "我想学习Python编程"},
        {"role": "assistant", "content": ai_response1}
    ],
    "system_prompt_type": "educational"
})

print(response2.json())
```

### 🌟 红色文化主题对话

```python
import requests

# 红色文化理论学习
response1 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请解释一下什么是中国特色社会主义",
    "system_prompt_type": "red_culture"
})

# 政策解读
response2 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请介绍一下'十四五'规划的主要内容",
    "system_prompt_type": "red_culture"
})

# 超出范围的问题（AI会拒绝回答）
response3 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "推荐一下最近有什么好看的电影",
    "system_prompt_type": "red_culture"
})
```

### 自定义提示词

```python
import requests

response = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请用幽默的方式解释什么是人工智能",
    "custom_system_prompt": "你是一个幽默风趣的AI助手，请用轻松有趣的方式回答问题，可以适当使用比喻和笑话。",
    "temperature": 0.9
})

print(response.json())
```

### JavaScript示例

```javascript
// 基础对话
async function chat(message, history = [], promptType = 'default') {
    const response = await fetch('/api/ai-chat/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            conversation_history: history,
            system_prompt_type: promptType
        })
    });
    
    return await response.json();
}

// 使用示例
// 普通对话
chat("你好，请介绍一下你自己").then(result => {
    console.log(result.data.response);
});

// 红色文化主题对话
chat("请介绍一下马克思主义的基本原理", [], "red_culture").then(result => {
    console.log(result.data.response);
});
```

## 错误处理

### 常见错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误（如空消息、无效格式） |
| 500 | Internal Server Error | 服务器内部错误（如AI模型调用失败） |
| 503 | Service Unavailable | 服务不可用（如健康检查失败） |

### 错误响应格式

```json
{
    "success": false,
    "error": "错误描述信息",
    "model_used": "使用的模型名称（如果可用）"
}
```

## 最佳实践

### 1. 对话历史管理

- 客户端应该维护对话历史记录
- 建议限制历史记录长度（不超过20轮）
- 定期清理过长的对话历史

### 2. 参数调优

- `temperature`: 0.0-0.3 适合事实性回答，0.7-1.0 适合创意性回答
- `max_tokens`: 根据需求设置，避免过长回复

### 3. 🌟 红色文化主题使用建议

- **适用场景**：理论学习、政策宣传、教育培训、思想教育
- **问题类型**：确保问题与红色文化、理论知识相关
- **回答质量**：AI会提供准确、严谨、有教育意义的回答
- **范围限制**：超出范围的问题会被礼貌拒绝

### 4. 错误处理

- 实现重试机制
- 处理网络异常和API错误
- 提供用户友好的错误提示

### 5. 性能优化

- 避免频繁的API调用
- 合理缓存对话历史
- 考虑使用流式API获得更好的用户体验

## 测试和调试

### 健康检查

```bash
curl http://localhost:8000/api/ai-chat/health/
```

### 获取配置信息

```bash
curl http://localhost:8000/api/ai-chat/config/
```

### 获取可用提示词

```bash
curl http://localhost:8000/api/ai-chat/prompts/
```

### 🌟 测试红色文化主题

```bash
# 测试正常范围内的红色文化问题
curl -X POST http://localhost:8000/api/ai-chat/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "请介绍一下马克思主义的基本原理", "system_prompt_type": "red_culture"}'

# 测试超出范围的问题
curl -X POST http://localhost:8000/api/ai-chat/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "最近有什么明星八卦新闻吗？", "system_prompt_type": "red_culture"}'
```

## 注意事项

1. **API密钥**: 确保正确设置 `ARK_API_KEY` 环境变量
2. **请求频率**: 避免过于频繁的API调用
3. **内容安全**: 注意用户输入内容的安全性
4. **成本控制**: 监控token使用量，控制API调用成本
5. **数据隐私**: 对话内容可能被用于模型训练，注意敏感信息
6. **🌟 红色文化主题**: 该主题具有严格的回答范围限制，确保内容的政治性和教育性

## 更新日志

- **v1.0.0**: 初始版本，支持基础多轮对话功能
- 支持多种系统提示词类型
- 支持自定义系统提示词
- 支持对话参数调节
- 完善的错误处理和输入验证
- **🌟 v1.1.0**: 新增红色文化主题，支持严格的回答范围限制

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。
