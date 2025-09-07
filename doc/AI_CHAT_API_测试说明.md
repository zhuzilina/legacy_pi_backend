# AI Chat API 测试程序使用说明

## 📋 概述

我为您创建了两个测试程序来测试 `ai_chat` 应用的所有API接口：

1. **`test_ai_chat_api.py`** - 完整的API测试套件
2. **`test_ai_chat_simple.py`** - 简单快速测试示例

## 🚀 快速开始

### 1. 确保服务运行

首先确保Django服务器正在运行：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务器
python manage.py runserver 0.0.0.0:8000
```

### 2. 简单测试（推荐新手）

```bash
# 只测试基础功能（不需要图片）
python test_ai_chat_simple.py

# 测试图片对话功能
python test_ai_chat_simple.py /path/to/your/image.jpg
```

### 3. 完整测试

```bash
# 只运行基础测试
python test_ai_chat_api.py --basic-only

# 运行完整测试（包含图片测试）
python test_ai_chat_api.py --images image1.jpg image2.png

# 指定服务器地址
python test_ai_chat_api.py --url http://your-server:8000 --images *.jpg
```

## 📊 测试内容

### 基础API测试
- ✅ 健康检查 (`/health/`)
- ✅ 获取配置 (`/config/`)
- ✅ 获取系统提示词 (`/prompts/`)
- ✅ 获取图片提示词 (`/image-prompts/`)
- ✅ 简单对话 (`/chat/`)
- ✅ 多轮对话 (`/chat/`)
- ✅ 流式对话 (`/stream/`)
- ✅ 图片缓存统计 (`/image-cache-stats/`)

### 图片相关测试
- ✅ 单张图片上传 (`/upload-image/`)
- ✅ 批量图片上传 (`/upload-images-batch/`)
- ✅ 图片对话 (`/chat-with-images/`)
- ✅ 流式图片对话 (`/stream-with-images/`)

## 🖼️ 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WEBP (.webp)

## 📝 使用示例

### 示例1：基础对话测试

```bash
python test_ai_chat_simple.py
```

输出：
```
🧪 AI Chat API 简单测试
==================================================
🏥 测试服务健康状态...
✅ 服务正常运行!
状态: healthy

🤖 测试简单对话...
✅ 对话成功!
AI回复: 你好！我是一个专业的AI知识助手，具备广泛的知识储备和专业的分析能力...
使用Token: 156

🎉 测试完成!
```

### 示例2：图片对话测试

```bash
python test_ai_chat_simple.py test_image.jpg
```

输出：
```
🧪 AI Chat API 简单测试
==================================================
🏥 测试服务健康状态...
✅ 服务正常运行!

🤖 测试简单对话...
✅ 对话成功!

🖼️  测试图片对话: test_image.jpg
📤 上传图片...
✅ 图片上传成功! ID: img_1234567890
💬 开始图片对话...
✅ 图片对话成功!
AI回复: 这张图片显示了一个美丽的风景，包含蓝天白云、绿色的草地和远山...
使用Token: 234

🎉 测试完成!
```

### 示例3：完整测试套件

```bash
python test_ai_chat_api.py --images test1.jpg test2.png
```

输出：
```
🧪 AI Chat API 完整测试
============================================================
测试目标: http://localhost:8000/api/ai-chat
开始时间: 2025-09-07 10:30:00

🚀 开始运行基础API测试...
============================================================
✅ 通过 健康检查: 服务正常运行
✅ 通过 获取配置: 配置获取成功
✅ 通过 获取系统提示词: 提示词获取成功
✅ 通过 获取图片提示词: 图片提示词获取成功
✅ 通过 简单对话: 对话成功
✅ 通过 多轮对话: 多轮对话成功
✅ 通过 流式对话: 流式对话成功，共15个数据块
✅ 通过 图片缓存统计: 统计信息获取成功

🖼️  开始运行图片API测试...
============================================================
✅ 通过 上传图片(test1.jpg): 图片上传成功，ID: img_1234567890
✅ 通过 上传图片(test2.png): 图片上传成功，ID: img_1234567891
✅ 通过 图片对话: 图片对话成功

============================================================
📊 测试总结
============================================================
总测试数: 11
通过: 11 ✅
失败: 0 ❌
成功率: 100.0%

测试完成时间: 2025-09-07 10:30:45
```

## 🔧 高级用法

### 自定义服务器地址

```bash
python test_ai_chat_api.py --url http://192.168.1.100:8000
```

### 批量测试多张图片

```bash
python test_ai_chat_api.py --images *.jpg *.png
```

### 只运行基础测试

```bash
python test_ai_chat_api.py --basic-only
```

## 🐛 故障排除

### 1. 连接失败

```
❌ 连接失败: Connection refused
```

**解决方案：**
- 确保Django服务器正在运行
- 检查端口是否正确（默认8000）
- 检查防火墙设置

### 2. 图片上传失败

```
❌ 图片上传失败: 文件格式不支持
```

**解决方案：**
- 确保图片格式为 JPEG、PNG、GIF 或 WEBP
- 检查图片文件大小（最大5MB）
- 确保图片文件没有损坏

### 3. API返回错误

```
❌ 对话失败: API key not configured
```

**解决方案：**
- 检查环境变量 `ARK_API_KEY` 是否设置
- 确保API key有效且有足够额度

## 📚 API接口说明

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health/` | GET | 健康检查 |
| `/config/` | GET | 获取配置 |
| `/chat/` | POST | 文本对话 |
| `/chat-with-images/` | POST | 图片对话 |
| `/upload-image/` | POST | 上传图片 |
| `/stream/` | POST | 流式对话 |
| `/prompts/` | GET | 获取提示词类型 |

### 请求格式示例

**文本对话：**
```json
{
    "message": "你好",
    "system_prompt_type": "default",
    "max_tokens": 500,
    "temperature": 0.7
}
```

**图片对话：**
```json
{
    "message": "描述这张图片",
    "image_ids": ["img_1234567890"],
    "image_prompt_type": "detailed"
}
```

## 🎯 测试建议

1. **首次使用**：先运行 `test_ai_chat_simple.py` 确保基础功能正常
2. **开发测试**：使用 `test_ai_chat_api.py --basic-only` 进行快速验证
3. **完整测试**：定期运行完整测试套件确保所有功能正常
4. **图片测试**：准备不同格式和大小的图片进行测试

## 📞 技术支持

如果遇到问题，请检查：
1. Django服务器是否正常运行
2. 网络连接是否正常
3. API key是否正确配置
4. 图片文件是否符合要求

测试程序会提供详细的错误信息帮助您定位问题。
