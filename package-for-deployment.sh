#!/bin/bash

# 项目打包脚本
# 用于打包整个项目，包括 Docker 镜像，以便在云端部署

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

# 检查环境
check_environment() {
    log_info "检查环境..."
    
    # 检查 Docker
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未运行或无法访问"
        exit 1
    fi
    
    # 检查必要文件
    required_files=(
        "docker-compose.prod.yml"
        "Dockerfile.prod"
        "env.example"
        "deploy_http.sh"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "必要文件不存在: $file"
            exit 1
        fi
    done
    
    log_success "环境检查通过"
}

# 清理旧文件
cleanup_old_files() {
    log_info "清理旧文件..."
    
    # 清理旧的导出目录
    if [ -d "docker-images" ]; then
        log_warning "删除旧的 docker-images 目录"
        rm -rf docker-images
    fi
    
    # 清理旧的打包文件
    if [ -f "legacy_pi_backend_deployment.tar.gz" ]; then
        log_warning "删除旧的打包文件"
        rm -f legacy_pi_backend_deployment.tar.gz
    fi
    
    log_success "清理完成"
}

# 导出 Docker 镜像
export_docker_images() {
    log_info "导出 Docker 镜像..."
    
    # 执行镜像导出脚本
    if [ -f "export-images.sh" ]; then
        ./export-images.sh
    else
        log_error "export-images.sh 不存在"
        exit 1
    fi
    
    log_success "Docker 镜像导出完成"
}

# 创建部署包
create_deployment_package() {
    log_info "创建部署包..."
    
    # 创建临时目录
    TEMP_DIR="legacy_pi_backend_deployment"
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
    mkdir -p "$TEMP_DIR"
    
    # 复制必要文件
    log_info "复制项目文件..."
    
    # 核心配置文件
    cp docker-compose.prod.yml "$TEMP_DIR/"
    cp Dockerfile.prod "$TEMP_DIR/"
    cp env.example "$TEMP_DIR/"
    cp requirements.txt "$TEMP_DIR/"
    
    # 部署脚本
    cp deploy_http.sh "$TEMP_DIR/"
    cp quick_deploy.sh "$TEMP_DIR/" 2>/dev/null || true
    
    # Nginx 配置
    if [ -d "nginx" ]; then
        cp -r nginx "$TEMP_DIR/"
    fi
    
    # MongoDB 初始化脚本
    if [ -d "mongo-init" ]; then
        cp -r mongo-init "$TEMP_DIR/"
    fi
    
    # 文档文件
    if [ -f "README.md" ]; then
        cp README.md "$TEMP_DIR/"
    fi
    
    if [ -f "DEPLOYMENT_GUIDE.md" ]; then
        cp DEPLOYMENT_GUIDE.md "$TEMP_DIR/"
    fi
    
    if [ -f "docker-images-list.md" ]; then
        cp docker-images-list.md "$TEMP_DIR/"
    fi
    
    # 复制 Docker 镜像
    if [ -d "docker-images" ]; then
        cp -r docker-images "$TEMP_DIR/"
    fi
    
    # 创建部署说明
    cat > "$TEMP_DIR/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# Legacy PI Backend 云端部署说明

## 快速部署

1. **解压项目**
   ```bash
   tar -xzf legacy_pi_backend_deployment.tar.gz
   cd legacy_pi_backend_deployment
   ```

2. **导入 Docker 镜像**
   ```bash
   cd docker-images
   ./import-images.sh
   cd ..
   ```

3. **配置环境变量**
   ```bash
   cp env.example env.production
   nano env.production  # 编辑配置
   ```

4. **执行部署**
   ```bash
   chmod +x deploy_http.sh
   ./deploy_http.sh deploy
   ```

## 详细说明

- 查看 `DEPLOYMENT_GUIDE.md` 获取详细部署指南
- 查看 `docker-images-list.md` 获取镜像清单
- 查看 `README.md` 获取项目说明

## 访问地址

部署完成后，通过以下地址访问：
- 主应用: http://your-server-ip
- API 文档: http://your-server-ip/api/
- 健康检查: http://your-server-ip/api/ai-chat/health/

## 管理命令

```bash
./deploy_http.sh stop      # 停止服务
./deploy_http.sh restart   # 重启服务
./deploy_http.sh logs      # 查看日志
./deploy_http.sh health    # 健康检查
./deploy_http.sh backup    # 备份数据
```
EOF

    # 创建快速部署脚本
    cat > "$TEMP_DIR/quick-deploy.sh" << 'EOF'
#!/bin/bash

# 快速部署脚本
set -e

echo "🚀 开始快速部署 Legacy PI Backend..."

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 导入镜像
echo "📦 导入 Docker 镜像..."
cd docker-images
./import-images.sh
cd ..

# 配置环境
echo "⚙️ 配置环境变量..."
if [ ! -f "env.production" ]; then
    cp env.example env.production
    echo "⚠️ 请编辑 env.production 文件配置您的环境变量"
    echo "特别是 ARK_API_KEY 和数据库密码"
    read -p "按 Enter 继续..."
fi

# 部署服务
echo "🚀 部署服务..."
chmod +x deploy_http.sh
./deploy_http.sh deploy

echo "✅ 部署完成！"
echo "访问地址: http://your-server-ip"
EOF

    chmod +x "$TEMP_DIR/quick-deploy.sh"
    
    log_success "部署包创建完成"
}

# 压缩部署包
compress_package() {
    log_info "压缩部署包..."
    
    # 计算压缩前大小
    size_before=$(du -sh legacy_pi_backend_deployment | cut -f1)
    
    # 压缩
    tar -czf legacy_pi_backend_deployment.tar.gz legacy_pi_backend_deployment/
    
    # 计算压缩后大小
    size_after=$(du -sh legacy_pi_backend_deployment.tar.gz | cut -f1)
    
    log_success "压缩完成"
    echo "压缩前大小: $size_before"
    echo "压缩后大小: $size_after"
}

# 生成传输说明
generate_transfer_instructions() {
    log_info "生成传输说明..."
    
    cat > TRANSFER_INSTRUCTIONS.md << 'EOF'
# 文件传输说明

## 传输文件

需要传输的文件: `legacy_pi_backend_deployment.tar.gz`

## 传输命令

### 使用 SCP 传输
```bash
# 传输到服务器
scp legacy_pi_backend_deployment.tar.gz user@your-server-ip:/home/user/

# 在服务器上解压
ssh user@your-server-ip
tar -xzf legacy_pi_backend_deployment.tar.gz
cd legacy_pi_backend_deployment
```

### 使用 SFTP 传输
```bash
# 连接服务器
sftp user@your-server-ip

# 上传文件
put legacy_pi_backend_deployment.tar.gz

# 退出 SFTP
quit

# 在服务器上解压
ssh user@your-server-ip
tar -xzf legacy_pi_backend_deployment.tar.gz
cd legacy_pi_backend_deployment
```

## 部署步骤

1. 解压项目: `tar -xzf legacy_pi_backend_deployment.tar.gz`
2. 进入目录: `cd legacy_pi_backend_deployment`
3. 执行快速部署: `./quick-deploy.sh`

## 注意事项

- 确保服务器有足够的磁盘空间 (>5GB)
- 确保网络连接稳定
- 传输完成后可以删除压缩包以节省空间
EOF

    log_success "传输说明生成完成"
}

# 显示最终结果
show_final_results() {
    log_success "项目打包完成！"
    echo "=========================="
    echo "📦 打包文件: legacy_pi_backend_deployment.tar.gz"
    echo "📁 解压后目录: legacy_pi_backend_deployment/"
    echo "📋 传输说明: TRANSFER_INSTRUCTIONS.md"
    echo "=========================="
    
    # 显示文件大小
    if [ -f "legacy_pi_backend_deployment.tar.gz" ]; then
        size=$(du -sh legacy_pi_backend_deployment.tar.gz | cut -f1)
        echo "📊 文件大小: $size"
    fi
    
    echo "=========================="
    echo "🚀 下一步操作:"
    echo "1. 将 legacy_pi_backend_deployment.tar.gz 传输到云端服务器"
    echo "2. 在服务器上解压: tar -xzf legacy_pi_backend_deployment.tar.gz"
    echo "3. 进入目录: cd legacy_pi_backend_deployment"
    echo "4. 执行部署: ./quick-deploy.sh"
    echo "=========================="
}

# 主函数
main() {
    log_info "开始打包 Legacy PI Backend 项目..."
    echo "=========================="
    
    # 检查环境
    check_environment
    
    # 清理旧文件
    cleanup_old_files
    
    # 导出 Docker 镜像
    export_docker_images
    
    # 创建部署包
    create_deployment_package
    
    # 压缩部署包
    compress_package
    
    # 生成传输说明
    generate_transfer_instructions
    
    # 显示结果
    show_final_results
}

# 执行主函数
main "$@"
