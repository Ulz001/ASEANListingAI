<template>
  <header class="header">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <span class="logo-text">SEA Detail AI</span>
      </router-link>

      <nav class="nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path"
          class="nav-item" :class="{ active: $route.path === item.path }">
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="user-avatar">U</div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = computed(() => [
  { path: '/', label: '工作台', icon: '✏️' },
  { path: '/templates', label: '模板库', icon: '📋' },
  { path: '/projects', label: '我的项目', icon: '📁' },
])
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 32px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, hsl(252 65% 48%), hsl(22 85% 55%));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}
.logo-text {
  font-weight: 600;
  font-size: 16px;
  color: var(--foreground);
  letter-spacing: -0.5px;
}
.nav {
  display: flex;
  gap: 4px;
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--muted-foreground);
  text-decoration: none;
  transition: all 0.15s;
}
.nav-item:hover {
  color: var(--foreground);
  background: var(--muted);
}
.nav-item.active {
  background: var(--accent);
  color: var(--accent-foreground);
}
.nav-icon { font-size: 14px; }
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, hsl(252 65% 48%), hsl(280 65% 48%));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .header-inner { gap: 16px; }
  .nav-item span:not(.nav-icon) { display: none; }
  .nav-item { padding: 8px 12px; }
}
</style>
