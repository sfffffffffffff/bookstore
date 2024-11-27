<template>
  <div class="panel-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 左侧菜单 -->
    <div class="side-menu">
      <div 
        v-for="menu in menus" 
        :key="menu.value"
        class="menu-item"
        :class="{ active: currentView === menu.value }"
        @click="currentView = menu.value"
      >
        {{ menu.label }}
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 用户管理视图 -->
      <div v-if="currentView === 'users'" class="view-container">
    <div class="action-bar">
      
      <button @click="createUser" class="primary-btn">新增用户</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>邮箱</th>
          <th>类型</th>
          <th>地址</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ getUserTypeText(user.type) }}</td>
          <td>{{ user.address }}</td>
          <td>
            <button 
              @click="editUser(user)"
              class="primary-btn"
            >
              编辑
            </button>
            <button 
              @click="handleDeleteUser(user.id)"
              class="delete-btn"
            >
              删除
            </button>
          </td>
        </tr>
        <tr v-if="users.length === 0">
          <td colspan="6" class="text-center">暂无数据</td>
        </tr>
      </tbody>
    </table>

    <!-- 分页器 -->
    <div class="pagination">
      <button 
        :disabled="userPage === 1"
        @click="changePage('users', userPage - 1)"
      >
        上一页
      </button>
      <span>第 {{ userPage }} 页</span>
      <button @click="changePage('users', userPage + 1)">下一页</button>
    </div>
  </div>
<!-- 新增/编辑用户对话框 -->
<div v-if="showEditUserDialog" class="dialog-overlay">
    <div class="dialog">
      <h3>{{ editingUser.id ? '编辑用户' : '新增用户' }}</h3>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <form @submit.prevent="saveUser" class="edit-form">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model.trim="editingUser.name"
            type="text"
            class="form-control"
            placeholder="请输入用户名"
          />
        </div>

        <!-- 只在创建新用户时显示邮箱输入框 -->
        <div v-if="!editingUser.id" class="form-group">
          <label>邮箱 <span class="required">*</span></label>
          <input 
            v-model.trim="editingUser.email"
            type="email"
            class="form-control"
            placeholder="请输入邮箱"
            required
          />
        </div>
        <!-- 在编辑模式下只显示邮箱而不允许修改 -->
        <div v-else class="form-group">
          <label>邮箱</label>
          <input 
            :value="editingUser.email"
            type="email"
            class="form-control"
            disabled
          />
        </div>

        <div class="form-group">
          <label>用户类型</label>
          <select 
            v-model="editingUser.type"
            class="form-control"
          >
            <option value="">请选择用户类型</option>
            <option value="buyer">买家</option>
            <option value="store">商家</option>
            <option value="administrator">管理员</option>
          </select>
        </div>

        <div class="form-group">
          <label>地址</label>
          <input 
            v-model.trim="editingUser.address"
            type="text"
            class="form-control"
            placeholder="请输入地址"
          />
        </div>

        <div class="form-group">
          <label>
            {{ editingUser.id ? '新密码' : '密码' }}
            <span class="required" v-if="!editingUser.id">*</span>
            <span class="optional" v-else>(可选)</span>
          </label>
          <input 
            v-model.trim="editingUser.password"
            type="password"
            class="form-control"
            :placeholder="editingUser.id ? '不修改请留空' : '请输入密码'"
            :required="!editingUser.id"
          />
        </div>

        <div class="dialog-footer">
          <button 
            type="submit" 
            class="primary-btn" 
            :disabled="loading"
          >
            {{ loading ? '保存中...' : '保存' }}
          </button>
          <button 
            type="button" 
            @click="closeEditUserDialog" 
            class="cancel-btn"
            :disabled="loading"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>

      <!-- 订单管理视图 -->
      <div v-if="currentView === 'orders'" class="view-container">
       
     

        <table class="data-table">
          <thead>
            <tr>
              <th>订单ID</th>
              <th>买家信息</th>
              <th>商家信息</th>
              <th>总价</th>
              <th>状态</th>
              <th>订单日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_id">
              <td>{{ order.order_id }}</td>
              <td>
                <div>买家: {{ order.buyer_name }}</div>
                <div class="address-text">地址: {{ order.shipping_address }}</div>
              </td>
              <td>
                <div>商家: {{ order.store_name }}</div>
                <div class="address-text">地址: {{ order.store_address }}</div>
              </td>
              <td>￥{{ formatPrice(order.total_price) }}</td>
              <td>
                <span :class="getOrderStatusClass(order.status)">
                  {{ getOrderStatusText(order.status) }}
                </span>
              </td>
              <td>{{ formatDate(order.order_date) }}</td>
              <td>
                <button @click="viewOrderDetails(order)" class="info-btn">查看</button>
                <button @click="deleteOrder(order.order_id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 分页器 -->
        <div class="pagination">
          <button 
            :disabled="orderPage === 1"
            @click="changePage('orders', orderPage - 1)"
          >
            上一页
          </button>
          <span>第 {{ orderPage }} 页</span>
          <button @click="changePage('orders', orderPage + 1)">下一页</button>
        </div>
      </div>

      <!-- 商品管理视图 -->
      <div v-if="currentView === 'books'" class="view-container">
        <div class="action-bar">
          
          <button @click="checkLowInventory" class="warning-btn">库存预警</button>
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
              <th>商家</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="book in books" :key="book.isbn">
              <td>{{ book.isbn }}</td>
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
              <td>{{ getBookCategoryText(book.category) }}</td>
              <td :class="{ 'low-inventory': book.inventory < 10 }">
                {{ book.inventory }}
              </td>
              <td>￥{{ formatPrice(book.price) }}</td>
              <td>{{ book.store_name || book.store_id }}</td>
              <td>
                <button @click="editBook(book)" class="primary-btn">编辑</button>
                <button @click="deleteBook(book.isbn)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 分页器 -->
        <div class="pagination">
          <button 
            :disabled="bookPage === 1"
            @click="changePage('books', bookPage - 1)"
          >
            上一页
          </button>
          <span>第 {{ bookPage }} 页</span>
          <button @click="changePage('books', bookPage + 1)">下一页</button>
        </div>
      </div>
    </div>
  </div>
    <!-- 用户编辑对话框 -->
<!-- 编辑用户对话框 -->
<div v-if="showEditUserDialog" class="dialog-overlay">
    <div class="dialog">
      <h3>编辑用户</h3>
      <!-- 错误提示 -->
      <div v-if="error" class="form-error">
        {{ error }}
      </div>
      <!-- 编辑表单 -->
      <form @submit.prevent="saveUser" class="edit-form">
        <div class="form-group">
          <label>用户名:</label>
          <input 
            v-model.trim="editingUser.name"
            type="text"
            required
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label>邮箱:</label>
          <input 
            v-model.trim="editingUser.email"
            type="email"
            required
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label>用户类型:</label>
          <select 
            v-model="editingUser.type"
            required
            class="form-control"
          >
            <option value="">请选择用户类型</option>
            <option value="buyer">买家</option>
            <option value="store">商家</option>
            <option value="administrator">管理员</option>
          </select>
        </div>
        <div class="form-group">
          <label>地址:</label>
          <input 
            v-model.trim="editingUser.address"
            type="text"
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label>新密码: <span class="optional">(可选)</span></label>
          <input 
            v-model.trim="editingUser.password"
            type="password"
            class="form-control"
            placeholder="不修改请留空"
            minlength="6"
          />
        </div>
        <div class="dialog-footer">
          <button type="submit" class="primary-btn" :disabled="loading">
            {{ loading ? '保存中...' : '保存' }}
          </button>
          <button 
            type="button" 
            @click="closeEditUserDialog" 
            class="cancel-btn"
            :disabled="loading"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
    <!-- 书籍编辑对话框 -->
    <div v-if="showEditBookDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>编辑书籍</h3>
        <form @submit.prevent="saveBook">
          <div class="form-group">
            <label>ISBN:</label>
            <input v-model="editingBook.isbn" disabled />
          </div>
          <div class="form-group">
            <label>书名:</label>
            <input v-model="editingBook.book_name" required />
          </div>
          <div class="form-group">
            <label>作者:</label>
            <input v-model="editingBook.authors" required />
          </div>
          <div class="form-group">
            <label>分类:</label>
            <select v-model="editingBook.category" required>
              <option value="history">文史哲</option>
              <option value="social">社科</option>
              <option value="medicicial_book">生医</option>
              <option value="art">艺术</option>
              <option value="reference">教材及参考书</option>
            </select>
          </div>
          <div class="form-group">
            <label>库存:</label>
            <input 
              type="number" 
              v-model.number="editingBook.inventory" 
              required 
              min="0"
            />
          </div>
          <div class="form-group">
            <label>价格:</label>
            <input 
              type="number" 
              v-model.number="editingBook.price" 
              required 
              min="0" 
              step="0.01"
            />
          </div>
          <div class="form-group">
            <label>图片:</label>
            <input 
              type="file" 
              accept="image/*"
              @change="handleImageUpload"
              class="file-input"
            />
            <div v-if="editingBook.image_url" class="preview-image">
              <img :src="getBookImageUrl(editingBook.image_url)" alt="当前图片" />
            </div>
          </div>
          <div class="dialog-footer">
            <button type="submit" class="primary-btn">保存</button>
            <button type="button" @click="closeEditBookDialog" class="cancel-btn">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 订单详情对话框 -->
    <div v-if="showOrderDetails" class="dialog-overlay">
      <div class="dialog">
        <h3>订单详情</h3>
        <div v-if="selectedOrder" class="order-details">
          <div class="order-info">
            <p><strong>订单ID：</strong>{{ selectedOrder.order_id }}</p>
            <p><strong>买家：</strong>{{ selectedOrder.buyer_name }} (ID: {{ selectedOrder.user_id }})</p>
            <p><strong>收货地址：</strong>{{ selectedOrder.shipping_address }}</p>
            <p><strong>商家：</strong>{{ selectedOrder.store_name }} (ID: {{ selectedOrder.store_id }})</p>
            <p><strong>发货地址：</strong>{{ selectedOrder.store_address }}</p>
            <p><strong>总价：</strong>￥{{ formatPrice(selectedOrder.total_price) }}</p>
            <p><strong>状态：</strong>{{ getOrderStatusText(selectedOrder.status) }}</p>
            <p><strong>下单时间：</strong>{{ formatDate(selectedOrder.order_date) }}</p>
          </div>
          
          <h4>订单商品</h4>
          <table class="details-table">
            <thead>
              <tr>
                <th>图片</th>
                <th>书名</th>
                <th>数量</th>
                <th>单价</th>
                <th>小计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="detail in selectedOrder.details" :key="detail.order_detail_id">
                <td class="book-image-cell">
                  <div class="image-container">
                    <img 
                      :src="getBookImageUrl(detail.image_url) || defaultBookImage"
                      :alt="detail.book_name"
                      class="book-thumbnail"
                      @error="handleImageError"
                    />
                  </div>
                </td>
                <td>
                  <div>{{ detail.book_name }}</div>
                  <div class="book-author">{{ detail.authors }}</div>
                </td>
                <td>{{ detail.quantity }}</td>
                <td>￥{{ formatPrice(detail.unit_price) }}</td>
                <td>￥{{ formatPrice(detail.quantity * detail.unit_price) }}</td>
              </tr>
            </tbody>
          </table>
          
          <div class="dialog-footer">
            <button @click="deleteOrder(selectedOrder.order_id)" class="delete-btn">删除订单</button>
            <button @click="closeOrderDetails" class="close-btn">关闭</button>
          </div>
        </div>
      </div>
    </div>
  
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

const store = useStore()
const pageSize = 10 // 每页显示数量

// 菜单配置
const menus = [
  { label: '用户管理', value: 'users' },
  { label: '订单管理', value: 'orders' },
  { label: '商品管理', value: 'books' }
]

// 状态管理
const currentView = ref('users')
const users = ref([])
const orders = ref([])
const books = ref([])
const loading = ref(false)
const error = ref(null)

// 搜索和分页
const userSearchQuery = ref('')
const orderSearchQuery = ref('')
const bookSearchQuery = ref('')
const userPage = ref(1)
const orderPage = ref(1)
const bookPage = ref(1)

// 筛选
const orderStatusFilter = ref('')
const userTypeFilter = ref('')
const totalUsers = ref(0)
const totalOrders = ref(0)
const totalBooks = ref(0)

// 对话框控制
const showEditUserDialog = ref(false)
const showEditBookDialog = ref(false)
const showOrderDetails = ref(false)
const editingUser = ref(null)
const editingBook = ref(null)
const selectedOrder = ref(null)

// 图片相关
const imageLoadErrors = new Set()
const imageCache = new Map()
const defaultBookImage = new URL('@/assets/default-book.jpg', import.meta.url).href
const createUser = () => {
  editingUser.value = {
    id: null, // 新用户没有ID
    name: '',
    email: '',
    type: '',
    address: '',
    password: '' // 新建时密码为必填
  }
  showEditUserDialog.value = true
  error.value = null
}

const saveUser = async () => {
  if (loading.value) return
  
  const errors = validateUserForm()
  if (errors.length > 0) {
    error.value = errors.join('\n')
    return
  }

  try {
    loading.value = true
    
    // 准备更新数据，只包含可更新的字段
    const updateData = {}
    
    // 只包含非空且已修改的字段
    if (editingUser.value.name && editingUser.value.name.trim() !== '') {
      updateData.name = editingUser.value.name.trim()
    }
    
    if (editingUser.value.type && editingUser.value.type !== '') {
      updateData.type = editingUser.value.type
    }
    
    if (editingUser.value.address && editingUser.value.address.trim() !== '') {
      updateData.address = editingUser.value.address.trim()
    }
    
    // 密码只在有值时才包含
    if (editingUser.value.password && editingUser.value.password.trim() !== '') {
      updateData.password = editingUser.value.password.trim()
    }

    console.log('Update data:', updateData) // 调试日志

    if (editingUser.value.id) {
      // 更新现有用户
      const response = await axios({
        method: 'put',
        url: `/user/${editingUser.value.id}`,
        data: updateData,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${store.state.token}`,
          'Accept': 'application/json'
        }
      })

      console.log('Update response:', response.data)
      // 更新成功后刷新用户列表并关闭弹窗
      await getUsers()
      closeEditUserDialog()
    } else {
      // 创建新用户需要邮箱字段
      if (!editingUser.value.email) {
        throw new Error('新用户必须设置邮箱')
      }
      
      const createData = {
        ...updateData,
        email: editingUser.value.email.trim()
      }

      if (!createData.password) {
        throw new Error('新用户必须设置密码')
      }

      const response = await axios({
        method: 'post',
        url: '/user/admin/create',
        data: createData,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${store.state.token}`,
          'Accept': 'application/json'
        }
      })

      console.log('Create response:', response.data)
      // 创建成功后刷新用户列表并关闭弹窗
      await getUsers()
      closeEditUserDialog()
    }
    
  } catch (err) {
    console.error('Save user error:', err.response || err)
    if (err.response?.status === 400) {
      error.value = err.response.data.detail || '输入数据无效'
    } else if (err.response?.status === 500) {
      error.value = '服务器错误，请稍后重试'
    } else {
      error.value = err.response?.data?.detail || err.message || '保存失败'
    }
  } finally {
    loading.value = false
  }
}
// 用户表单验证
const validateUserForm = () => {
  const errors = []
  const { name, type } = editingUser.value

  // 验证用户名
  if (name !== undefined && name !== null) {
    if (name.trim() === '') {
      errors.push('用户名不能为空')
    }
    if (name.length < 2 || name.length > 50) {
      errors.push('用户名长度必须在2-50个字符之间')
    }
  }

  // 验证用户类型
  if (type !== undefined && type !== null) {
    const validTypes = ['buyer', 'store', 'administrator']
    if (!validTypes.includes(type)) {
      errors.push('请选择有效的用户类型')
    }
  }

  // 验证密码（如果提供）
  if (editingUser.value.password) {
    if (editingUser.value.password.length < 6) {
      errors.push('密码长度至少为6个字符')
    }
  }

  return errors
}
// 修改获取用户列表函数
const getUsers = async () => {
  if (loading.value) return

  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/user/', {
      params: {
        skip: (userPage.value - 1) * pageSize,
        limit: pageSize
      },
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })

    console.log('Raw API response:', response.data)

    if (!Array.isArray(response.data)) {
      throw new Error('Invalid response format')
    }

    // 解析并处理返回的数据
    users.value = response.data.map(row => {
      // 检查row是否是数组格式
      if (Array.isArray(row)) {
        return {
          id: row[0],
          name: row[1],
          email: row[2],
          type: row[3],
          address: row[4]
        }
      }
      // 如果是对象格式
      return {
        id: row.id,
        name: row.name,
        email: row.email,
        type: row.type,
        address: row.address
      }
    })

    console.log('Processed users:', users.value)
    totalUsers.value = users.value.length

  } catch (err) {
    console.error('获取用户列表失败:', err)
    error.value = err.response?.data?.detail || '获取用户失败'
    users.value = []
  } finally {
    loading.value = false
  }
}
// 修改编辑用户函数
const editUser = (user) => {
  console.log('Editing user:', user)
  
  if (!user || !user.id) {
    console.error('Invalid user data:', user)
    error.value = '无效的用户数据'
    return
  }

  editingUser.value = {
    id: user.id, // 使用数据库返回的实际id
    name: user.name,
    email: user.email,
    type: user.type,
    address: user.address,
    password: ''
  }

  console.log('Prepared editing user:', editingUser.value)
  showEditUserDialog.value = true
  error.value = null
}

// 修改删除用户函数
const handleDeleteUser = async (userId) => {
  if (!userId) {
    console.error('No user ID provided')
    error.value = '无效的用户ID'
    return
  }

  const userToDelete = users.value.find(user => user.id === userId)
  if (!userToDelete) {
    error.value = '找不到要删除的用户'
    return
  }

  if (!confirm(`确定要删除用户 "${userToDelete.name}" 吗？此操作不可恢复`)) {
    return
  }

  try {
    loading.value = true
    console.log('Deleting user with ID:', userId) // 调试日志

    // 确保使用正确的API路径
    const response = await axios.delete(`/user/${userId}`, {
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })

    if (response.status === 200) {
      // 删除成功后更新本地数据
      users.value = users.value.filter(user => user.id !== userId)
      if (users.value.length === 0 && userPage.value > 1) {
        userPage.value--
      }
      // 重新获取用户列表
      await getUsers()
    }

  } catch (err) {
    console.error('删除用户失败:', err)
    if (err.response?.status === 404) {
      error.value = '找不到要删除的用户'
    } else {
      error.value = err.response?.data?.detail || '删除用户失败'
    }
  } finally {
    loading.value = false
  }
}





// 修改编辑用户函数
const closeEditUserDialog = () => {
  if (loading.value) return
  showEditUserDialog.value = false
  editingUser.value = null
  error.value = null
}

// 计算属性
const totalPages = computed(() => {
  const totalMap = {
    users: totalUsers.value,
    orders: totalOrders.value,
    books: totalBooks.value
  }
  return Math.ceil(totalMap[currentView.value] / pageSize)
})

const totalRecords = computed(() => {
  const totalMap = {
    users: totalUsers.value,
    orders: totalOrders.value,
    books: totalBooks.value
  }
  return totalMap[currentView.value]
})

const currentPage = computed(() => {
  const pageMap = {
    users: userPage.value,
    orders: orderPage.value,
    books: bookPage.value
  }
  return pageMap[currentView.value]
})

// 文本转换函数
const getUserTypeText = (type) => {
  const typeMap = {
    'buyer': '买家',
    'store': '商家',
    'administrator': '管理员'
  }
  return typeMap[type] || type
}

const getOrderStatusText = (status) => {
  const statusMap = {
    'pending': '待付款',
    'processing': '待发货',
    'shipped': '已发货',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

const getOrderStatusClass = (status) => {
  const classMap = {
    'pending': 'status-pending',
    'processing': 'status-processing',
    'shipped': 'status-shipped',
    'completed': 'status-completed'
  }
  return classMap[status] || ''
}

const getBookCategoryText = (category) => {
  const categoryMap = {
    'history': '文史哲',
    'social': '社科',
    'medicicial_book': '生医',
    'art': '艺术',
    'reference': '教材及参考书'
  }
  return categoryMap[category] || category
}

// 格式化函数
const formatPrice = (price) => Number(price).toFixed(2)

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 图片处理函数
const getBookImageUrl = (url) => {
  try {
    if (!url) return defaultBookImage
    if (url.startsWith('http')) return url
    return `http://localhost:8000${url.startsWith('/') ? url : '/' + url}`
  } catch (error) {
    console.error('图片URL处理错误:', error)
    return defaultBookImage
  }
}

const handleImageError = (event, isbn) => {
  if (!event || !event.target) return
  event.target.src = defaultBookImage
  if (isbn) {
    imageLoadErrors.add(isbn)
    const container = event.target.closest('.image-container')
    if (container) {
      container.classList.add('load-error')
    }
  }
}



 

const validateBookForm = () => {
  if (!editingBook.value) return ['书籍数据无效']

  const errors = []
  const { book_name, authors, category, inventory, price } = editingBook.value

  if (!book_name?.trim()) errors.push('书名不能为空')
  if (!authors?.trim()) errors.push('作者不能为空')
  if (!category) errors.push('请选择分类')
  if (typeof inventory !== 'number' || inventory < 0) {
    errors.push('库存必须是非负数')
  }
  if (typeof price !== 'number' || price <= 0) {
    errors.push('价格必须大于0')
  }

  return errors
}

   

const getAllOrders = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/bookorders/', {
      params: {
        skip: (orderPage.value - 1) * pageSize,
        limit: pageSize
      },
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    // 直接使用返回的数据
    orders.value = response.data
    totalOrders.value = response.data.length
  } catch (error) {
    console.error('获取订单列表失败:', error)
    error.value = error.response?.data?.detail || '获取订单失败'
  } finally {
    loading.value = false
  }
}
const getAllBooks = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/book/search', {
      params: {
        skip: (bookPage.value - 1) * pageSize,
        limit: pageSize
      },
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    // 直接使用返回的数据
    books.value = response.data
    totalBooks.value = response.data.length
  } catch (error) {
    console.error('加载书籍失败:', error)
    error.value = error.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

// 用户管理
// 编辑用户函数





// 订单管理
const viewOrderDetails = async (order) => {
  try {
    loading.value = true
    const response = await axios.get(`/bookorders/${order.order_id}`, {
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    selectedOrder.value = response.data
    showOrderDetails.value = true
  } catch (error) {
    console.error('获取订单详情失败:', error)
    error.value = error.response?.data?.detail || '获取订单详情失败'
  } finally {
    loading.value = false
  }
}

const closeOrderDetails = () => {
  showOrderDetails.value = false
  selectedOrder.value = null
}

const deleteOrder = async (orderId) => {
  if (!confirm('确定要删除这个订单记录吗？此操作不可恢复')) return
  
  try {
    loading.value = true
    await axios.delete(`/bookorders/${orderId}`, {
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    await getAllOrders()
    if (showOrderDetails.value) {
      closeOrderDetails()
    }
  } catch (error) {
    console.error('删除订单失败:', error)
    error.value = error.response?.data?.detail || '删除失败'
  } finally {
    loading.value = false
  }
}

// 书籍管理
const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    error.value = '只能上传图片文件'
    return
  }
  
  const maxSize = 2 * 1024 * 1024 // 2MB
  if (file.size > maxSize) {
    error.value = '图片大小不能超过2MB'
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(
      `/upload/${editingBook.value.isbn}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${store.state.token}`
        }
      }
    )

    editingBook.value.image_url = response.data.url
  } catch (error) {
    console.error('上传图片失败:', error)
    error.value = error.response?.data?.detail || '上传失败'
  }
}

const editBook = (book) => {
  editingBook.value = { ...book }
  showEditBookDialog.value = true
}

const closeEditBookDialog = () => {
  showEditBookDialog.value = false
  editingBook.value = null
  error.value = null
}

const saveBook = async () => {
  const errors = validateBookForm()
  if (errors.length > 0) {
    error.value = errors.join('\n')
    return
  }

  try {
    loading.value = true
    await axios.put(
      `/book/${editingBook.value.isbn}`,
      editingBook.value,
      {
        headers: {
          'Authorization': `Bearer ${store.state.token}`
        }
      }
    )
    await getAllBooks()
    closeEditBookDialog()
  } catch (error) {
    console.error('更新书籍失败:', error)
    error.value = error.response?.data?.detail || '更新失败'
  } finally {
    loading.value = false
  }
}

const deleteBook = async (isbn) => {
  if (!confirm('确定要删除这本书吗？此操作不可恢复')) return
  
  try {
    loading.value = true
    await axios.delete(`/book/${isbn}`, {
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    await getAllBooks()
  } catch (error) {
    console.error('删除书籍失败:', error)
    error.value = error.response?.data?.detail || '删除失败'
  } finally {
    loading.value = false
  }
}

// 搜索和筛选
const searchUsers = async () => {
  userPage.value = 1
  await getUsers()
}


const searchOrders = async () => {
  orderPage.value = 1
  await getAllOrders()
}

const searchBooks = async () => {
  bookPage.value = 1
  await getAllBooks()
}

const checkLowInventory = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/book/inventory/low', {
      headers: {
        'Authorization': `Bearer ${store.state.token}`
      }
    })
    books.value = response.data
  } catch (error) {
    console.error('获取低库存书籍失败:', error)
    error.value = error.response?.data?.detail || '获取失败'
  } finally {
    loading.value = false
  }
}

// 分页处理
const changePage = async (type, page) => {
  if (page < 1 || page > totalPages.value) return
  
  const pageRef = {
    users: userPage,
    orders: orderPage,
    books: bookPage
  }[type]
  
  pageRef.value = page
  
  switch (type) {
    case 'users':
      await getUsers()
      break
    case 'orders':
      await getAllOrders()
      break
    case 'books':
      await getAllBooks()
      break
  }
}

// 初始化
onMounted(async () => {
  const token = store.state.token
  const userType = store.state.userInfo?.type
  
  if (!token || userType !== 'administrator') {
    router.push('/login')
    return
  }
  
  try {
    await Promise.all([
      getUsers(),
      getAllOrders(),
      getAllBooks()
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})
</script>

<style scoped>
/* 基础布局 */
.panel-container {
  display: flex;
  min-height: calc(100vh - 64px);
}

/* 左侧菜单 */
.side-menu {
  width: 200px;
  background-color: #001529;
  padding: 20px 0;
  flex-shrink: 0;
}

.menu-item {
  padding: 12px 24px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.menu-item:hover {
  background-color: #1890ff;
}

.menu-item.active {
  background-color: #1890ff;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 24px;
  background-color: #f0f2f5;
  overflow-x: auto;
}

.view-container {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 表格样式 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  font-size: 14px;
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
  color: #595959;
}

.data-table tbody tr:hover {
  background-color: #fafafa;
}

/* 搜索栏和筛选器 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.search-bar {
  display: flex;
  gap: 12px;
  flex: 1;
  max-width: 400px;
}

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  transition: all 0.3s;
}

.search-bar input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
  outline: none;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 120px;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-bar select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
  outline: none;
}

/* 按钮样式 */
.primary-btn,
.info-btn,
.warning-btn,
.delete-btn,
.cancel-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.primary-btn {
  background-color: #1890ff;
  color: white;
}

.primary-btn:hover {
  background-color: #40a9ff;
}

.info-btn {
  background-color: #722ed1;
  color: white;
}

.info-btn:hover {
  background-color: #9254de;
}

.warning-btn {
  background-color: #faad14;
  color: white;
}

.warning-btn:hover {
  background-color: #ffc53d;
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
}

.delete-btn:hover {
  background-color: #ff7875;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #595959;
}

.cancel-btn:hover {
  background-color: #d9d9d9;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog h3 {
  margin: 0 0 24px;
  color: #262626;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #595959;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  transition: all 0.3s;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
  outline: none;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.file-input {
  border: none !important;
  padding: 0 !important;
}

/* 状态标签 */
.status-pending,
.status-processing,
.status-shipped,
.status-completed {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-pending {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.status-processing {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-shipped {
  background-color: #f9f0ff;
  color: #722ed1;
  border: 1px solid #d3adf7;
}

.status-completed {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

/* 图片相关样式 */
.book-image-cell {
  width: 80px;
  height: 120px;
}

.image-container {
  width: 100%;
  height: 100%;
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
  object-fit: cover;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #999;
}

.no-image-icon {
  font-size: 24px;
}

.no-image-text {
  font-size: 12px;
}

/* 订单详情样式 */
.order-info {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 24px;
}

.order-info p {
  margin: 8px 0;
  color: #595959;
}

.order-info strong {
  color: #262626;
  margin-right: 8px;
}

/* 错误提示 */
.form-error {
  color: #ff4d4f;
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  white-space: pre-line;
}

/* 分页器 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  color: #595959;
}

.pagination button {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination button:not(:disabled):hover {
  border-color: #1890ff;
  color: #1890ff;
}

.pagination button:disabled {
  background-color: #f5f5f5;
  color: #d9d9d9;
  cursor: not-allowed;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 40px;
  color: #1890ff;
}

/* 库存预警 */
.low-inventory {
  color: #ff4d4f;
  font-weight: bold;
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

  .dialog {
    width: 95%;
    padding: 16px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .search-bar {
    max-width: none;
  }
}
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.required {
  color: #ff4d4f;
  margin-left: 4px;
}

.optional {
  color: #999;
  margin-left: 4px;
}
</style>