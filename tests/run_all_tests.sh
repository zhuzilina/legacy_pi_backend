#!/bin/bash

# Legacy PI Backend 测试运行脚本
# 用于运行所有测试文件

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
    log_info "检查测试环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查服务状态
    if ! docker-compose ps | grep -q "Up"; then
        log_warning "Docker服务未运行，请先启动服务"
        log_info "运行: docker-compose up -d"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 运行Python测试
run_python_tests() {
    log_info "运行Python测试..."
    
    local python_tests=(
        "test_ai_chat_api.py"
        "test_ai_chat.py"
        "test_ai_chat_simple.py"
        "test_ai_interpreter.py"
        "test_interpret_api.py"
        "test_stream_api.py"
        "test_image_chat.py"
        "test_image_cache.py"
        "test_specific_image.py"
        "test_tts_api.py"
        "test_md_docs_system.py"
        "test_knowledge_quiz.py"
        "test_knowledge_ai.py"
        "test_key_points.py"
        "test_all_prompts.py"
        "debug_robot_article.py"
        "quick_test.py"
        "quick_test_ai.py"
    )
    
    local success_count=0
    local failed_count=0
    
    for test in "${python_tests[@]}"; do
        if [ -f "$test" ]; then
            log_info "运行测试: $test"
            if python3 "$test"; then
                log_success "测试通过: $test"
                ((success_count++))
            else
                log_error "测试失败: $test"
                ((failed_count++))
            fi
            echo "---"
        else
            log_warning "测试文件不存在: $test"
        fi
    done
    
    echo "Python测试结果: 成功 $success_count, 失败 $failed_count"
}

# 运行Shell测试
run_shell_tests() {
    log_info "运行Shell测试..."
    
    local shell_tests=(
        "test_nginx_deployment.sh"
        "test_performance_optimization.sh"
        "test_admin_access.sh"
    )
    
    local success_count=0
    local failed_count=0
    
    for test in "${shell_tests[@]}"; do
        if [ -f "$test" ]; then
            log_info "运行测试: $test"
            if ./"$test"; then
                log_success "测试通过: $test"
                ((success_count++))
            else
                log_error "测试失败: $test"
                ((failed_count++))
            fi
            echo "---"
        else
            log_warning "测试文件不存在: $test"
        fi
    done
    
    echo "Shell测试结果: 成功 $success_count, 失败 $failed_count"
}

# 运行特定类别测试
run_category_tests() {
    local category=$1
    
    case $category in
        "ai")
            log_info "运行AI服务测试..."
            python3 test_ai_chat_api.py
            python3 test_ai_interpreter.py
            python3 test_stream_api.py
            python3 test_image_chat.py
            ;;
        "content")
            log_info "运行内容管理测试..."
            python3 test_md_docs_system.py
            python3 test_knowledge_quiz.py
            python3 test_knowledge_ai.py
            ;;
        "deployment")
            log_info "运行部署测试..."
            ./test_nginx_deployment.sh
            ./test_performance_optimization.sh
            ./test_admin_access.sh
            ;;
        "quick")
            log_info "运行快速测试..."
            python3 quick_test.py
            python3 quick_test_ai.py
            ;;
        *)
            log_error "未知测试类别: $category"
            log_info "可用类别: ai, content, deployment, quick"
            exit 1
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "Legacy PI Backend 测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -a, --all           运行所有测试"
    echo "  -p, --python        只运行Python测试"
    echo "  -s, --shell         只运行Shell测试"
    echo "  -c, --category      运行特定类别测试"
    echo "  --check             只检查环境"
    echo ""
    echo "测试类别:"
    echo "  ai                  AI服务测试"
    echo "  content             内容管理测试"
    echo "  deployment          部署测试"
    echo "  quick               快速测试"
    echo ""
    echo "示例:"
    echo "  $0 --all                    # 运行所有测试"
    echo "  $0 --python                 # 只运行Python测试"
    echo "  $0 --category ai            # 运行AI服务测试"
    echo "  $0 --check                  # 只检查环境"
}

# 主函数
main() {
    local run_all=false
    local run_python=false
    local run_shell=false
    local category=""
    local check_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--all)
                run_all=true
                shift
                ;;
            -p|--python)
                run_python=true
                shift
                ;;
            -s|--shell)
                run_shell=true
                shift
                ;;
            -c|--category)
                category="$2"
                shift 2
                ;;
            --check)
                check_only=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查环境
    check_environment
    
    if [ "$check_only" = true ]; then
        log_success "环境检查完成"
        exit 0
    fi
    
    # 运行测试
    if [ "$run_all" = true ]; then
        run_python_tests
        run_shell_tests
    elif [ "$run_python" = true ]; then
        run_python_tests
    elif [ "$run_shell" = true ]; then
        run_shell_tests
    elif [ -n "$category" ]; then
        run_category_tests "$category"
    else
        log_info "未指定测试类型，运行所有测试..."
        run_python_tests
        run_shell_tests
    fi
    
    log_success "测试运行完成"
}

# 运行主函数
main "$@"
