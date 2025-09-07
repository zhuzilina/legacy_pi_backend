#!/bin/bash

# Nginx + uWSGI 部署测试脚本

echo "🚀 Legacy PI Backend - Nginx + uWSGI 部署测试"
echo "=============================================="

# 测试基础连接
echo ""
echo "📡 测试基础连接..."
echo -n "Nginx 主页: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/ && echo " ✅" || echo " ❌"

# 测试API健康检查
echo ""
echo "🏥 测试API健康检查..."
echo -n "AI对话健康检查: "
response=$(curl -s http://localhost/api/ai-chat/health/)
if echo "$response" | grep -q "healthy"; then
    echo " ✅"
else
    echo " ❌"
fi

# 测试AI对话API
echo ""
echo "🤖 测试AI对话API..."
echo -n "AI对话功能: "
response=$(curl -s -X POST "http://localhost/api/ai-chat/chat/" \
    -H "Content-Type: application/json" \
    -d '{"message": "你好，测试Nginx部署"}')
if echo "$response" | grep -q "success.*true"; then
    echo " ✅"
else
    echo " ❌"
fi

# 测试AI解读API
echo ""
echo "📖 测试AI解读API..."
echo -n "AI解读功能: "
response=$(curl -s -X POST "http://localhost/api/ai/interpret/" \
    -H "Content-Type: application/json" \
    -d '{"text": "测试文本", "prompt_type": "summary"}')
if echo "$response" | grep -q "success.*true"; then
    echo " ✅"
else
    echo " ❌"
fi

# 测试TTS API
echo ""
echo "🔊 测试TTS API..."
echo -n "TTS语音列表: "
response=$(curl -s "http://localhost/api/tts/voices/")
if echo "$response" | grep -q "success.*true"; then
    echo " ✅"
else
    echo " ❌"
fi

# 测试知识问答API
echo ""
echo "📚 测试知识问答API..."
echo -n "知识库查询: "
response=$(curl -s "http://localhost/api/knowledge-quiz/knowledge/")
if echo "$response" | grep -q "success.*true"; then
    echo " ✅"
else
    echo " ❌"
fi

# 测试静态文件服务
echo ""
echo "📁 测试静态文件服务..."
echo -n "静态文件目录: "
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/)
if [ "$status" = "403" ] || [ "$status" = "200" ]; then
    echo " ✅ (状态码: $status)"
else
    echo " ❌ (状态码: $status)"
fi

# 测试缓存头
echo ""
echo "💾 测试缓存配置..."
echo -n "API缓存头: "
cache_status=$(curl -s -I http://localhost/api/ai-chat/health/ | grep -i "x-cache-status" || echo "未设置")
echo " $cache_status"

# 测试Gzip压缩
echo ""
echo "🗜️  测试Gzip压缩..."
echo -n "Gzip压缩: "
gzip_header=$(curl -s -H "Accept-Encoding: gzip" -X POST -H "Content-Type: application/json" -d '{"message": "测试Gzip压缩"}' http://localhost/api/ai-chat/chat/ -I 2>/dev/null | grep -i "content-encoding" || echo "未启用")
if echo "$gzip_header" | grep -q "gzip"; then
    echo " ✅ 已启用"
else
    echo " ❌ 未启用"
fi

# 性能测试
echo ""
echo "⚡ 性能测试..."
echo "执行10次API请求测试响应时间..."

total_time=0
success_count=0

for i in {1..10}; do
    start_time=$(date +%s%N)
    response=$(curl -s -X POST "http://localhost/api/ai-chat/chat/" \
        -H "Content-Type: application/json" \
        -d '{"message": "性能测试"}')
    end_time=$(date +%s%N)
    
    if echo "$response" | grep -q "success.*true"; then
        duration=$(( (end_time - start_time) / 1000000 ))
        total_time=$((total_time + duration))
        success_count=$((success_count + 1))
        echo "  请求 $i: ${duration}ms ✅"
    else
        echo "  请求 $i: 失败 ❌"
    fi
done

if [ $success_count -gt 0 ]; then
    avg_time=$((total_time / success_count))
    echo ""
    echo "📊 性能统计:"
    echo "  成功请求: $success_count/10"
    echo "  平均响应时间: ${avg_time}ms"
    
    if [ $avg_time -lt 1000 ]; then
        echo "  性能评级: 🟢 优秀 (< 1秒)"
    elif [ $avg_time -lt 2000 ]; then
        echo "  性能评级: 🟡 良好 (< 2秒)"
    else
        echo "  性能评级: 🔴 需要优化 (> 2秒)"
    fi
fi

# 容器状态检查
echo ""
echo "🐳 容器状态检查..."
docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"

# 资源使用情况
echo ""
echo "💻 资源使用情况..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "🎉 测试完成！"
echo ""
echo "📋 服务访问地址:"
echo "  - 主应用 (Nginx): http://localhost"
echo "  - API文档: http://localhost/api/"
echo "  - 管理后台: http://localhost/admin/"
echo "  - MongoDB管理: http://localhost:8081"
echo ""
echo "🛠️  管理命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 重启服务: docker-compose restart"
echo "  - 停止服务: docker-compose down"
echo "  - 性能监控: ./monitor_performance.sh"
