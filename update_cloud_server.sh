#!/bin/bash

# 更新云端服务器代码的脚本
# 用于在云端服务器上更新题目上传API

echo "🚀 开始更新云端服务器代码..."
echo "=================================="

# 1. 检查当前目录
echo "1. 检查当前目录:"
pwd
echo ""

# 2. 检查Git状态
echo "2. 检查Git状态:"
git status
echo ""

# 3. 拉取最新代码
echo "3. 拉取最新代码:"
git pull origin main
echo ""

# 4. 检查文件是否存在
echo "4. 检查关键文件:"
if [ -f "knowledge_quiz/views.py" ]; then
    echo "✅ knowledge_quiz/views.py 存在"
    # 检查是否包含批量上传函数
    if grep -q "def batch_upload_questions" knowledge_quiz/views.py; then
        echo "✅ batch_upload_questions 函数存在"
    else
        echo "❌ batch_upload_questions 函数不存在"
    fi
else
    echo "❌ knowledge_quiz/views.py 不存在"
fi

if [ -f "knowledge_quiz/urls.py" ]; then
    echo "✅ knowledge_quiz/urls.py 存在"
    # 检查是否包含批量上传URL
    if grep -q "batch-upload-questions" knowledge_quiz/urls.py; then
        echo "✅ batch-upload-questions URL 存在"
    else
        echo "❌ batch-upload-questions URL 不存在"
    fi
else
    echo "❌ knowledge_quiz/urls.py 不存在"
fi
echo ""

# 5. 重启Django服务
echo "5. 重启Django服务:"
echo "停止现有容器..."
docker-compose down
echo ""

echo "重新构建并启动容器..."
docker-compose up -d --build
echo ""

# 6. 等待服务启动
echo "6. 等待服务启动..."
sleep 10

# 7. 检查服务状态
echo "7. 检查服务状态:"
docker-compose ps
echo ""

# 8. 测试API
echo "8. 测试API:"
echo "测试每日一题API:"
curl -s "http://localhost/api/knowledge-quiz/daily-question/" | head -c 100
echo ""
echo ""

echo "测试批量上传API:"
curl -s -X POST "http://localhost/api/knowledge-quiz/batch-upload-questions/" \
     -H "Content-Type: application/json" \
     -d '{"questions": []}' | head -c 100
echo ""
echo ""

# 9. 检查日志
echo "9. 检查Django日志:"
docker-compose logs django-app --tail=20
echo ""

echo "✅ 云端服务器更新完成！"
echo "=================================="
echo "📋 更新总结:"
echo "   - 已拉取最新代码"
echo "   - 已重启Django服务"
echo "   - 已测试API接口"
echo ""
echo "💡 如果API仍然返回404，请检查:"
echo "   1. 代码是否正确推送到Git仓库"
echo "   2. 服务器是否正确拉取了最新代码"
echo "   3. Django服务是否正常启动"
echo "   4. URL配置是否正确"
