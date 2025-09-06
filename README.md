# Legacy PI Backend - 薪传𝝿 数据后端

## 🎯 项目概述

Legacy PI Backend 是一个基于 Django 的智能内容处理平台，集成了多种 AI 服务和内容管理功能。项目采用微服务架构，支持容器化部署，提供完整的 API 服务套件。

## ✨ 核心功能

### 🤖 AI 智能服务
- **AI 对话服务** - 支持多轮对话的智能聊天，基于方舟大模型
- **AI 解读服务** - 提供多种模式的文本解读和分析
- **图片理解** - 支持图片上传和 AI 视觉理解
- **文本转语音** - 集成 Edge TTS 引擎，支持中文语音合成

### 📚 内容管理系统
- **MD 文档管理** - 支持 Markdown 文档的存储、分类和检索
- **知识问答系统** - 党政理论知识管理和每日一题功能
- **内容爬取** - 自动爬取人民网等新闻源内容
- **文档摘要** - 智能提取文档关键信息

### 🔧 技术特性
- **容器化部署** - 完整的 Docker Compose 配置
- **微服务架构** - 模块化设计，易于扩展
- **Redis 缓存** - 高性能数据缓存
- **MongoDB 存储** - 灵活的文档数据库
- **RESTful API** - 标准化的 API 接口

## 🏗️ 系统架构

### 服务组件

| 服务 | 描述 | 端口 |
|------|------|------|
| Django 应用 | 主应用服务 | 8000 |
| Redis 缓存 | 数据缓存服务 | 6379 |
| MongoDB | 文档数据库 | 27017 |
| Mongo Express | 数据库管理界面 | 8081 |

### 应用模块

- **ai_chat** - AI 对话和图片理解服务
- **ai_interpreter** - AI 文本解读服务
- **crawler** - 内容爬取和缓存服务
- **tts_service** - 文本转语音服务
- **knowledge_quiz** - 知识问答系统
- **md_docs** - Markdown 文档管理

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.12+ (本地开发)
- 方舟 API 密钥

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd legacy_pi_backend

# 设置环境变量
export ARK_API_KEY="你的火山方舟API密钥"

# 启动所有服务
./start_services.sh
```

### 验证部署

```bash
# 检查服务状态
docker-compose ps

# 测试 API 健康状态
curl http://localhost:8000/api/ai-chat/health/
```

## 📖 API 文档

### 主要 API 端点

| 服务 | 端点 | 描述 |
|------|------|------|
| AI 对话 | `/api/ai-chat/` | 智能对话和图片理解 |
| AI 解读 | `/api/ai/` | 文本解读和分析 |
| 内容爬取 | `/api/crawler/` | 新闻内容爬取 |
| 文档管理 | `/api/md-docs/` | Markdown 文档管理 |
| 知识问答 | `/api/knowledge-quiz/` | 知识管理和问答 |
| 语音合成 | `/api/tts/` | 文本转语音 |

### 快速测试

```bash
# AI 对话测试
curl -X POST "http://localhost:8000/api/ai-chat/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下人工智能"}'

# 文档解读测试
curl -X POST "http://localhost:8000/api/ai/interpret/" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能正在改变世界...", "prompt_type": "summary"}'
```

## 🛠️ 开发指南

### 本地开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python manage.py runserver
```

### 环境配置

创建 `.env` 文件：
```bash
# AI 服务配置
ARK_API_KEY=你的方舟API密钥

# 数据库配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis123

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password123
```

## 📊 功能特性详解

### AI 对话服务
- **多轮对话** - 支持连续对话上下文
- **图片理解** - 上传图片进行 AI 分析
- **角色扮演** - 多种 AI 角色和风格
- **流式输出** - 实时响应生成

### 内容管理
- **智能分类** - 自动内容分类和标签
- **全文搜索** - 支持关键词搜索
- **批量处理** - 批量文档处理
- **格式转换** - 多种文档格式支持

### 数据存储
- **Redis 缓存** - 高性能数据缓存
- **MongoDB** - 灵活文档存储
- **文件管理** - 媒体文件管理
- **数据备份** - 自动数据备份

## 🔧 运维管理

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f
```

### 数据管理

```bash
# 备份数据
docker-compose exec redis redis-cli -a redis123 --rdb /data/backup.rdb
docker-compose exec mongodb mongodump --out /data/backup

# 清理缓存
docker-compose exec redis redis-cli -a redis123 FLUSHALL
```

### 监控检查

```bash
# 健康检查
curl http://localhost:8000/api/ai-chat/health/
docker-compose exec redis redis-cli -a redis123 ping
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# 资源监控
docker stats
```

## 📚 详细文档

### 核心文档
- [Docker 容器化集成说明](doc/README_DOCKER_INTEGRATION.md)
- [AI 对话 API 使用说明](doc/AI对话API_使用说明.md)
- [AI 解读 API 完整文档](doc/AI解读API_完整文档.md)
- [MD 文档管理系统 API](doc/MD_DOCS_API_Documentation.md)

### 配置文档
- [快速配置指南](doc/快速配置指南.md)
- [环境变量配置说明](doc/环境变量配置说明.md)
- [知识问答 API 使用说明](doc/知识问答API_使用说明.md)
- [TTS API 使用说明](doc/TTS_API_使用说明.md)


## 🔒 安全特性

- **API 密钥管理** - 环境变量安全存储
- **容器隔离** - Docker 容器安全隔离
- **数据加密** - 敏感数据加密存储
- **访问控制** - 基于角色的访问控制
- **审计日志** - 完整的操作审计

## 🚀 性能优化

- **缓存策略** - Redis 多级缓存
- **异步处理** - 后台任务异步执行
- **负载均衡** - 支持多实例部署
- **资源限制** - 容器资源限制
- **健康检查** - 自动故障恢复

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持与联系

- 项目文档: [doc/](doc/)
- 问题反馈: [Issues](https://github.com/your-repo/issues)
- 功能建议: [Discussions](https://github.com/your-repo/discussions)

---

**版本**: v2.0  
**更新时间**: 2025-09-05  
**状态**: ✅ 生产就绪

> 🎉 感谢使用 Legacy PI Backend！如有问题，请查看详细文档或提交 Issue。
