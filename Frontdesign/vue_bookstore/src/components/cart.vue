<template>
  <div class="cart-container">
    <h2 class="cart-title">我的购物车</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 购物车为空 -->
    <div v-if="!loading && !error && cartItems.length === 0" class="empty-cart">
      <p>购物车是空的,去逛逛吧~</p>
      <button @click="$router.push('/')" class="browse-btn">浏览商品</button>
    </div>

    <!-- 购物车内容 -->
    <template v-if="cartItems.length > 0">
      <table class="cart-table">
        <thead>
          <tr>
            <th class="check-col">
              <input 
                type="checkbox" 
                v-model="allSelected"
                class="select-all"
              />
            </th>
            <th>商品信息</th>
            <th>单价</th>
            <th>数量</th>
            <th>店铺</th>
            <th>小计</th>
            <th>操作</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in cartItems" :key="item.cart_item_id" class="cart-item">
            <td>
              <input 
                type="checkbox" 
                v-model="item.selected"
                class="select-item"
              />
            </td>
            <td class="item-info">
              <img 
                :src="item.book_info.image_url || defaultImg" 
                :alt="item.book_info.book_name"
              />
              <div class="item-details">
                <h4>{{ item.book_info.book_name }}</h4>
                <p class="authors">{{ item.book_info.authors }}</p>
              </div>
            </td>
            <td class="price">¥{{ formatPrice(item.book_info.price) }}</td>
            <td class="quantity">
              <button 
                @click="updateQuantity(item, -1)"
                :disabled="item.quantity <= 1"
                class="quantity-btn"
              >-</button>
              <input 
                type="number" 
                v-model.number="item.quantity" 
                min="1"
                @change="validateQuantity(item)"
                class="quantity-input"
              />
              <button 
                @click="updateQuantity(item, 1)"
                class="quantity-btn"
              >+</button>
            </td>
            <td>{{ item.book_info.store_name }}</td>
            <td class="subtotal">
              ¥{{ formatPrice(item.book_info.price * item.quantity) }}
            </td>
            <td>
              <button 
                @click="removeItem(item.cart_item_id)"
                class="delete-btn"
              >删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 结算栏 -->
      <div class="cart-footer">
        <div class="select-all">
          <input 
            type="checkbox" 
            v-model="allSelected"
          />
          <span>全选</span>
        </div>
        <div class="total-info">
          <span>已选择 {{ selectedCount }} 件商品</span>
          <span class="total-price">总计: ¥{{ formatPrice(totalPrice) }}</span>
        </div>
        <button 
          @click="checkout"
          :disabled="selectedCount === 0"
          class="checkout-btn"
        >
          结算({{ selectedCount }})
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import axios from 'axios'

const store = useStore()
const router = useRouter()
const cartItems = ref([])
const loading = ref(false)
const error = ref(null)

// 默认图片
const defaultImg = new URL('@/assets/default-book.jpg', import.meta.url).href

// 获取购物车内容
const getCartItems = async () => {
  loading.value = true
  error.value = null
  try {
    const token = store.state.token
    if (!token) {
      router.push('/login')
      return
    }

    const response = await axios.get('/cart/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    cartItems.value = response.data.map(item => ({
      ...item,
      selected: false
    }))
  } catch (err) {
    console.error('获取购物车失败:', err)
    error.value = err.response?.data?.detail || '获取购物车失败'
    if (err.response?.status === 401) {
      store.commit('clearUser')
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

// 全选/取消全选
const allSelected = computed({
  get: () => cartItems.value.length > 0 && cartItems.value.every(item => item.selected),
  set: val => cartItems.value.forEach(item => item.selected = val)
})

// 选中商品数量
const selectedCount = computed(() => 
  cartItems.value.filter(item => item.selected).length
)

// 总价
const totalPrice = computed(() => 
  cartItems.value
    .filter(item => item.selected)
    .reduce((sum, item) => sum + item.book_info.price * item.quantity, 0)
)

// 更新商品数量
const updateQuantity = async (item, change) => {
  const newQuantity = item.quantity + change
  if (newQuantity < 1) return

  try {
    const token = store.state.token
    await axios.put(`/cart/${item.cart_item_id}`, {
      quantity: newQuantity
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    item.quantity = newQuantity
  } catch (err) {
    console.error('更新数量失败:', err)
    error.value = err.response?.data?.detail || '更新失败'
  }
}

// 验证数量输入
const validateQuantity = (item) => {
  if (item.quantity < 1) {
    item.quantity = 1
  }
  updateQuantity(item, 0)
}

// 移除商品
const removeItem = async (cartItemId) => {
  if (!confirm('确定要删除这个商品吗？')) return

  try {
    const token = store.state.token
    await axios.delete(`/cart/${cartItemId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    cartItems.value = cartItems.value.filter(item => item.cart_item_id !== cartItemId)
  } catch (err) {
    console.error('删除失败:', err)
    error.value = err.response?.data?.detail || '删除失败'
  }
}

// 结算
const checkout = async () => {
  try {
    const token = store.state.token
    const response = await axios.post('/cart/checkout', {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('结算成功!')
    router.push(`/orders/${response.data.order_ids[0]}`)
  } catch (err) {
    console.error('结算失败:', err)
    error.value = err.response?.data?.detail || '结算失败'
  }
}

// 格式化价格
const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

onMounted(() => {
  getCartItems()
})
</script>

<style scoped>
.cart-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.cart-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.loading-state,
.error-message,
.empty-cart {
  text-align: center;
  padding: 40px;
}

.error-message {
  color: #ff4d4f;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
}

.cart-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th, td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.item-info {
  display: flex;
  gap: 16px;
}

.item-info img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}

.quantity {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #d9d9d9;
  background: white;
  cursor: pointer;
}

.quantity-input {
  width: 50px;
  text-align: center;
  border: 1px solid #d9d9d9;
  padding: 4px;
}

.cart-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}

.checkout-btn {
  background: #1890ff;
  color: white;
  padding: 8px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.checkout-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.delete-btn {
  color: #ff4d4f;
  background: none;
  border: none;
  cursor: pointer;
}

.delete-btn:hover {
  color: #ff7875;
}

@media (max-width: 768px) {
  .cart-container {
    padding: 10px;
  }

  .cart-table {
    font-size: 14px;
  }

  .item-info img {
    width: 60px;
    height: 60px;
  }

  .cart-footer {
    flex-direction: column;
    gap: 10px;
    position: static;
  }
}
</style>