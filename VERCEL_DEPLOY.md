# ASEANListingAI Vercel 部署指南

## 方式1：本地部署（推荐）

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录 Vercel
```bash
vercel login
```
按提示完成 GitHub/邮箱登录

### 3. 进入前端目录
```bash
cd ASEANListingAI/frontend
```

### 4. 部署
```bash
# 预览部署
vercel

# 生产部署
vercel deploy --prod
```

### 5. 配置环境变量
```bash
vercel env add AGNES_API_KEY
# 输入你的 Agnes AI API Key
```

---

## 方式2：GitHub 集成部署

### 1. 访问 Vercel
https://vercel.com/new

### 2. 导入项目
- 选择 GitHub 仓库：`Ulz001/ASEANListingAI`
- 框架预设：Vite
- 构建命令：`npm run build`
- 输出目录：`frontend/dist`

### 3. 配置环境变量
在 Vercel Dashboard 中添加：
- `AGNES_API_KEY` = 你的 API Key

### 4. 部署
点击 Deploy，等待完成

---

## 方式3：GitHub Actions 自动部署

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install Dependencies
        run: cd frontend && npm install
        
      - name: Build
        run: cd frontend && npm run build
        
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

---

## 配置说明

### vercel.json
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-server.com/api/$1" },
    { "source": "/static/(.*)", "destination": "https://your-server.com/static/$1" }
  ]
}
```

### 环境变量
| 变量名 | 说明 | 必填 |
|--------|------|------|
| AGNES_API_KEY | Agnes AI API密钥 | 是 |
| AGNES_API_URL | AI API地址 | 否 |

---

## 访问地址

部署完成后，访问：
```
https://your-project.vercel.app
```

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 构建失败 | 检查 Node.js 版本（需要 18+） |
| API 请求失败 | 检查 CORS 配置和后端地址 |
| 环境变量未生效 | 在 Vercel Dashboard 检查配置 |
| 部署超时 | 增加构建时间限制 |

---

**部署完成后，记得更新前端 API 地址指向你的后端服务器！**
