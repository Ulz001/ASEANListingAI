"""
ASEAN Listing AI - 东南亚跨境电商详情页 AI 生成工具
FastAPI + Agnes AI
"""

import os
import json
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

# ============ 配置 ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AGNES_API_KEY = os.getenv("AGNES_API_KEY")
AGNES_API_URL = os.getenv("AGNES_API_URL", "https://api.agnes.ai/v1")
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR = DATA_DIR / "uploads"
IMAGES_DIR.mkdir(exist_ok=True)
PROJECTS_FILE = DATA_DIR / "projects.json"
TEMPLATES_FILE = DATA_DIR / "templates.json"
COPIES_FILE = DATA_DIR / "copies.json"

# ============ 模板数据 ============
DEFAULT_TEMPLATES = [
    {
        "id": "tpl_1",
        "name": "无线耳机爆款",
        "category": "3c",
        "platforms": ["shopee", "lazada", "tiktokshop"],
        "thumbnail": "/static/templates/3c-default.jpg",
        "usage_count": 2840,
    },
    {
        "id": "tpl_2",
        "name": "精华液护肤套装",
        "category": "beauty",
        "platforms": ["shopee", "tiktokshop"],
        "thumbnail": "/static/templates/beauty-default.jpg",
        "usage_count": 1650,
    },
    {
        "id": "tpl_3",
        "name": "运动鞋潮流款",
        "category": "fashion",
        "platforms": ["lazada", "shopify"],
        "thumbnail": "/static/templates/fashion-default.jpg",
        "usage_count": 920,
    },
]

DEFAULT_DETAIL_MODULES = [
    {"id": "hero", "name": "首屏主视觉", "description": "主图 + 核心卖点 + 品牌标语"},
    {"id": "selling-points", "name": "核心卖点图", "description": "3-5个核心卖点图文展示"},
    {"id": "usage-scene", "name": "使用场景图", "description": "产品在不同场景下的使用展示"},
    {"id": "multi-angle", "name": "多角度展示", "description": "产品多角度细节图"},
    {"id": "atmosphere", "name": "场景氛围图", "description": "氛围感拉满的生活场景图"},
    {"id": "feature-detail", "name": "功能细节图", "description": "产品细节特写 + 功能标注"},
    {"id": "brand-story", "name": "品牌故事", "description": "品牌理念和故事视觉呈现"},
    {"id": "specs", "name": "规格参数", "description": "产品规格参数信息表格"},
    {"id": "series", "name": "系列展示", "description": "同系列多SKU展示"},
    {"id": "reviews", "name": "买家好评", "description": "用户评价和晒图展示"},
    {"id": "logistics", "name": "物流支付", "description": "本地物流和支付方式说明"},
    {"id": "promotion", "name": "促销信息", "description": "折扣、满减、赠品等促销模块"},
]

# ============ 数据持久化 ============
def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

projects: List[Dict] = load_json(PROJECTS_FILE, [])
copies_store: Dict[str, str] = {}  # project_id -> copywriting

# ============ Pydantic 模型 ============
class GenerationSettings(BaseModel):
    platform: str = "shopee"
    ratio: str = "3:4"
    language: str = "zh"
    style: str = "modern-minimal"
    version_count: int = 3

class ModuleItem(BaseModel):
    id: str
    name: str
    selected: bool = False
    order: int

class GenerateRequest(BaseModel):
    settings: GenerationSettings
    copywriting: str
    modules: List[ModuleItem]
    images: List[Dict]  # [{"id": str, "url": str}]

class CopywritingRequest(BaseModel):
    product_features: str
    target_audience: str = "东南亚跨境电商消费者"
    target_language: str = "中文"
    project_id: Optional[str] = None

class TranslateRequest(BaseModel):
    source_text: str
    target_language: str

class ImageGenerationRequest(BaseModel):
    product_info: str
    selling_points: str
    design_style: str
    module_type: str
    image_ratio: str = "3:4"

class ProjectItem(BaseModel):
    id: str
    name: str
    thumbnail_url: str = ""
    platform: str
    language: str
    created_at: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    api_key_configured: bool
    timestamp: str

# ============ FastAPI 应用 ============
app = FastAPI(
    title="ASEAN Listing AI API",
    version="1.0.0",
    description="AI驱动的东南亚跨境电商详情页生成工具",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（上传的图片等）
app.mount("/static/uploads", StaticFiles(directory=str(IMAGES_DIR)), name="uploads")
app.mount("/static/templates", StaticFiles(directory=str(DATA_DIR / "templates")), name="templates")

# ============ 工具函数 ============
def generate_id() -> str:
    return uuid.uuid4().hex[:12]

def build_copywriting_prompt(product_features: str, target_audience: str, target_language: str) -> str:
    return f"""你是一位资深的跨境电商营销文案专家，擅长撰写高转化率的商品卖点文案，精通多国语言表达习惯和消费心理。

请根据以下商品信息生成专业卖点文案：
商品特点/核心卖点：{product_features}
目标受众：{target_audience}
目标输出语言：{target_language}

文案要求：
1. 语言精准匹配目标语言的母语表达习惯，符合当地消费文化
2. 突出核心卖点，直击用户痛点，激发购买欲望
3. 结构清晰：
   - 主标题（1-2句，简洁有吸引力）
   - 核心卖点（3-5条，每条用短句）
   - 场景化描述（1段）
   - 行动号召（1句）
4. 风格符合电商平台展示规范
5. 不同语言版本适配对应平台的关键词偏好

输出要求：仅输出文案内容，无需额外解释。"""

def build_translate_prompt(source_text: str, target_language: str) -> str:
    lang_names = {
        "en": "English", "id": "Bahasa Indonesia", "th": "Thai",
        "vi": "Vietnamese", "ms": "Malay", "zh-CN": "Chinese (Simplified)",
        "zh-TW": "Chinese (Traditional)",
    }
    lang_name = lang_names.get(target_language, target_language)
    return f"将以下商品卖点文案流畅地翻译成{lang_name}，保持电商文案风格，适合东南亚消费者阅读：\n\n{source_text}"

def build_image_prompt(product_info: str, selling_points: str, design_style: str, module_type: str, image_ratio: str) -> str:
    return f"""你是一位专业的电商详情页设计专家，擅长根据商品特性和品牌风格设计高转化率的详情页视觉图片。

商品信息：{product_info}
核心卖点：{selling_points}
设计风格：{design_style}
模块类型：{module_type}

设计要求：
1. 画面主体突出，清晰展示商品核心卖点
2. 视觉层次分明，重点信息醒目易读
3. 色彩搭配协调，符合品类特性和设计风格
4. 整体质感精致，符合电商平台视觉规范
5. 无多余元素干扰，保持画面简洁专业
6. 图片比例：{image_ratio}"""

async def call_agnes_api(prompt: str, stream: bool = False, **kwargs) -> Any:
    """调用 Agnes AI API"""
    if not AGNES_API_KEY:
        raise HTTPException(status_code=500, detail="API 密钥未配置，请设置 AGNES_API_KEY")

    messages = [
        {"role": "system", "content": "You are a professional e-commerce AI assistant for ASEAN markets."},
        {"role": "user", "content": prompt},
    ]

    payload = {
        "model": "agnes/2.0-flash",
        "messages": messages,
        "stream": stream,
        "temperature": 0.7,
        "top_p": 0.9,
        **kwargs,
    }

    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGNES_API_URL}/chat/completions",
                json=payload,
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI API 调用超时，请重试")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI API 错误: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

# ============ API 端点 ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="ASEAN Listing AI",
        version="1.0.0",
        api_key_configured=bool(AGNES_API_KEY),
        timestamp=datetime.utcnow().isoformat(),
    )

@app.get("/api/templates")
async def get_templates():
    """获取模板列表"""
    return DEFAULT_TEMPLATES

@app.get("/api/templates/categories")
async def get_template_categories():
    """获取模板分类"""
    return [
        {"value": "all", "label": "全部"},
        {"value": "3c", "label": "3C 电子"},
        {"value": "beauty", "label": "美妆护肤"},
        {"value": "fashion", "label": "服饰鞋包"},
        {"value": "home", "label": "家居生活"},
        {"value": "food", "label": "食品饮料"},
    ]

@app.get("/api/modules")
async def get_modules():
    """获取详情页模块配置"""
    return DEFAULT_DETAIL_MODULES

@app.post("/api/copywriting")
async def generate_copywriting(req: CopywritingRequest):
    """AI 生成卖点文案"""
    prompt = build_copywriting_prompt(req.product_features, req.target_audience, req.target_language)
    result = await call_agnes_api(prompt)

    if "choices" in result and len(result["choices"]) > 0:
        copy = result["choices"][0]["message"]["content"].strip()
    else:
        raise HTTPException(status_code=500, detail="AI 返回格式异常")

    # 保存文案
    if req.project_id:
        copies_store[req.project_id] = copy

    return {
        "project_id": req.project_id,
        "copywriting": copy,
        "request_id": generate_id(),
    }

@app.post("/api/translate")
async def translate_copywriting(req: TranslateRequest):
    """翻译卖点文案"""
    prompt = build_translate_prompt(req.source_text, req.target_language)
    result = await call_agnes_api(prompt)

    if "choices" in result and len(result["choices"]) > 0:
        translated = result["choices"][0]["message"]["content"].strip()
    else:
        raise HTTPException(status_code=500, detail="AI 返回格式异常")

    return {
        "source_text": req.source_text,
        "target_language": req.target_language,
        "translated_text": translated,
        "request_id": generate_id(),
    }

@app.post("/api/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """上传商品图片"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")

    file_id = generate_id()
    ext = Path(file.filename).suffix or ".jpg"
    file_path = IMAGES_DIR / f"{file_id}{ext}"

    content = await file.read()
    file_path.write_bytes(content)

    return {
        "id": file_id,
        "url": f"/static/uploads/{file_id}{ext}",
        "filename": file.filename,
        "size": len(content),
    }

@app.delete("/api/images/{image_id}")
async def delete_image(image_id: str):
    """删除图片"""
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        path = IMAGES_DIR / f"{image_id}{ext}"
        if path.exists():
            path.unlink()
            return {"deleted": True, "id": image_id}
    raise HTTPException(status_code=404, detail="图片不存在")

@app.post("/api/generate-images")
async def generate_detail_images(req: GenerateRequest):
    """AI 生成详情页各模块图片"""
    results = []

    for module in req.modules:
        if not module.selected:
            continue

        product_info = f"商品图片已上传 {len(req.images)} 张，平台: {req.settings.platform}"
        prompt = build_image_prompt(
            product_info=product_info,
            selling_points=req.copywriting,
            design_style=req.settings.style,
            module_type=module.name,
            image_ratio=req.settings.ratio,
        )

        try:
            result = await call_agnes_api(prompt)
            # 文生图结果解析
            module_images = []
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                # 尝试从 data URL 或 URL 提取
                if "image_url" in choice:
                    module_images.append(choice["image_url"])
                elif "text" in choice:
                    module_images.append(choice["text"])
                # 如果有 images 字段
                if "images" in choice:
                    module_images.extend(choice["images"])

            results.append({
                "module_id": module.id,
                "module_name": module.name,
                "images": module_images[:1] if module_images else [],
                "status": "success" if module_images else "failed",
            })
        except Exception as e:
            logger.error(f"生成模块 {module.name} 失败: {e}")
            results.append({
                "module_id": module.id,
                "module_name": module.name,
                "images": [],
                "status": "error",
                "error": str(e),
            })

    return {
        "request_id": generate_id(),
        "results": results,
        "total": len(results),
        "success_count": sum(1 for r in results if r["status"] == "success"),
    }

@app.post("/api/generate", response_model=ProjectItem)
async def generate_detail_page(req: GenerateRequest, background_tasks: BackgroundTasks):
    """完整生成流程：保存项目 + 生成图片"""
    project_id = generate_id()

    # 保存项目
    project = ProjectItem(
        id=project_id,
        name=f"详情页项目 {datetime.now().strftime('%Y-%m-%d')}",
        platform=req.settings.platform,
        language=req.settings.language,
        created_at=datetime.utcnow().isoformat(),
    )

    # 保存文案
    if project_id not in copies_store:
        copies_store[project_id] = req.copywriting

    # 保存结果
    projects.append({
        "id": project_id,
        "name": project.name,
        "platform": req.settings.platform,
        "language": req.settings.language,
        "style": req.settings.style,
        "ratio": req.settings.ratio,
        "copywriting": req.copywriting,
        "images": req.images,
        "modules": [m.model_dump() for m in req.modules],
        "settings": req.settings.model_dump(),
        "created_at": project.created_at,
    })
    save_json(PROJECTS_FILE, projects)

    # 异步生成图片
    async def _generate():
        await generate_detail_images(req)

    background_tasks.add_task(_generate)

    return project

@app.get("/api/projects")
async def list_projects():
    """获取项目列表"""
    return projects

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """获取项目详情"""
    for p in projects:
        if p["id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail="项目不存在")

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    global projects
    projects = [p for p in projects if p["id"] != project_id]
    copies_store.pop(project_id, None)
    save_json(PROJECTS_FILE, projects)
    return {"deleted": True, "id": project_id}

@app.get("/api/projects/{project_id}/copywriting")
async def get_project_copywriting(project_id: str):
    """获取项目文案"""
    if project_id in copies_store:
        return {"project_id": project_id, "copywriting": copies_store[project_id]}
    for p in projects:
        if p["id"] == project_id and "copywriting" in p:
            return {"project_id": project_id, "copywriting": p["copywriting"]}
    raise HTTPException(status_code=404, detail="文案不存在")


# ============ 入口 ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
