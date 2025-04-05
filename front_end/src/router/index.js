import { createRouter, createWebHashHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AdminView from '../views/AdminView.vue'

const routes = [
  { path: '/', component: DashboardView },
  { path: '/admin', component: AdminView }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
