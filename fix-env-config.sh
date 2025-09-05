#!/bin/bash

# 修复环境变量配置脚本
# 用于设置生产环境的实际环境变量值

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

# 生成随机字符串
generate_random_string() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# 生成 Django SECRET_KEY
generate_secret_key() {
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
print(secret_key)
"
}

# 修复环境变量配置
fix_environment_config() {
    log_info "修复环境变量配置..."
    
    # 备份原文件
    if [ -f "env.production" ]; then
        cp env.production env.production.backup.$(date +%Y%m%d_%H%M%S)
        log_info "已备份原配置文件"
    fi
    
    # 生成新的环境变量值
    SECRET_KEY=$(generate_secret_key)
    REDIS_PASSWORD=$(generate_random_string 16)
    MONGODB_PASSWORD=$(generate_random_string 16)
    
    # 获取服务器 IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    # 创建新的环境变量文件
    cat > env.production << EOF
# 生产环境配置
DEBUG=False
SECRET_KEY=$SECRET_KEY

# 数据库配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=$REDIS_PASSWORD

# MongoDB 配置
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=$MONGODB_PASSWORD
MONGODB_DATABASE=md_docs

# 方舟 API 配置
ARK_API_KEY=your-production-ark-api-key

# 服务器配置
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://$SERVER_IP

# 安全配置 (HTTP 模式)
SECURE_SSL_REDIRECT=False
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# 静态文件配置
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 日志配置
LOG_LEVEL=INFO
EOF

    log_success "环境变量配置已修复"
    
    # 显示重要信息
    echo ""
    log_info "重要配置信息:"
    echo "=========================="
    echo "SECRET_KEY: $SECRET_KEY"
    echo "REDIS_PASSWORD: $REDIS_PASSWORD"
    echo "MONGODB_PASSWORD: $MONGODB_PASSWORD"
    echo "SERVER_IP: $SERVER_IP"
    echo "=========================="
    echo ""
    log_warning "请手动设置 ARK_API_KEY 在 env.production 文件中"
}

# 验证环境变量
validate_environment() {
    log_info "验证环境变量配置..."
    
    if [ ! -f "env.production" ]; then
        log_error "env.production 文件不存在"
        return 1
    fi
    
    # 检查必要的环境变量
    source env.production
    
    if [ "$SECRET_KEY" = "your-production-secret-key-here" ]; then
        log_error "SECRET_KEY 未正确设置"
        return 1
    fi
    
    if [ "$REDIS_PASSWORD" = "your-secure-redis-password" ]; then
        log_error "REDIS_PASSWORD 未正确设置"
        return 1
    fi
    
    if [ "$MONGODB_PASSWORD" = "your-secure-mongodb-password" ]; then
        log_error "MONGODB_PASSWORD 未正确设置"
        return 1
    fi
    
    if [ "$ARK_API_KEY" = "your-production-ark-api-key" ]; then
        log_warning "ARK_API_KEY 仍为占位符，请手动设置"
    fi
    
    log_success "环境变量验证通过"
}

# 清理失败的容器
cleanup_failed_containers() {
    log_info "清理失败的容器..."
    
    # 停止所有相关容器
    docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
    
    # 清理未使用的容器
    docker container prune -f 2>/dev/null || true
    
    log_success "容器清理完成"
}

# 重新启动服务
restart_services() {
    log_info "重新启动服务..."
    
    # 启动服务
    docker-compose -f docker-compose.prod.yml up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    docker-compose -f docker-compose.prod.yml ps
    
    log_success "服务重启完成"
}

# 主函数
main() {
    log_info "开始修复环境变量配置..."
    echo "=========================="
    
    # 修复环境变量配置
    fix_environment_config
    
    echo ""
    
    # 验证环境变量
    validate_environment
    
    echo ""
    
    # 清理失败的容器
    cleanup_failed_containers
    
    echo ""
    
    # 重新启动服务
    restart_services
    
    echo ""
    log_success "环境变量配置修复完成！"
    echo "=========================="
    echo "下一步:"
    echo "1. 编辑 env.production 文件，设置正确的 ARK_API_KEY"
    echo "2. 运行: docker-compose -f docker-compose.prod.yml restart django-app"
    echo "3. 检查服务状态: docker-compose -f docker-compose.prod.yml ps"
    echo "=========================="
}

# 执行主函数
main "$@"
