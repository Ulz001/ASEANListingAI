#!/bin/bash
# ASEANListingAI Vercel 部署脚本
# 使用方法: bash deploy.sh

set -e

echo "🚀 ASEANListingAI Vercel 部署脚本"
echo "=================================="

# 检查 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI 未安装"
    echo "请运行: npm install -g vercel"
    exit 1
fi

# 检查是否已登录
if ! vercel whoami &> /dev/null; then
    echo "🔐 未登录 Vercel，正在启动登录..."
    vercel login
fi

# 进入前端目录
cd "$(dirname "$0")/frontend"

# 构建前端
echo "📦 正在构建前端..."
npm run build

# 部署到 Vercel
echo "🚀 正在部署到 Vercel..."
vercel deploy --prod --yes

echo ""
echo "✅ 部署完成！"
echo "访问地址将在部署完成后显示"
