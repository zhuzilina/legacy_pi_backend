#!/bin/bash

# 本地部署测试脚本
set -e

echo "🧪 本地部署测试开始..."
echo "=========================="

# 检查环境变量
if [ -z "$ARK_API_KEY" ]; then
    echo "⚠️  警告: 未设置 ARK_API_KEY 环境变量"
    echo "请设置: export ARK_API_KEY='your_api_key'"
    echo "继续使用默认值进行测试..."
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose -f docker-compose.local.yml down 2>/dev/null || true

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建镜像
echo "🔨 构建镜像..."
docker-compose -f docker-compose.local.yml build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose -f docker-compose.local.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.local.yml ps

# 等待健康检查
echo "🏥 等待健康检查..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/api/ai-chat/health/ >/dev/null 2>&1; then
        echo "✅ Django 服务健康检查通过"
        break
    fi
    echo "   等待中... ($((attempt+1))/$max_attempts)"
    sleep 5
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Django 服务健康检查失败"
    echo "查看日志:"
    docker-compose -f docker-compose.local.yml logs django-app
    exit 1
fi

# 测试 API 端点
echo "🔍 测试 API 端点..."

# 测试健康检查
echo "1. 测试健康检查 API..."
if curl -f http://localhost:8000/api/ai-chat/health/; then
    echo "✅ 健康检查 API 正常"
else
    echo "❌ 健康检查 API 失败"
fi

# 测试系统提示词 API
echo -e "\n2. 测试系统提示词 API..."
if curl -f http://localhost:8000/api/ai-chat/prompts/ >/dev/null 2>&1; then
    echo "✅ 系统提示词 API 正常"
else
    echo "❌ 系统提示词 API 失败"
fi

# 测试图片提示词 API
echo -e "\n3. 测试图片提示词 API..."
if curl -f http://localhost:8000/api/ai-chat/image-prompts/ >/dev/null 2>&1; then
    echo "✅ 图片提示词 API 正常"
else
    echo "❌ 图片提示词 API 失败"
fi

# 测试对话配置 API
echo -e "\n4. 测试对话配置 API..."
if curl -f http://localhost:8000/api/ai-chat/config/ >/dev/null 2>&1; then
    echo "✅ 对话配置 API 正常"
else
    echo "❌ 对话配置 API 失败"
fi

# 测试主页面 API
echo -e "\n5. 测试主页面 API..."
if curl -f http://localhost:8000/api/ai-chat/ >/dev/null 2>&1; then
    echo "✅ 主页面 API 正常"
else
    echo "❌ 主页面 API 失败"
fi

# 测试 AI 对话 API (如果有 API 密钥)
if [ -n "$ARK_API_KEY" ] && [ "$ARK_API_KEY" != "your_api_key_here" ]; then
    echo -e "\n6. 测试 AI 对话 API..."
    response=$(curl -s -X POST "http://localhost:8000/api/ai-chat/chat/" \
        -H "Content-Type: application/json" \
        -d '{"message": "你好，请简单介绍一下自己"}')
    
    if echo "$response" | grep -q "success"; then
        echo "✅ AI 对话 API 正常"
    else
        echo "❌ AI 对话 API 失败"
        echo "响应: $response"
    fi
else
    echo -e "\n6. 跳过 AI 对话 API 测试 (未设置有效 API 密钥)"
fi

# 显示访问信息
echo -e "\n🎉 本地部署测试完成！"
echo "=========================="
echo "📱 访问地址:"
echo "  - 主应用: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/api/"
echo "  - 健康检查: http://localhost:8000/api/ai-chat/health/"
echo "  - 管理界面: http://localhost:8000/admin/"
echo ""
echo "🔧 管理命令:"
echo "  - 查看日志: docker-compose -f docker-compose.local.yml logs -f"
echo "  - 停止服务: docker-compose -f docker-compose.local.yml down"
echo "  - 重启服务: docker-compose -f docker-compose.local.yml restart"
echo ""
echo "📊 服务状态:"
docker-compose -f docker-compose.local.yml ps
