# ASEAN Listing AI

AI 驱动的东南亚跨境电商详情页生成工具

## 🚀 技术栈

- **后端：** Python 3.11+ / FastAPI / Uvicorn
- **前端：** Vue 3 / Vite / Axios
- **AI：** SiliconFlow API (deepseek-ai/DeepSeek-V3 / Qwen2.5-72B-Instruct / GLM-4)
- **部署：** Docker 支持

## 📁 功能模块

| 模块 | 功能 |
|------|------|
| **商品图片上传** | 拖拽或点击上传最多 9 张商品图 |
| **生成设置** | 平台（Shopee/Lazada/TikTok/Amazon/Shopify）、比例、语言、风格、版本数 |
| **卖点文案** | AI 智能撰写高转化率卖点文案 + 多语言翻译 |
| **详情页模块** | 12 种模块可选（首屏主视觉、核心卖点、使用场景、品牌故事等） |
| **AI 图片生成** | 按模块逐个生成详情页图片 |
| **模板库** | 按品类选择预设模板快速开始 |
| **项目管理** | 保存历史项目，支持下载 |

## 🔧 快速开始

### 1. 配置 API Key

编辑 `backend/.env`：
```bash
# SiliconFlow API（必需）
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here
# 可选：选择模型
# SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3
# SILICONFLOW_MODEL=Qwen/Qwen2.5-72B-Instruct
# SILICONFLOW_MODEL=THUDM/glm-4-9b-chat

# Agnes AI（可选，用于图片生成）
AGNES_API_KEY=
```

### 2. 安装依赖

```bash
# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 3. 运行

```bash
# 方式一：分别启动
# 终端1 - 后端
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# 终端2 - 前端
cd frontend && npm run dev

# 方式二：一键启动
bash scripts/start.sh
```

### 4. 访问

- 前端：http://localhost:8080
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📋 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/templates | 获取模板列表 |
| GET | /api/modules | 获取详情页模块配置 |
| POST | /api/copywriting | AI 生成卖点文案 |
| POST | /api/translate | 翻译文案 |
| POST | /api/images/upload | 上传商品图片 |
| DELETE | /api/images/{id} | 删除图片 |
| POST | /api/generate | 完整生成流程 |
| POST | /api/generate-images | 生成详情页图片 |
| GET | /api/projects | 项目列表 |
| GET | /api/projects/{id} | 项目详情 |
| DELETE | /api/projects/{id} | 删除项目 |

## 📦 目录结构

```
ASEANListingAI/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 主应用（含所有 API 端点）
│   ├── requirements.txt        # Python 依赖
│   └── .env                    # API 密钥配置
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── main.js             # 入口
│   │   ├── App.vue             # 根组件
│   │   ├── api.js              # API 客户端 + 状态管理
│   │   ├── style.css           # 全局样式
│   │   ├── router/             # 路由配置
│   │   ├── components/         # 公共组件
│   │   └── views/              # 页面视图
│   ├── package.json
│   └── vite.config.js
├── data/                       # 数据持久化目录
│   ├── uploads/               # 上传的图片
│   ├── templates.json         # 模板数据
│   ├── projects.json          # 项目数据
│   └── copies.json            # 文案数据
├── scripts/
│   ├── setup_env.sh           # 环境初始化
│   └── start.sh               # 一键启动
├── .env                        # 环境变量模板
├── README.md
└── DEPLOYMENT.md              # 部署文档
```

## 🌐 支持平台

- Shopee
- Lazada
- TikTok Shop
- Amazon SG
- Shopify

## 🌏 支持语言

- 中文 (zh)
- 英语 (en)
- 泰语 (th)
- 越南语 (vi)
- 印尼语 (id)
- 马来语 (ms)

## 📝 设计风格

- 现代简约 (modern-minimal)
- 活泼多彩 (vibrant-colorful)
- 高端商务 (premium-business)
- 节日促销 (festive-promo)

## 🏗️ Docker 部署

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建并运行
docker build -t asank-backend:latest .
docker run -d -p 8000:8000 \
  -e AGNES_API_KEY=your_key \
  --name asank-backend asank-backend:latest
```

## 📄 详情页模块

| 模块 | 说明 |
|------|------|
| 首屏主视觉 | 主图 + 核心卖点 + 品牌标语 |
| 核心卖点图 | 3-5个核心卖点图文展示 |
| 使用场景图 | 产品在不同场景下的使用展示 |
| 多角度展示 | 产品多角度细节图 |
| 场景氛围图 | 氛围感拉满的生活场景图 |
| 功能细节图 | 产品细节特写 + 功能标注 |
| 品牌故事 | 品牌理念和故事视觉呈现 |
| 规格参数 | 产品规格参数信息表格 |
| 系列展示 | 同系列多SKU展示 |
| 买家好评 | 用户评价和晒图展示 |
| 物流支付 | 本地物流和支付方式说明 |
| 促销信息 | 折扣、满减、赠品等促销模块 |

## 🔑 SiliconFlow 模型推荐

| 模型 | 特点 | 推荐场景 |
|------|------|----------|
| `deepseek-ai/DeepSeek-V3` | 深度思考，推理能力强 | 文案生成、翻译 |
| `Qwen/Qwen2.5-72B-Instruct` | 通义千问，通用能力强 | 多语言任务 |
| `THUDM/glm-4-9b-chat` | 智谱 GLM，中文优秀 | 中文文案优化 |
| `mistralai/Mistral-7B-Instruct` | Mistral，多语言能力 | 东南亚语言翻译 |

获取 API Key：https://cloud.siliconflow.cn/

## 🤝 贡献

欢迎提交 Issue 和 PR！
