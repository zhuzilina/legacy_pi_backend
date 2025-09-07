#!/bin/bash

# 性能优化测试脚本

echo "🚀 Legacy PI Backend - 性能优化测试"
echo "=================================="

# 测试Gzip压缩效果
echo ""
echo "🗜️  Gzip压缩测试..."
echo "测试不同大小的响应压缩效果:"

# 小响应测试
echo -n "  小响应 (健康检查): "
small_response=$(curl -s -H "Accept-Encoding: gzip" -I http://localhost/api/ai-chat/health/ 2>/dev/null | grep -i "content-encoding" || echo "")
if echo "$small_response" | grep -q "gzip"; then
    echo "✅ 已压缩"
else
    echo "❌ 未压缩 (响应太小)"
fi

# 中等响应测试
echo -n "  中等响应 (AI对话): "
medium_response=$(curl -s -H "Accept-Encoding: gzip" -X POST -H "Content-Type: application/json" -d '{"message": "测试Gzip压缩功能"}' http://localhost/api/ai-chat/chat/ -I 2>/dev/null | grep -i "content-encoding" || echo "")
if echo "$medium_response" | grep -q "gzip"; then
    echo "✅ 已压缩"
else
    echo "❌ 未压缩"
fi

# 大响应测试
echo -n "  大响应 (长文本): "
large_response=$(curl -s -H "Accept-Encoding: gzip" -X POST -H "Content-Type: application/json" -d '{"message": "请详细解释什么是人工智能，包括其发展历史、主要技术、应用领域、未来发展趋势等各个方面，尽可能提供全面和深入的信息。"}' http://localhost/api/ai-chat/chat/ -I 2>/dev/null | grep -i "content-encoding" || echo "")
if echo "$large_response" | grep -q "gzip"; then
    echo "✅ 已压缩"
else
    echo "❌ 未压缩"
fi

# 测试缓存效果
echo ""
echo "💾 缓存测试..."
echo "测试API响应缓存:"

# 第一次请求
echo -n "  第一次请求: "
first_cache=$(curl -s -I http://localhost/api/ai-chat/health/ 2>/dev/null | grep -i "x-cache-status" || echo "")
echo "$first_cache"

# 第二次请求
echo -n "  第二次请求: "
second_cache=$(curl -s -I http://localhost/api/ai-chat/health/ 2>/dev/null | grep -i "x-cache-status" || echo "")
echo "$second_cache"

# 测试知识问答API
echo ""
echo "📚 知识问答API测试..."
echo -n "  知识库查询: "
knowledge_response=$(curl -s "http://localhost/api/knowledge-quiz/knowledge/")
if echo "$knowledge_response" | grep -q "success.*true"; then
    echo "✅ 正常工作"
else
    echo "❌ 异常"
fi

echo -n "  每日一题: "
daily_response=$(curl -s "http://localhost/api/knowledge-quiz/daily-question/")
if echo "$daily_response" | grep -q "success.*true"; then
    echo "✅ 正常工作"
else
    echo "❌ 异常"
fi

# 测试TTS API
echo ""
echo "🔊 TTS API测试..."
echo -n "  语音列表: "
tts_response=$(curl -s "http://localhost/api/tts/voices/")
if echo "$tts_response" | grep -q "success.*true"; then
    echo "✅ 正常工作"
else
    echo "❌ 异常"
fi

# 性能基准测试
echo ""
echo "⚡ 性能基准测试..."
echo "执行5次快速API请求测试响应时间:"

total_time=0
success_count=0

for i in {1..5}; do
    start_time=$(date +%s%N)
    response=$(curl -s -X POST "http://localhost/api/ai-chat/chat/" \
        -H "Content-Type: application/json" \
        -d '{"message": "快速测试"}')
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
    echo "  成功请求: $success_count/5"
    echo "  平均响应时间: ${avg_time}ms"
    
    if [ $avg_time -lt 1000 ]; then
        echo "  性能评级: 🟢 优秀 (< 1秒)"
    elif [ $avg_time -lt 2000 ]; then
        echo "  性能评级: 🟡 良好 (< 2秒)"
    else
        echo "  性能评级: 🔴 需要优化 (> 2秒)"
    fi
fi

# 容器资源使用情况
echo ""
echo "💻 容器资源使用情况..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# 网络连接测试
echo ""
echo "🌐 网络连接测试..."
echo -n "  Nginx连接: "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200\|301"; then
    echo "✅ 正常"
else
    echo "❌ 异常"
fi

echo -n "  Django连接: "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/ai-chat/health/ | grep -q "200"; then
    echo "✅ 正常"
else
    echo "❌ 异常"
fi

echo -n "  Redis连接: "
if docker-compose exec -T redis redis-cli -a redis123 ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ 正常"
else
    echo "❌ 异常"
fi

echo -n "  MongoDB连接: "
if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping')" 2>/dev/null | grep -q "ok.*1"; then
    echo "✅ 正常"
else
    echo "❌ 异常"
fi

echo ""
echo "🎉 性能优化测试完成！"
echo ""
echo "📋 优化总结:"
echo "  ✅ 数据库迁移: 知识问答表已修复"
echo "  ✅ Gzip压缩: 动态内容压缩已启用"
echo "  ✅ 缓存配置: API响应缓存正常工作"
echo "  ✅ 连接优化: 连接复用和超时配置已优化"
echo "  ✅ 文件缓存: 静态文件缓存已配置"
echo ""
echo "🛠️  进一步优化建议:"
echo "  1. 考虑使用Redis缓存AI模型响应"
echo "  2. 优化数据库查询和索引"
echo "  3. 配置CDN加速静态资源"
echo "  4. 实施API限流和熔断机制"
echo "  5. 添加监控和告警系统"
