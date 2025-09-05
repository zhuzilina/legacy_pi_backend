# AI对话应用 (ai_chat)

## 概述

AI对话应用是一个基于Django的智能聊天服务，支持多轮对话交互。该应用采用客户端维护对话历史的架构，服务端专注于AI模型调用和响应生成。

## 主要特性

- 🗣️ **多轮对话支持**：支持连续的多轮对话交互
- 📝 **客户端维护历史**：对话记录完全由客户端管理，服务端无状态
- 🎭 **多种AI角色**：提供多种预设的系统提示词风格
- ⚙️ **灵活参数配置**：支持自定义提示词、温度、最大token数等参数
- 🔒 **安全可靠**：完善的错误处理和输入验证
- 📊 **详细响应信息**：返回模型信息、token使用量等详细信息
- 🌟 **红色文化主题**：专门用于红色文化和理论知识问答，具有严格的回答范围限制

## 技术架构

### 核心组件

- **AIChatService**: 核心服务类，负责与AI模型交互
- **配置管理**: 支持多种系统提示词和对话参数配置
- **输入验证**: 完善的请求参数验证和错误处理
- **响应格式化**: 统一的API响应格式
- **🌟 红色文化主题处理**: 专门的系统提示词和内容验证机制

### 依赖关系

- Django 5.2+
- OpenAI SDK
- Python 3.8+

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

## 🌟 红色文化主题详解

### 功能特点

红色文化主题是一个特殊的系统提示词类型，专门用于红色文化和理论知识问答，同时也关注教育、科技、新闻、生活等积极正面的话题。该主题具有以下特点：

#### 优先回答范围
AI优先回答与以下主题相关的问题：
- **马克思主义理论**：马克思主义哲学、政治经济学、科学社会主义
- **中国特色社会主义理论体系**：邓小平理论、"三个代表"重要思想、科学发展观、习近平新时代中国特色社会主义思想
- **中国共产党历史、理论、路线方针政策**：党的历史、理论创新、政策解读
- **中国革命历史、建设历史、改革历史**：重要历史事件、历史人物、历史经验
- **社会主义核心价值观、中华优秀传统文化**：价值观念、文化传承、道德建设
- **国家法律法规、政策文件**：法律条文、政策解读、制度说明
- **时事政治、国际关系中的相关理论问题**：政治理论、国际关系理论

#### 积极正面话题
AI也可以回答以下积极正面的内容：
- **教育话题**：学习方法、知识科普、技能培训、学术研究等
- **科技话题**：科技创新、技术发展、科学发现、工程应用等
- **新闻话题**：时事新闻、社会进步、经济发展、国际关系等
- **生活话题**：健康生活、环保理念、社会公益、文化传承等
- **职业发展**：职场技能、创业指导、职业规划、个人成长等

#### 自动内容验证和过滤
- **智能识别**：自动识别用户问题是否在允许范围内
- **强制拒绝**：对于超出范围的问题，AI必须明确拒绝回答
- **后处理验证**：系统会对AI回答进行二次验证，确保符合要求
- **积极引导**：对积极正面话题提供鼓励性的回答

#### 政治性和教育性保证
- **权威性**：基于权威理论、政策文件、科学事实和正面价值观
- **严谨性**：语言准确、严谨、有教育意义和启发性
- **引导性**：引导用户树立正确的价值观和世界观
- **正面性**：在回答其他话题时，也要体现积极正面的价值导向

### 使用场景

- **理论学习**：马克思主义理论学习、政策理论学习
- **政策宣传**：党的路线方针政策宣传、国家政策解读
- **教育培训**：党校培训、干部教育、学生思想政治教育
- **思想教育**：价值观教育、理想信念教育、爱国主义教育
- **知识科普**：科学知识普及、技术发展介绍
- **生活指导**：健康生活指导、职业发展建议

### 技术实现

- **增强系统提示词**：在原有提示词基础上增加强化要求
- **参数自动调整**：温度参数自动降低到0.5以下，确保回答严谨
- **内容关键词检测**：检测用户问题中的关键词，识别超出范围的问题
- **智能回复修正**：对于超出范围的问题，自动生成拒绝说明
- **积极话题识别**：自动识别教育、科技、新闻、生活等积极正面话题

## 快速开始

### 1. 环境配置

确保设置了正确的环境变量：
```bash
export ARK_API_KEY="你的API密钥"
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python manage.py migrate
```

### 4. 启动服务

```bash
python manage.py runserver
```

### 5. 测试API

```bash
python test_ai_chat.py
```

## 使用示例

### 基础对话

```python
import requests

response = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "你好，请介绍一下你自己",
    "system_prompt_type": "default"
})

print(response.json())
```

### 🌟 红色文化主题对话

```python
import requests

# 正常范围内的红色文化问题
response1 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请介绍一下马克思主义的基本原理",
    "system_prompt_type": "red_culture"
})

# 超出范围的娱乐问题（AI会拒绝回答）
response2 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "最近有什么明星八卦新闻吗？",
    "system_prompt_type": "red_culture"
})

print("红色文化问题回答:", response1.json())
print("超出范围问题回答:", response2.json())
```

### 多轮对话

```python
import requests

# 第一轮对话
response1 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "我想学习马克思主义理论",
    "system_prompt_type": "red_culture"
})

result1 = response1.json()
ai_response1 = result1['data']['response']

# 第二轮对话（带历史记录）
response2 = requests.post("http://localhost:8000/api/ai-chat/chat/", json={
    "message": "请给我一个具体的例子",
    "conversation_history": [
        {"role": "user", "content": "我想学习马克思主义理论"},
        {"role": "assistant", "content": ai_response1}
    ],
    "system_prompt_type": "red_culture"
})

print(response2.json())
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

## 系统提示词类型

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `default` | 智能、友好、有帮助的AI助手 | 通用对话 |
| `professional` | 专业、严谨的AI助手 | 工作、学习 |
| `creative` | 富有创造力和想象力的AI助手 | 创意、艺术 |
| `educational` | 耐心、细致的AI教育助手 | 教学、学习 |
| `casual` | 轻松、友好的AI助手 | 休闲聊天 |
| `technical` | 技术专家AI助手 | 技术问题 |
| 🌟 `red_culture` | **红色文化和理论知识专用AI助手** | **理论学习、政策宣传、教育培训、思想教育、知识科普、生活指导** |

## 配置参数

### 默认配置

```json
{
    "max_tokens": 2000,
    "temperature": 0.7,
    "max_history_length": 20,
    "default_system_prompt": "default"
}
```

### 🌟 红色文化主题特殊配置

当使用 `red_culture` 主题时，系统会自动调整以下参数：
- **温度参数**：自动降低到0.5以下，确保回答更加严谨
- **最大token数**：自动增加到2500，确保回答的完整性
- **内容验证**：自动验证用户问题是否在允许范围内
- **积极话题识别**：自动识别教育、科技、新闻、生活等积极正面话题

### 参数说明

- `max_tokens`: 控制AI回复的最大长度
- `temperature`: 控制回复的创造性（0.0=保守，1.0=创造性）
- `max_history_length`: 建议的最大对话历史长度

## 开发指南

### 项目结构

```
ai_chat/
├── __init__.py          # 应用初始化
├── admin.py             # 管理界面配置
├── apps.py              # 应用配置
├── config.py            # 配置文件（包含红色文化主题配置）
├── models.py            # 数据模型（目前为空）
├── services.py          # 核心服务逻辑（包含红色文化主题处理）
├── tests.py             # 测试用例
├── urls.py              # URL路由配置
├── views.py             # 视图函数和类
└── README.md            # 本文档
```

### 添加新功能

1. 在 `services.py` 中添加新的服务方法
2. 在 `views.py` 中添加对应的视图函数
3. 在 `urls.py` 中添加URL路由
4. 在 `tests.py` 中添加测试用例

### 🌟 红色文化主题扩展

如需扩展红色文化主题的功能：

1. **修改配置文件**：在 `config.py` 中调整系统提示词
2. **增强验证逻辑**：在 `services.py` 中完善内容验证机制
3. **添加新主题**：可以创建更多专门的主题类型

### 自定义配置

修改 `config.py` 文件中的配置参数：

```python
# 添加新的系统提示词
CHAT_SYSTEM_PROMPTS['custom'] = '你的自定义提示词'

# 修改默认参数
CHAT_CONFIG['max_tokens'] = 3000
CHAT_CONFIG['temperature'] = 0.8

# 扩展红色文化主题
CHAT_SYSTEM_PROMPTS['red_culture'] += '\n\n额外的要求说明'
```

## 测试

### 运行所有测试

```bash
python test_ai_chat.py
```

### 测试覆盖率

当前测试覆盖以下功能：
- ✅ 健康检查API
- ✅ 获取系统提示词API
- ✅ 获取配置API
- ✅ 单轮对话API
- ✅ 带历史记录的对话API
- ✅ 自定义提示词对话API
- ✅ 🌟 红色文化主题对话API
- ✅ 基于类的对话视图
- ✅ 错误处理

### 🌟 红色文化主题测试

测试脚本包含以下红色文化主题测试：
- 正常范围内的红色文化问题
- 教育话题（积极正面）
- 科技话题（积极正面）
- 生活话题（积极正面）
- 超出范围的娱乐问题
- 超出范围的电影推荐问题

## 部署说明

### 生产环境配置

1. 设置 `DEBUG = False`
2. 配置生产数据库
3. 设置正确的 `ALLOWED_HOSTS`
4. 配置静态文件服务
5. 使用生产级Web服务器（如Nginx + Gunicorn）

### 环境变量

```bash
# 必需的环境变量
ARK_API_KEY=your_api_key_here

# 可选的环境变量
DJANGO_SETTINGS_MODULE=legacy_pi_backend.settings
```

## 故障排除

### 常见问题

1. **API密钥错误**: 检查 `ARK_API_KEY` 环境变量是否正确设置
2. **网络连接问题**: 检查网络连接和防火墙设置
3. **模型响应慢**: 调整 `max_tokens` 和 `temperature` 参数
4. **内存使用过高**: 限制 `max_history_length` 参数

### 🌟 红色文化主题相关问题

1. **AI拒绝回答正常问题**: 检查问题是否确实在允许范围内
2. **回答不够严谨**: 系统会自动调整参数，确保回答质量
3. **超出范围问题未被拒绝**: 检查系统提示词配置是否正确
4. **积极话题识别问题**: 检查关键词配置是否正确

### 日志查看

```bash
tail -f server.log
```

## 更新日志

- **v1.0.0**: 初始版本，支持基础多轮对话功能
- 支持多种系统提示词类型
- 支持自定义系统提示词
- 支持对话参数调节
- 完善的错误处理和输入验证
- **🌟 v1.1.0**: 新增红色文化主题，支持严格的回答范围限制
- 自动内容验证和过滤
- 政治性和教育性保证
- 智能问题识别和拒绝
- **🌟 v1.2.0**: 放宽红色文化主题限制，支持教育、科技、新闻、生活等积极正面话题
- 积极话题智能识别
- 正面价值导向引导
- 更灵活的内容范围

## 贡献指南

欢迎提交Issue和Pull Request来改进这个应用！

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请联系开发团队。