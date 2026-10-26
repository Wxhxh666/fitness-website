import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '@/views/admin/AdminLayout.vue'
import { getToken, getUser } from '@/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { title: '首页' } },
    { path: '/exercises', name: 'exercises', component: () => import('@/views/ExercisesView.vue'), meta: { title: '动作教学' } },
    { path: '/plans', name: 'plans', component: () => import('@/views/PlansView.vue'), meta: { title: '计划制定' } },
    { path: '/plans/:id', name: 'planDetail', component: () => import('@/views/PlanDetailView.vue'), meta: { title: '计划详情' } },
    {
      path: '/workouts',
      name: 'workouts',
      component: () => import('@/views/WorkoutsView.vue'),
      meta: { title: '运动记录', requiresAuth: true },
    },
    { path: '/body-data', name: 'bodyData', component: () => import('@/views/BodyDataView.vue'), meta: { title: '身体概览' } },
    { path: '/body-data/trends', name: 'bodyDataTrends', component: () => import('@/views/BodyDataTrends.vue'), meta: { title: '指标趋势' } },
    { path: '/body-data/diet', name: 'bodyDataDiet', component: () => import('@/views/BodyDataDiet.vue'), meta: { title: 'AI 饮食' } },
    { path: '/body-data/records', name: 'bodyDataRecords', component: () => import('@/views/BodyDataRecords.vue'), meta: { title: '数据管理' } },
    { path: '/contact', name: 'contact', component: () => import('@/views/ContactView.vue'), meta: { title: '联系我们' } },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { title: '登录' } },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { title: '个人中心', requiresAuth: true },
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: () => import('@/views/admin/AdminDashboard.vue'), meta: { title: '控制台' } },
        { path: 'messages', component: () => import('@/views/admin/AdminMessages.vue'), meta: { title: '留言管理' } },
        { path: 'users', component: () => import('@/views/admin/AdminUsers.vue'), meta: { title: '用户管理' } },
        { path: 'exercises', component: () => import('@/views/admin/AdminExercises.vue'), meta: { title: '动作管理' } },
        { path: 'plans', component: () => import('@/views/admin/AdminPlans.vue'), meta: { title: '计划管理' } },
        { path: 'review', component: () => import('@/views/admin/AdminReview.vue'), meta: { title: '申请审核' } },
        { path: 'coaches', component: () => import('@/views/admin/AdminCoaches.vue'), meta: { title: '教练审核' } },
      ],
    },
    {
      path: '/coach',
      component: () => import('@/views/coach/CoachLayout.vue'),
      meta: { requiresAuth: true, requiresCoach: true },
      children: [
        { path: '', redirect: '/coach/dashboard' },
        { path: 'dashboard', component: () => import('@/views/coach/CoachDashboard.vue'), meta: { title: '教练工作台' } },
        { path: 'profile', component: () => import('@/views/coach/CoachProfileEdit.vue'), meta: { title: '教练资料' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

/**
 * 全局路由守卫
 * 注意：这只是体验层的拦截，真正的权限校验永远在后端（require_auth / require_admin）。
 */
router.beforeEach((to) => {
  const loggedIn = !!getToken()

  if (to.meta.requiresAuth && !loggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin) {
    const user = getUser()
    if (!user?.is_admin) {
      return { path: '/' }
    }
  }

  if (to.meta.requiresCoach) {
    const user = getUser()
    // 教练或管理员都可进入工作台；is_coach 以最新登录数据为准
    if (!user?.is_coach && !user?.is_admin) {
      return { path: '/profile', query: { redirect: to.fullPath } }
    }
  }

  // 已登录再访问登录页，直接回首页
  if (to.path === '/login' && loggedIn) {
    return { path: '/' }
  }

  return true
})

router.afterEach((to) => {
  const title = (to.meta.title as string) || ''
  document.title = title ? `${title} · FITLUXE` : 'FITLUXE · 极致塑形·专业健身'
})

export default router
