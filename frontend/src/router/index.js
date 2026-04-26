import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../page/LoginView.vue'
import DashboardView from '../page/DashboardView.vue'
import EnvironnementView from '../page/EnvironnementView.vue'
import VerificationView from '../page/VerificationView.vue'
import ServeursView from '../page/ServeursView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/environnement',
      name: 'environnement',
      component: EnvironnementView
    },
    {
      path: '/serveurs',
      name: 'serveurs',
      component: ServeursView
    },
    {
      path: '/verification',
      name: 'verification',
      component: VerificationView
    },
    {
      path: '/',
      redirect: '/login'
    }
  ]
})

export default router
