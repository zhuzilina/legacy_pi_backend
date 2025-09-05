#!/bin/bash

# Git 部署包打包脚本
# 用于打包基础镜像和部署脚本，支持云端动态构建

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
        "deploy-from-git.sh"
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
    if [ -d "docker-base-images" ]; then
        log_warning "删除旧的 docker-base-images 目录"
        rm -rf docker-base-images
    fi
    
    # 清理旧的打包文件
    if [ -f "legacy_pi_backend_git_deployment.tar.gz" ]; then
        log_warning "删除旧的打包文件"
        rm -f legacy_pi_backend_git_deployment.tar.gz
    fi
    
    log_success "清理完成"
}

# 导出基础镜像
export_base_images() {
    log_info "导出基础 Docker 镜像..."
    
    # 执行基础镜像导出脚本
    if [ -f "export-base-images.sh" ]; then
        ./export-base-images.sh
    else
        log_error "export-base-images.sh 不存在"
        exit 1
    fi
    
    log_success "基础镜像导出完成"
}

# 创建部署包
create_deployment_package() {
    log_info "创建 Git 部署包..."
    
    # 创建临时目录
    TEMP_DIR="legacy_pi_backend_git_deployment"
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
    mkdir -p "$TEMP_DIR"
    
    # 复制基础镜像
    if [ -d "docker-base-images" ]; then
        cp -r docker-base-images "$TEMP_DIR/"
    fi
    
    # 复制部署脚本
    cp deploy-from-git.sh "$TEMP_DIR/"
    
    # 创建快速部署脚本
    cat > "$TEMP_DIR/quick-git-deploy.sh" << 'EOF'
#!/bin/bash

# 快速 Git 部署脚本
set -e

echo "🚀 开始快速 Git 部署 Legacy PI Backend..."

# 检查环境
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装，请先安装 Git"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 导入基础镜像
echo "📦 导入基础镜像..."
cd docker-base-images
./import-base-images.sh
cd ..

# 获取 Git 仓库信息
echo "📋 请输入 Git 仓库信息:"
read -p "Git 仓库 URL: " GIT_URL
read -p "分支名 (默认: main): " BRANCH
BRANCH=${BRANCH:-main}

# 执行部署
echo "🚀 开始部署..."
chmod +x deploy-from-git.sh
./deploy-from-git.sh "$GIT_URL" "$BRANCH"

echo "✅ 部署完成！"
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
EOF

    chmod +x "$TEMP_DIR/quick-git-deploy.sh"
    
    # 创建部署说明
    cat > "$TEMP_DIR/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# Legacy PI Backend Git 部署说明

## 快速部署

1. **解压项目**
   ```bash
   tar -xzf legacy_pi_backend_git_deployment.tar.gz
   cd legacy_pi_backend_git_deployment
   ```

2. **执行快速部署**
   ```bash
   ./quick-git-deploy.sh
   ```

## 手动部署

1. **导入基础镜像**
   ```bash
   cd docker-base-images
   ./import-base-images.sh
   cd ..
   ```

2. **执行 Git 部署**
   ```bash
   ./deploy-from-git.sh https://github.com/your-repo/legacy_pi_backend.git main
   ```

## 优势

- 文件更小 (只包含基础镜像)
- 代码最新 (从 Git 动态获取)
- 易于更新 (重新运行脚本即可)
- 支持多分支部署

## 访问地址

部署完成后，通过以下地址访问：
- 主应用: http://your-server-ip
- API 文档: http://your-server-ip/api/
- 健康检查: http://your-server-ip/api/ai-chat/health/

## 管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 更新到最新版本
./deploy-from-git.sh https://github.com/your-repo/legacy_pi_backend.git main
```
EOF

    log_success "Git 部署包创建完成"
}

# 压缩部署包
compress_package() {
    log_info "压缩部署包..."
    
    # 计算压缩前大小
    size_before=$(du -sh legacy_pi_backend_git_deployment | cut -f1)
    
    # 压缩
    tar -czf legacy_pi_backend_git_deployment.tar.gz legacy_pi_backend_git_deployment/
    
    # 计算压缩后大小
    size_after=$(du -sh legacy_pi_backend_git_deployment.tar.gz | cut -f1)
    
    log_success "压缩完成"
    echo "压缩前大小: $size_before"
    echo "压缩后大小: $size_after"
}

# 生成传输说明
generate_transfer_instructions() {
    log_info "生成传输说明..."
    
    cat > GIT_TRANSFER_INSTRUCTIONS.md << 'EOF'
# Git 部署文件传输说明

## 传输文件

需要传输的文件: `legacy_pi_backend_git_deployment.tar.gz`

## 传输命令

### 使用 SCP 传输
```bash
# 传输到服务器
scp legacy_pi_backend_git_deployment.tar.gz user@your-server-ip:/home/user/

# 在服务器上解压
ssh user@your-server-ip
tar -xzf legacy_pi_backend_git_deployment.tar.gz
cd legacy_pi_backend_git_deployment
```

### 使用 SFTP 传输
```bash
# 连接服务器
sftp user@your-server-ip

# 上传文件
put legacy_pi_backend_git_deployment.tar.gz

# 退出 SFTP
quit

# 在服务器上解压
ssh user@your-server-ip
tar -xzf legacy_pi_backend_git_deployment.tar.gz
cd legacy_pi_backend_git_deployment
```

## 部署步骤

1. 解压项目: `tar -xzf legacy_pi_backend_git_deployment.tar.gz`
2. 进入目录: `cd legacy_pi_backend_git_deployment`
3. 执行快速部署: `./quick-git-deploy.sh`

## 优势

- 文件更小 (只包含基础镜像，约 350MB)
- 代码最新 (从 Git 动态获取)
- 易于更新 (重新运行脚本即可)
- 支持多分支部署

## 注意事项

- 确保服务器有网络连接以克隆代码
- 确保 Docker 和 Docker Compose 已安装
- 确保网络端口 80 已开放
- 传输完成后可以删除压缩包以节省空间
EOF

    log_success "传输说明生成完成"
}

# 显示最终结果
show_final_results() {
    log_success "Git 部署包打包完成！"
    echo "=========================="
    echo "📦 打包文件: legacy_pi_backend_git_deployment.tar.gz"
    echo "📁 解压后目录: legacy_pi_backend_git_deployment/"
    echo "📋 传输说明: GIT_TRANSFER_INSTRUCTIONS.md"
    echo "=========================="
    
    # 显示文件大小
    if [ -f "legacy_pi_backend_git_deployment.tar.gz" ]; then
        size=$(du -sh legacy_pi_backend_git_deployment.tar.gz | cut -f1)
        echo "📊 文件大小: $size"
    fi
    
    echo "=========================="
    echo "🚀 下一步操作:"
    echo "1. 将 legacy_pi_backend_git_deployment.tar.gz 传输到云端服务器"
    echo "2. 在服务器上解压: tar -xzf legacy_pi_backend_git_deployment.tar.gz"
    echo "3. 进入目录: cd legacy_pi_backend_git_deployment"
    echo "4. 执行快速部署: ./quick-git-deploy.sh"
    echo "=========================="
    echo "✨ 优势:"
    echo "- 文件更小 (只包含基础镜像)"
    echo "- 代码最新 (从 Git 动态获取)"
    echo "- 易于更新 (重新运行脚本即可)"
    echo "- 支持多分支部署"
    echo "=========================="
}

# 主函数
main() {
    log_info "开始打包 Legacy PI Backend Git 部署包..."
    echo "=========================="
    log_info "注意: Django 应用将在云端动态构建"
    echo "=========================="
    
    # 检查环境
    check_environment
    
    # 清理旧文件
    cleanup_old_files
    
    # 导出基础镜像
    export_base_images
    
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
