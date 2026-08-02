import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// ============ 状态管理 ============
const state = {
  images: [],           // 上传的商品图片
  settings: {           // 生成设置
    platform: 'shopee',
    ratio: '3:4',
    language: 'zh',
    style: 'modern-minimal',
    versionCount: 3,
  },
  copywriting: '',      // 卖点文案
  translatedCopy: {},   // 翻译结果
  modules: [],          // 模块列表
  generatedResults: [], // 生成结果
  currentVersion: 0,    // 当前版本
  isGenerating: false,  // 生成中
  projects: [],         // 项目列表
}

// ============ 常量 ============
export const PLATFORMS = [
  { value: 'shopee', label: 'Shopee', icon: '🛒' },
  { value: 'lazada', label: 'Lazada', icon: '🛍️' },
  { value: 'tiktokshop', label: 'TikTok Shop', icon: '📱' },
  { value: 'amazonsg', label: 'Amazon SG', icon: '📦' },
  { value: 'shopify', label: 'Shopify', icon: '🌐' },
]

export const RATIOS = [
  { value: '1:1', label: '1:1', description: '主图' },
  { value: '3:4', label: '3:4', description: '详情页' },
  { value: '9:16', label: '9:16', description: '短视频' },
  { value: '16:9', label: '16:9', description: '横幅' },
]

export const LANGUAGES = [
  { value: 'en', label: 'English', nativeName: 'English' },
  { value: 'id', label: 'Bahasa Indonesia', nativeName: 'Bahasa Indonesia' },
  { value: 'th', label: 'ภาษาไทย', nativeName: 'ภาษาไทย' },
  { value: 'vi', label: 'Tiếng Việt', nativeName: 'Tiếng Việt' },
  { value: 'ms', label: 'Bahasa Melayu', nativeName: 'Bahasa Melayu' },
  { value: 'zh', label: '中文', nativeName: '中文' },
]

export const STYLES = [
  { value: 'modern-minimal', label: '现代简约', description: '简洁干净，突出产品' },
  { value: 'vibrant-colorful', label: '活泼多彩', description: '色彩丰富，吸引眼球' },
  { value: 'premium-business', label: '高端商务', description: '质感高级，彰显品质' },
  { value: 'festive-promo', label: '节日促销', description: '节日氛围，促进转化' },
]

export const VERSION_COUNTS = [
  { value: 3, label: '3 个版本' },
  { value: 6, label: '6 个版本' },
  { value: 9, label: '9 个版本' },
]

export const DEFAULT_MODULES = [
  { id: 'hero', name: '首屏主视觉', description: '主图 + 核心卖点 + 品牌标语', selected: true, order: 0 },
  { id: 'selling-points', name: '核心卖点图', description: '3-5个核心卖点图文展示', selected: true, order: 1 },
  { id: 'usage-scene', name: '使用场景图', description: '产品在不同场景下的使用展示', selected: true, order: 2 },
  { id: 'multi-angle', name: '多角度展示', description: '产品多角度细节图', selected: true, order: 3 },
  { id: 'atmosphere', name: '场景氛围图', description: '氛围感拉满的生活场景图', selected: true, order: 4 },
  { id: 'feature-detail', name: '功能细节图', description: '产品细节特写 + 功能标注', selected: true, order: 5 },
  { id: 'brand-story', name: '品牌故事', description: '品牌理念和故事视觉呈现', selected: false, order: 6 },
  { id: 'specs', name: '规格参数', description: '产品规格参数信息表格', selected: false, order: 7 },
  { id: 'series', name: '系列展示', description: '同系列多SKU展示', selected: false, order: 8 },
  { id: 'reviews', name: '买家好评', description: '用户评价和晒图展示', selected: false, order: 9 },
  { id: 'logistics', name: '物流支付', description: '本地物流和支付方式说明', selected: false, order: 10 },
  { id: 'promotion', name: '促销信息', description: '折扣、满减、赠品等促销模块', selected: false, order: 11 },
]

// ============ API 调用 ============
export const apiClient = {
  // 健康检查
  health: () => api.get('/health'),

  // 模板
  getTemplates: () => api.get('/api/templates'),
  getTemplateCategories: () => api.get('/api/templates/categories'),

  // 模块
  getModules: () => api.get('/api/modules'),

  // 文案生成
  generateCopywriting: (data) => api.post('/api/copywriting', data),

  // 翻译
  translate: (data) => api.post('/api/translate', data),

  // 图片上传
  uploadImage: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/images/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteImage: (imageId) => api.delete(`/api/images/${imageId}`),

  // 生成详情页
  generate: (data) => api.post('/api/generate', data),
  generateImages: (data) => api.post('/api/generate-images', data),

  // 项目
  listProjects: () => api.get('/api/projects'),
  getProject: (id) => api.get(`/api/projects/${id}`),
  deleteProject: (id) => api.delete(`/api/projects/${id}`),
  getProjectCopywriting: (id) => api.get(`/api/projects/${id}/copywriting`),
}

// ============ 工具函数 ============
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

export function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// ============ Toast 通知 ============
let toastId = 0
export function showToast(message, type = 'info') {
  // 简单的 toast 实现，后续可替换为更好的方案
  const el = document.createElement('div')
  const colors = {
    success: '#16a34a',
    error: '#dc2626',
    warning: '#d97706',
    info: '#6366f1',
  }
  el.style.cssText = `
    position: fixed; top: 80px; right: 20px; z-index: 9999;
    padding: 12px 20px; border-radius: 8px; color: white;
    font-size: 14px; font-weight: 500; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    background: ${colors[type] || colors.info};
    animation: slideIn 0.3s ease;
    max-width: 360px; word-break: break-word;
  `
  el.textContent = message
  document.body.appendChild(el)
  setTimeout(() => {
    el.style.opacity = '0'
    el.style.transition = 'opacity 0.3s'
    setTimeout(() => el.remove(), 300)
  }, 3000)
}

// 添加 CSS 动画
if (!document.getElementById('toast-animations')) {
  const style = document.createElement('style')
  style.id = 'toast-animations'
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `
  document.head.appendChild(style)
}

export default state
