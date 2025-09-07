# Legacy PI Backend - 生产环境部署指南

## 🚀 uWSGI + Nginx 架构升级

本项目已从单线程的Django开发服务器升级到生产级的 **uWSGI + Nginx** 架构，大幅提升了并发处理能力和系统性能。

## 🏗️ 新架构特性

### 性能提升
- **多进程处理**: uWSGI 支持多进程并发处理请求
- **负载均衡**: Nginx 作为反向代理，提供负载均衡
- **静态文件优化**: Nginx 直接处理静态文件，减少Django负载
- **连接复用**: 支持HTTP/1.1连接复用，提高效率
- **Gzip压缩**: 自动压缩响应内容，减少带宽使用

### 高可用性
- **健康检查**: 自动监控服务状态
- **优雅重启**: 支持零停机时间重启
- **错误恢复**: 自动重启异常进程
- **日志管理**: 完整的访问和错误日志

## 📊 性能对比

| 指标 | 开发服务器 | uWSGI + Nginx |
|------|------------|---------------|
| 并发处理 | 单线程 | 多进程 (4进程 × 2线程) |
| 静态文件 | Django处理 | Nginx直接处理 |
| 内存使用 | 较低 | 优化配置 |
| 响应时间 | 较慢 | 显著提升 |
| 稳定性 | 开发级 | 生产级 |

## 🛠️ 部署步骤

### 1. 环境准备
```bash
# 设置API密钥
export ARK_API_KEY="your_volcano_ark_api_key"

# 确保Docker和Docker Compose已安装
docker --version
docker-compose --version
```

### 2. 一键启动
```bash
# 使用生产环境启动脚本
./start_production.sh
```

### 3. 手动启动
```bash
# 停止现有服务
docker-compose down

# 构建并启动所有服务
docker-compose up --build -d

# 检查服务状态
docker-compose ps
```

## 🔧 配置说明

### uWSGI 配置 (uwsgi.ini)
```ini
# 核心配置
processes = 4          # 工作进程数
threads = 2            # 每进程线程数
max-requests = 1000    # 最大请求数后重启进程
harakiri = 120         # 请求超时时间(秒)

# 性能优化
buffer-size = 32768    # 缓冲区大小
post-buffering = 8192  # POST缓冲区
offload-threads = 2    # 卸载线程数
```

### Nginx 配置 (nginx/nginx.conf)
```nginx
# 上游服务器
upstream django_backend {
    server django-app:8000;
    keepalive 32;  # 连接池大小
}

# 性能优化
worker_processes auto;           # 自动检测CPU核心数
worker_connections 1024;         # 每进程最大连接数
client_max_body_size 100M;       # 最大请求体大小
gzip_comp_level 6;              # Gzip压缩级别
```

## 📈 性能监控

### 实时监控
```bash
# 运行性能监控脚本
./monitor_performance.sh

# 查看容器资源使用
docker stats

# 查看服务日志
docker-compose logs -f
```

### 关键指标
- **响应时间**: 目标 < 500ms
- **并发连接**: 支持 1000+ 并发
- **内存使用**: 监控进程内存泄漏
- **CPU使用**: 保持 < 80%

## 🔍 故障排查

### 常见问题

#### 1. 服务启动失败
```bash
# 检查日志
docker-compose logs django-app
docker-compose logs nginx

# 检查配置
docker-compose config
```

#### 2. 性能问题
```bash
# 检查资源使用
docker stats

# 检查连接数
docker-compose exec nginx wget -qO- http://localhost/nginx_status
```

#### 3. 内存泄漏
```bash
# 重启uWSGI进程
docker-compose restart django-app

# 检查进程状态
docker-compose exec django-app ps aux
```

## 🚀 性能优化建议

### 1. 调整uWSGI参数
根据服务器配置调整 `uwsgi.ini`:
```ini
# 高配置服务器
processes = 8
threads = 4
max-requests = 2000

# 低配置服务器
processes = 2
threads = 1
max-requests = 500
```

### 2. 优化Nginx配置
```nginx
# 增加连接数
worker_connections 2048;

# 启用更多缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
```

### 3. 数据库优化
- 启用Redis缓存
- 优化MongoDB索引
- 使用连接池

## 📊 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 主应用 | http://localhost | 通过Nginx代理 |
| API文档 | http://localhost/api/ | RESTful API |
| 管理后台 | http://localhost/admin/ | Django Admin |
| MongoDB管理 | http://localhost:8081 | Mongo Express |
| 健康检查 | http://localhost/health/ | 服务状态 |

## 🔒 安全配置

### 已实现的安全特性
- **安全头**: X-Frame-Options, X-XSS-Protection等
- **请求限制**: 防止DDoS攻击
- **连接限制**: 限制单IP连接数
- **HTTPS就绪**: 支持SSL/TLS配置

### 生产环境建议
1. 配置HTTPS证书
2. 设置防火墙规则
3. 定期更新依赖包
4. 监控异常访问

## 📝 日志管理

### 日志位置
- **Nginx访问日志**: `/var/log/nginx/access.log`
- **Nginx错误日志**: `/var/log/nginx/error.log`
- **uWSGI日志**: `/var/log/uwsgi/uwsgi.log`
- **Django日志**: 容器内标准输出

### 日志轮转
```bash
# 清理旧日志
docker-compose exec nginx logrotate /etc/logrotate.d/nginx

# 查看日志大小
docker-compose exec nginx du -sh /var/log/nginx/*
```

## 🎯 下一步优化

1. **负载均衡**: 支持多实例部署
2. **缓存优化**: Redis集群配置
3. **数据库优化**: 读写分离
4. **监控告警**: Prometheus + Grafana
5. **自动扩缩容**: Kubernetes部署

---

**升级完成！** 🎉

您的Legacy PI Backend现在运行在生产级的uWSGI + Nginx架构上，具备了更好的性能、稳定性和可扩展性。
