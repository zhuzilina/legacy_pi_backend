#!/bin/bash

# Django管理后台访问测试脚本

echo "🔐 Django管理后台访问测试"
echo "=========================="

# 测试管理后台页面
echo ""
echo "📄 测试管理后台页面..."
echo -n "  登录页面: "
login_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/login/)
if [ "$login_status" = "200" ]; then
    echo "✅ 可访问 (状态码: $login_status)"
else
    echo "❌ 无法访问 (状态码: $login_status)"
fi

# 测试静态文件
echo ""
echo "🎨 测试静态文件..."
echo -n "  CSS样式文件: "
css_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css)
if [ "$css_status" = "200" ]; then
    echo "✅ 可访问 (状态码: $css_status)"
else
    echo "❌ 无法访问 (状态码: $css_status)"
fi

echo -n "  JavaScript文件: "
js_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/js/core.js)
if [ "$js_status" = "200" ]; then
    echo "✅ 可访问 (状态码: $js_status)"
else
    echo "❌ 无法访问 (状态码: $js_status)"
fi

# 测试页面标题
echo ""
echo "📋 测试页面内容..."
echo -n "  页面标题: "
title=$(curl -s http://localhost/admin/login/ | grep -o '<title>.*</title>' | sed 's/<[^>]*>//g')
if [ -n "$title" ]; then
    echo "✅ $title"
else
    echo "❌ 无法获取标题"
fi

# 测试用户认证
echo ""
echo "👤 测试用户认证..."
echo -n "  超级用户存在: "
user_exists=$(docker-compose exec -T django-app python manage.py shell -c "from django.contrib.auth.models import User; print('exists' if User.objects.filter(username='admin').exists() else 'not_exists')" 2>/dev/null)
if [ "$user_exists" = "exists" ]; then
    echo "✅ 用户 'admin' 存在"
else
    echo "❌ 用户 'admin' 不存在"
fi

# 显示访问信息
echo ""
echo "🌐 访问信息:"
echo "  管理后台地址: http://localhost/admin/"
echo "  用户名: admin"
echo "  密码: admin123"

# 显示可管理的模型
echo ""
echo "📊 可管理的模型:"
echo "  - 知识问答 (Knowledge Quiz)"
echo "  - 知识AI服务 (Knowledge AI)"
echo "  - AI对话服务 (AI Chat)"
echo "  - AI解读服务 (AI Interpreter)"
echo "  - TTS语音服务 (TTS Service)"
echo "  - 爬虫服务 (Crawler)"
echo "  - 文档服务 (MD Docs)"
echo "  - 系统管理 (Users, Groups, Permissions)"

echo ""
echo "🎉 管理后台测试完成！"
echo ""
echo "💡 使用提示:"
echo "  1. 在浏览器中访问 http://localhost/admin/"
echo "  2. 使用 admin/admin123 登录"
echo "  3. 开始管理您的数据"
