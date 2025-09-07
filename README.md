# Legacy PI Backend - 薪传𝝿 数据后端

## 🎯 项目概述

Legacy PI Backend 是一个基于 Django 的智能内容处理平台，集成了多种 AI 服务和内容管理功能。项目采用微服务架构，支持容器化部署，提供完整的 API 服务套件。

**🚀 最新架构**: 采用 uWSGI + Nginx 高性能架构，支持多进程并发处理，具备完整的性能优化和缓存机制。

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
- **高性能架构** - uWSGI + Nginx 多进程并发处理
- **容器化部署** - 完整的 Docker Compose 配置
- **微服务架构** - 模块化设计，易于扩展
- **Redis 缓存** - 高性能数据缓存
- **MongoDB 存储** - 灵活的文档数据库
- **RESTful API** - 标准化的 API 接口
- **Gzip 压缩** - 动态内容压缩优化
- **静态文件优化** - Nginx 高效静态文件服务
- **中文化界面** - Django管理后台完全中文化

## 🏗️ 系统架构

### 服务组件

| 服务 | 描述 | 端口 | 状态 |
|------|------|------|------|
| **Nginx** | 反向代理和静态文件服务 | 80, 443 | ✅ 生产就绪 |
| **Django + uWSGI** | 主应用服务 | 8000 (内部) | ✅ 多进程并发 |
| **Redis 缓存** | 数据缓存服务 | 6379 | ✅ 高性能缓存 |
| **MongoDB** | 文档数据库 | 27017 | ✅ 文档存储 |
| **Mongo Express** | 数据库管理界面 | 8081 | ✅ 管理界面 |

### 应用模块

- **ai_chat** - AI 对话和图片理解服务
- **ai_interpreter** - AI 文本解读服务
- **crawler** - 内容爬取和缓存服务
- **tts_service** - 文本转语音服务
- **knowledge_quiz** - 知识问答系统
- **md_docs** - Markdown 文档管理
- **knowledge_ai** - 知识AI服务

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

# 测试 API 健康状态 (通过Nginx代理)
curl http://localhost/api/ai-chat/health/

# 测试管理后台
curl http://localhost/admin/

# 运行所有测试
cd tests/
./run_all_tests.sh --all

# 测试管理后台中文化
python3 test_admin_chinese.py
```

## 📖 API 文档

### 主要 API 端点

| 服务 | 端点 | 描述 | 状态 |
|------|------|------|------|
| **AI 对话** | `/api/ai-chat/` | 智能对话和图片理解 | ✅ 生产就绪 |
| **AI 解读** | `/api/ai/` | 文本解读和分析 | ✅ 生产就绪 |
| **内容爬取** | `/api/crawler/` | 新闻内容爬取 | ✅ 生产就绪 |
| **文档管理** | `/api/md-docs/` | Markdown 文档管理 | ✅ 生产就绪 |
| **知识问答** | `/api/knowledge-quiz/` | 知识管理和问答 | ✅ 生产就绪 |
| **语音合成** | `/api/tts/` | 文本转语音 | ✅ 生产就绪 |
| **知识AI** | `/api/knowledge-ai/` | 知识AI服务 | ✅ 生产就绪 |

### 快速测试

```bash
# AI 对话测试 (通过Nginx代理)
curl -X POST "http://localhost/api/ai-chat/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下人工智能"}'

# 文档解读测试
curl -X POST "http://localhost/api/ai/interpret/" \
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
curl http://localhost/api/ai-chat/health/
docker-compose exec redis redis-cli -a redis123 ping
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# 资源监控
docker stats
```

## 📚 详细文档

### 🚀 部署和运维文档
- [生产环境部署指南](doc/README_PRODUCTION.md) - 完整的生产环境部署说明
- [Docker 容器化集成说明](doc/README_DOCKER_INTEGRATION.md) - 容器化部署详解
- [性能优化总结](doc/OPTIMIZATION_SUMMARY.md) - 数据库迁移和Gzip压缩优化
- [最终状态报告](doc/FINAL_STATUS_REPORT.md) - 部署成功状态报告

### 🔧 配置和测试文档
- [快速配置指南](doc/快速配置指南.md) - 快速配置说明
- [环境变量配置说明](doc/环境变量配置说明.md) - 环境变量详解
- [快速测试指南](doc/快速测试指南.md) - 快速测试说明
- [AI对话API测试说明](doc/AI_CHAT_API_测试说明.md) - AI对话API测试

### 📖 API 使用文档
- [API访问指南](doc/API_ACCESS_GUIDE.md) - 所有API端点访问指南
- [AI对话API使用说明](doc/AI对话API_使用说明.md) - AI对话服务详解
- [AI解读API完整文档](doc/AI解读API_完整文档.md) - AI解读服务详解
- [MD文档管理系统API](doc/MD_DOCS_API_Documentation.md) - 文档管理API
- [知识问答API使用说明](doc/知识问答API_使用说明.md) - 知识问答服务
- [TTS API使用说明](doc/TTS_API_使用说明.md) - 语音合成服务
- [知识AI服务API使用说明](doc/知识AI服务API_使用说明.md) - 知识AI服务

### 🛠️ 工具和开发文档
- [MD文档上传工具指南](doc/MD_UPLOAD_TOOL_GUIDE.md) - MD文档上传工具使用
- [管理后台访问指南](doc/ADMIN_ACCESS_GUIDE.md) - Django管理后台使用
- [题目表重构完成报告](doc/题目表重构完成报告.md) - 数据库重构报告
- [题目ID设计改进建议](doc/题目ID设计改进建议.md) - 题目ID设计优化
- [知识AI服务说明](doc/README_KNOWLEDGE_AI.md) - 知识AI服务详解

## 🧪 测试文档
- [测试文件集合](tests/README.md) - 所有测试文件说明和使用指南
- [测试运行脚本](tests/run_all_tests.sh) - 一键运行所有测试
- [测试配置文件](tests/test_config.py) - 测试参数和配置管理
- [测试工具类](tests/test_utils.py) - 通用测试功能工具

## 🌏 国际化配置
- [Django管理后台中文化配置](doc/DJANGO_ADMIN_CHINESE_CONFIGURATION.md) - 完整的中文化配置指南

## 🔒 安全特性

- **API 密钥管理** - 环境变量安全存储
- **容器隔离** - Docker 容器安全隔离
- **数据加密** - 敏感数据加密存储
- **访问控制** - 基于角色的访问控制
- **审计日志** - 完整的操作审计
- **安全头部** - Nginx 安全头部配置

## 🚀 性能优化

- **uWSGI 多进程** - 4进程2线程并发处理
- **Nginx 反向代理** - 高性能请求代理
- **Redis 多级缓存** - 高性能数据缓存
- **Gzip 压缩** - 动态内容压缩优化
- **静态文件优化** - Nginx 高效静态文件服务
- **连接池** - 数据库连接池优化
- **健康检查** - 自动故障恢复

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 Apache License 2.0 许可证。

### 许可证摘要

**Apache License 2.0** 是一个宽松的开源许可证，允许您：

- ✅ **自由使用** - 商业和非商业用途
- ✅ **修改代码** - 创建衍生作品
- ✅ **分发软件** - 以源代码或二进制形式分发
- ✅ **专利保护** - 包含专利授权条款
- ✅ **私有使用** - 无需公开修改后的代码

### 主要要求

- 📋 **保留版权声明** - 必须保留原始版权和许可证声明
- 📋 **包含许可证** - 分发时必须包含 Apache License 2.0 全文
- 📋 **声明修改** - 修改的文件必须声明已更改
- 📋 **NOTICE 文件** - 如果存在 NOTICE 文件，必须包含在分发中

### 完整许可证

查看完整的许可证条款：[LICENSE](LICENSE) 文件

**版权信息**: Copyright 2025 榆见晴天

**许可证链接**: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

## 📞 支持与联系

- 项目文档: [doc/](doc/)
- 问题反馈: [Issues](https://github.com/your-repo/issues)
- 功能建议: [Discussions](https://github.com/your-repo/discussions)

---

**版本**: v3.0  
**更新时间**: 2025-09-07  
**状态**: ✅ 生产就绪 (uWSGI + Nginx 架构)

> 🎉 感谢使用 Legacy PI Backend！如有问题，请查看详细文档或提交 Issue。