<template>
  <div class="panel-container">
    <!-- 左侧菜单 -->
    <div class="side-menu">
      <div 
        class="menu-item" 
        :class="{ active: currentView === 'orders' }"
        @click="currentView = 'orders'"
      >
        订单管理
      </div>
      <div 
        class="menu-item" 
        :class="{ active: currentView === 'books' }"
        @click="currentView = 'books'"
      >
        商品管理
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 订单管理视图 -->
      <div v-if="currentView === 'orders'" class="view-container">
        <div class="search-bar">
          <input 
            v-model="orderSearchQuery" 
            placeholder="搜索订单..." 
            @keyup.enter="searchOrders"
          />
          <button @click="searchOrders">搜索</button>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>订单ID</th>
              <th>用户ID</th>
              <th>总价</th>
              <th>状态</th>
              <th>订单日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_id">
              <td>{{ order.order_id }}</td>
              <td>{{ order.user_id }}</td>
              <td>￥{{ formatPrice(order.total_price) }}</td>
              <td>
                <select 
                  v-model="order.status"
                  @change="updateOrderStatus(order.order_id, order.status)"
                >
                  <option value="pending">待处理</option>
                  <option value="shipped">已发货</option>
                  <option value="completed">已完成</option>
                </select>
              </td>
              <td>{{ formatDate(order.order_date) }}</td>
              <td>
                <button @click="viewOrderDetails(order.order_id)">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 商品管理视图 -->
      <div v-if="currentView === 'books'" class="view-container">
        <div class="action-bar">
          <div class="search-bar">
            <input 
              v-model="bookSearchQuery" 
              placeholder="搜索书籍..." 
              @keyup.enter="searchBooks"
            />
            <button @click="searchBooks">搜索</button>
          </div>
          <button @click="showAddBookDialog" class="add-btn">添加新书籍</button>
          <button @click="checkLowInventory" class="warning-btn">查看库存预警</button>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>ISBN</th>
              <th>图片</th>
              <th>书名</th>
              <th>作者</th>
              <th>分类</th>
              <th>库存</th>
              <th>价格</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="book in books" :key="book.isbn">
              <td>{{ book.isbn }}</td>
              <!-- 在表格的图片列中 -->
<!-- 修改图片列的代码 -->
<td class="book-image-cell">
    <div class="image-container" :class="{ 'is-loading': !book.image_url }">
      <img 
        v-if="book.image_url"
        :src="getBookImageUrl(book.image_url)"
        :alt="book.book_name"
        @error="(e) => handleImageError(e, book.isbn)"
        class="book-thumbnail"
      />
      <div v-else class="no-image">
        <span class="no-image-icon">📚</span>
        <span class="no-image-text">暂无图片</span>
      </div>
    </div>
  </td>
              <td>{{ book.book_name }}</td>
              <td>{{ book.authors }}</td>
              <td>{{ book.category }}</td>
              <td :class="{ 'low-inventory': book.inventory < 10 }">
                {{ book.inventory }}
              </td>
              <td>￥{{ formatPrice(book.price) }}</td>
              <td>
                <button @click="editBook(book)">编辑</button>
                <button @click="deleteBook(book.isbn)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加/编辑书籍对话框 -->
    <div v-if="showBookDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>{{ editingBook ? '编辑书籍' : '添加新书籍' }}</h3>
        <form @submit.prevent="saveBook" class="book-form">
          <div class="form-group" v-if="!editingBook">
            <label>ISBN：</label>
            <input v-model="bookForm.isbn" required />
          </div>
          <div class="form-group">
            <label>书名：</label>
            <input v-model="bookForm.book_name" required />
          </div>
          <div class="form-group">
            <label>作者：</label>
            <input v-model="bookForm.authors" required />
          </div>
          <div class="form-group">
            <label>分类：</label>
            <select v-model="bookForm.category" required>
              <option value="history">文史哲</option>
              <option value="social">社科</option>
              <option value="medicicial_book">生医</option>
              <option value="art">艺术</option>
              <option value="reference">教材及参考书</option>
            </select>
          </div>
          <div class="form-group">
            <label>库存：</label>
            <input type="number" v-model.number="bookForm.inventory" required min="0" />
          </div>
          <div class="form-group">
            <label>价格：</label>
            <input type="number" v-model.number="bookForm.price" required min="0" step="0.01" />
          </div>
          <div class="form-group">
            <label>图片：</label>
            <input 
              type="file" 
              accept="image/*"
              @change="handleImageUpload"
              class="file-input"
            />
          </div>
          <!-- 图片预览 -->
          <div v-if="previewUrl || bookForm.image_url" class="image-preview">
            <img :src="previewUrl || getBookImageUrl(bookForm.image_url)" alt="预览" />
          </div>
          <div class="dialog-buttons">
            <button type="submit" class="submit-btn">保存</button>
            <button type="button" @click="closeDialog" class="cancel-btn">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 订单详情对话框 -->
    <div v-if="showOrderDetails" class="dialog-overlay">
      <div class="dialog">
        <h3>订单详情</h3>
        <div v-if="selectedOrder" class="order-details">
          <p><strong>订单ID：</strong>{{ selectedOrder.order_id }}</p>
          <p><strong>用户ID：</strong>{{ selectedOrder.user_id }}</p>
          <p><strong>总价：</strong>￥{{ formatPrice(selectedOrder.total_price) }}</p>
          <p><strong>状态：</strong>{{ selectedOrder.status }}</p>
          <p><strong>订单日期：</strong>{{ formatDate(selectedOrder.order_date) }}</p>
          
          <h4>订单商品</h4>
          <table class="details-table">
            <thead>
              <tr>
                <th>书名</th>
                <th>数量</th>
                <th>单价</th>
                <th>小计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="detail in selectedOrder.details" :key="detail.order_detail_id">
                <td>{{ detail.book_name }}</td>
                <td>{{ detail.quantity }}</td>
                <td>￥{{ formatPrice(detail.unit_price) }}</td>
                <td>￥{{ formatPrice(detail.quantity * detail.unit_price) }}</td>
              </tr>
            </tbody>
          </table>
          
          <button @click="closeOrderDetails" class="close-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

const store = useStore()
const currentView = ref('orders')
const orders = ref([])
const books = ref([])
const orderSearchQuery = ref('')
const bookSearchQuery = ref('')
const showBookDialog = ref(false)
const showOrderDetails = ref(false)
const selectedOrder = ref(null)
const editingBook = ref(null)
const previewUrl = ref('')

// 图片处理相关
const imageLoadErrors = new Set()
const imageCache = new Map()
const defaultBookImage = new URL('@/assets/default-book.jpg', import.meta.url).href

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

// 书籍表单
const bookForm = ref({
  isbn: '',
  book_name: '',
  authors: '',
  category: '',
  inventory: 0,
  price: 0,
  image_url: ''
})

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

// 修改图片错误处理函数
const handleImageError = (event, isbn) => {
  try {
    if (!event || !event.target) return
    if (imageLoadErrors.has(isbn)) return
    
    imageLoadErrors.add(isbn)
    const container = event.target.closest('.image-container')
    if (container) {
      container.classList.add('load-error')
    }
  } catch (error) {
    console.error('图片错误处理失败:', error)
  }
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    alert('只能上传图片文件')
    return
  }
  
  const maxSize = 2 * 1024 * 1024 // 2MB
  if (file.size > maxSize) {
    alert('图片大小不能超过2MB')
    return
  }

  try {
    previewUrl.value = URL.createObjectURL(file)

    const formData = new FormData()
    formData.append('file', file)

    const isbn = editingBook.value ? editingBook.value.isbn : bookForm.value.isbn
    if (!isbn) {
      alert('请先填写ISBN')
      return
    }

    const response = await axios.post(
      `/upload/${isbn}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    bookForm.value.image_url = response.data.url
    await preloadImage(getBookImageUrl(response.data.url))
    
  } catch (error) {
    console.error('上传图片失败:', error)
    alert(error.response?.data?.detail || '上传失败，请重试')
    previewUrl.value = ''
  }
}

// 获取店铺订单
const getStoreOrders = async () => {
  try {
    const response = await axios.get('/bookorders/store-orders')
    orders.value = response.data
  } catch (error) {
    console.error('获取订单失败:', error)
  }
}

// 更新订单状态
const updateOrderStatus = async (orderId, status) => {
  try {
    await axios.put(`/bookorders/${orderId}`, { status })
    alert('订单状态已更新')
  } catch (error) {
    console.error('更新订单状态失败:', error)
  }
}

// 查看订单详情
const viewOrderDetails = async (orderId) => {
  try {
    const response = await axios.get(`/bookorders/${orderId}`)
    selectedOrder.value = response.data
    showOrderDetails.value = true
  } catch (error) {
    console.error('获取订单详情失败:', error)
  }
}

// 获取店铺书籍
const getStoreBooks = async () => {
  try {
    const response = await axios.get(`/book/store/${store.state.userInfo.id}`)
    books.value = response.data
    
    // 预加载图片
    books.value.forEach(book => {
      if (book.image_url) {
        preloadImage(getBookImageUrl(book.image_url))
      }
    })
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  }
}

// 显示添加书籍对话框
const showAddBookDialog = () => {
  editingBook.value = null
  previewUrl.value = ''
  bookForm.value = {
    isbn: '',
    book_name: '',
    authors: '',
    category: '',
    inventory: 0,
    price: 0,
    image_url: ''
  }
  showBookDialog.value = true
}

// 编辑书籍
const editBook = (book) => {
  editingBook.value = book
  previewUrl.value = ''
  bookForm.value = { ...book }
  showBookDialog.value = true
}
const saveBook = async () => {
  try {
    if (editingBook.value) {
      await axios.put(`/book/${editingBook.value.isbn}`, bookForm.value)
    } else {
      // Fix: Send bookForm.value directly instead of spreading individual properties
      await axios.post('/book', {
        isbn: bookForm.value.isbn,
        book_name: bookForm.value.book_name,
        authors: bookForm.value.authors,
        category: bookForm.value.category,
        inventory: bookForm.value.inventory,
        price: bookForm.value.price,
        store_id: store.state.userInfo.id,
        image_url: bookForm.value.image_url
      })
    }
    // Add success handling
    ElMessage.success('保存成功')
    closeDialog()
    fetchBooks() // Refresh book list
  } catch (error) {
    // Add error handling
    ElMessage.error(`保存失败: ${error.response?.data?.detail || error.message}`)
    console.error('Save book error:', error)
  }
}


// 删除书籍
const deleteBook = async (isbn) => {
  if (!confirm('确定要删除这本书吗？')) return
  try {
    await axios.delete(`/book/${isbn}`)
    getStoreBooks()
  } catch (error) {
    console.error('删除书籍失败:', error)
  }
}

// 查看低库存书籍
const checkLowInventory = async () => {
  try {
    const response = await axios.get('/book/inventory/low')
    books.value = response.data
  } catch (error) {
    console.error('获取低库存书籍失败:', error)
  }
}

// 关闭对话框
const closeDialog = () => {
  showBookDialog.value = false
  editingBook.value = null
  previewUrl.value = ''
}

// 关闭订单详情
const closeOrderDetails = () => {
  showOrderDetails.value = false
  selectedOrder.value = null
}

// 格式化价格
const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  getStoreOrders()
  getStoreBooks()
})
</script>
<style scoped>
.panel-container {
  display: flex;
  min-height: calc(100vh - 64px);
}

.side-menu {
  width: 200px;
  background-color: #001529;
  padding: 20px 0;
}

.menu-item {
  padding: 12px 24px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.menu-item:hover {
  background-color: #1890ff;
}

.menu-item.active {
  background-color: #1890ff;
}

.main-content {
  flex: 1;
  padding: 24px;
  background-color: #f0f2f5;
}

.view-container {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  gap: 8px;
  flex: 1;
  max-width: 300px;
}

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background-color: #fafafa;
  font-weight: 500;
}

/* 更新图片相关样式 */
.book-image-cell {
  width: 100px;
  padding: 8px;
}

.image-container {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: white;
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

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.low-inventory {
  color: #ff4d4f;
  font-weight: bold;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog h3 {
  margin: 0 0 20px;
  font-size: 18px;
}

.book-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 16px;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  width: 100%;
}

.file-input {
  border: none !important;
  padding: 0 !important;
}

.image-preview {
  margin-top: 12px;
  text-align: center;
}

.image-preview img {
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
  border-radius: 4px;
}

.dialog-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.submit-btn,
.cancel-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  background-color: #1890ff;
  color: white;
  border: none;
}

.cancel-btn {
  background-color: white;
  border: 1px solid #d9d9d9;
}

.delete-btn {
  color: #ff4d4f;
  margin-left: 8px;
}

.details-table {
  width: 100%;
  margin-top: 16px;
  border-collapse: collapse;
}

.details-table th,
.details-table td {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.close-btn {
  margin-top: 20px;
  width: 100%;
  padding: 8px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-btn {
  background-color: #52c41a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.warning-btn {
  background-color: #faad14;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 8px;
}

/* 按钮通用样式 */
button {
  transition: all 0.3s;
}

button:hover {
  opacity: 0.8;
}

button:active {
  opacity: 0.6;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .panel-container {
    flex-direction: column;
  }

  .side-menu {
    width: 100%;
    padding: 10px 0;
  }

  .main-content {
    padding: 12px;
  }

  .form-group {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .dialog {
    width: 95%;
    padding: 16px;
  }

  .book-thumbnail {
    width: 60px;
    height: 80px;
  }

  .action-bar {
    flex-direction: column;
    gap: 10px;
  }

  .search-bar {
    max-width: none;
  }
}
</style>