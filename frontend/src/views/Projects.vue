<template>
  <div class="projects-page">
    <div class="page-header">
      <div>
        <h1>我的项目</h1>
        <p>管理和查看你生成过的详情页项目</p>
      </div>
    </div>

    <div v-if="projects.length" class="project-grid">
      <div
        v-for="proj in projects"
        :key="proj.id"
        class="project-card"
      >
        <div class="project-thumb">
          <div v-if="proj.thumbnailUrl" class="thumb-img">
            <img :src="proj.thumbnailUrl" :alt="proj.name">
          </div>
          <div v-else class="thumb-placeholder">
            <span>{{ PLATFORM_EMOJI[proj.platform] || '📄' }}</span>
          </div>
        </div>
        <div class="project-info">
          <div class="project-name">{{ proj.name }}</div>
          <div class="project-tags">
            <span class="tag platform">{{ PLATFORM_LABELS[proj.platform] || proj.platform }}</span>
            <span class="tag language">{{ LANGUAGE_LABELS[proj.language] || proj.language }}</span>
          </div>
          <div class="project-date">{{ formatDate(proj.created_at) }}</div>
        </div>
        <div class="project-actions">
          <button class="btn btn-sm" @click="openProject(proj)">打开</button>
          <button class="btn btn-sm btn-danger" @click="confirmDelete(proj.id)">删除</button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>还没有生成过详情页</h3>
      <p>去工作台试试吧，AI 帮你快速生成专业详情页</p>
      <button class="btn btn-primary" @click="$router.push('/')">前往工作台</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from '@/api.js'

const router = useRouter()
const projects = ref([])

const PLATFORM_LABELS = {
  shopee: 'Shopee', lazada: 'Lazada', tiktokshop: 'TikTok Shop',
  amazonsg: 'Amazon SG', shopify: 'Shopify',
}
const PLATFORM_EMOJI = {
  shopee: '🛒', lazada: '🛍️', tiktokshop: '📱', amazonsg: '📦', shopify: '🌐',
}
const LANGUAGE_LABELS = {
  en: 'English', id: 'Bahasa', th: 'Thai', vi: 'Vietnamese', ms: 'Malay', zh: '中文',
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const openProject = (proj) => {
  router.push({ path: '/', query: { project: proj.id } })
}

const confirmDelete = (id) => {
  if (!confirm('确定要删除此项目吗？删除后无法恢复。')) return
  projects.value = projects.value.filter(p => p.id !== id)
  localStorage.setItem('asean_projects', JSON.stringify(projects.value))
  showToast('项目已删除', 'success')
}

onMounted(() => {
  try {
    const stored = localStorage.getItem('asean_projects')
    projects.value = stored ? JSON.parse(stored) : []
  } catch (e) {
    projects.value = []
  }
})
</script>

<style scoped>
.projects-page { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.page-header p { font-size: 14px; color: var(--muted-foreground); }

.project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 24px; }
.project-card {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--card);
  overflow: hidden;
  transition: all 0.2s;
}
.project-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-2px); }
.project-thumb { aspect-ratio: 4/3; overflow: hidden; }
.thumb-img img { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, hsl(252 65% 48% / 0.08), hsl(22 85% 55% / 0.08));
  font-size: 48px;
}
.project-info { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.project-name { font-size: 15px; font-weight: 600; }
.project-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 4px; background: var(--muted); color: var(--muted-foreground); }
.project-date { font-size: 12px; color: var(--muted-foreground); }
.project-actions { display: flex; gap: 8px; padding: 0 16px 16px; }
.btn-danger { color: var(--destructive); border-color: var(--destructive); }
.btn-danger:hover { background: hsl(0 65% 48% / 0.1); }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 64px; margin-bottom: 16px; opacity: 0.3; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--foreground); }
.empty-state p { font-size: 14px; color: var(--muted-foreground); margin-bottom: 24px; }
</style>
