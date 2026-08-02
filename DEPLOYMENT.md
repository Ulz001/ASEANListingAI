# ASEAN Listing AI - 部署文档

## 开发环境准备

### 1. 安装依赖

**后端 (Python 3.11+)**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**前端 (Node.js 18+)**
```bash
cd frontend
npm install
```

## 配置 API 密钥

编辑 `backend/.env` 文件：
```bash
AGNES_API_KEY=your_api_key_here
AGNES_API_URL=https://api.agnes.ai/v1
```

## 开发模式

### 启动后端（自动重载）
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```
访问 `http://localhost:8000/docs` 查看 Swagger API 文档

### 启动前端
```bash
cd frontend
npm run dev
```
访问 `http://localhost:8080` 查看应用

### 一键启动
```bash
bash scripts/start.sh
```

## 生产模式

### 构建前端
```bash
cd frontend
npm run build
```
构建产物输出到 `frontend/dist/`

### 生产环境启动后端
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker 部署

### 1. 创建 Dockerfile (backend)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 构建并运行
```bash
# 构建
docker build -t asank-backend:latest .

# 运行
docker run -d -p 8000:8000 \
  -e AGNES_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  --name asank-backend asank-backend:latest
```

## 服务器部署指南

### 1. 服务器准备
- Ubuntu 20.04/22.04 LTS
- 2 vCPU, 4GB RAM (最小)
- Nginx (反向代理)

### 2. 使用 PM2 守护后端
```bash
# 安装 PM2
npm install -g pm2

# 进入后端目录
cd backend
source venv/bin/activate

# 启动
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "asank-backend"
pm2 save
```

### 3. Nginx 配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态资源
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
    }
}
```

## 环境变量说明

| 变量 | 必填 | 默认 | 说明 |
|------|------|------|------|
| AGNES_API_KEY | 是 | - | Agnes AI API密钥 |
| AGNES_API_URL | 否 | https://api.agnes.ai/v1 | AI服务端点 |
| PORT | 否 | 8000 | 后端端口 |

## 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取模板
curl http://localhost:8000/api/templates

# 获取模块配置
curl http://localhost:8000/api/modules

# 生成文案
curl -X POST http://localhost:8000/api/copywriting \
  -H "Content-Type: application/json" \
  -d '{
    "product_features": "防水手机壳，50MP摄像头，5000mAh电池",
    "target_audience": "东南亚跨境电商消费者",
    "target_language": "中文"
  }'

# 翻译
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "防水手机壳，50MP摄像头",
    "target_language": "th"
  }'
```

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| API 401错误 | API密钥无效或过期 | 检查 AGNES_API_KEY 配置 |
| 后端无法启动 | 依赖未安装 | `pip install -r requirements.txt` |
| 前端无法访问 | 端口被占用 | 检查 `lsof -i :8080` 并终止冲突进程 |
| CORS错误 | 前端跨域请求 | 检查 CORS 中间件配置 |
| 图片上传失败 | data目录权限 | `chmod -R 755 data/` |

## 安全提示

⚠️ **重要**：
- `.env` 文件中的 API Key 不要提交到 Git 仓库
- 生产环境使用 HTTPS
- 限制 API 访问频率（建议添加速率限制中间件）
- 定期备份 data/ 目录
