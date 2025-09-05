#!/bin/bash

# 基础 Docker 镜像导出脚本
# 用于在本地导出基础镜像，Django 应用将在云端动态构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否运行
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未运行或无法访问"
        exit 1
    fi
    log_success "Docker 运行正常"
}

# 创建导出目录
create_export_dir() {
    EXPORT_DIR="docker-base-images"
    if [ -d "$EXPORT_DIR" ]; then
        log_warning "导出目录已存在，将清空现有内容"
        rm -rf "$EXPORT_DIR"
    fi
    mkdir -p "$EXPORT_DIR"
    log_success "创建导出目录: $EXPORT_DIR"
}

# 拉取基础镜像
pull_base_images() {
    log_info "拉取基础镜像..."
    
    # 拉取 Python 基础镜像
    log_info "拉取 Python 3.12-slim..."
    docker pull python:3.12-slim
    
    # 拉取 Nginx 镜像
    log_info "拉取 Nginx Alpine..."
    docker pull nginx:alpine
    
    # 拉取 Redis 镜像
    log_info "拉取 Redis 7.2-alpine..."
    docker pull redis:7.2-alpine
    
    # 拉取 MongoDB 镜像
    log_info "拉取 MongoDB 7.0..."
    docker pull mongo:7.0
    
    log_success "所有基础镜像拉取完成"
}

# 导出基础镜像
export_base_images() {
    log_info "开始导出基础镜像..."
    
    # 导出 Python 基础镜像
    log_info "导出 Python 3.12-slim..."
    docker save python:3.12-slim | gzip > docker-base-images/python-3.12-slim.tar.gz
    
    # 导出 Nginx 镜像
    log_info "导出 Nginx Alpine..."
    docker save nginx:alpine | gzip > docker-base-images/nginx-alpine.tar.gz
    
    # 导出 Redis 镜像
    log_info "导出 Redis 7.2-alpine..."
    docker save redis:7.2-alpine | gzip > docker-base-images/redis-7.2-alpine.tar.gz
    
    # 导出 MongoDB 镜像
    log_info "导出 MongoDB 7.0..."
    docker save mongo:7.0 | gzip > docker-base-images/mongo-7.0.tar.gz
    
    log_success "所有基础镜像导出完成"
}

# 生成导入脚本
generate_import_script() {
    log_info "生成导入脚本..."
    
    cat > docker-base-images/import-base-images.sh << 'EOF'
#!/bin/bash

# 基础 Docker 镜像导入脚本
# 在云端服务器上执行此脚本来导入基础镜像

set -e

echo "开始导入基础 Docker 镜像..."

# 检查镜像文件是否存在
if [ ! -d "." ]; then
    echo "错误: 当前目录不是 docker-base-images 目录"
    exit 1
fi

# 导入基础镜像
echo "导入 Python 基础镜像..."
gunzip -c python-3.12-slim.tar.gz | docker load

echo "导入 Nginx 镜像..."
gunzip -c nginx-alpine.tar.gz | docker load

echo "导入 Redis 镜像..."
gunzip -c redis-7.2-alpine.tar.gz | docker load

echo "导入 MongoDB 镜像..."
gunzip -c mongo-7.0.tar.gz | docker load

echo "所有基础镜像导入完成！"
echo "验证镜像:"
docker images | grep -E "(python|nginx|redis|mongo)"
EOF

    chmod +x docker-base-images/import-base-images.sh
    log_success "导入脚本生成完成"
}

# 生成部署说明
generate_deployment_guide() {
    log_info "生成部署说明..."
    
    cat > docker-base-images/DEPLOYMENT_README.md << 'EOF'
# 云端部署说明 (Git 动态构建模式)

## 文件说明

- `python-3.12-slim.tar.gz` - Python 基础镜像
- `nginx-alpine.tar.gz` - Nginx 反向代理镜像
- `redis-7.2-alpine.tar.gz` - Redis 缓存镜像
- `mongo-7.0.tar.gz` - MongoDB 数据库镜像
- `import-base-images.sh` - 基础镜像导入脚本

## 部署步骤

### 方法一：使用 Git 部署脚本 (推荐)

1. 将 `docker-base-images` 目录上传到云端服务器
2. 导入基础镜像: `cd docker-base-images && ./import-base-images.sh`
3. 使用 Git 部署脚本:
   ```bash
   # 下载部署脚本
   curl -O https://raw.githubusercontent.com/your-repo/legacy_pi_backend/main/deploy-from-git.sh
   chmod +x deploy-from-git.sh
   
   # 执行部署
   ./deploy-from-git.sh https://github.com/your-repo/legacy_pi_backend.git main
   ```

### 方法二：手动部署

1. 将 `docker-base-images` 目录上传到云端服务器
2. 导入基础镜像: `cd docker-base-images && ./import-base-images.sh`
3. 克隆项目代码: `git clone https://github.com/your-repo/legacy_pi_backend.git`
4. 进入项目目录: `cd legacy_pi_backend`
5. 配置环境变量: `cp env.example env.production && nano env.production`
6. 构建并启动服务: `docker-compose -f docker-compose.prod.yml up -d --build`

## 优势

- **代码最新**: 每次部署都从 Git 仓库获取最新代码
- **文件更小**: 只传输基础镜像，减少传输时间
- **灵活部署**: 支持不同分支和版本
- **易于更新**: 重新运行脚本即可更新到最新版本

## 注意事项

- 确保云端服务器有网络连接以克隆代码
- 确保 Docker 和 Docker Compose 已安装
- 确保网络端口 80 已开放
- 导入完成后可以删除 `docker-base-images` 目录以节省空间
EOF

    log_success "部署说明生成完成"
}

# 显示导出结果
show_export_results() {
    log_info "导出结果统计:"
    echo "=========================="
    
    total_size=0
    for file in docker-base-images/*.tar.gz; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            filename=$(basename "$file")
            echo "  $filename: $size"
            # 计算总大小 (以 MB 为单位)
            size_mb=$(du -m "$file" | cut -f1)
            total_size=$((total_size + size_mb))
        fi
    done
    
    echo "=========================="
    echo "总大小: ${total_size}MB (约 $((total_size/1024))GB)"
    echo "=========================="
    
    log_success "基础镜像导出完成！"
    log_info "下一步:"
    echo "1. 将 docker-base-images 目录上传到云端服务器"
    echo "2. 在云端服务器执行: cd docker-base-images && ./import-base-images.sh"
    echo "3. 使用 Git 部署脚本: ./deploy-from-git.sh [Git仓库URL] [分支名]"
    echo ""
    log_info "优势:"
    echo "- 文件更小 (只包含基础镜像)"
    echo "- 代码最新 (从 Git 动态获取)"
    echo "- 易于更新 (重新运行脚本即可)"
}

# 主函数
main() {
    log_info "开始导出基础 Docker 镜像..."
    echo "=========================="
    log_info "注意: Django 应用将在云端动态构建"
    echo "=========================="
    
    # 检查 Docker
    check_docker
    
    # 创建导出目录
    create_export_dir
    
    # 拉取基础镜像
    pull_base_images
    
    # 导出基础镜像
    export_base_images
    
    # 生成导入脚本
    generate_import_script
    
    # 生成部署说明
    generate_deployment_guide
    
    # 显示结果
    show_export_results
}

# 执行主函数
main "$@"
