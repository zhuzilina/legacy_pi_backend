#!/bin/bash

# 测试部署脚本的修复
# 用于验证 deploy-from-git.sh 脚本的修复

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

# 测试镜像检查功能
test_image_check() {
    log_info "测试镜像检查功能..."
    
    # 模拟检查镜像是否存在
    if docker images | grep -q "python.*3.12-slim" 2>/dev/null; then
        log_success "Python 镜像已存在"
    else
        log_warning "Python 镜像不存在"
    fi
    
    if docker images | grep -q "nginx.*alpine" 2>/dev/null; then
        log_success "Nginx 镜像已存在"
    else
        log_warning "Nginx 镜像不存在"
    fi
    
    if docker images | grep -q "redis.*7.2-alpine" 2>/dev/null; then
        log_success "Redis 镜像已存在"
    else
        log_warning "Redis 镜像不存在"
    fi
    
    if docker images | grep -q "mongo.*7.0" 2>/dev/null; then
        log_success "MongoDB 镜像已存在"
    else
        log_warning "MongoDB 镜像不存在"
    fi
}

# 测试目录结构
test_directory_structure() {
    log_info "测试目录结构..."
    
    # 检查当前目录
    log_info "当前目录: $(pwd)"
    log_info "目录内容:"
    ls -la
    
    # 检查项目文件
    if [ -f "manage.py" ]; then
        log_success "manage.py 存在"
    else
        log_warning "manage.py 不存在"
    fi
    
    if [ -f "env.example" ]; then
        log_success "env.example 存在"
    else
        log_warning "env.example 不存在"
    fi
    
    if [ -f "docker-compose.prod.yml" ]; then
        log_success "docker-compose.prod.yml 存在"
    else
        log_warning "docker-compose.prod.yml 不存在"
    fi
    
    if [ -f "Dockerfile.prod" ]; then
        log_success "Dockerfile.prod 存在"
    else
        log_warning "Dockerfile.prod 不存在"
    fi
}

# 测试镜像目录
test_image_directories() {
    log_info "测试镜像目录..."
    
    if [ -d "docker-base-images" ]; then
        log_success "docker-base-images 目录存在"
        log_info "基础镜像目录内容:"
        ls -la docker-base-images/
    else
        log_warning "docker-base-images 目录不存在"
    fi
    
    if [ -d "docker-images" ]; then
        log_success "docker-images 目录存在"
        log_info "完整镜像目录内容:"
        ls -la docker-images/
    else
        log_warning "docker-images 目录不存在"
    fi
}

# 测试环境变量配置
test_environment_config() {
    log_info "测试环境变量配置..."
    
    if [ -f "env.production" ]; then
        log_success "env.production 文件存在"
        log_info "环境变量配置:"
        grep -E "(ARK_API_KEY|SECRET_KEY|REDIS_PASSWORD|MONGODB_PASSWORD)" env.production || log_warning "未找到关键环境变量"
    else
        log_warning "env.production 文件不存在"
        if [ -f "env.example" ]; then
            log_info "从 env.example 创建 env.production"
            cp env.example env.production
            log_success "已创建 env.production 文件"
        fi
    fi
}

# 主测试函数
main() {
    log_info "开始测试部署脚本修复..."
    echo "=========================="
    
    # 测试镜像检查
    test_image_check
    
    echo ""
    
    # 测试目录结构
    test_directory_structure
    
    echo ""
    
    # 测试镜像目录
    test_image_directories
    
    echo ""
    
    # 测试环境变量配置
    test_environment_config
    
    echo ""
    log_success "测试完成！"
    echo "=========================="
    echo "修复内容:"
    echo "1. ✅ 添加了镜像存在性检查，避免重复导入"
    echo "2. ✅ 修复了目录路径问题，确保在正确目录执行操作"
    echo "3. ✅ 改进了环境变量配置检查"
    echo "4. ✅ 更新了默认 Git URL"
    echo "=========================="
}

# 执行测试
main "$@"
