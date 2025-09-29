import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/questionnaire',
      name: 'questionnaire',
      component: () => import('../views/QuestionnaireView.vue'),
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
    },
    {
      path: '/report/:id?',
      name: 'report-overview',
      component: () => import('../views/ReportOverview.vue'),
    },
  ],
})

export default router
