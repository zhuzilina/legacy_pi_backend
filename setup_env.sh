#!/bin/bash

# 环境变量设置脚本
# 用于配置AI解读应用所需的API密钥

echo "🔑 AI解读应用环境变量配置"
echo "================================"

# 检查是否已经设置了环境变量
if [ -n "$ARK_API_KEY" ]; then
    echo "✅ 环境变量 ARK_API_KEY 已设置"
    echo "当前值: ${ARK_API_KEY:0:10}..."
else
    echo "❌ 环境变量 ARK_API_KEY 未设置"
fi

echo ""

# 提示用户设置环境变量
echo "📝 请按以下步骤设置环境变量："
echo ""
echo "方法1: 临时设置（当前会话有效）"
echo "export ARK_API_KEY='你的API key'"
echo ""
echo "方法2: 永久设置（推荐）"
echo "echo 'export ARK_API_KEY=\"你的API key\"' >> ~/.bashrc"
echo "source ~/.bashrc"
echo ""
echo "方法3: 创建.env文件（项目级别）"
echo "echo 'ARK_API_KEY=你的API key' > .env"
echo ""

# 检查.env文件
if [ -f ".env" ]; then
    echo "✅ 发现.env文件"
    echo "内容预览:"
    head -5 .env
else
    echo "❌ 未发现.env文件"
    echo "建议创建.env文件来管理环境变量"
fi

echo ""
echo "🔍 验证环境变量设置："
echo "echo \$ARK_API_KEY"
echo ""

# 如果环境变量已设置，显示验证信息
if [ -n "$ARK_API_KEY" ]; then
    echo "✅ 验证成功！环境变量已正确设置"
    echo "现在可以启动AI解读应用了"
    echo ""
    echo "启动命令: ./start_server.sh"
else
    echo "⚠️  请先设置环境变量再启动应用"
fi
