#!/bin/bash

# Legacy PI Backend 生产环境部署脚本
# 使用方法: ./deploy.sh [环境] [操作]
# 示例: ./deploy.sh production deploy

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
    log_info "检查部署环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查环境文件
    if [ ! -f "env.production" ]; then
        log_error "生产环境配置文件 env.production 不存在"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 生成密钥
generate_secret_key() {
    log_info "生成 Django 密钥..."
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# 备份数据
backup_data() {
    log_info "备份现有数据..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份 Redis 数据
    if docker-compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
        log_info "备份 Redis 数据..."
        docker-compose -f docker-compose.prod.yml exec -T redis redis-cli -a "$REDIS_PASSWORD" --rdb /data/backup.rdb
        docker cp legacy_pi_redis_prod:/data/backup.rdb "$BACKUP_DIR/"
    fi
    
    # 备份 MongoDB 数据
    if docker-compose -f docker-compose.prod.yml ps mongodb | grep -q "Up"; then
        log_info "备份 MongoDB 数据..."
        docker-compose -f docker-compose.prod.yml exec -T mongodb mongodump --out /data/backup
        docker cp legacy_pi_mongodb_prod:/data/backup "$BACKUP_DIR/"
    fi
    
    # 备份媒体文件
    if [ -d "media" ]; then
        log_info "备份媒体文件..."
        cp -r media "$BACKUP_DIR/"
    fi
    
    log_success "数据备份完成: $BACKUP_DIR"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动生产服务..."
    docker-compose -f docker-compose.prod.yml up -d
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待 Redis
    log_info "等待 Redis 服务..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.prod.yml exec redis redis-cli -a "$REDIS_PASSWORD" ping; do sleep 2; done'
    
    # 等待 MongoDB
    log_info "等待 MongoDB 服务..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.runCommand(\"ping\")"; do sleep 2; done'
    
    # 等待 Django
    log_info "等待 Django 服务..."
    timeout 120 bash -c 'until curl -f http://localhost:8000/api/ai-chat/health/; do sleep 5; done'
    
    log_success "所有服务已就绪"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    docker-compose -f docker-compose.prod.yml exec django-app python manage.py migrate
    log_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    docker-compose -f docker-compose.prod.yml exec django-app python manage.py collectstatic --noinput
    log_success "静态文件收集完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查 API 健康状态
    if curl -f http://localhost:8000/api/ai-chat/health/; then
        log_success "API 健康检查通过"
    else
        log_error "API 健康检查失败"
        exit 1
    fi
    
    # 检查 Redis 连接
    if docker-compose -f docker-compose.prod.yml exec redis redis-cli -a "$REDIS_PASSWORD" ping; then
        log_success "Redis 连接正常"
    else
        log_error "Redis 连接失败"
        exit 1
    fi
    
    # 检查 MongoDB 连接
    if docker-compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.runCommand('ping')"; then
        log_success "MongoDB 连接正常"
    else
        log_error "MongoDB 连接失败"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止生产服务..."
    docker-compose -f docker-compose.prod.yml down
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理未使用的 Docker 资源..."
    docker system prune -f
    docker volume prune -f
    log_success "清理完成"
}

# 显示日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose -f docker-compose.prod.yml logs -f
}

# 主部署函数
deploy() {
    log_info "开始部署 Legacy PI Backend 到生产环境..."
    
    # 检查环境
    check_environment
    
    # 备份数据
    backup_data
    
    # 构建镜像
    build_images
    
    # 启动服务
    start_services
    
    # 等待服务就绪
    wait_for_services
    
    # 运行迁移
    run_migrations
    
    # 收集静态文件
    collect_static
    
    # 健康检查
    health_check
    
    log_success "部署完成！"
    log_info "服务访问地址: https://your-domain.com"
    log_info "管理界面: https://your-domain.com/admin/"
    log_info "API 文档: https://your-domain.com/api/"
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            deploy
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            wait_for_services
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            backup_data
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        "secret")
            generate_secret_key
            ;;
        *)
            echo "使用方法: $0 [deploy|stop|restart|logs|backup|health|cleanup|secret]"
            echo ""
            echo "命令说明:"
            echo "  deploy   - 完整部署到生产环境"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  logs     - 显示服务日志"
            echo "  backup   - 备份数据"
            echo "  health   - 健康检查"
            echo "  cleanup  - 清理 Docker 资源"
            echo "  secret   - 生成 Django 密钥"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
