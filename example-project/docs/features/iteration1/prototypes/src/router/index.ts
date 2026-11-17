import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
    { path: '/user', name: 'user-home', component: () => import('@/views/user/Home.vue') },
    { path: '/user/login', name: 'user-login', component: () => import('@/views/user/Login.vue') },
    { path: '/user/search', name: 'user-search', component: () => import('@/views/user/Search.vue') },
    {
      path: '/user/consultant-detail',
      name: 'user-consultant-detail',
      component: () => import('@/views/user/ConsultantDetail.vue'),
    },
    { path: '/user/booking', name: 'user-booking', component: () => import('@/views/user/Booking.vue') },
    { path: '/user/my-orders', name: 'user-my-orders', component: () => import('@/views/user/MyOrders.vue') },
    {
      path: '/user/order-detail',
      name: 'user-order-detail',
      component: () => import('@/views/user/OrderDetail.vue'),
    },
    { path: '/user/profile', name: 'user-profile', component: () => import('@/views/user/Profile.vue') },
    {
      path: '/consultant',
      name: 'consultant-home',
      component: () => import('@/views/consultant/Dashboard.vue'),
    },
    {
      path: '/consultant/application',
      name: 'consultant-application',
      component: () => import('@/views/consultant/Application.vue'),
    },
    {
      path: '/consultant/profile',
      name: 'consultant-profile',
      component: () => import('@/views/consultant/Profile.vue'),
    },
    {
      path: '/consultant/schedule',
      name: 'consultant-schedule',
      component: () => import('@/views/consultant/Schedule.vue'),
    },
    {
      path: '/consultant/orders',
      name: 'consultant-orders',
      component: () => import('@/views/consultant/Orders.vue'),
    },
    {
      path: '/consultant/settlements',
      name: 'consultant-settlements',
      component: () => import('@/views/consultant/Settlements.vue'),
    },
    { path: '/admin', name: 'admin-home', component: () => import('@/views/admin/Dashboard.vue') },
    {
      path: '/admin/applications',
      name: 'admin-applications',
      component: () => import('@/views/admin/Applications.vue'),
    },
    {
      path: '/admin/categories',
      name: 'admin-categories',
      component: () => import('@/views/admin/Categories.vue'),
    },
    { path: '/admin/users', name: 'admin-users', component: () => import('@/views/admin/Users.vue') },
    { path: '/admin/orders', name: 'admin-orders', component: () => import('@/views/admin/Orders.vue') },
    { path: '/admin/reports', name: 'admin-reports', component: () => import('@/views/admin/Reports.vue') },
  ],
})

export default router
