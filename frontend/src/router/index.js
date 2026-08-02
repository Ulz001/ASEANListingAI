import { createRouter, createWebHistory } from 'vue-router'
import Workspace from '@/views/Workspace.vue'
import Templates from '@/views/Templates.vue'
import Projects from '@/views/Projects.vue'

const routes = [
  { path: '/', name: 'Workspace', component: Workspace },
  { path: '/templates', name: 'Templates', component: Templates },
  { path: '/projects', name: 'Projects', component: Projects },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
