import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '@/views/admin/AdminLayout.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/exercises', name: 'exercises', component: () => import('@/views/ExercisesView.vue') },
    { path: '/plans', name: 'plans', component: () => import('@/views/PlansView.vue') },
    { path: '/plans/:id', name: 'planDetail', component: () => import('@/views/PlanDetailView.vue') },
    { path: '/body-data', name: 'bodyData', component: () => import('@/views/BodyDataView.vue') },
    { path: '/contact', name: 'contact', component: () => import('@/views/ContactView.vue') },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
        { path: 'messages', component: () => import('@/views/admin/AdminMessages.vue') },
        { path: 'users', component: () => import('@/views/admin/AdminUsers.vue') },
        { path: 'exercises', component: () => import('@/views/admin/AdminExercises.vue') },
        { path: 'plans', component: () => import('@/views/admin/AdminPlans.vue') },
        { path: 'review', component: () => import('@/views/admin/AdminReview.vue') },
      ],
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router

