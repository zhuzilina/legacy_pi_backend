# TTS文本转语音API使用说明

## 概述

本项目集成了微软Edge TTS引擎，提供高质量的文本转语音服务。支持中文语音，采用流式传输和分段解析技术，能够实时将文本转换为语音并返回给客户端。

## 技术特点

- **流式传输**: 支持实时音频流传输，减少延迟
- **分段解析**: 自动将长文本分段处理，提高转换效率
- **中文优化**: 专门针对中文文本优化，支持多种中文语音
- **CPU友好**: 使用微软Edge TTS引擎，无需GPU，CPU即可运行
- **高质量音频**: 输出WAV格式音频，音质清晰

## 支持的语音

### 中文语音
- `zh-CN-XiaoxiaoNeural` - 晓晓(女声，默认)
- `zh-CN-YunxiNeural` - 云希(男声)
- `zh-CN-YunyangNeural` - 云扬(男声)
- `zh-CN-XiaoyiNeural` - 晓伊(女声)
- `zh-CN-YunfengNeural` - 云枫(男声)
- `zh-CN-XiaohanNeural` - 晓涵(女声)
- `zh-CN-XiaomoNeural` - 晓墨(女声)
- `zh-CN-XiaoxuanNeural` - 晓萱(女声)
- `zh-CN-XiaoyanNeural` - 晓颜(女声)

## API接口

### 基础URL
```
http://localhost:8000/api/tts/
```

### 1. 流式TTS转换

**接口**: `POST /api/tts/stream/`

**功能**: 将文本转换为语音并实时流式返回

**请求参数**:
```json
{
    "text": "要转换的文本内容",
    "voice": "zh-CN-XiaoxiaoNeural",
    "language": "zh-CN"
}
```

**响应**: 音频流 (audio/wav)

**特点**: 
- 实时流式传输
- 适合长文本
- 减少内存占用

**使用示例**:
```python
import requests

data = {
    "text": "你好，这是一个测试文本。",
    "voice": "zh-CN-XiaoxiaoNeural",
    "language": "zh-CN"
}

response = requests.post(
    "http://localhost:8000/api/tts/stream/",
    json=data,
    stream=True
)

# 接收音频数据
for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        # 处理音频数据
        pass
```

### 2. 文件式TTS转换

**接口**: `POST /api/tts/file/`

**功能**: 将文本转换为语音并保存为文件

**请求参数**:
```json
{
    "text": "要转换的文本内容",
    "voice": "zh-CN-YunxiNeural",
    "language": "zh-CN"
}
```

**响应**:
```json
{
    "success": true,
    "request_id": 123,
    "audio_file": "/absolute/path/to/audio.wav",
    "audio_url": "/media/tts/tts_123_20250902_081637.wav",
    "file_size": 1024000,
    "voice": "zh-CN-YunxiNeural",
    "language": "zh-CN",
    "message": "TTS转换成功"
}
```

**字段说明**:
- `audio_file`: 音频文件的绝对路径（用于内部处理）
- `audio_url`: 音频文件的相对URL（用于客户端访问）

**特点**:
- 保存为文件
- 返回文件信息
- 适合批量处理

### 3. 获取可用语音列表

**接口**: `GET /api/tts/voices/`

**功能**: 获取所有可用的语音类型

**响应**:
```json
{
    "success": true,
    "voices": {
        "zh-CN-XiaoxiaoNeural": "晓晓",
        "zh-CN-YunxiNeural": "云希"
    },
    "default_voice": "zh-CN-XiaoxiaoNeural",
    "default_language": "zh-CN"
}
```

### 4. 查询TTS请求状态

**接口**: `GET /api/tts/status/{request_id}/`

**功能**: 查询指定TTS请求的处理状态

**响应**:
```json
{
    "success": true,
    "request_id": 123,
    "status": "completed",
    "text": "要转换的文本...",
    "voice": "zh-CN-XiaoxiaoNeural",
    "language": "zh-CN",
    "audio_file": "/absolute/path/to/audio.wav",
    "audio_url": "/media/tts/tts_123_20250902_081637.wav",
    "duration": 5.2,
    "created_at": "2025-09-02T10:00:00Z",
    "completed_at": "2025-09-02T10:00:05Z"
}
```

**字段说明**:
- `audio_file`: 音频文件的绝对路径（用于内部处理）
- `audio_url`: 音频文件的相对URL（用于客户端访问）

### 5. 下载音频文件

**接口**: `GET /api/tts/download/{request_id}/`

**功能**: 下载指定TTS请求生成的音频文件

**响应**: 音频文件 (audio/wav)

## 使用流程

### 流式TTS使用流程

1. **发送请求**: 向 `/api/tts/stream/` 发送POST请求
2. **接收音频流**: 实时接收音频数据块
3. **处理音频**: 将音频数据保存或播放

### 文件式TTS使用流程

1. **发送请求**: 向 `/api/tts/file/` 发送POST请求
2. **获取结果**: 接收包含文件信息的JSON响应
3. **访问音频**: 使用返回的`audio_url`直接访问音频文件
4. **下载文件**: 使用返回的request_id下载音频文件

### 音频文件访问

**直接访问**: 使用`audio_url`字段可以直接在浏览器中播放或下载音频文件
```
http://localhost:8000/media/tts/tts_123_20250902_081637.wav
```

**API下载**: 使用下载API获取音频文件
```
GET /api/tts/download/{request_id}/
```

**重定向访问**: 使用重定向API处理绝对路径访问
```
GET /api/tts/audio/{request_id}/
```

## 错误处理

### 常见错误码

- `400`: 请求参数错误
  - 文本为空
  - 文本过长（超过5000字符）
  - 文本不包含中文字符
- `404`: 资源不存在
- `500`: 服务器内部错误

### 错误响应格式

```json
{
    "error": "错误描述信息",
    "request_id": 123
}
```

## 性能优化

### 文本分段策略

- 自动按句子分割
- 每段最大长度200字符
- 段落间添加短暂停顿

### 缓存策略

- 相同文本和语音参数的结果会被缓存
- 减少重复转换的开销

## 部署说明

### 环境要求

- Python 3.9+
- Django 5.2+
- edge-tts库

### 安装依赖

```bash
pip install edge-tts
```

### 配置设置

在Django设置中添加:

```python
INSTALLED_APPS = [
    # ... 其他应用
    'tts_service',
]

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 数据库迁移

```bash
python manage.py makemigrations tts_service
python manage.py migrate
```

## 测试

### 运行测试脚本

```bash
python test_tts_api.py
```

### 测试用例

1. **基础功能测试**: 测试文本转语音的基本功能
2. **流式传输测试**: 测试实时音频流传输
3. **文件保存测试**: 测试音频文件保存和下载
4. **错误处理测试**: 测试各种错误情况的处理

## 注意事项

1. **文本长度**: 单次请求文本长度建议不超过5000字符
2. **语音选择**: 根据应用场景选择合适的语音类型
3. **网络环境**: 流式传输需要稳定的网络连接
4. **存储空间**: 文件式TTS会占用服务器存储空间

## 扩展功能

### 未来计划

- 支持更多语言
- 添加语音情感控制
- 支持SSML标记
- 集成更多TTS引擎

## 技术支持

如有问题或建议，请联系开发团队或提交Issue。

---

*最后更新: 2025年9月2日*
