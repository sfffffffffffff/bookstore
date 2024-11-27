<template>
  <div class="orders-page">
    <!-- 头部区域：标题和搜索框 -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold">我的订单</h2>
      <div class="flex items-center space-x-4">
        <!-- 状态筛选 -->
        <select 
          v-model="statusFilter"
          class="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
        >
          <option value="">全部状态</option>
          <option value="pending">待付款</option>
          <option value="processing">待发货</option>
          <option value="shipped">已发货</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        <!-- 搜索框 -->
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索订单号或书籍信息"
            class="border border-gray-300 rounded-md pl-3 pr-10 py-1.5 text-sm w-64"
            @keyup.enter="handleSearch"
          />
          <button 
            @click="handleSearch"
            class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <i class="fas fa-search"></i>
          </button>
        </div>
      </div>
    </div>
 
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center p-8">
      <span>加载中...</span>
    </div>
 
    <!-- 错误提示 -->
    <div v-if="error" class="bg-red-50 text-red-500 p-4 rounded-md mb-4">
      {{ error }}
    </div>
 
    <!-- 订单列表 -->
    <div v-if="!loading && !error" class="orders-list space-y-4">
      <div v-for="order in filteredOrders" :key="order.order_id" class="bg-white rounded-lg shadow overflow-hidden">
        <!-- 订单头部 -->
        <div class="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
          <div class="text-sm">
            <span class="font-medium">订单号：</span>
            <span>{{ order.order_id }}</span>
            <span class="mx-4">|</span>
            <span class="font-medium">下单时间：</span>
            <span>{{ formatDate(order.order_date) }}</span>
          </div>
          <div>
            <span :class="getStatusClass(order.status)" class="px-3 py-1 rounded-full text-sm">
              {{ getStatusText(order.status) }}
            </span>
          </div>
        </div>
 
        <!-- 订单详情 -->
        <div class="p-6">
          <!-- 书籍信息 -->
          <div v-for="detail in order.details" :key="detail.order_detail_id" class="flex items-center py-3 border-b last:border-b-0">
            <div class="flex-grow flex items-center">
              <div class="flex-none w-16 h-16 bg-gray-200 rounded overflow-hidden mr-4">
                <img :src="detail.image_url || '/default-book.jpg'" :alt="detail.book_isbn" class="w-full h-full object-cover">
              </div>
              <div>
                <h4 class="font-medium text-sm">{{ detail.book_isbn }}</h4>
                <p class="text-gray-500 text-xs mt-1">数量：{{ detail.quantity }}</p>
                <p class="text-gray-500 text-xs mt-1">单价：¥{{ formatPrice(detail.unit_price) }}</p>
              </div>
            </div>
            <div class="flex-none text-right">
              <p class="font-medium">¥{{ formatPrice(detail.unit_price * detail.quantity) }}</p>
            </div>
          </div>
 
          <!-- 订单底部 -->
          <div class="mt-4 flex justify-between items-center">
            <div class="text-sm text-gray-500">
              共 {{ order.details.length }} 件商品
            </div>
            <div>
              <span class="font-medium mr-2">总价：</span>
              <span class="text-lg font-bold text-red-500">¥{{ formatPrice(order.total_price) }}</span>
            </div>
          </div>
 
          <!-- 操作按钮 -->
          <div class="mt-4 flex justify-end space-x-4">
            <button
              v-if="canCancel(order.status)"
              @click="cancelOrder(order.order_id)"
              class="px-4 py-2 border border-red-500 text-red-500 rounded hover:bg-red-50 text-sm"
            >
              取消订单
            </button>
          </div>
        </div>
      </div>
    </div>
 
    <!-- 空状态 -->
    <div v-if="!loading && !error && filteredOrders.length === 0" class="text-center py-12 text-gray-500">
      暂无订单
    </div>
  </div>
 </template>
 
 <script setup>
 import { ref, computed, onMounted } from 'vue'
 import { useStore } from 'vuex'
 import axios from 'axios'
 
 const store = useStore()
 const orders = ref([])
 const loading = ref(true)
 const error = ref(null)
 const searchQuery = ref('')
 const statusFilter = ref('')
 
 // 筛选订单
 const filteredOrders = computed(() => {
  if (!orders.value) return []
  
  let result = orders.value

  if (statusFilter.value) {
    result = result.filter(order => order.status === statusFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(order => 
      order.order_id.toString().includes(query) ||
      (order.details && order.details.some(detail => 
        detail.book_isbn.toLowerCase().includes(query)
      ))
    )
  }

  return result
})

// 获取订单列表
const fetchOrders = async () => {
  try {
    loading.value = true
    const token = store.state.token
    
    if (!token) {
      router.push('/login')
      return
    }
    
    const response = await axios.get('/bookorders/my-orders', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params: {
        skip: 0,
        limit: 10
      }
    })

    orders.value = response.data.map(order => ({
      ...order,
      total_price: parseFloat(order.total_price),
      details: order.details.map(detail => ({
        ...detail,
        unit_price: parseFloat(detail.unit_price)
      }))
    }))
    
    error.value = null
  } catch (err) {
    console.error('获取订单失败:', err)
    error.value = err.response?.data?.detail || '获取订单失败'
  } finally {
    loading.value = false
  }
}


// 取消订单
const cancelOrder = async (orderId) => {
  try {
    const token = store.state.token
    await axios.delete(`/bookorders/${orderId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    await fetchOrders()  // 重新加载订单列表
  } catch (err) {
    console.error('取消订单失败:', err)
    error.value = err.response?.data?.detail || '取消订单失败'
  }
}

onMounted(() => {
  if (store.state.token) {
    fetchOrders()
  }
})
 // 取消订单
 
 // 判断订单是否可以取消
 const canCancel = (status) => {
  return ['pending', 'processing'].includes(status)
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
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
 }
 
 // 获取状态文本
 const getStatusText = (status) => {
  const statusMap = {
    'pending': '待付款',
    'processing': '待发货',
    'shipped': '已发货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}
 
 // 获取状态样式类
 const getStatusClass = (status) => {
  const classMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'processing': 'bg-blue-100 text-blue-800',
    'shipped': 'bg-purple-100 text-purple-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-gray-100 text-gray-800'
  }
  return classMap[status] || ''
 }
 
 // 搜索处理
 const handleSearch = () => {
  fetchOrders()
 }
 
 onMounted(() => {
  fetchOrders()
 })
 </script>
 
 <style scoped>
 .orders-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
 }
 
 @media (max-width: 1024px) {
  .orders-page {
    padding: 1rem;
  }
 }
 </style>