#!/bin/bash

# Legacy PI Backend 性能监控脚本

echo "📊 Legacy PI Backend 性能监控"
echo "================================"

# 检查容器状态
echo "🐳 容器状态:"
docker-compose ps

echo ""

# 检查资源使用情况
echo "💻 资源使用情况:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""

# 检查服务健康状态
echo "🏥 服务健康检查:"
echo -n "Django 应用: "
curl -s -f http://localhost:8000/api/ai-chat/health/ > /dev/null && echo "✅ 健康" || echo "❌ 异常"

echo -n "Nginx 代理: "
curl -s -f http://localhost/health/ > /dev/null && echo "✅ 健康" || echo "❌ 异常"

echo -n "Redis 缓存: "
docker-compose exec -T redis redis-cli -a redis123 ping > /dev/null 2>&1 && echo "✅ 健康" || echo "❌ 异常"

echo -n "MongoDB 数据库: "
docker-compose exec -T mongodb mongosh --quiet --eval "db.runCommand('ping')" > /dev/null 2>&1 && echo "✅ 健康" || echo "❌ 异常"

echo ""

# 检查连接数
echo "🔗 连接统计:"
echo -n "Nginx 活跃连接: "
docker-compose exec -T nginx wget -qO- http://localhost/nginx_status 2>/dev/null | grep -o "Active connections: [0-9]*" || echo "无法获取"

echo ""

# 检查日志错误
echo "📝 最近错误日志 (最后10行):"
echo "Django 错误:"
docker-compose logs --tail=10 django-app 2>&1 | grep -i error || echo "无错误"

echo ""
echo "Nginx 错误:"
docker-compose logs --tail=10 nginx 2>&1 | grep -i error || echo "无错误"

echo ""

# 性能建议
echo "💡 性能优化建议:"
echo "1. 如果 CPU 使用率持续 > 80%，考虑增加 worker 进程数"
echo "2. 如果内存使用率持续 > 80%，考虑增加容器内存限制"
echo "3. 如果响应时间 > 2秒，检查数据库查询和缓存配置"
echo "4. 定期清理日志文件以节省磁盘空间"

echo ""
echo "🛠️  优化命令:"
echo "  - 重启服务: docker-compose restart"
echo "  - 查看详细日志: docker-compose logs -f"
echo "  - 清理未使用的镜像: docker system prune"
echo "  - 查看磁盘使用: docker system df"
