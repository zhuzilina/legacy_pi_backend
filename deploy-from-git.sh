#!/bin/bash

# 基于 Git 克隆的云端部署脚本
# 使用方法: ./deploy-from-git.sh [Git仓库URL] [分支名]

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

# 默认配置
DEFAULT_GIT_URL="https://github.com/zhuzilina/legacy_pi_backend.git"
DEFAULT_BRANCH="main"
PROJECT_DIR="legacy_pi_backend"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# 获取参数
GIT_URL=${1:-$DEFAULT_GIT_URL}
BRANCH=${2:-$DEFAULT_BRANCH}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 克隆或更新项目
clone_or_update_project() {
    log_info "处理项目代码..."
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "项目目录已存在，更新代码..."
        cd "$PROJECT_DIR"
        
        # 检查是否是 Git 仓库
        if [ -d ".git" ]; then
            # 获取当前远程 URL
            current_url=$(git remote get-url origin 2>/dev/null || echo "")
            
            if [ "$current_url" != "$GIT_URL" ]; then
                log_warning "远程 URL 不匹配，重新克隆..."
                cd ..
                rm -rf "$PROJECT_DIR"
                git clone -b "$BRANCH" "$GIT_URL" "$PROJECT_DIR"
            else
                # 更新代码
                git fetch origin
                git reset --hard "origin/$BRANCH"
                git clean -fd
            fi
        else
            log_warning "目录不是 Git 仓库，重新克隆..."
            cd ..
            rm -rf "$PROJECT_DIR"
            git clone -b "$BRANCH" "$GIT_URL" "$PROJECT_DIR"
        fi
    else
        log_info "克隆项目代码..."
        git clone -b "$BRANCH" "$GIT_URL" "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
    log_success "项目代码准备完成"
}

# 检查镜像是否已存在
check_images_exist() {
    log_info "检查 Docker 镜像是否已存在..."
    
    # 检查基础镜像是否已存在
    if docker images | grep -q "python.*3.12-slim" && \
       docker images | grep -q "nginx.*alpine" && \
       docker images | grep -q "redis.*7.2-alpine" && \
       docker images | grep -q "mongo.*7.0"; then
        log_success "基础镜像已存在，跳过导入"
        return 0
    else
        log_info "基础镜像不存在，需要导入"
        return 1
    fi
}

# 导入基础镜像
import_base_images() {
    log_info "导入基础 Docker 镜像..."
    
    # 首先检查镜像是否已存在
    if check_images_exist; then
        return 0
    fi
    
    # 检查是否有镜像文件
    if [ -d "docker-base-images" ]; then
        log_info "发现基础镜像文件，开始导入..."
        cd docker-base-images
        
        if [ -f "import-base-images.sh" ]; then
            ./import-base-images.sh
        else
            log_warning "导入脚本不存在，手动导入镜像..."
            
            # 手动导入镜像
            for image_file in *.tar.gz; do
                if [ -f "$image_file" ]; then
                    log_info "导入 $image_file..."
                    gunzip -c "$image_file" | docker load
                fi
            done
        fi
        
        cd ..
        log_success "基础镜像导入完成"
    elif [ -d "docker-images" ]; then
        log_info "发现完整镜像文件，开始导入..."
        cd docker-images
        
        if [ -f "import-images.sh" ]; then
            ./import-images.sh
        else
            log_warning "导入脚本不存在，手动导入镜像..."
            
            # 手动导入镜像
            for image_file in *.tar.gz; do
                if [ -f "$image_file" ]; then
                    log_info "导入 $image_file..."
                    gunzip -c "$image_file" | docker load
                fi
            done
        fi
        
        cd ..
        log_success "镜像导入完成"
    else
        log_warning "未找到镜像文件，尝试从 Docker Hub 拉取..."
        pull_base_images
    fi
}

# 从 Docker Hub 拉取基础镜像
pull_base_images() {
    log_info "从 Docker Hub 拉取基础镜像..."
    
    # 拉取基础镜像
    docker pull python:3.12-slim
    docker pull nginx:alpine
    docker pull redis:7.2-alpine
    docker pull mongo:7.0
    
    log_success "基础镜像拉取完成"
}

# 配置环境变量
configure_environment() {
    log_info "配置环境变量..."
    
    # 确保在项目目录中
    if [ ! -f "manage.py" ]; then
        log_error "当前不在项目根目录，请检查路径"
        exit 1
    fi
    
    # 检查环境配置文件
    if [ ! -f "env.production" ]; then
        if [ -f "env.example" ]; then
            cp env.example env.production
            log_warning "已创建 env.production 文件，请编辑配置"
        else
            log_error "未找到环境配置文件模板 env.example"
            log_info "当前目录文件列表:"
            ls -la
            exit 1
        fi
    fi
    
    # 检查必要的环境变量
    if ! grep -q "ARK_API_KEY=" env.production || grep -q "your.*api.*key" env.production; then
        log_warning "请配置 ARK_API_KEY 在 env.production 文件中"
    fi
    
    if ! grep -q "SECRET_KEY=" env.production || grep -q "your.*secret.*key" env.production; then
        log_warning "请配置 SECRET_KEY 在 env.production 文件中"
    fi
    
    log_success "环境配置检查完成"
}

# 构建 Django 应用
build_django_app() {
    log_info "构建 Django 应用..."
    
    # 检查 Dockerfile
    if [ ! -f "Dockerfile.prod" ]; then
        log_error "Dockerfile.prod 不存在"
        exit 1
    fi
    
    # 构建镜像
    docker-compose -f "$DOCKER_COMPOSE_FILE" build django-app
    
    log_success "Django 应用构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d redis mongodb
    
    # 等待基础服务就绪
    log_info "等待基础服务就绪..."
    sleep 10
    
    # 启动 Django 应用
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d django-app
    
    # 等待 Django 应用就绪
    log_info "等待 Django 应用就绪..."
    sleep 15
    
    # 启动 Nginx
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d nginx
    
    log_success "所有服务启动完成"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    # 等待 Django 应用完全启动
    sleep 10
    
    # 运行迁移
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec django-app python manage.py migrate
    
    log_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    # 收集静态文件
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec django-app python manage.py collectstatic --noinput
    
    log_success "静态文件收集完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    # 等待服务完全启动
    sleep 10
    
    # 检查 API 健康状态
    if curl -f http://localhost/api/ai-chat/health/ >/dev/null 2>&1; then
        log_success "API 健康检查通过"
    else
        log_warning "API 健康检查失败，请检查日志"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs django-app
    fi
    
    # 检查 Redis 连接
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec redis redis-cli -a "${REDIS_PASSWORD:-redis123}" ping >/dev/null 2>&1; then
        log_success "Redis 连接正常"
    else
        log_warning "Redis 连接失败"
    fi
    
    # 检查 MongoDB 连接
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mongodb mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        log_success "MongoDB 连接正常"
    else
        log_warning "MongoDB 连接失败"
    fi
}

# 显示部署结果
show_deployment_result() {
    log_success "部署完成！"
    echo "=========================="
    echo "📱 访问地址:"
    echo "  - 主应用: http://$(hostname -I | awk '{print $1}')"
    echo "  - API 文档: http://$(hostname -I | awk '{print $1}')/api/"
    echo "  - 健康检查: http://$(hostname -I | awk '{print $1}')/api/ai-chat/health/"
    echo ""
    echo "🔧 管理命令:"
    echo "  - 查看日志: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  - 停止服务: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "  - 重启服务: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "  - 更新代码: ./deploy-from-git.sh $GIT_URL $BRANCH"
    echo ""
    echo "📊 服务状态:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

# 主函数
main() {
    log_info "开始基于 Git 的云端部署..."
    echo "=========================="
    echo "Git 仓库: $GIT_URL"
    echo "分支: $BRANCH"
    echo "=========================="
    
    # 检查环境
    check_environment
    
    # 克隆或更新项目
    clone_or_update_project
    
    # 导入基础镜像 (在项目目录外执行)
    cd ..
    import_base_images
    cd "$PROJECT_DIR"
    
    # 配置环境变量 (在项目目录内执行)
    configure_environment
    
    # 构建 Django 应用
    build_django_app
    
    # 启动服务
    start_services
    
    # 运行数据库迁移
    run_migrations
    
    # 收集静态文件
    collect_static
    
    # 健康检查
    health_check
    
    # 显示结果
    show_deployment_result
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [Git仓库URL] [分支名]"
    echo ""
    echo "参数:"
    echo "  Git仓库URL  - 项目的 Git 仓库地址 (默认: $DEFAULT_GIT_URL)"
    echo "  分支名      - 要部署的分支 (默认: $DEFAULT_BRANCH)"
    echo ""
    echo "示例:"
    echo "  $0 https://github.com/user/repo.git main"
    echo "  $0 https://github.com/user/repo.git develop"
    echo "  $0  # 使用默认配置"
    echo ""
    echo "环境要求:"
    echo "  - Git"
    echo "  - Docker"
    echo "  - Docker Compose"
    echo "  - 网络连接 (用于克隆代码和拉取镜像)"
}

# 检查参数
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"
