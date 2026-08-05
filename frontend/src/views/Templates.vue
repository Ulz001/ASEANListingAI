<template>
  <div class="templates-page">
    <div class="page-header">
      <div>
        <h1>模板库</h1>
        <p>选择东南亚热门品类的详情页模板，快速开始你的项目</p>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="filter-bar">
      <button
        v-for="cat in categories"
        :key="cat.value"
        class="filter-btn"
        :class="{ active: activeCategory === cat.value }"
        @click="activeCategory = cat.value"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- 模板网格 -->
    <div v-if="filtered.length" class="template-grid">
      <div
        v-for="tpl in filtered"
        :key="tpl.id"
        class="template-card"
      >
        <div class="template-thumb">
          <div class="thumb-placeholder">
            <span class="category-emoji">{{ getCategoryEmoji(tpl.category) }}</span>
          </div>
        </div>
        <div class="template-info">
          <h3>{{ tpl.name }}</h3>
          <div class="platforms">
            <span v-for="p in tpl.platforms" :key="p" class="platform-tag">{{ PLATFORM_LABELS[p] || p }}</span>
          </div>
          <div class="template-footer">
            <span class="usage-count">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                <polyline points="17 6 23 6 23 12"/>
              </svg>
              {{ (tpl.usage_count || tpl.usageCount || 0).toLocaleString() }} 次使用
            </span>
            <button class="btn btn-primary btn-sm" @click="useTemplate(tpl)">使用此模板 →</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>该分类暂无模板</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '@/api.js'

const router = useRouter()
const activeCategory = ref('all')
const templates = ref([])

const categories = [
  { value: 'all', label: '全部' },
  { value: '3c', label: '3C 电子' },
  { value: 'beauty', label: '美妆护肤' },
  { value: 'fashion', label: '服饰鞋包' },
  { value: 'home', label: '家居生活' },
  { value: 'food', label: '食品饮料' },
]

const PLATFORM_LABELS = {
  shopee: 'Shopee', lazada: 'Lazada', tiktokshop: 'TikTok Shop',
  amazonsg: 'Amazon SG', shopify: 'Shopify',
}

const filtered = computed(() => {
  if (activeCategory.value === 'all') return templates.value
  return templates.value.filter(t => t.category === activeCategory.value)
})

const getCategoryEmoji = (cat) => {
  const map = { '3c': '📱', beauty: '💄', fashion: '👟', home: '🏠', food: '🍜' }
  return map[cat] || '📦'
}

const useTemplate = (tpl) => {
  router.push({ path: '/', query: { template: tpl.id } })
}

onMounted(async () => {
  try {
    const res = await apiClient.getTemplates()
    templates.value = res.data
  } catch (e) {
    // 使用默认数据
    templates.value = [
      { id: '1', name: '无线耳机爆款', category: '3c', platforms: ['shopee','lazada','tiktokshop'], usage_count: 2840, usageCount: 2840 },
      { id: '2', name: '精华液护肤套装', category: 'beauty', platforms: ['shopee','tiktokshop'], usage_count: 1650, usageCount: 1650 },
      { id: '3', name: '运动鞋潮流款', category: 'fashion', platforms: ['lazada','shopify'], usage_count: 920, usageCount: 920 },
    ]
  }
})
</script>

<style scoped>
.templates-page { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.page-header p { font-size: 14px; color: var(--muted-foreground); }

.filter-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 24px 0; }
.filter-btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted-foreground);
  cursor: pointer;
  transition: all 0.15s;
}
.filter-btn:hover { color: var(--foreground); background: var(--muted); }
.filter-btn.active { background: var(--primary); color: var(--primary-foreground); border-color: var(--primary); }

.template-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
.template-card {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--card);
  overflow: hidden;
  transition: all 0.2s;
}
.template-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-2px); }
.template-thumb { aspect-ratio: 4/3; overflow: hidden; }
.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, hsl(252 65% 48% / 0.08), hsl(22 85% 55% / 0.08));
  font-size: 64px;
}
.template-info { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.template-info h3 { font-size: 16px; font-weight: 600; }
.platforms { display: flex; gap: 6px; flex-wrap: wrap; }
.platform-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--muted);
  color: var(--muted-foreground);
}
.template-footer { display: flex; align-items: center; justify-content: space-between; }
.usage-count { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--muted-foreground); }
.empty-state { text-align: center; padding: 60px 0; color: var(--muted-foreground); }
</style>
