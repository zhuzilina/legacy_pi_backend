# AI对话API 使用说明

## 概述

AI对话API是一个支持多轮对话的智能聊天服务，基于大语言模型提供自然语言交互能力。该API采用客户端维护对话历史的架构，服务端专注于AI模型调用和响应生成。

## 主要特性

- 🗣️ **多轮对话支持**：支持连续的多轮对话交互
- 📝 **客户端维护历史**：对话记录完全由客户端管理，服务端无状态
- 🎭 **专业AI助手**：专业的AI知识助手，具备广泛的知识储备和专业的分析能力
- ⚙️ **灵活参数配置**：支持自定义提示词、温度、最大token数等参数
- 🔒 **安全可靠**：完善的错误处理和输入验证
- 📊 **详细响应信息**：返回模型信息、token使用量等详细信息
- 🖼️ **图片理解功能**：支持图片上传、缓存和AI图片分析
- 📤 **图片缓存管理**：图片自动缓存到Redis，支持批量上传
- 🎨 **多种图片分析风格**：提供详细、简洁、创意、技术等多种图片理解模式
- ⚡ **流式对话支持**：支持实时流式响应，使用Server-Sent Events技术
- 🔄 **实时流式响应**：AI回复内容实时流式返回，提升用户体验

## API端点

### 基础URL
```
http://your-domain/api/ai-chat/
```

### 可用端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/chat/` | POST | 主要对话API，支持多轮对话 |
| `/chat-with-images/` | POST | 带图片的AI对话API |
| `/upload-image/` | POST | 上传单张图片到Redis缓存 |
| `/upload-images-batch/` | POST | 批量上传图片到Redis缓存 |
| `/stream/` | POST | 流式对话API（Server-Sent Events） |
| `/stream-with-images/` | POST | 流式带图片的AI对话API |
| `/prompts/` | GET | 获取可用的系统提示词类型 |
| `/image-prompts/` | GET | 获取可用的图片理解提示词类型 |
| `/image-cache-stats/` | GET | 获取图片缓存统计信息 |
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

### 2. 图片上传API (`/upload-image/`)

#### 请求格式
```http
POST /api/ai-chat/upload-image/
Content-Type: multipart/form-data

image: [图片文件]
```

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `image` | file | ✅ | 要上传的图片文件 |

#### 支持的图片格式
- JPEG
- PNG
- GIF
- WEBP

#### 图片限制
- 最大文件大小：5MB
- 缓存过期时间：7天

#### 响应格式

```json
{
    "success": true,
    "data": {
        "image_id": "abc123def456",
        "image_info": {
            "filename": "example.jpg",
            "size": 1024000,
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "content_type": "image/jpeg"
        }
    }
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 上传是否成功 |
| `data.image_id` | string | 图片的唯一标识符，用于后续对话 |
| `data.image_info.filename` | string | 原始文件名 |
| `data.image_info.size` | integer | 文件大小（字节） |
| `data.image_info.width` | integer | 图片宽度 |
| `data.image_info.height` | integer | 图片高度 |
| `data.image_info.format` | string | 图片格式 |
| `data.image_info.content_type` | string | MIME类型 |

### 3. 批量图片上传API (`/upload-images-batch/`)

#### 请求格式
```http
POST /api/ai-chat/upload-images-batch/
Content-Type: multipart/form-data

images: [图片文件1]
images: [图片文件2]
...
```

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `images` | file[] | ✅ | 要上传的图片文件列表 |

#### 限制
- 一次最多上传5张图片
- 每张图片最大5MB

#### 响应格式

```json
{
    "success": true,
    "data": {
        "total_count": 3,
        "success_count": 2,
        "results": [
            {
                "index": 0,
                "success": true,
                "image_id": "abc123def456",
                "image_info": {
                    "filename": "image1.jpg",
                    "size": 1024000,
                    "width": 1920,
                    "height": 1080,
                    "format": "JPEG",
                    "content_type": "image/jpeg"
                }
            },
            {
                "index": 1,
                "success": false,
                "error": "图片文件过大，最大支持 5MB"
            },
            {
                "index": 2,
                "success": true,
                "image_id": "def456ghi789",
                "image_info": {
                    "filename": "image2.png",
                    "size": 2048000,
                    "width": 1280,
                    "height": 720,
                    "format": "PNG",
                    "content_type": "image/png"
                }
            }
        ]
    }
}
```

### 4. 带图片的AI对话API (`/chat-with-images/`)

#### 请求格式
```http
POST /api/ai-chat/chat-with-images/
Content-Type: application/json

{
    "message": "请分析这些图片",
    "image_ids": ["abc123def456", "def456ghi789"],
    "conversation_history": [
        {"role": "user", "content": "之前的用户消息"},
        {"role": "assistant", "content": "之前的AI回复"}
    ],
    "image_prompt_type": "default",
    "custom_image_prompt": "自定义图片理解提示词（可选）",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `message` | string | ❌ | "" | 用户输入的消息内容 |
| `image_ids` | array | ✅ | - | 图片ID列表 |
| `conversation_history` | array | ❌ | [] | 对话历史记录 |
| `image_prompt_type` | string | ❌ | "default" | 图片理解提示词类型 |
| `custom_image_prompt` | string | ❌ | null | 自定义图片理解提示词 |
| `max_tokens` | integer | ❌ | 2000 | 最大输出token数 |
| `temperature` | float | ❌ | 0.7 | 温度参数（0.0-1.0） |

#### 响应格式

```json
{
    "success": true,
    "data": {
        "response": "AI对图片的分析结果",
        "model_used": "doubao-seed-1-6-250615",
        "image_prompt_type": "default",
        "images_processed": 2,
        "tokens_used": 1234,
        "conversation_length": 3,
        "suggested_next_history": [
            {"role": "user", "content": "请分析这些图片"},
            {"role": "assistant", "content": "AI对图片的分析结果"}
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
| `data.image_prompt_type` | string | 使用的图片理解提示词类型 |
| `data.images_processed` | integer | 成功处理的图片数量 |
| `data.tokens_used` | integer | 本次对话使用的token总数 |
| `data.conversation_length` | integer | 当前对话的消息数量 |
| `data.suggested_next_history` | array | 建议的下一轮对话历史 |

### 5. 系统提示词类型

#### 预设提示词类型

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `default` | **专业的AI知识助手**，具备广泛的知识储备和专业的分析能力 | 通用知识问答、专业咨询 |

#### 默认提示词特点

当前的 `default` 系统提示词具有以下特点：

##### 核心能力
- **专业知识解答**：提供准确、专业、有深度的知识解答
- **科学分析**：基于科学事实、权威理论和实践经验进行分析
- **逻辑清晰**：以逻辑清晰、结构化的方式组织回答
- **智能调整**：根据问题复杂度调整回答的详细程度

##### 回答原则
1. **准确性优先**：确保信息的准确性和可靠性，避免传播错误信息
2. **专业深度**：提供有见地的分析，不仅仅是表面信息
3. **逻辑清晰**：条理分明地组织答案，便于理解
4. **实用导向**：注重回答的实用价值和可操作性
5. **持续学习**：承认知识边界，对不确定的内容保持谦逊

##### 知识领域
涵盖但不限于：科学技术、人文社科、商业管理、教育学习、生活健康、文化艺术、历史哲学、法律法规等各个领域的专业知识。

##### 回答风格
- 语言专业但不失亲和力
- 结构清晰，重点突出
- 适当使用例子和类比帮助理解
- 根据用户需求调整详细程度

#### 自定义提示词

除了使用预设类型，还可以通过 `custom_system_prompt` 参数自定义AI助手的角色和行为。

### 6. 图片理解提示词类型

#### 预设图片理解提示词

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `default` | 详细描述图片内容，包括主要对象、场景、颜色、构图等元素 | 通用图片分析 |
| `detailed` | 详细分析图片，包括主要内容、场景环境、颜色光线、构图布局、含义用途 | 深度图片分析 |
| `simple` | 用简洁的语言描述图片的主要内容 | 快速图片理解 |
| `creative` | 发挥想象力，为图片创作有趣的故事或描述 | 创意图片解读 |
| `technical` | 从技术角度分析图片，包括构图、色彩、光线、焦点等摄影技术要素 | 技术图片分析 |
| `educational` | 以教育者角度分析图片，指出知识点、学习价值或教育意义 | 教育图片分析 |
| `qa` | 基于图片回答用户的问题 | 图片问答 |

#### 自定义图片理解提示词

除了使用预设类型，还可以通过 `custom_image_prompt` 参数自定义AI如何理解和分析图片。

### 7. 图片缓存统计API (`/image-cache-stats/`)

#### 请求格式
```http
GET /api/ai-chat/image-cache-stats/
```

#### 响应格式

```json
{
    "success": true,
    "data": {
        "total_images": 25,
        "total_size_bytes": 52428800,
        "total_size_mb": 50.0,
        "cache_expire_time": 604800,
        "max_image_size": 5242880,
        "supported_formats": ["JPEG", "PNG", "GIF", "WEBP"]
    }
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `data.total_images` | integer | 当前缓存的图片总数 |
| `data.total_size_bytes` | integer | 缓存图片的总大小（字节） |
| `data.total_size_mb` | float | 缓存图片的总大小（MB） |
| `data.cache_expire_time` | integer | 缓存过期时间（秒） |
| `data.max_image_size` | integer | 单张图片最大大小（字节） |
| `data.supported_formats` | array | 支持的图片格式列表 |

### 8. 流式对话API (`/stream/`)

#### 请求格式
```http
POST /api/ai-chat/stream/
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
与普通对话API相同，请参考 [对话API参数说明](#1-对话api-chat)

#### 响应格式
流式响应使用Server-Sent Events (SSE)格式，每个数据块包含：

```json
data: {"type": "start", "message": "开始流式对话"}

data: {"type": "content", "content": "AI回复的", "model": "doubao-seed-1-6-250615", "system_prompt_type": "default"}

data: {"type": "content", "content": "内容片段", "model": "doubao-seed-1-6-250615", "system_prompt_type": "default"}

data: {"type": "done", "finish_reason": "stop", "model": "doubao-seed-1-6-250615", "tokens_used": 1234}

data: {"type": "end"}
```

#### 响应类型说明

| 类型 | 描述 | 字段 |
|------|------|------|
| `start` | 开始信号 | `message`: 开始消息 |
| `content` | 内容片段 | `content`: 文本内容，`model`: 模型名称，`system_prompt_type`: 提示词类型 |
| `done` | 完成信号 | `finish_reason`: 完成原因，`tokens_used`: 使用的token数 |
| `error` | 错误信号 | `error`: 错误信息 |
| `end` | 结束信号 | 无额外字段 |

### 9. 流式带图片对话API (`/stream-with-images/`)

#### 请求格式
```http
POST /api/ai-chat/stream-with-images/
Content-Type: application/json

{
    "message": "请分析这些图片",
    "image_ids": ["abc123def456", "def456ghi789"],
    "conversation_history": [],
    "image_prompt_type": "detailed",
    "custom_image_prompt": "自定义图片理解提示词（可选）",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

#### 请求参数
与带图片对话API相同，请参考 [带图片的AI对话API参数说明](#4-带图片的ai对话api-chat-with-images)

#### 响应格式
流式响应格式与普通流式对话相同，但内容类型为图片分析结果。

### 10. 配置参数

#### 对话配置

```json
{
    "max_tokens": 2000,
    "temperature": 0.7,
    "max_history_length": 20,
    "default_system_prompt": "default"
}
```

#### 图片处理配置

```json
{
    "max_image_size": 5242880,
    "supported_formats": ["JPEG", "PNG", "GIF", "WEBP"],
    "cache_expire_time": 604800,
    "max_images_per_request": 5
}
```

#### 参数说明

**对话参数**：
- `max_tokens`: 控制AI回复的最大长度
- `temperature`: 控制回复的创造性（0.0=保守，1.0=创造性）
- `max_history_length`: 建议的最大对话历史长度
- `default_system_prompt`: 默认系统提示词类型

**图片处理参数**：
- `max_image_size`: 单张图片最大大小（5MB）
- `supported_formats`: 支持的图片格式列表
- `cache_expire_time`: 图片缓存过期时间（7天）
- `max_images_per_request`: 每次请求最大图片数量（5张）

## 使用示例

### 基础对话

```python
import requests

# 单轮对话
response = requests.post("http://10.0.2.2:8000/api/ai-chat/chat/", json={
    "message": "你好，请介绍一下你自己",
    "system_prompt_type": "default"
})

print(response.json())
```

### 多轮对话

```python
import requests

# 第一轮对话
response1 = requests.post("http://10.0.2.2:8000/api/ai-chat/chat/", json={
    "message": "我想学习Python编程",
    "system_prompt_type": "educational"
})

result1 = response1.json()
ai_response1 = result1['data']['response']

# 第二轮对话（带历史记录）
response2 = requests.post("http://10.0.2.2:8000/api/ai-chat/chat/", json={
    "message": "请给我一个具体的例子",
    "conversation_history": [
        {"role": "user", "content": "我想学习Python编程"},
        {"role": "assistant", "content": ai_response1}
    ],
    "system_prompt_type": "educational"
})

print(response2.json())
```

### 图片上传和对话

```python
import requests

# 1. 上传图片
with open('example.jpg', 'rb') as f:
    files = {'image': f}
    upload_response = requests.post("http://10.0.2.2:8000/api/ai-chat/upload-image/", files=files)
    
upload_result = upload_response.json()
if upload_result['success']:
    image_id = upload_result['data']['image_id']
    print(f"图片上传成功，ID: {image_id}")
    
    # 2. 使用图片进行对话
    chat_response = requests.post("http://10.0.2.2:8000/api/ai-chat/chat-with-images/", json={
        "message": "请详细分析这张图片",
        "image_ids": [image_id],
        "image_prompt_type": "detailed"
    })
    
    print(chat_response.json())
```

### 批量图片上传和对话

```python
import requests

# 1. 批量上传图片
files = []
for i in range(3):
    files.append(('images', open(f'image{i+1}.jpg', 'rb')))

batch_response = requests.post("http://10.0.2.2:8000/api/ai-chat/upload-images-batch/", files=files)
batch_result = batch_response.json()

if batch_result['success']:
    # 提取成功上传的图片ID
    image_ids = []
    for result in batch_result['data']['results']:
        if result['success']:
            image_ids.append(result['image_id'])
    
    # 2. 使用多张图片进行对话
    chat_response = requests.post("http://10.0.2.2:8000/api/ai-chat/chat-with-images/", json={
        "message": "请比较这些图片的异同点",
        "image_ids": image_ids,
        "image_prompt_type": "comparison"
    })
    
    print(chat_response.json())
```

### 自定义提示词

```python
import requests

response = requests.post("http://10.0.2.2:8000/api/ai-chat/chat/", json={
    "message": "请用幽默的方式解释什么是人工智能",
    "custom_system_prompt": "你是一个幽默风趣的AI助手，请用轻松有趣的方式回答问题，可以适当使用比喻和笑话。",
    "temperature": 0.9
})

print(response.json())
```

### 流式对话示例

```python
import requests
import json

# 流式对话
def stream_chat(message, history=None):
    url = "http://10.0.2.2:8000/api/ai-chat/stream/"
    data = {
        "message": message,
        "conversation_history": history or [],
        "system_prompt_type": "default"
    }
    
    response = requests.post(url, json=data, stream=True)
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # 去掉 'data: ' 前缀
                    if data['type'] == 'content':
                        print(data['content'], end='', flush=True)
                    elif data['type'] == 'done':
                        print(f"\n\n[完成] Token使用量: {data.get('tokens_used', 'N/A')}")
                    elif data['type'] == 'error':
                        print(f"\n[错误] {data['error']}")
                except json.JSONDecodeError:
                    continue

# 使用示例
stream_chat("请详细介绍一下人工智能的发展历史")
```

### 流式图片对话示例

```python
import requests
import json

# 1. 先上传图片
with open('example.jpg', 'rb') as f:
    files = {'image': f}
    upload_response = requests.post("http://10.0.2.2:8000/api/ai-chat/upload-image/", files=files)
    
upload_result = upload_response.json()
if upload_result['success']:
    image_id = upload_result['data']['image_id']
    
    # 2. 流式图片对话
    def stream_chat_with_images(message, image_ids):
        url = "http://10.0.2.2:8000/api/ai-chat/stream-with-images/"
        data = {
            "message": message,
            "image_ids": image_ids,
            "image_prompt_type": "detailed"
        }
        
        response = requests.post(url, json=data, stream=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data['type'] == 'content':
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'done':
                            print(f"\n\n[完成] 处理图片数: {data.get('images_processed', 'N/A')}")
                    except json.JSONDecodeError:
                        continue
    
    stream_chat_with_images("请详细分析这张图片", [image_id])
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

// 图片上传
async function uploadImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/api/ai-chat/upload-image/', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// 带图片的对话
async function chatWithImages(message, imageIds, history = [], imagePromptType = 'default') {
    const response = await fetch('/api/ai-chat/chat-with-images/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            image_ids: imageIds,
            conversation_history: history,
            image_prompt_type: imagePromptType
        })
    });
    
    return await response.json();
}

// 使用示例
// 普通对话
chat("你好，请介绍一下你自己").then(result => {
    console.log(result.data.response);
});

// 流式对话
async function streamChat(message, history = [], promptType = 'default') {
    const response = await fetch('/api/ai-chat/stream/', {
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
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.type === 'content') {
                        console.log(data.content);
                    } else if (data.type === 'done') {
                        console.log(`[完成] Token使用量: ${data.tokens_used}`);
                    } else if (data.type === 'error') {
                        console.error(`[错误] ${data.error}`);
                    }
                } catch (e) {
                    // 忽略解析错误
                }
            }
        }
    }
}

// 图片上传和对话
const fileInput = document.getElementById('imageInput');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        // 上传图片
        const uploadResult = await uploadImage(file);
        if (uploadResult.success) {
            const imageId = uploadResult.data.image_id;
            
            // 使用图片进行对话
            const chatResult = await chatWithImages(
                "请分析这张图片", 
                [imageId], 
                [], 
                "detailed"
            );
            console.log(chatResult.data.response);
        }
    }
});

// 流式对话使用示例
streamChat("请详细介绍一下人工智能的发展历史").then(() => {
    console.log("流式对话完成");
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
curl http://10.0.2.2:8000/api/ai-chat/health/
```

### 获取配置信息

```bash
curl http://10.0.2.2:8000/api/ai-chat/config/
```

### 获取可用提示词

```bash
curl http://10.0.2.2:8000/api/ai-chat/prompts/
```

### 测试图片功能

```bash
# 测试图片上传
curl -X POST http://10.0.2.2:8000/api/ai-chat/upload-image/ \
  -F "image=@example.jpg"

# 测试带图片的对话（需要先上传图片获取image_id）
curl -X POST http://10.0.2.2:8000/api/ai-chat/chat-with-images/ \
  -H "Content-Type: application/json" \
  -d '{"message": "请分析这张图片", "image_ids": ["your_image_id_here"], "image_prompt_type": "detailed"}'

# 测试获取图片理解提示词
curl http://10.0.2.2:8000/api/ai-chat/image-prompts/

# 测试获取图片缓存统计
curl http://10.0.2.2:8000/api/ai-chat/image-cache-stats/

# 测试流式对话
curl -X POST http://10.0.2.2:8000/api/ai-chat/stream/ \
  -H "Content-Type: application/json" \
  -d '{"message": "请介绍一下人工智能", "system_prompt_type": "default"}' \
  --no-buffer

# 测试流式图片对话（需要先上传图片获取image_id）
curl -X POST http://10.0.2.2:8000/api/ai-chat/stream-with-images/ \
  -H "Content-Type: application/json" \
  -d '{"message": "请分析这张图片", "image_ids": ["your_image_id_here"], "image_prompt_type": "detailed"}' \
  --no-buffer
```

## 注意事项

1. **API密钥**: 确保正确设置 `ARK_API_KEY` 环境变量
2. **请求频率**: 避免过于频繁的API调用
3. **内容安全**: 注意用户输入内容的安全性
4. **成本控制**: 监控token使用量，控制API调用成本
5. **数据隐私**: 对话内容可能被用于模型训练，注意敏感信息
6. **图片处理**: 图片会被缓存到Redis中，注意存储空间管理
7. **图片格式**: 仅支持JPEG、PNG、GIF、WEBP格式，单张图片最大5MB
8. **缓存管理**: 图片缓存7天后自动过期，可通过统计API监控缓存使用情况
9. **流式响应**: 流式API使用Server-Sent Events，需要客户端支持流式读取
10. **连接管理**: 流式连接会保持开启直到完成，注意连接超时设置

## 更新日志

- **v1.0.0**: 初始版本，支持基础多轮对话功能
- 支持多种系统提示词类型
- 支持自定义系统提示词
- 支持对话参数调节
- 完善的错误处理和输入验证
- **v1.1.0**: 新增图片理解功能
- 支持图片上传到Redis缓存
- 支持单张和批量图片上传
- 支持带图片的AI对话
- 支持多种图片理解提示词类型
- 新增图片缓存统计API
- 优化为专业的AI知识助手角色
- **v1.2.0**: 新增流式对话功能
- 支持流式AI对话（Server-Sent Events）
- 支持流式带图片的AI对话
- 实时流式响应，提升用户体验
- 支持流式文本解读功能

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。
