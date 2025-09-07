# 🧪 Legacy PI Backend 测试文件集合

本目录包含了 Legacy PI Backend 项目的所有测试文件，按功能分类组织。

## 📋 测试文件分类

### 🤖 AI 服务测试

#### AI 对话服务测试
| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_ai_chat_api.py` | AI对话API完整测试 | 测试AI对话服务的所有功能 |
| `test_ai_chat.py` | AI对话基础测试 | 基础对话功能测试 |
| `test_ai_chat_simple.py` | AI对话简单测试 | 简化版对话测试 |
| `test_stream_api.py` | 流式API测试 | 测试流式响应功能 |
| `test_image_chat.py` | 图片对话测试 | 测试图片理解功能 |

#### AI 解读服务测试
| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_ai_interpreter.py` | AI解读服务测试 | 测试文本解读功能 |
| `test_interpret_api.py` | 解读API测试 | 测试解读API接口 |
| `test_all_prompts.py` | 所有提示词测试 | 测试各种解读模式 |

### 📚 内容管理测试

#### 文档管理测试
| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_md_docs_system.py` | MD文档系统测试 | 测试Markdown文档管理 |
| `test_key_points.py` | 关键点提取测试 | 测试文档关键点提取 |

#### 知识问答测试
| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_knowledge_quiz.py` | 知识问答测试 | 测试知识问答系统 |
| `test_knowledge_ai.py` | 知识AI测试 | 测试知识AI服务 |

### 🔊 语音服务测试

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_tts_api.py` | TTS API测试 | 测试文本转语音功能 |

### 🖼️ 图片处理测试

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_image_cache.py` | 图片缓存测试 | 测试图片缓存功能 |
| `test_specific_image.py` | 特定图片测试 | 测试特定图片处理 |

### 🚀 部署和性能测试

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `test_nginx_deployment.sh` | Nginx部署测试 | 测试Nginx部署状态 |
| `test_performance_optimization.sh` | 性能优化测试 | 测试性能优化效果 |
| `test_admin_access.sh` | 管理后台测试 | 测试Django管理后台 |

### 🔧 调试和快速测试

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `debug_robot_article.py` | 机器人文章调试 | 调试机器人文章功能 |
| `quick_test.py` | 快速测试 | 快速功能测试 |
| `quick_test_ai.py` | AI快速测试 | AI功能快速测试 |

## 🚀 使用方法

### 运行单个测试

```bash
# 进入测试目录
cd tests/

# 运行Python测试
python3 test_ai_chat_api.py
python3 test_knowledge_quiz.py
python3 test_tts_api.py

# 运行Shell测试
./test_nginx_deployment.sh
./test_performance_optimization.sh
./test_admin_access.sh
```

### 运行所有测试

```bash
# 运行所有Python测试
cd tests/
for test in test_*.py; do
    echo "运行测试: $test"
    python3 "$test"
    echo "---"
done

# 运行所有Shell测试
for test in test_*.sh; do
    echo "运行测试: $test"
    ./"$test"
    echo "---"
done
```

### 按类别运行测试

```bash
# AI服务测试
python3 test_ai_chat_api.py
python3 test_ai_interpreter.py
python3 test_stream_api.py

# 内容管理测试
python3 test_md_docs_system.py
python3 test_knowledge_quiz.py

# 部署测试
./test_nginx_deployment.sh
./test_performance_optimization.sh
```

## 📊 测试统计

### 文件统计
- **总测试文件数**: 21 个
- **Python测试文件**: 18 个
- **Shell测试文件**: 3 个

### 功能覆盖
- **AI服务测试**: 8 个文件
- **内容管理测试**: 4 个文件
- **语音服务测试**: 1 个文件
- **图片处理测试**: 2 个文件
- **部署性能测试**: 3 个文件
- **调试快速测试**: 3 个文件

## 🔧 测试环境要求

### 基础要求
- Python 3.12+
- Docker & Docker Compose
- 方舟 API 密钥

### 服务依赖
- Django 应用服务运行中
- Redis 缓存服务运行中
- MongoDB 数据库运行中
- Nginx 代理服务运行中

### 环境变量
```bash
export ARK_API_KEY="你的火山方舟API密钥"
```

## 📝 测试说明

### 测试原则
1. **独立性**: 每个测试文件独立运行
2. **完整性**: 覆盖主要功能点
3. **可重复性**: 测试结果可重复
4. **清晰性**: 测试输出清晰易懂

### 测试输出
- ✅ **成功**: 测试通过
- ❌ **失败**: 测试失败
- ⚠️ **警告**: 测试警告
- ℹ️ **信息**: 测试信息

### 错误处理
- 网络连接错误
- API响应错误
- 数据格式错误
- 服务状态错误

## 🛠️ 维护指南

### 添加新测试
1. 创建测试文件
2. 添加测试说明
3. 更新README
4. 验证测试功能

### 更新测试
1. 修改测试逻辑
2. 更新测试说明
3. 验证测试结果
4. 更新文档

### 删除测试
1. 确认测试不再需要
2. 删除测试文件
3. 更新README
4. 清理相关引用

## 📞 支持与联系

- **测试问题**: 查看具体测试文件注释
- **环境问题**: 检查服务状态和配置
- **API问题**: 查看API文档和日志
- **部署问题**: 查看部署文档和日志

---

**测试目录版本**: v1.0  
**最后更新**: 2025-09-07  
**维护状态**: ✅ 活跃维护

> 🧪 测试文件已整理完成！现在可以方便地运行各种测试来验证系统功能。
