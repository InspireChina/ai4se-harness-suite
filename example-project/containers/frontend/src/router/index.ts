import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/home/HomePage.vue') },
    {
      path: '/user/login',
      name: 'user-login',
      component: () => import('@/views/auth/Login.vue'),
    },
    {
      path: '/user/profile',
      name: 'user-profile',
      component: () => import('@/views/user/Profile.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(to => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return { path: '/user/login' }
  }
})

export default router
