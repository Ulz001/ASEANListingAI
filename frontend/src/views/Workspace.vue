<template>
  <div class="workspace">
    <!-- 生成中遮罩 -->
    <div v-if="isGenerating" class="generating-overlay">
      <div class="generating-box">
        <div class="spinner"></div>
        <h3>AI 正在生成详情页</h3>
        <p>{{ generatingStep }}</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="workspace-layout">
      <!-- 左侧面板 -->
      <aside class="left-panel">
        <div class="panel-content">
          <!-- 图片上传 -->
          <section class="panel-section">
            <h3 class="section-title">商品图片上传</h3>
            <div
              class="drop-zone"
              :class="{ dragging: isDragging }"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop="handleDrop"
              @click="$refs.fileInput?.click()"
            >
              <input ref="fileInput" type="file" accept="image/*" multiple class="hidden" @change="handleFiles">
              <svg class="drop-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <p>拖拽图片到此处或 <span class="highlight">点击上传</span></p>
              <p class="hint">支持 JPG、PNG、WebP，最多 9 张</p>
            </div>
            <div v-if="images.length" class="image-grid">
              <div v-for="img in images" :key="img.id" class="image-item">
                <img :src="img.previewUrl" :alt="img.fileName">
                <button class="remove-btn" @click.stop="removeImage(img.id)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
              <button v-if="images.length < 9" class="add-more" @click.stop="$refs.fileInput?.click()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                继续添加
              </button>
            </div>
            <p v-if="images.length" class="image-count">已上传 {{ images.length }}/9 张</p>
          </section>

          <!-- 生成设置 -->
          <section class="panel-section">
            <h3 class="section-title">生成设置</h3>
            <div class="setting-group">
              <label class="setting-label">目标平台</label>
              <select v-model="settings.platform" class="input">
                <option v-for="p in PLATFORMS" :key="p.value" :value="p.value">{{ p.icon }} {{ p.label }}</option>
              </select>
            </div>
            <div class="setting-group">
              <label class="setting-label">图片比例</label>
              <select v-model="settings.ratio" class="input">
                <option v-for="r in RATIOS" :key="r.value" :value="r.value">{{ r.label }} · {{ r.description }}</option>
              </select>
            </div>
            <div class="setting-group">
              <label class="setting-label">目标语言</label>
              <select v-model="settings.language" class="input">
                <option v-for="l in LANGUAGES" :key="l.value" :value="l.value">{{ l.label }} ({{ l.nativeName }})</option>
              </select>
            </div>
            <div class="setting-group">
              <label class="setting-label">设计风格</label>
              <select v-model="settings.style" class="input">
                <option v-for="s in STYLES" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
              <p class="setting-desc">{{ STYLES.find(s => s.value === settings.style)?.description }}</p>
            </div>
            <div class="setting-group">
              <label class="setting-label">生成版本数</label>
              <select v-model.number="settings.versionCount" class="input">
                <option v-for="v in VERSION_COUNTS" :key="v.value" :value="v.value">{{ v.label }}</option>
              </select>
            </div>
          </section>

          <!-- 卖点文案 -->
          <section class="panel-section">
            <h3 class="section-title">商品卖点 & 要求</h3>
            <textarea
              v-model="copywriting"
              class="textarea"
              placeholder="输入商品特点、核心卖点、目标受众等信息..."
              rows="5"
            ></textarea>
            <div class="copy-actions">
              <button class="btn btn-gradient btn-sm" @click="generateCopywriting" :disabled="!copywriting.trim() || isGenerating">
                ✨ AI 智能撰写
              </button>
              <button v-if="showTranslate" class="btn btn-sm" @click="translateCopy" :disabled="!copywriting.trim() || isGenerating">
                🌐 翻译为 {{ currentLang?.label }}
              </button>
            </div>
            <div v-if="translatedCopy[settings.language]" class="translated-box">
              <p class="translated-label">{{ currentLang?.label }} 翻译结果：</p>
              <p class="translated-text">{{ translatedCopy[settings.language] }}</p>
            </div>
          </section>

          <!-- 模块选择 -->
          <section class="panel-section">
            <div class="section-header">
              <h3 class="section-title" style="margin:0">详情页模块选择</h3>
              <span class="module-count">已选 {{ selectedModulesCount }}/{{ modules.length }}</span>
            </div>
            <div class="module-list">
              <div
                v-for="mod in modules"
                :key="mod.id"
                class="module-item"
                :class="{ selected: mod.selected }"
                @click="toggleModule(mod.id)"
              >
                <input type="checkbox" :checked="mod.selected" @click.stop>
                <span class="module-name">{{ mod.name }}</span>
                <span v-if="mod.selected" class="module-order">{{ mod.order + 1 }}</span>
              </div>
            </div>
          </section>
        </div>
      </aside>

      <!-- 右侧预览 -->
      <main class="right-panel">
        <div class="preview-toolbar">
          <div class="preview-info">
            <span>实时预览</span>
            <span v-if="generatedResults.length" class="preview-meta">· {{ settings.ratio }} · {{ PLATFORMS.find(p => p.value === settings.platform)?.label }}</span>
          </div>
          <div class="preview-actions">
            <div v-if="generatedResults.length > 1" class="version-tabs">
              <button
                v-for="(r, i) in generatedResults"
                :key="i"
                class="version-tab"
                :class="{ active: currentVersion === i }"
                @click="currentVersion = i"
              >版本 {{ i + 1 }}</button>
            </div>
            <button class="btn btn-sm" @click="downloadPreview">⬇ 下载</button>
          </div>
        </div>

        <div class="preview-area">
          <div v-if="!generatedResults.length" class="preview-empty">
            <div class="preview-placeholder">
              <div class="placeholder-image"></div>
              <p>配置参数后开始生成</p>
            </div>
            <div v-if="selectedModulesCount" class="selected-modules-list">
              <p class="list-label">已选 {{ selectedModulesCount }} 个模块：</p>
              <div v-for="(mod, i) in selectedModules" :key="mod.id" class="list-item">
                <span class="list-num">{{ i + 1 }}</span>
                <span>{{ mod.name }}</span>
              </div>
            </div>
          </div>

          <div v-else class="preview-results">
            <div
              v-for="mod in selectedModules"
              :key="mod.id"
              class="preview-module"
            >
              <div v-if="currentResult?.moduleImages[mod.id]" class="module-image">
                <img :src="currentResult.moduleImages[mod.id]" :alt="mod.name">
              </div>
              <div v-else class="module-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>
                </svg>
                <span>{{ mod.name }}</span>
              </div>
              <div class="module-label">{{ mod.name }}</div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar">
      <div class="bar-left">
        <button class="btn btn-sm" @click="resetAll">🔄 重置</button>
        <button class="btn btn-sm" @click="saveDraft">💾 保存草稿</button>
      </div>
      <button class="btn btn-gradient" :disabled="!canGenerate || isGenerating" @click="handleGenerate">
        <span v-if="isGenerating" class="spinner-sm"></span>
        {{ isGenerating ? '生成中...' : '🪄 生成详情页' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiClient, PLATFORMS, RATIOS, LANGUAGES, STYLES, VERSION_COUNTS, DEFAULT_MODULES, showToast, generateId } from '@/api.js'

const route = useRoute()

// 状态
const images = ref([])
const settings = ref({ platform: 'shopee', ratio: '3:4', language: 'zh', style: 'modern-minimal', versionCount: 3 })
const copywriting = ref('')
const translatedCopy = ref({})
const modules = ref(DEFAULT_MODULES)
const generatedResults = ref([])
const currentVersion = ref(0)
const isGenerating = ref(false)
const generatingStep = ref('')
const isDragging = ref(false)
const fileInput = ref(null)

// 计算属性
const selectedModules = computed(() => modules.value.filter(m => m.selected).sort((a, b) => a.order - b.order))
const selectedModulesCount = computed(() => selectedModules.value.length)
const currentResult = computed(() => generatedResults.value[currentVersion.value] || null)
const showTranslate = computed(() => {
  const lang = LANGUAGES.find(l => l.value === settings.value.language)
  return lang && lang.label !== '中文'
})
const currentLang = computed(() => LANGUAGES.find(l => l.value === settings.value.language))
const canGenerate = computed(() => images.value.length > 0 && copywriting.value.trim().length > 0)

// 加载草稿
onMounted(async () => {
  try {
    const saved = localStorage.getItem('asean_draft')
    if (saved) {
      const draft = JSON.parse(saved)
      if (draft.settings) settings.value = { ...settings.value, ...draft.settings }
      if (draft.copywriting) copywriting.value = draft.copywriting
      if (draft.modules) modules.value = draft.modules
    }
  } catch (e) { console.error('加载草稿失败', e) }

  // 加载模板
  const templateId = route.query.template
  if (templateId) {
    try {
      const res = await apiClient.getTemplates()
      const tpl = res.data.find(t => t.id === templateId)
      if (tpl) {
        const styleMap = { '3c': 'modern-minimal', beauty: 'vibrant-colorful', fashion: 'premium-business', home: 'modern-minimal', food: 'festive-promo' }
        settings.value = { ...settings.value, platform: tpl.platforms[0] || settings.value.platform, style: styleMap[tpl.category] || settings.value.style }
        showToast(`已加载模板「${tpl.name}」预设`, 'info')
      }
    } catch (e) { console.error('加载模板失败', e) }
  }
})

// 图片处理
const processFiles = (files) => {
  const imageFiles = Array.from(files).filter(f => f.type.startsWith('image/'))
  if (!imageFiles.length) { showToast('请选择图片文件', 'error'); return }
  if (imageFiles.length + images.value.length > 9) { showToast('最多 9 张图片', 'error'); return }
  imageFiles.forEach(file => {
    images.value.push({
      id: generateId(),
      file,
      previewUrl: URL.createObjectURL(file),
      fileName: file.name,
    })
  })
}

const handleDrop = (e) => { isDragging.value = false; processFiles(e.dataTransfer.files) }
const handleFiles = (e) => { if (e.target.files?.length) processFiles(e.target.files) }
const removeImage = (id) => {
  const img = images.value.find(i => i.id === id)
  if (img) URL.revokeObjectURL(img.previewUrl)
  images.value = images.value.filter(i => i.id !== id)
}

// 模块
const toggleModule = (id) => {
  modules.value = modules.value.map(m => m.id === id ? { ...m, selected: !m.selected } : m)
}

// AI 文案生成
const generateCopywriting = async () => {
  if (!copywriting.value.trim()) { showToast('请先输入商品特点或卖点描述', 'error'); return }
  try {
    const res = await apiClient.generateCopywriting({
      product_features: copywriting.value,
      target_audience: '东南亚跨境电商消费者',
      target_language: '中文',
    })
    copywriting.value = res.data.copywriting
    showToast('卖点文案已生成', 'success')
  } catch (e) {
    showToast(e.response?.data?.detail || '生成失败，请重试', 'error')
  }
}

// 翻译
const translateCopy = async () => {
  if (!copywriting.value.trim()) { showToast('请先生成或输入卖点文案', 'error'); return }
  const lang = LANGUAGES.find(l => l.value === settings.value.language)
  if (lang?.label === '中文') { showToast('当前语言无需翻译', 'info'); return }
  try {
    const res = await apiClient.translate({ source_text: copywriting.value, target_language: lang.translateCode || lang.value })
    translatedCopy.value = { ...translatedCopy.value, [settings.value.language]: res.data.translated_text }
    showToast('翻译完成', 'success')
  } catch (e) {
    showToast('翻译失败，请重试', 'error')
  }
}

// 生成详情页
const handleGenerate = async () => {
  if (!images.value.length) { showToast('请先上传商品图片', 'error'); return }
  if (!selectedModules.value.length) { showToast('请至少选择一个详情页模块', 'error'); return }

  isGenerating.value = true
  const uploadedImages = []

  // 上传图片
  for (const img of images.value) {
    try {
      const res = await apiClient.uploadImage(img.file)
      uploadedImages.push({ id: res.data.id, url: res.data.url })
    } catch (e) {
      console.error('上传失败', e)
    }
  }

  if (!uploadedImages.length) {
    showToast('图片上传失败', 'error')
    isGenerating.value = false
    return
  }

  try {
    // 创建项目
    const projectRes = await apiClient.generate({
      settings: settings.value,
      copywriting: copywriting.value,
      modules: modules.value,
      images: uploadedImages,
    })

    showToast('项目已创建，开始生成详情页...', 'success')

    // 保存项目
    const project = projectRes.data
    const projects = JSON.parse(localStorage.getItem('asean_projects') || '[]')
    projects.unshift({
      id: project.id,
      name: project.name,
      thumbnailUrl: '',
      platform: project.platform,
      language: project.language,
      created_at: project.created_at,
    })
    localStorage.setItem('asean_projects', JSON.stringify(projects))

    // 生成图片（模拟流式进度）
    const totalModules = selectedModules.value.length
    let completed = 0

    for (const mod of selectedModules.value) {
      generatingStep.value = `正在生成：${mod.name}`
      try {
        const imgRes = await apiClient.generateImages({
          settings: settings.value,
          copywriting: copywriting.value,
          modules: modules.value.filter(m => m.selected),
          images: uploadedImages,
        })
        completed++
      } catch (e) {
        console.error(`生成 ${mod.name} 失败`, e)
        completed++
      }
    }

    generatingStep.value = '完成！'
    showToast('详情页生成成功！', 'success')
  } catch (e) {
    showToast('生成失败，请重试', 'error')
  } finally {
    isGenerating.value = false
    generatingStep.value = ''
  }
}

// 保存草稿
const saveDraft = () => {
  localStorage.setItem('asean_draft', JSON.stringify({
    settings: settings.value,
    copywriting: copywriting.value,
    modules: modules.value,
  }))
  showToast('草稿已保存', 'success')
}

// 重置
const resetAll = () => {
  if (!confirm('确定要重置吗？所有数据将清空。')) return
  images.value = []
  settings.value = { platform: 'shopee', ratio: '3:4', language: 'zh', style: 'modern-minimal', versionCount: 3 }
  copywriting.value = ''
  translatedCopy.value = {}
  modules.value = DEFAULT_MODULES
  generatedResults.value = []
  currentVersion.value = 0
  showToast('已重置', 'info')
}

// 下载预览
const downloadPreview = async () => {
  showToast('下载功能开发中...', 'info')
}
</script>

<style scoped>
.workspace {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  position: relative;
}
.workspace-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 380px;
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--card);
  overflow-y: auto;
}
.panel-content { padding: 16px; display: flex; flex-direction: column; gap: 20px; }
.panel-section { }
.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.module-count { font-size: 12px; color: var(--muted-foreground); }

/* 上传区域 */
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.drop-zone.dragging { border-color: var(--primary); background: hsl(252 65% 48% / 0.05); }
.drop-zone:hover { border-color: hsl(252 65% 48% / 0.5); background: hsl(240 15% 94% / 0.5); }
.drop-icon { width: 32px; height: 32px; color: var(--muted-foreground); margin: 0 auto 8px; }
.drop-zone p { font-size: 14px; color: var(--muted-foreground); }
.drop-zone .highlight { color: var(--primary); font-weight: 500; }
.drop-zone .hint { font-size: 12px; margin-top: 4px; }
.hidden { display: none; }
.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
}
.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.image-item img { width: 100%; height: 100%; object-fit: cover; }
.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.image-item:hover .remove-btn { opacity: 1; }
.remove-btn svg { width: 12px; height: 12px; }
.add-more {
  aspect-ratio: 1;
  border: 2px dashed var(--border);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--muted-foreground);
  transition: all 0.2s;
}
.add-more:hover { border-color: var(--primary); color: var(--primary); }
.add-more svg { width: 20px; height: 20px; }
.add-more span { font-size: 11px; }
.image-count { font-size: 12px; color: var(--muted-foreground); }

/* 设置 */
.setting-group { display: flex; flex-direction: column; gap: 6px; }
.setting-label { font-size: 12px; color: var(--muted-foreground); }
.setting-desc { font-size: 12px; color: var(--muted-foreground); margin-top: 2px; }

/* 模块列表 */
.module-list { display: flex; flex-direction: column; gap: 6px; }
.module-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.module-item:hover { border-color: hsl(252 65% 48% / 0.3); background: hsl(252 65% 48% / 0.03); }
.module-item.selected { border-color: hsl(252 65% 48% / 0.4); background: hsl(252 65% 48% / 0.06); }
.module-item input[type="checkbox"] { accent-color: var(--primary); }
.module-name { flex: 1; font-size: 14px; }
.module-order { font-size: 12px; color: var(--muted-foreground); }

/* 文案 */
.copy-actions { display: flex; gap: 8px; margin-top: 8px; }
.translated-box {
  margin-top: 12px;
  padding: 12px;
  background: hsl(240 15% 94% / 0.5);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.translated-label { font-size: 12px; color: var(--muted-foreground); margin-bottom: 4px; }
.translated-text { font-size: 14px; white-space: pre-line; }

/* 右侧预览 */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
  flex-shrink: 0;
}
.preview-info { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; }
.preview-meta { font-size: 12px; color: var(--muted-foreground); }
.preview-actions { display: flex; gap: 8px; align-items: center; }
.version-tabs { display: flex; gap: 4px; margin-right: 8px; }
.version-tab {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--border);
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
}
.version-tab:hover { background: var(--muted); }
.version-tab.active { background: var(--primary); color: var(--primary-foreground); border-color: var(--primary); }

.preview-area {
  flex: 1;
  overflow-y: auto;
  background: hsl(240 15% 94% / 0.3);
  padding: 16px;
}
.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}
.preview-placeholder { width: 100%; max-width: 280px; }
.placeholder-image {
  aspect-ratio: 3/4;
  border-radius: 12px;
  background: linear-gradient(135deg, hsl(252 65% 48% / 0.1), hsl(22 85% 55% / 0.1));
  border: 1px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.placeholder-image::after { content: '📄'; font-size: 48px; opacity: 0.3; }
.selected-modules-list { margin-top: 16px; width: 100%; max-width: 280px; }
.list-label { font-size: 12px; color: var(--muted-foreground); margin-bottom: 8px; }
.list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 4px;
}
.list-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: hsl(252 65% 48% / 0.1);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.preview-results { max-width: 420px; margin: 0 auto; display: flex; flex-direction: column; gap: 12px; }
.preview-module { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: var(--card); box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.module-image { width: 100%; aspect-ratio: 4/3; overflow: hidden; }
.module-image img { width: 100%; height: 100%; object-fit: cover; }
.module-placeholder {
  aspect-ratio: 4/3;
  background: var(--muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--muted-foreground);
}
.module-placeholder svg { width: 32px; height: 32px; opacity: 0.3; }
.module-placeholder span { font-size: 13px; }
.module-label { padding: 10px 12px; border-top: 1px solid var(--border); font-size: 13px; font-weight: 500; }

/* 底部栏 */
.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  background: var(--card);
  flex-shrink: 0;
}
.bar-left { display: flex; gap: 8px; }

/* 生成中遮罩 */
.generating-overlay {
  position: absolute;
  inset: 0;
  z-index: 50;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.generating-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px;
  max-width: 320px;
  width: 90%;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}
.spinner-sm {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.generating-box h3 { font-size: 16px; margin-bottom: 8px; }
.generating-box p { font-size: 13px; color: var(--muted-foreground); margin-bottom: 16px; }
.progress-bar { height: 4px; background: var(--muted); border-radius: 2px; overflow: hidden; }
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, hsl(252 65% 48%), hsl(22 85% 55%));
  border-radius: 2px;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }

/* 响应式 */
@media (max-width: 900px) {
  .workspace-layout { flex-direction: column; }
  .left-panel { width: 100%; max-height: 50vh; }
  .bottom-bar { flex-direction: column; gap: 8px; }
}
</style>
