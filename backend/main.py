"""
ASEAN Listing AI - 东南亚跨境电商详情页 AI 生成工具
FastAPI + SiliconFlow API
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Response
import zipfile
import io
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

# ============ 配置 ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SiliconFlow 配置（主）
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_API_URL = os.getenv("SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1")
SILICONFLOW_MODEL = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")

# Agnes AI 配置（备用，用于图片生成）
AGNES_API_KEY = os.getenv("AGNES_API_KEY", "")
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
    {
        "id": "tpl_4",
        "name": "节日促销套装",
        "category": "festival",
        "platforms": ["shopee", "lazada", "tiktokshop"],
        "thumbnail": "/static/templates/festival-default.jpg",
        "usage_count": 450,
    },
    {
        "id": "tpl_5",
        "name": "家居生活必备",
        "category": "home",
        "platforms": ["shopee", "amazonsg"],
        "thumbnail": "/static/templates/home-default.jpg",
        "usage_count": 680,
    },
    {
        "id": "tpl_6",
        "name": "泰国庆特供",
        "category": "festival",
        "platforms": ["shopee", "lazada"],
        "thumbnail": "/static/templates/temasek-default.jpg",
        "usage_count": 320,
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

class AnalyzeImagesRequest(BaseModel):
    images: List[Dict]  # [{"id": str, "url": str}]
    target_language: str = "中文"

class AnalyzeImagesResponse(BaseModel):
    product_name: str
    product_category: str
    selling_points: List[str]
    target_audience: str
    product_features: str
    brand_keywords: List[str]


class CopywritingRequest(BaseModel):
    product_features: str
    target_audience: str = "东南亚跨境电商消费者"
    target_language: str = "中文"
    project_id: Optional[str] = None
    image_analysis: Optional[Dict] = None  # 可选：图片分析结果

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
    siliconflow_configured: bool
    agnes_configured: bool
    model: str
    timestamp: str

# ============ FastAPI 应用 ============
app = FastAPI(
    title="ASEAN Listing AI API",
    version="1.1.0",
    description="AI驱动的东南亚跨境电商详情页生成工具 (SiliconFlow)",
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

def build_image_analysis_prompt(images: List[Dict], target_language: str) -> str:
    """构建图片分析提示词"""
    return f"""你是一位专业的跨境电商商品分析专家，擅长从商品图片中提取关键信息和卖点。

请仔细分析以下商品图片，提取以下信息并返回JSON格式：

{{
  "product_name": "商品名称",
  "product_category": "商品类别（如：电子产品、美妆护肤、服饰鞋包等）",
  "selling_points": ["卖点1", "卖点2", "卖点3", "卖点4", "卖点5"],
  "target_audience": "目标受众描述",
  "product_features": "综合商品特点描述（200字以内）",
  "brand_keywords": ["关键词1", "关键词2", "关键词3"]
}}

分析要求：
1. 从图片中识别商品的外观、颜色、材质、设计特点
2. 推断商品的功能和使用场景
3. 结合跨境电商特点，提取有竞争力的卖点
4. 考虑东南亚消费者的偏好和文化特点
5. 输出语言：{target_language}

仅输出JSON，无需额外解释。"""


async def call_siliconflow_vl_api(prompt: str, image_data: List[Dict] = None) -> Dict[str, Any]:
    """调用 SiliconFlow 视觉语言模型 API
    
    Args:
        prompt: 文本提示词
        image_data: 图片数据列表 [{"content": "base64编码", "mime_type": "image/jpeg"}]
    """
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="SiliconFlow API 密钥未配置")

    # 构建消息内容
    content = [{"type": "text", "text": prompt}]
    
    if image_data:
        for img in image_data:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{img.get('mime_type', 'image/jpeg')};base64,{img['content']}"}
            })

    messages = [{"role": "user", "content": content}]

    payload = {
        "model": "Qwen/Qwen3-VL-32B-Instruct",
        "messages": messages,
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{SILICONFLOW_API_URL}/chat/completions",
                json=payload,
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": data["choices"][0]["message"]["content"]}
                }]
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="视觉分析API调用超时，请重试")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"视觉分析API错误: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视觉分析API调用失败: {str(e)}")


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
6. 图片比例：{image_ratio}

请以JSON格式返回设计描述，包含：
{{
  "theme": "视觉主题描述",
  "colors": ["主色1", "主色2", "辅色"],
  "layout": "布局描述",
  "text_overlay": "建议的文字叠加内容",
  "visual_elements": ["元素1", "元素2", "元素3"],
  "mood": "氛围关键词"
}}
仅输出JSON，无需额外解释。"""

# ============ SiliconFlow API 调用 ============
async def call_siliconflow_api(prompt: str, system_prompt: str = None, response_format: dict = None) -> Dict[str, Any]:
    """调用 SiliconFlow API (OpenAI 兼容格式)"""
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="SiliconFlow API 密钥未配置，请设置 SILICONFLOW_API_KEY")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": SILICONFLOW_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048,
    }

    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{SILICONFLOW_API_URL}/chat/completions",
                json=payload,
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": data["choices"][0]["message"]["content"]}
                }]
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="SiliconFlow API 调用超时，请重试")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"SiliconFlow API 错误: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SiliconFlow API 调用失败: {str(e)}")


# ============ Agnes AI API 调用（备用） ============
async def call_agnes_api(prompt: str, stream: bool = False, **kwargs) -> Any:
    """调用 Agnes AI API（备用，用于图片生成）"""
    if not AGNES_API_KEY:
        raise HTTPException(status_code=500, detail="Agnes API 密钥未配置")

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
        raise HTTPException(status_code=504, detail="Agnes AI API 调用超时，请重试")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agnes AI 错误: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agnes AI 调用失败: {str(e)}")


# ============ API 端点 ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="ASEAN Listing AI",
        version="1.1.0",
        siliconflow_configured=bool(SILICONFLOW_API_KEY),
        agnes_configured=bool(AGNES_API_KEY),
        model=SILICONFLOW_MODEL,
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

@app.post("/api/analyze-images", response_model=AnalyzeImagesResponse)
async def analyze_images(req: AnalyzeImagesRequest):
    """AI 分析商品图片，提取卖点和特点"""
    # 调试日志
    logger.info(f"收到 analyze-images 请求，图片数量: {len(req.images)}")
    for i, img in enumerate(req.images):
        logger.info(f"图片 {i}: url={img.get('url', '')[:100]}...")
    
    # 读取图片数据并转换为 base64
    import base64
    image_data = []
    
    for img in req.images:
        url = img.get("url", "")
        if not url:
            logger.warning(f"图片 {img} 没有 URL")
            continue
        
        try:
            # 如果是 base64 数据 URL
            if url.startswith("data:"):
                # 解析 base64 数据
                # 格式: data:image/jpeg;base64,/9j/4AAQSkZJRg...
                parts = url.split(",")
                if len(parts) == 2:
                    header = parts[0]
                    base64_data = parts[1]
                    # 从 header 提取 MIME 类型
                    if ";" in header:
                        mime_type = header.split(";")[0].replace("data:", "")
                    else:
                        mime_type = "image/jpeg"
                    
                    import base64 as b64
                    img_bytes = b64.b64decode(base64_data)
                    image_data.append({
                        "content": base64.b64encode(img_bytes).decode(),
                        "mime_type": mime_type
                    })
                    logger.info(f"成功解析 base64 图片，大小: {len(img_bytes)} bytes")
                    continue
            
            # 如果是本地路径，读取文件
            if url.startswith("/static/uploads/"):
                # 提取文件ID
                file_id = url.split("/")[-1].split("?")[0]
                # 尝试找到文件
                for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                    file_path = IMAGES_DIR / f"{file_id}{ext}"
                    if file_path.exists():
                        with open(file_path, "rb") as f:
                            img_bytes = f.read()
                        mime_type = f"image/{ext.lstrip('.')}" if ext in [".jpg", ".jpeg"] else f"image/{ext.lstrip('.')}"
                        image_data.append({
                            "content": base64.b64encode(img_bytes).decode(),
                            "mime_type": mime_type
                        })
                        break
            # 如果是 HTTP URL，下载图片
            elif url.startswith("http"):
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    img_bytes = resp.content
                    # 检测 MIME 类型
                    mime_type = resp.headers.get("content-type", "image/jpeg")
                    image_data.append({
                        "content": base64.b64encode(img_bytes).decode(),
                        "mime_type": mime_type
                    })
        except Exception as e:
            logger.warning(f"读取图片失败 {url}: {e}")
            continue
    
    if not image_data:
        raise HTTPException(status_code=400, detail="没有有效的图片数据")
    
    # 构建分析提示词
    prompt = build_image_analysis_prompt(req.images, req.target_language)
    
    # 调用视觉模型
    result = await call_siliconflow_vl_api(prompt, image_data)
    
    # 解析JSON响应
    if "choices" in result and len(result["choices"]) > 0:
        content = result["choices"][0]["message"]["content"].strip()
        # 尝试解析JSON
        try:
            # 移除可能的markdown代码块
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            analysis = json.loads(content)
        except json.JSONDecodeError:
            # 如果解析失败，返回默认结构
            analysis = {
                "product_name": "商品",
                "product_category": "其他",
                "selling_points": [],
                "target_audience": "跨境电商消费者",
                "product_features": content[:500],
                "brand_keywords": []
            }
    else:
        raise HTTPException(status_code=500, detail="AI 返回格式异常")
    
    return AnalyzeImagesResponse(**analysis)


@app.post("/api/copywriting")
async def generate_copywriting(req: CopywritingRequest):
    """AI 生成卖点文案（支持图片分析或手动输入）"""
    # 如果有图片分析结果，优先使用
    if req.image_analysis:
        product_features = req.image_analysis.get("product_features", req.product_features)
        target_audience = req.image_analysis.get("target_audience", req.target_audience)
    else:
        product_features = req.product_features
        target_audience = req.target_audience
    
    prompt = build_copywriting_prompt(product_features, target_audience, req.target_language)
    result = await call_siliconflow_api(prompt)

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
        "model": SILICONFLOW_MODEL,
        "analysis": req.image_analysis,
    }

@app.post("/api/translate")
async def translate_copywriting(req: TranslateRequest):
    """翻译卖点文案（SiliconFlow）"""
    prompt = build_translate_prompt(req.source_text, req.target_language)
    result = await call_siliconflow_api(prompt)

    if "choices" in result and len(result["choices"]) > 0:
        translated = result["choices"][0]["message"]["content"].strip()
    else:
        raise HTTPException(status_code=500, detail="AI 返回格式异常")

    return {
        "source_text": req.source_text,
        "target_language": req.target_language,
        "translated_text": translated,
        "request_id": generate_id(),
        "model": SILICONFLOW_MODEL,
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
    """AI 生成详情页各模块图片（SiliconFlow 生成设计描述 + Agnes 生成图片）"""
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
            # 1. 用 SiliconFlow 生成设计描述
            design_result = await call_siliconflow_api(prompt)
            design_desc = ""
            if "choices" in design_result and len(design_result["choices"]) > 0:
                design_desc = design_result["choices"][0]["message"]["content"].strip()

            # 2. 如果有 Agnes API，尝试生成图片
            image_urls = []
            if AGNES_API_KEY:
                try:
                    # 用设计描述生成图片（简化处理，实际需要根据 Agnes 的图像生成 API 调整）
                    agnes_prompt = f"电商详情页图片，{module.name}模块，{design_desc[:500]}"
                    agnes_result = await call_agnes_api(agnes_prompt)
                    if "choices" in agnes_result and len(agnes_result["choices"]) > 0:
                        choice = agnes_result["choices"][0]
                        if "image_url" in choice:
                            image_urls.append(choice["image_url"])
                        elif "text" in choice:
                            image_urls.append(choice["text"])
                except Exception as e:
                    logger.warning(f"Agnes 图片生成失败: {e}")
            
            # 如果没有生成图片，使用上传的商品图片作为占位符
            if not image_urls and req.images:
                image_urls = [req.images[0]["url"]]  # 使用第一张商品图片

            results.append({
                "module_id": module.id,
                "module_name": module.name,
                "design_description": design_desc[:500],
                "images": image_urls,
                "status": "success",
                "model": SILICONFLOW_MODEL,
                "has_ai_image": len(image_urls) > 0 and bool(AGNES_API_KEY),
            })
        except Exception as e:
            logger.error(f"生成模块 {module.name} 失败: {e}")
            results.append({
                "module_id": module.id,
                "module_name": module.name,
                "design_description": "",
                "images": [],
                "status": "error",
                "error": str(e),
                "model": SILICONFLOW_MODEL,
            })

    return {
        "request_id": generate_id(),
        "results": results,
        "total": len(results),
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "model": SILICONFLOW_MODEL,
    }

@app.post("/api/generate", response_model=ProjectItem)
async def generate_detail_page(req: GenerateRequest, background_tasks: BackgroundTasks):
    """完整生成流程：保存项目 + 生成图片（SiliconFlow）"""
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

@app.get("/api/download/{project_id}")
async def download_project(project_id: str):
    """下载项目图片为ZIP"""
    # 查找项目
    project = None
    for p in projects:
        if p["id"] == project_id:
            project = p
            break
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 创建ZIP文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加项目信息
        project_info = {
            "id": project["id"],
            "name": project.get("name", "项目"),
            "platform": project.get("platform", ""),
            "language": project.get("language", ""),
            "style": project.get("style", ""),
            "created_at": project.get("created_at", ""),
        }
        zip_file.writestr(f"{project_id}/project.json", json.dumps(project_info, ensure_ascii=False, indent=2))
        
        # 添加文案
        if project.get("copywriting"):
            zip_file.writestr(f"{project_id}/copywriting.txt", project["copywriting"])
        
        # 添加图片（如果有URL）
        if project.get("images"):
            for i, img in enumerate(project["images"]):
                img_url = img.get("url", "")
                if img_url and img_url.startswith("/static/uploads/"):
                    # 提取文件ID
                    file_id = Path(img_url).stem
                    img_path = IMAGES_DIR / f"{file_id}.jpg"
                    if img_path.exists():
                        with open(img_path, 'rb') as f:
                            zip_file.writestr(f"{project_id}/images/{i+1}_{img.get('filename', 'image.jpg')}", f.read())
    
    # 返回ZIP文件
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.read(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={project_id}_detail_images.zip"
        }
    )

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

@app.get("/api/models")
async def get_available_models():
    """获取可用的 SiliconFlow 模型列表"""
    return {
        "current_model": SILICONFLOW_MODEL,
        "available_models": [
            {"id": "deepseek-ai/DeepSeek-V3", "name": "DeepSeek-V3", "description": "深度思考，强大推理"},
            {"id": "Qwen/Qwen2.5-72B-Instruct", "name": "Qwen2.5-72B", "description": "通义千问，通用能力强"},
            {"id": "THUDM/glm-4-9b-chat", "name": "GLM-4", "description": "智谱 GLM，中文优秀"},
            {"id": "mistralai/Mistral-7B-Instruct", "name": "Mistral-7B", "description": "Mistral，多语言能力"},
        ]
    }


# ============ 入口 ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
