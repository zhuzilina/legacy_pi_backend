# Django 容器化集成说明

## 概述

本项目已成功将所有 Python Django 应用容器化，并集成到 Docker Compose 中，实现了完整的微服务架构。

## 服务架构

### 容器服务列表

1. **Django 应用容器** (`legacy_pi_django`)
   - 基于 Python 3.12-slim
   - 使用 Gunicorn WSGI 服务器
   - 包含所有 Django 应用模块

2. **Redis 缓存容器** (`legacy_pi_redis`)
   - Redis 7.2-alpine
   - 密码认证保护
   - 数据持久化

3. **MongoDB 数据库容器** (`md_docs_mongodb`)
   - MongoDB 7.0
   - 用户认证
   - 数据持久化

4. **MongoDB 管理界面** (`md_docs_mongo_express`)
   - Web 管理界面
   - 数据库可视化

## 技术特性

### Django 应用容器

**基础镜像**: `python:3.12-slim`

**主要特性**:
- 多阶段构建优化
- 系统依赖自动安装
- Python 依赖管理
- 静态文件收集
- 健康检查机制
- 生产级 WSGI 配置

**WSGI 配置**:
```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 3 \
         --timeout 120 \
         --keep-alive 2 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         legacy_pi_backend.wsgi:application
```

### 环境变量配置

**Django 配置**:
- `DEBUG`: 调试模式开关
- `REDIS_HOST`: Redis 主机地址
- `REDIS_PORT`: Redis 端口
- `REDIS_PASSWORD`: Redis 密码
- `MONGODB_HOST`: MongoDB 主机地址
- `MONGODB_PORT`: MongoDB 端口
- `MONGODB_USERNAME`: MongoDB 用户名
- `MONGODB_PASSWORD`: MongoDB 密码
- `ARK_API_KEY`: 方舟 API 密钥

### 网络配置

**统一网络**: `legacy_pi_network`
- 容器间可通过服务名通信
- 支持外部访问
- 网络隔离保护

### 数据持久化

**卷挂载**:
- `./media:/app/media` - 媒体文件
- `./static:/app/static` - 静态文件
- `redis_data:/data` - Redis 数据
- `mongodb_data:/data/db` - MongoDB 数据

## 使用方法

### 快速启动

```bash
# 启动所有服务
./start_services.sh

# 或使用 Docker Compose
docker-compose up -d
```

### 服务管理

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f django-app

# 重启服务
docker-compose restart django-app

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 容器操作

```bash
# 进入 Django 容器
docker-compose exec django-app bash

# 进入 Redis 容器
docker-compose exec redis redis-cli -a redis123

# 进入 MongoDB 容器
docker-compose exec mongodb mongosh

# 查看容器资源使用
docker stats
```

## 应用模块

### 已集成的 Django 应用

1. **ai_chat** - AI 对话服务
   - 文本对话 API
   - 图片理解 API
   - 系统提示词管理
   - 图片上传和缓存

2. **ai_interpreter** - AI 解读服务
   - 文档解读 API
   - 内容分析功能

3. **crawler** - 爬虫服务
   - 文章爬取功能
   - Redis 缓存管理
   - 数据统计功能

4. **tts_service** - 文本转语音服务
   - Edge TTS 集成
   - 语音文件生成

5. **knowledge_quiz** - 知识问答服务
   - 题目管理
   - 问答功能

6. **md_docs** - Markdown 文档服务
   - 文档管理
   - MongoDB 集成

## API 端点

### 主要 API 服务

**Django 应用**: `http://localhost:8000`

**核心 API 端点**:
- `/api/ai-chat/` - AI 对话服务
- `/api/ai-interpreter/` - AI 解读服务
- `/api/crawler/` - 爬虫服务
- `/api/tts/` - 文本转语音服务
- `/api/knowledge-quiz/` - 知识问答服务
- `/api/md-docs/` - Markdown 文档服务

**管理界面**:
- `/admin/` - Django 管理界面
- `http://localhost:8081` - MongoDB 管理界面

## 健康检查

### 自动健康检查

**Django 应用**:
```bash
curl -f http://localhost:8000/api/ai-chat/health/
```

**Redis 服务**:
```bash
docker-compose exec redis redis-cli -a redis123 ping
```

**MongoDB 服务**:
```bash
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"
```

### 健康检查配置

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/ai-chat/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 开发环境

### 本地开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python manage.py runserver
```

### 容器开发

```bash
# 进入开发容器
docker-compose exec django-app bash

# 运行 Django 命令
docker-compose exec django-app python manage.py migrate
docker-compose exec django-app python manage.py collectstatic
```

## 生产部署

### 环境配置

1. **设置环境变量**:
   ```bash
   export ARK_API_KEY=your_actual_api_key
   export DEBUG=False
   ```

2. **配置反向代理** (推荐使用 Nginx):
   ```nginx
   upstream django_app {
       server localhost:8000;
   }
   
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://django_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 安全配置

1. **修改默认密码**:
   - Redis 密码: `redis123`
   - MongoDB 密码: `password123`
   - Mongo Express 密码: `admin123`

2. **网络安全**:
   - 使用防火墙限制端口访问
   - 配置 SSL/TLS 证书
   - 定期更新容器镜像

## 监控和日志

### 日志管理

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f django-app

# 查看错误日志
docker-compose logs --tail=100 django-app | grep ERROR
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看容器详细信息
docker inspect legacy_pi_django

# 查看网络连接
docker network ls
docker network inspect legacy_pi_backend_legacy_pi_network
```

## 故障排除

### 常见问题

1. **容器启动失败**:
   ```bash
   # 检查容器日志
   docker-compose logs django-app
   
   # 检查镜像构建
   docker-compose build --no-cache django-app
   ```

2. **服务连接失败**:
   ```bash
   # 检查网络连接
   docker-compose exec django-app ping redis
   docker-compose exec django-app ping mongodb
   
   # 检查端口占用
   netstat -tlnp | grep 8000
   ```

3. **数据持久化问题**:
   ```bash
   # 检查卷挂载
   docker volume ls
   docker volume inspect legacy_pi_backend_redis_data
   ```

### 调试命令

```bash
# 进入容器调试
docker-compose exec django-app bash

# 检查 Django 配置
docker-compose exec django-app python manage.py check

# 检查数据库连接
docker-compose exec django-app python manage.py dbshell

# 检查 Redis 连接
docker-compose exec django-app python -c "import redis; r=redis.Redis(host='redis', port=6379, password='redis123'); print(r.ping())"
```

## 扩展配置

### 水平扩展

```yaml
# 扩展 Django 应用实例
docker-compose up -d --scale django-app=3
```

### 负载均衡

```yaml
# 添加 Nginx 负载均衡器
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - django-app
```

### 集群部署

```yaml
# Redis 集群配置
redis-master:
  image: redis:7.2-alpine
  command: redis-server --appendonly yes

redis-slave:
  image: redis:7.2-alpine
  command: redis-server --slaveof redis-master 6379
```

## 更新和维护

### 应用更新

```bash
# 更新代码
git pull origin main

# 重新构建容器
docker-compose build django-app

# 重启服务
docker-compose up -d django-app
```

### 数据备份

```bash
# 备份 Redis 数据
docker-compose exec redis redis-cli -a redis123 --rdb /data/backup.rdb

# 备份 MongoDB 数据
docker-compose exec mongodb mongodump --out /data/backup

# 备份媒体文件
tar -czf media_backup.tar.gz media/
```

## 性能优化

### 容器优化

1. **多阶段构建**: 减少镜像大小
2. **依赖缓存**: 优化构建时间
3. **资源限制**: 防止资源滥用
4. **健康检查**: 自动故障恢复

### 应用优化

1. **静态文件**: 使用 CDN 加速
2. **数据库**: 连接池优化
3. **缓存策略**: Redis 缓存优化
4. **负载均衡**: 多实例部署

## 联系支持

如有问题，请查看：
1. Docker Compose 日志
2. 容器健康状态
3. 网络连接状态
4. 资源使用情况

**常用命令总结**:
- 启动: `docker-compose up -d`
- 停止: `docker-compose down`
- 重启: `docker-compose restart`
- 日志: `docker-compose logs -f`
- 状态: `docker-compose ps`
