#!/bin/bash

# 启动Django服务器脚本

# 检查环境变量
if [ -z "$ARK_API_KEY" ] || [ "$ARK_API_KEY" = "你的API key" ]; then
    echo "❌ 错误: 请先设置 ARK_API_KEY 环境变量"
    echo ""
    echo "📝 设置方法："
    echo "1. 临时设置: export ARK_API_KEY='你的实际API key'"
    echo "2. 永久设置: echo 'export ARK_API_KEY=\"你的实际API key\"' >> ~/.bashrc && source ~/.bashrc"
    echo "3. 使用配置脚本: ./setup_env.sh"
    echo ""
    echo "🔑 或者创建 .env 文件: echo 'ARK_API_KEY=你的实际API key' > .env"
    echo ""
    exit 1
fi

echo "✅ 环境变量检查通过"
echo "正在启动Django服务器..."

# 激活虚拟环境
source .venv/bin/activate

# 检查Django配置
echo "检查Django配置..."
python manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Django配置检查通过"
    echo "🚀 启动服务器..."
            echo "📱 爬虫API: http://127.0.0.1:8000/api/crawler/"
        echo "🤖 AI解读API: http://127.0.0.1:8000/api/ai/"
        echo "🔍 解读端点: http://127.0.0.1:8000/api/ai/interpret/"
        echo "📊 批量解读: http://127.0.0.1:8000/api/ai/batch/"
        echo "💚 健康检查: http://127.0.0.1:8000/api/ai/health/"
        echo "📝 提示词类型: default, summary, analysis, qa, detailed_explanation, educational, research, key_points"
        echo "📖 管理后台: http://127.0.0.1:8000/admin/"
    echo ""
    echo "按 Ctrl+C 停止服务器"
    echo ""
    
    # 启动Django服务器
    python manage.py runserver 127.0.0.1:8000
else
    echo "❌ Django配置检查失败"
    exit 1
fi
