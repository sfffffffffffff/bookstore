// router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import store from '@/stores/store'

// 路由组件
import Home from '@/components/home.vue'
import Login from '@/components/Login.vue'
import AdminPanel from '@/components/AdminPanel.vue'
import StorePanel from '@/components/StorePanel.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { 
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/store',
    name: 'StorePanel', 
    component: StorePanel,
    meta: {
      requiresAuth: true,
      requiresStore: true
    }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/components/orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/components/cart.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/components/ForgotPassword.vue')
  },
 
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const token = store.state.token
  const userInfo = store.state.userInfo

  // 需要认证的路由
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 需要管理员权限的路由
  if (to.meta.requiresAdmin && userInfo?.type !== 'administrator') {
    next('/')
    return
  }

  // 需要商家权限的路由  
  if (to.meta.requiresStore && userInfo?.type !== 'store') {
    next('/')
    return
  }

  next()
})

export default router