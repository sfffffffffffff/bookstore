//home.vue
<template>
  <div class="home-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <!-- 搜索框 -->
    <div class="search-box">
        <input 
          v-model="searchQuery" 
          placeholder="请输入关键词模糊搜索,加@进行精确搜索" 
          @keyup.enter="handleSearch" 
        />
        <button @click="handleSearch">搜索</button>
      </div>

    <!-- 筛选和查看全部 -->
    <div class="action-bar">
      <div class="filter-buttons">
        <button 
          v-for="category in categories" 
          :key="category.value"
          @click="filterByCategory(category.value)"
          :class="['filter-btn', { active: currentCategory === category.value }]"
        >
          {{ category.label }}
        </button>
      </div>
      <button class="view-all-btn" @click="loadAllBooks">查看全部</button>
    </div>

    <!-- 图书展示区域 -->
    <div v-if="!loading && !error" class="book-grid">
      <div v-for="book in displayBooks" :key="book.isbn" class="book-card">
        <div class="book-image">
          <div class="image-container" :class="{ 'is-loading': !book.imageLoaded }">
            <div v-if="!book.image_url" class="no-image">
              <span class="no-image-icon">📚</span>
              <span class="no-image-text">暂无图片</span>
            </div>
            <img
              v-else
              :src="getBookImageUrl(book.image_url)"
              :alt="book.book_name"
              @error="(e) => handleImageError(e, book.isbn)"
              class="book-cover"
            />
          </div>
        </div>
        <div class="book-info">
          <h3 class="book-title">{{ book.book_name }}</h3>
          <p class="book-author">{{ book.authors }}</p>
          <p class="book-price">￥{{ formatPrice(book.price) }}</p>
          <div class="book-actions">
            <button 
              @click="addToCart(book)" 
              class="add-cart-btn"
              :disabled="loading"
            >
              加入购物车
            </button>
            <button 
              @click="buyNow(book)" 
              class="buy-now-btn"
              :disabled="loading"
            >
              立即购买
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !error && displayBooks.length === 0" class="empty-state">
      暂无图书
    </div>

    <!-- 登录提示弹窗 -->
    <div v-if="showLoginPrompt" class="modal-overlay" @click="showLoginPrompt = false">
      <div class="modal-content" @click.stop>
        <h3>请先登录</h3>
        <p>您需要登录后才能进行购买操作</p>
        <div class="modal-actions">
          <button @click="$router.push('/login')" class="login-btn">去登录</button>
          <button @click="showLoginPrompt = false" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const store = useStore()

// 状态管理
const displayBooks = ref([])
const loading = ref(false)
const error = ref(null)
const showLoginPrompt = ref(false)
const currentCategory = ref('')
const searchQuery = ref('')
// 图片处理相关
const imageLoadErrors = new Set()
const imageCache = new Map()

// 默认图片
const defaultBookImage = new URL('@/assets/default-book.jpg', import.meta.url).href

// 图片 URL 处理函数
const getBookImageUrl = (url) => {
  try {
    if (!url) return null
    if (url.startsWith('http')) return url
    return `http://localhost:8000${url.startsWith('/') ? url : '/' + url}`
  } catch (error) {
    console.error('图片URL处理错误:', error)
    return null
  }
}

// 图片预加载函数
const preloadImage = (url) => {
  if (imageCache.has(url)) return imageCache.get(url)
  
  const promise = new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(url)
    img.onerror = reject
    img.src = url
  })
  
  imageCache.set(url, promise)
  return promise
}

// 图片错误处理函数
const handleImageError = (event, isbn) => {
  try {
    if (!event || !event.target) return
    if (imageLoadErrors.has(isbn)) return
    
    imageLoadErrors.add(isbn)
    const container = event.target.closest('.image-container')
    if (container) {
      container.classList.add('load-error')
    }
    event.target.src = defaultBookImage
  } catch (error) {
    console.error('图片错误处理失败:', error)
  }
}

// 图书分类
const categories = [
  { label: '文史哲', value: 'history' },
  { label: '社科', value: 'social' },
  { label: '生医', value: 'medicicial_book' },
  { label: '艺术', value: 'art' },
  { label: '教材及参考书', value: 'reference' }
]

// 加载初始数据
const loadInitialBooks = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/book/search')
    displayBooks.value = response.data.map(book => ({
      ...book,
      image_url: book.image_url || null,
    }))
    
    // 预加载所有图片
    displayBooks.value.forEach(book => {
      if (book.image_url) {
        preloadImage(getBookImageUrl(book.image_url))
      }
    })
  } catch (err) {
    console.error('加载图书失败:', err)
    error.value = err.response?.data?.detail || '加载图书失败'
  } finally {
    loading.value = false
  }
}

// 搜索图书
const searchBooks = async (query) => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`/book/search?q=${query}`)
    displayBooks.value = response.data.map(book => ({
      ...book,
      image_url: book.image_url || null
    }))
    
    // 预加载搜索结果的图片
    displayBooks.value.forEach(book => {
      if (book.image_url) {
        preloadImage(getBookImageUrl(book.image_url))
      }
    })
  } catch (err) {
    console.error('搜索图书失败:', err)
    error.value = err.response?.data?.detail || '搜索图书失败'
  } finally {
    loading.value = false
  }
}
// 搜索图书
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    // 注意这里的 URL 参数构建
    const response = await axios.get('/book/search', {
      params: {
        q: searchQuery.value
      }
    })
    
    if (response.data && response.data.length > 0) {
      displayBooks.value = response.data
    } else {
      displayBooks.value = []
    }
    
    console.log('搜索结果:', response.data) // 添加调试日志
  } catch (err) {
    console.error('搜索错误:', err)
    error.value = '搜索失败'
  }
}
// 按分类筛选
const filterByCategory = async (category) => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`/book/category/${category}`)
    displayBooks.value = response.data.map(book => ({
      ...book,
      image_url: book.image_url || null
    }))
    currentCategory.value = category
    
    // 预加载分类结果的图片
    displayBooks.value.forEach(book => {
      if (book.image_url) {
        preloadImage(getBookImageUrl(book.image_url))
      }
    })
  } catch (err) {
    console.error('筛选图书失败:', err)
    error.value = err.response?.data?.detail || '筛选图书失败'
  } finally {
    loading.value = false
  }
}

// 加载所有图书
const loadAllBooks = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/book/search')
    displayBooks.value = response.data.map(book => ({
      ...book,
      image_url: book.image_url || null
    }))
    currentCategory.value = ''
    
    // 预加载所有图片
    displayBooks.value.forEach(book => {
      if (book.image_url) {
        preloadImage(getBookImageUrl(book.image_url))
      }
    })
  } catch (err) {
    console.error('加载图书失败:', err)
    error.value = err.response?.data?.detail || '加载图书失败'
  } finally {
    loading.value = false
  }
}

// 加入购物车
const addToCart = async (book) => {
  const token = store.state.token
  if (!token) {
    showLoginPrompt.value = true
    return
  }

  try {
    await axios.post('/cart/', {
      book_isbn: book.isbn,
      quantity: 1
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('已添加到购物车')
  } catch (err) {
    console.error('添加到购物车失败:', err)
    if (err.response?.status === 401) {
      showLoginPrompt.value = true
    } else {
      alert(err.response?.data?.detail || '添加失败，请重试')
    }
  }
}

// 立即购买
const buyNow = async (book) => {
  const token = store.state.token
  if (!token) {
    showLoginPrompt.value = true
    return
  }
  
  try {
    await addToCart(book)
    router.push('/cart')
  } catch (err) {
    console.error('购买失败:', err)
  }
}

// 格式化价格
const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

// 生命周期钩子
onMounted(() => {
  if (route.query.q) {
    searchBooks(route.query.q)
  } else {
    loadInitialBooks()
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 12px;
  border-radius: 4px;
  color: #ff4d4f;
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.view-all-btn {
  padding: 6px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.book-card {
  background-color: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.book-image {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}

.no-image-icon {
  font-size: 24px;
}

.no-image-text {
  font-size: 12px;
}

.is-loading {
  position: relative;
}

.is-loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 25%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite linear;
}

.load-error {
  border: 1px solid #ffccc7;
  background-color: #fff2f0;
}

.book-info {
  padding: 12px;
}

.book-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
 
}

.book-author {
  color: #666;
  font-size: 14px;
  margin: 0 0 8px;
}

.book-price {
  color: #ff4d4f;
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 12px;
}


.add-cart-btn,
.buy-now-btn {
  flex: 1;
  padding: 6px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.add-cart-btn {
  background: #fff;
  border: 1px solid #1890ff;
  color: #1890ff;
}

.buy-now-btn {
  background: #1890ff;
  color: white;
}

.add-cart-btn:hover {
  background: #e6f7ff;
}

.buy-now-btn:hover {
  background: #40a9ff;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
}

.modal-content h3 {
  margin: 0 0 16px;
}

.modal-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.login-btn,
.cancel-btn {
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.login-btn {
  background: #1890ff;
  color: white;
  border: none;
}

.cancel-btn {
  background: white;
  border: 1px solid #d9d9d9;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: 10px;
  }

  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }

  .filter-buttons {
    flex-wrap: wrap;
  }

  .book-title {
    font-size: 14px;
  }

  .book-actions {
    flex-direction: column;
  }

  .modal-content {
    width: 95%;
    padding: 16px;
  }

  .action-bar {
    flex-direction: column;
    gap: 10px;
  }

  .filter-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-btn {
    font-size: 12px;
    padding: 4px 8px;
  }

  .view-all-btn {
    width: 100%;
  }
}
</style>