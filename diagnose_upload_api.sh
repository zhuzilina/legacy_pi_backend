#!/bin/bash

# 诊断题目上传API问题的脚本

echo "🔍 诊断题目上传API问题..."
echo "=================================="

# 1. 检查本地代码
echo "1. 检查本地代码:"
echo "检查 knowledge_quiz/views.py:"
if grep -q "def batch_upload_questions" knowledge_quiz/views.py; then
    echo "✅ batch_upload_questions 函数存在"
else
    echo "❌ batch_upload_questions 函数不存在"
fi

echo "检查 knowledge_quiz/urls.py:"
if grep -q "batch-upload-questions" knowledge_quiz/urls.py; then
    echo "✅ batch-upload-questions URL 存在"
else
    echo "❌ batch-upload-questions URL 不存在"
fi
echo ""

# 2. 检查云端服务器API
echo "2. 检查云端服务器API:"
echo "测试每日一题API:"
response1=$(curl -s "http://121.36.87.174/api/knowledge-quiz/daily-question/")
echo "响应: $response1"
echo ""

echo "测试批量上传API:"
response2=$(curl -s -X POST "http://121.36.87.174/api/knowledge-quiz/batch-upload-questions/" \
     -H "Content-Type: application/json" \
     -d '{"questions": []}')
echo "响应: $response2"
echo ""

# 3. 检查API路径
echo "3. 检查API路径:"
echo "尝试不同的API路径:"

echo "测试路径1: /api/knowledge-quiz/batch-upload-questions/"
curl -s -X POST "http://121.36.87.174/api/knowledge-quiz/batch-upload-questions/" \
     -H "Content-Type: application/json" \
     -d '{"questions": []}' | head -c 200
echo ""
echo ""

echo "测试路径2: /api/batch-upload-questions/"
curl -s -X POST "http://121.36.87.174/api/batch-upload-questions/" \
     -H "Content-Type: application/json" \
     -d '{"questions": []}' | head -c 200
echo ""
echo ""

echo "测试路径3: /batch-upload-questions/"
curl -s -X POST "http://121.36.87.174/batch-upload-questions/" \
     -H "Content-Type: application/json" \
     -d '{"questions": []}' | head -c 200
echo ""
echo ""

# 4. 检查服务器状态
echo "4. 检查服务器状态:"
echo "测试服务器连接:"
if curl -s --connect-timeout 5 "http://121.36.87.174/api/knowledge-quiz/daily-question/" > /dev/null; then
    echo "✅ 服务器连接正常"
else
    echo "❌ 服务器连接失败"
fi
echo ""

# 5. 检查Excel上传工具
echo "5. 检查Excel上传工具:"
echo "测试Excel上传工具:"
if [ -f "excel_question_uploader.py" ]; then
    echo "✅ excel_question_uploader.py 存在"
    echo "测试工具帮助信息:"
    python3 excel_question_uploader.py --help | head -5
else
    echo "❌ excel_question_uploader.py 不存在"
fi
echo ""

echo "✅ 诊断完成！"
echo "=================================="
echo "📋 诊断结果:"
echo "   - 如果本地代码正确但云端API返回404，说明云端代码未更新"
echo "   - 如果所有API路径都返回404，说明服务器配置有问题"
echo "   - 如果服务器连接失败，说明网络或服务器有问题"
echo ""
echo "💡 解决方案:"
echo "   1. 在云端服务器上运行: ./update_cloud_server.sh"
echo "   2. 或者手动在云端服务器上:"
echo "      - git pull origin main"
echo "      - docker-compose down"
echo "      - docker-compose up -d --build"
