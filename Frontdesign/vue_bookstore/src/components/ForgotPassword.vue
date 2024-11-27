
<template>
    <div class="forgot-password-container">
      <div class="forgot-password-box">
        <h2>找回密码</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>邮箱：</label>
            <input 
              type="email" 
              v-model="email" 
              required 
              placeholder="请输入注册邮箱"
            />
          </div>
          <button type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? '发送中...' : '发送重置链接' }}
          </button>
        </form>
        <div class="back-to-login">
          <a @click="$router.push('/login')">返回登录</a>
        </div>
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  
  const router = useRouter()
  const email = ref('')
  const isSubmitting = ref(false)
  const message = ref('')
  const messageType = ref('info')
  
  const handleSubmit = async () => {
    if (isSubmitting.value) return
    
    try {
      isSubmitting.value = true
      const response = await axios.post('/forgot-password/', { email: email.value })
      message.value = '重置链接已发送到您的邮箱，请查收'
      messageType.value = 'success'
      // 5秒后返回登录页
      setTimeout(() => {
        router.push('/login')
      }, 5000)
    } catch (error) {
      message.value = error.response?.data?.detail || '发送失败，请重试'
      messageType.value = 'error'
    } finally {
      isSubmitting.value = false
    }
  }
  </script>
  
  <style scoped>
  /* 样式与登录页面类似 */
  </style>