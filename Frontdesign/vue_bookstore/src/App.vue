<template>
  <div class="home-container">
    <!-- 顶部背景图 -->
    <div class="banner-image">
      <img src="@/assets/Title.png" alt="Banner" />
    </div>

    <!-- 导航栏 -->
    <div class="nav-bar">
      <!-- 左侧分类导航 -->
      
      

      <!-- 用户操作区 -->
      <div class="user-actions">
        <!-- 显示用户信息 -->
        <span v-if="userInfo" class="user-welcome">
          {{ userInfo.name }}，欢迎您！
        </span>
        
        <!-- 根据用户类型显示不同的管理按钮 -->
        <template v-if="userInfo">
          <!-- 商家用户显示店家面板 -->
          <button 
            v-if="userInfo.type === 'store'" 
            @click="$router.push('/store')" 
            class="manage-btn"
          >
            店家面板
          </button>

          <!-- 管理员用户显示管理员面板 -->
          <button 
            v-if="userInfo.type === 'administrator'" 
            @click="$router.push('/admin')" 
            class="manage-btn"
          >
            管理员面板
          </button>

          

  <button 
    @click="$router.push('/orders')" 
    class="feature-btn"
  >
    我的订单
  </button>
  <button 
    @click="$router.push('/cart')" 
    class="feature-btn"
  >
    购物车
  </button>

        </template>

        <!-- 所有用户都可见的按钮 -->
        <button @click="$router.push('/profile')" class="common-btn">
          我的账户
        </button>

        <!-- 登录/登出按钮 -->
        <button 
          v-if="userInfo" 
          @click="handleLogout" 
          class="logout-btn"
        >
          退出登录
        </button>
        <button 
          v-else 
          @click="$router.push('/login')" 
          class="login-btn"
        >
          登录
        </button>
      </div>
    </div>

    <!-- 路由视图 -->
    <RouterView :key="$route.fullPath"></RouterView>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useStore } from 'vuex'

// 初始化
const router = useRouter()
const route = useRoute()
const store = useStore() // 使用 Vuex Store
const searchQuery = ref('')

// 使用 Vuex 的计算属性来获取全局状态
const userInfo = computed(() => store.state.userInfo)

// 获取用户信息
const getUserInfo = async () => {
  try {
    const token = store.state.token || localStorage.getItem('token')
    if (!token) {
      store.commit('clearUser')
      return
    }

    const response = await axios({
      method: 'get',
      url: '/user/me',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    store.commit('setUser', response.data)
    console.log('用户信息已更新:', response.data)
  } catch (error) {
    console.error('获取用户信息失败:', error)
    if (error.response?.status === 401) {
      store.commit('clearUser')
      if (route.meta.requiresAuth) {
        router.push('/login')
      }
    }
  }
}

onMounted(() => {
  getUserInfo()
})

// 登出处理
const handleLogout = () => {
  // 清除 Vuex 状态
  store.commit('clearUser')
  // 跳转到登录页
  router.push('/login')
}



</script>

<style scoped>
/* 通用样式 */
.home-container {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* Banner样式 */
.banner-image {
  width: 100%;
  height: 25vh;
  min-height: 150px;
  max-height: 300px;
  overflow: hidden;
  position: relative;
}

.banner-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 导航栏样式 */
.nav-bar {
  width: 100%;
  padding: 15px 2vw;
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 15px;
}

/* 导航链接样式 */
.nav-links {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.nav-link {
  color: #333;
  text-decoration: none;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-link:hover {
  color: #1890ff;
  background-color: rgba(24, 144, 255, 0.1);
}

/* 搜索框样式 */
.search-box {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 400px;
  min-width: 200px;
}

.search-box input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-right: 10px;
  transition: all 0.3s;
}

.search-box input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  outline: none;
}

.search-box button {
  padding: 8px 15px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.search-box button:hover {
  background-color: #40a9ff;
}

/* 用户操作区样式 */
.user-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.user-welcome {
  color: #666;
  font-size: 14px;
}

/* 按钮基础样式 */
.user-actions button {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

/* 管理按钮样式 */
.manage-btn {
  background-color: #1890ff !important;
  color: white !important;
  border: none !important;
}

.manage-btn:hover {
  background-color: #40a9ff !important;
}

/* 功能按钮样式 */
.feature-btn {
  background-color: white;
  color: #1890ff;
  border-color: #1890ff;
}

.feature-btn:hover {
  background-color: #e6f7ff;
}

/* 通用按钮样式 */
.common-btn {
  background-color: white;
  color: #666;
}

.common-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
}

/* 登录/登出按钮样式 */
.login-btn {
  background-color: #52c41a;
  color: white;
  border: none;
}

.login-btn:hover {
  background-color: #73d13d;
}

.logout-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
}

.logout-btn:hover {
  background-color: #ff7875;
}

/* 响应式布局 */
@media screen and (max-width: 1200px) {
  .nav-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-links {
    justify-content: center;
  }

  .search-box {
    max-width: none;
    order: -1;
  }

  .user-actions {
    justify-content: center;
  }
}

@media screen and (max-width: 768px) {
  .banner-image {
    height: 20vh;
  }

  .user-actions {
    flex-direction: column;
    width: 100%;
  }

  .user-actions button {
    width: 100%;
  }
}

@media screen and (max-width: 480px) {
  .nav-link {
    padding: 4px 8px;
    font-size: 14px;
  }
}
</style>