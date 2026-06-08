import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { SYSTEM_NAME } from '@/utils/constants'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '首页看板', icon: 'Odometer' },
      },
      {
        path: 'records',
        name: 'records',
        component: () => import('@/views/RecordsView.vue'),
        meta: { title: '监控记录', icon: 'VideoCamera' },
      },
      {
        path: 'records/:id',
        name: 'record-detail',
        component: () => import('@/views/RecordDetailView.vue'),
        meta: { title: '监控详情', hideInMenu: true, activeMenu: '/records' },
      },
      {
        path: 'categories',
        name: 'categories',
        component: () => import('@/views/CategoriesView.vue'),
        meta: { title: '违章类别' },
      },
      {
        path: 'review',
        name: 'review',
        component: () => import('@/views/ReviewLogsView.vue'),
        meta: { title: '审核记录' },
      },
      {
        path: 'fence',
        name: 'fence',
        component: () => import('@/views/FenceView.vue'),
        meta: { title: '电子围栏' },
      },
      {
        path: 'recognition-config',
        name: 'recognition-config',
        component: () => import('@/views/RecognitionConfigView.vue'),
        meta: { title: '识别项配置' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: '个人设置', hideInMenu: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  document.title = to.meta?.title
    ? `${to.meta.title} · ${SYSTEM_NAME}`
    : SYSTEM_NAME

  // 已登录访问登录页 -> 跳首页
  if (to.path === '/login' && userStore.isLoggedIn) {
    return { path: '/dashboard' }
  }

  // 未登录访问受保护页 -> 跳登录
  if (!to.meta?.public && !userStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
