#!/bin/bash

# 快速部署脚本 - 适用于新服务器
# 使用方法: ./quick_deploy.sh

set -e

echo "🚀 Legacy PI Backend 快速部署脚本"
echo "=================================="

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要使用 root 用户运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装必要工具
echo "🔧 安装必要工具..."
sudo apt install -y curl wget git nano htop

# 安装 Docker
echo "🐳 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

# 安装 Docker Compose
echo "🔧 安装 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
else
    echo "✅ Docker Compose 已安装"
fi

# 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 创建项目目录
echo "📁 创建项目目录..."
mkdir -p ~/legacy_pi_backend
cd ~/legacy_pi_backend

# 提示用户上传项目文件
echo ""
echo "📋 下一步操作："
echo "1. 将项目文件上传到 ~/legacy_pi_backend 目录"
echo "2. 配置 env.production 文件"
echo "3. 运行 ./deploy.sh deploy 进行部署"
echo ""
echo "💡 提示："
echo "- 可以使用 git clone 或 scp 上传项目文件"
echo "- 记得修改 env.production 中的配置"
echo "- 需要准备 SSL 证书用于 HTTPS"
echo ""
echo "✅ 服务器环境准备完成！"
echo "请重新登录以使 Docker 组权限生效："
echo "exit"
echo "然后重新 SSH 连接到服务器"
