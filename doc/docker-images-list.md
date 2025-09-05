# Docker 镜像清单

## 概述

本文档列出了 Legacy PI Backend 项目所需的所有 Docker 镜像，用于在无法访问 Docker 仓库的云端环境中部署。

## 镜像清单

### 1. 基础镜像

| 镜像名称 | 标签 | 大小 (约) | 用途 | 下载命令 |
|---------|------|-----------|------|----------|
| `python` | `3.12-slim` | 45MB | Django 应用基础镜像 | `docker pull python:3.12-slim` |
| `nginx` | `alpine` | 23MB | 反向代理服务器 | `docker pull nginx:alpine` |
| `redis` | `7.2-alpine` | 7MB | 缓存数据库 | `docker pull redis:7.2-alpine` |
| `mongo` | `7.0` | 700MB | 文档数据库 | `docker pull mongo:7.0` |

### 2. 应用镜像

| 镜像名称 | 标签 | 大小 (约) | 用途 | 说明 |
|---------|------|-----------|------|------|
| `legacy_pi_backend_django-app` | `latest` | 1.2GB | Django 应用 | 需要本地构建 |

## 镜像导出和导入脚本

### 导出脚本 (在本地执行)

```bash
#!/bin/bash
# 文件名: export-images.sh

echo "开始导出 Docker 镜像..."

# 创建导出目录
mkdir -p docker-images

# 导出基础镜像
echo "导出 Python 基础镜像..."
docker save python:3.12-slim -o docker-images/python-3.12-slim.tar

echo "导出 Nginx 镜像..."
docker save nginx:alpine -o docker-images/nginx-alpine.tar

echo "导出 Redis 镜像..."
docker save redis:7.2-alpine -o docker-images/redis-7.2-alpine.tar

echo "导出 MongoDB 镜像..."
docker save mongo:7.0 -o docker-images/mongo-7.0.tar

# 构建并导出 Django 应用镜像
echo "构建 Django 应用镜像..."
docker build -f Dockerfile.prod -t legacy_pi_backend_django-app:latest .

echo "导出 Django 应用镜像..."
docker save legacy_pi_backend_django-app:latest -o docker-images/legacy_pi_backend_django-app-latest.tar

echo "所有镜像导出完成！"
echo "导出文件位于: docker-images/ 目录"
echo "总大小约: 2GB"
```

### 导入脚本 (在云端服务器执行)

```bash
#!/bin/bash
# 文件名: import-images.sh

echo "开始导入 Docker 镜像..."

# 检查镜像文件是否存在
if [ ! -d "docker-images" ]; then
    echo "错误: docker-images 目录不存在"
    exit 1
fi

# 导入基础镜像
echo "导入 Python 基础镜像..."
docker load -i docker-images/python-3.12-slim.tar

echo "导入 Nginx 镜像..."
docker load -i docker-images/nginx-alpine.tar

echo "导入 Redis 镜像..."
docker load -i docker-images/redis-7.2-alpine.tar

echo "导入 MongoDB 镜像..."
docker load -i docker-images/mongo-7.0.tar

echo "导入 Django 应用镜像..."
docker load -i docker-images/legacy_pi_backend_django-app-latest.tar

echo "所有镜像导入完成！"
echo "验证镜像:"
docker images | grep -E "(python|nginx|redis|mongo|legacy_pi_backend)"
```

## 文件传输清单

### 需要传输的文件

```
legacy_pi_backend/
├── docker-images/                    # 导出的镜像文件
│   ├── python-3.12-slim.tar         # ~45MB
│   ├── nginx-alpine.tar             # ~23MB
│   ├── redis-7.2-alpine.tar         # ~7MB
│   ├── mongo-7.0.tar                # ~700MB
│   └── legacy_pi_backend_django-app-latest.tar  # ~1.2GB
├── docker-compose.prod.yml          # Docker Compose 配置
├── Dockerfile.prod                  # Django 应用 Dockerfile
├── env.production                   # 生产环境配置
├── nginx/                           # Nginx 配置
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── mongo-init/                      # MongoDB 初始化脚本
│   └── init.js
├── deploy_http.sh                   # 部署脚本
├── import-images.sh                 # 镜像导入脚本
└── requirements.txt                 # Python 依赖
```

### 传输命令

```bash
# 在本地执行 - 压缩整个项目
tar -czf legacy_pi_backend.tar.gz legacy_pi_backend/

# 传输到云端服务器
scp legacy_pi_backend.tar.gz user@your-server-ip:/home/user/

# 在云端服务器执行 - 解压
tar -xzf legacy_pi_backend.tar.gz
cd legacy_pi_backend
```

## 部署步骤

### 1. 本地准备

```bash
# 1. 导出镜像
chmod +x export-images.sh
./export-images.sh

# 2. 压缩项目
tar -czf legacy_pi_backend.tar.gz legacy_pi_backend/
```

### 2. 云端部署

```bash
# 1. 解压项目
tar -xzf legacy_pi_backend.tar.gz
cd legacy_pi_backend

# 2. 导入镜像
chmod +x import-images.sh
./import-images.sh

# 3. 配置环境变量
cp env.example env.production
nano env.production  # 编辑配置

# 4. 部署服务
chmod +x deploy_http.sh
./deploy_http.sh deploy
```

## 镜像大小优化建议

### 1. 使用多阶段构建

```dockerfile
# 在 Dockerfile.prod 中使用多阶段构建
FROM python:3.12-slim as builder
# ... 构建阶段

FROM python:3.12-slim as runtime
# ... 运行阶段
```

### 2. 清理缓存

```bash
# 在构建后清理
docker system prune -f
docker image prune -f
```

### 3. 压缩镜像

```bash
# 使用 gzip 压缩导出的镜像
gzip docker-images/*.tar
```

## 验证清单

### 部署前检查

- [ ] 所有镜像文件已传输
- [ ] 环境变量已配置
- [ ] 网络端口已开放
- [ ] 磁盘空间充足 (>5GB)

### 部署后验证

- [ ] 所有容器正常运行
- [ ] API 健康检查通过
- [ ] 数据库连接正常
- [ ] 静态文件服务正常

## 故障排除

### 常见问题

1. **镜像导入失败**
   ```bash
   # 检查文件完整性
   ls -la docker-images/
   # 重新导入
   docker load -i docker-images/image-name.tar
   ```

2. **容器启动失败**
   ```bash
   # 查看日志
   docker-compose -f docker-compose.prod.yml logs
   # 检查配置
   docker-compose -f docker-compose.prod.yml config
   ```

3. **网络连接问题**
   ```bash
   # 检查网络
   docker network ls
   # 检查端口
   netstat -tlnp | grep :80
   ```

## 总结

- **总镜像大小**: 约 2GB
- **传输时间**: 取决于网络速度
- **部署时间**: 约 10-15 分钟
- **存储需求**: 至少 5GB 可用空间

通过这个清单，您可以在无法访问 Docker 仓库的环境中成功部署 Legacy PI Backend 项目。
