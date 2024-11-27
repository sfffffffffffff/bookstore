<template>
  <div class="login-container">
    <div class="login-box">
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      
      <!-- 登录/注册表单 -->
      <form @submit.prevent="handleSubmit">
        <!-- 登录表单 -->
        <template v-if="isLogin">
          <div class="form-group">
            <label>昵称：</label>
            <input 
              type="text" 
              v-model="loginForm.username" 
              required 
              placeholder="请输入昵称"
            />
          </div>

          <div class="form-group">
            <label>密码：</label>
            <input 
              type="password" 
              v-model="loginForm.password" 
              required 
              placeholder="请输入密码"
            />
          </div>

          <div class="form-group">
            <label>用户类型：</label>
            <select v-model="loginForm.userType" required>
              <option value="buyer">买家</option>
              <option value="store">商家</option>
              <option value="administrator">管理员</option>
            </select>
          </div>
        </template>

        <!-- 注册表单 -->
        <template v-else>
          <div class="form-group">
            <label>昵称：</label>
            <input 
              type="text" 
              v-model="registerForm.name" 
              required 
              placeholder="请输入昵称"
            />
          </div>

          <div class="form-group">
            <label>邮箱：</label>
            <input 
              type="email" 
              v-model="registerForm.email" 
              required 
              placeholder="请输入邮箱"
            />
          </div>

          <div class="form-group">
            <label>密码：</label>
            <input 
              type="password" 
              v-model="registerForm.password" 
              required 
              placeholder="请输入密码"
            />
          </div>

          <div class="form-group">
            <label>地址：</label>
            <input 
              type="text" 
              v-model="registerForm.address" 
              required 
              placeholder="请输入地址"
            />
          </div>

          <div class="form-group">
            <label>用户类型：</label>
            <select v-model="registerForm.type" required>
              <option value="buyer">买家</option>
              <option value="store">商家</option>
            </select>
          </div>
        </template>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="submit" :disabled="isSubmitting" class="submit-btn">
            {{ isSubmitting ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </div>
      </form>

      <!-- 底部操作区 -->
      <div class="form-footer">
        <div class="toggle-auth">
          <a href="#" @click.prevent="toggleAuthMode">
            {{ isLogin ? '没有账号？点击注册' : '已有账号？点击登录' }}
          </a>
        </div>
        
        <!-- 登录状态下显示忘记密码链接 -->
        <div v-if="isLogin" class="forgot-password">
          <a href="#" @click.prevent="handleForgotPassword">忘记密码？</a>
        </div>
      </div>

      <!-- 错误消息显示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex' // 引入 Vuex Store
import axios from 'axios'

const router = useRouter()
const store = useStore() // 获取 Vuex 实例

// 状态管理
const isLogin = ref(true)
const errorMessage = ref('')
const isSubmitting = ref(false)

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  userType: 'buyer'
})

// 注册表单数据
const registerForm = ref({
  name: '',
  email: '',
  password: '',
  address: '',
  type: 'buyer'
})

// 切换登录/注册模式
const toggleAuthMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
}

// 处理忘记密码
const handleForgotPassword = () => {
  router.push('/forgot-password')
}

// 表单提交处理
const handleSubmit = async () => {
  if (isSubmitting.value) return

  try {
    isSubmitting.value = true
    errorMessage.value = ''

    if (isLogin.value) {
      // 登录处理
      const formData = new URLSearchParams()
      formData.append('username', loginForm.value.username)
      formData.append('password', loginForm.value.password)
      formData.append('scope', loginForm.value.userType)

      const response = await axios.post('/login/', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      // 处理登录成功
      const { access_token, token_type, user_type } = response.data
      store.commit('setToken', access_token) // 保存 Token 到 Vuex
      store.commit('setUser', {
        type: user_type,
        name: loginForm.value.username
      }) // 保存用户信息到 Vuex

      router.push('/')
    } else {
      // 注册处理
      if (registerForm.value.type === 'administrator') {
        errorMessage.value = '管理员账号需要联系网站管理员创建'
        return
      }

      await axios.post('/participants/', {
        name: registerForm.value.name,
        email: registerForm.value.email,
        password: registerForm.value.password,
        address: registerForm.value.address,
        type: registerForm.value.type
      })

      // 注册成功后自动填充登录表单
      loginForm.value.username = registerForm.value.name
      loginForm.value.userType = registerForm.value.type
      
      // 切换到登录模式
      isLogin.value = true
      errorMessage.value = '注册成功！请登录'
    }
  } catch (error) {
    console.error('操作失败:', error)
    errorMessage.value = error.response?.data?.detail || '操作失败，请重试'
  } finally {
    isSubmitting.value = false
  }
}
</script>




<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
  outline: none;
}

.form-actions {
  margin-top: 24px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.submit-btn:not(:disabled):hover {
  background-color: #40a9ff;
}

.submit-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.toggle-auth a,
.forgot-password a {
  color: #1890ff;
  text-decoration: none;
  cursor: pointer;
}

.toggle-auth a:hover,
.forgot-password a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #fff1f0;
  border: 1px solid #ffa39e;
  border-radius: 4px;
  color: #f5222d;
  text-align: center;
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .login-box {
    padding: 20px;
  }

  .form-footer {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style>