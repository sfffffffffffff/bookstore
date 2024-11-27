<template>
  <div class="profile-container">
    <div class="profile-header">
      <h2>我的账户</h2>
    </div>
 
    <div class="profile-content">
      <form @submit.prevent="handleSubmit" class="profile-form">
        <!-- 昵称 -->
        <div class="form-group">
          <label>昵称:</label>
          <div class="input-group">
            <input 
              type="text"
              v-model="userForm.name"
              :disabled="!isEditing"
              required
            />
            <div v-if="isEditing" class="input-tip">新昵称不能与其他用户重复</div>
          </div>
        </div>
 
        <!-- 邮箱 -->
        <div class="form-group">
          <label>邮箱:</label>
          <div class="input-group">
            <input 
              type="email"
              v-model="userForm.email"
              :disabled="!isEditing"
              required
            />
            <div v-if="isEditing" class="input-tip">新邮箱不能与其他用户重复</div>
          </div>
        </div>
 
        <!-- 地址 -->
        <div class="form-group">
          <label>地址:</label>
          <input
            type="text" 
            v-model="userForm.address"
            :disabled="!isEditing"
          />
        </div>
 
        <!-- 用户类型 -->
        <div class="form-group">
          <label>用户类型:</label>
          <input
            type="text"
            v-model="userForm.type"
            disabled
          />
        </div>
 
        <!-- 密码修改 -->
        <div v-if="isEditing" class="form-group">
          <label>新密码:</label>
          <input
            type="password"
            v-model="userForm.password"
            placeholder="如需修改密码请输入新密码"
          />
        </div>
 
        <!-- 按钮区域 -->
        <div class="form-actions">
          <template v-if="!isEditing">
            <button type="button" @click="startEditing" class="edit-btn">
              修改资料
            </button>
            <button type="button" @click="confirmDelete" class="delete-btn">
              注销账号
            </button>
          </template>
          <template v-else>
            <button type="submit" class="save-btn">保存</button>
            <button type="button" @click="cancelEditing" class="cancel-btn">
              取消
            </button>
          </template>
        </div>
      </form>
    </div>
 
    <!-- 提示框 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
 
    <!-- 删除账号确认对话框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal">
        <h3>确认注销账号</h3>
        <p>注销账号后将无法恢复，是否继续？</p>
        <div class="modal-actions">
          <button @click="deleteAccount" class="confirm-btn">确认注销</button>
          <button @click="showDeleteConfirm = false" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'

const router = useRouter()
const store = useStore()
const isEditing = ref(false)
const message = ref('')
const messageType = ref('info')
const showDeleteConfirm = ref(false)

const userForm = ref({
name: '',
email: '', 
address: '',
type: '',
password: ''
})

// 获取用户信息
const getUserInfo = async () => {
try {
  const token = store.state.token
  if (!token) {
    router.push('/login')
    return
  }

  const response = await axios.get('/user/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
  const { name, email, address, type } = response.data
  userForm.value = {
    name,
    email,
    address: address || '',
    type,
    password: ''
  }
} catch (error) {
  console.error('获取用户信息失败:', error)
  showError('获取用户信息失败')
}
}

const startEditing = () => {
isEditing.value = true
}

const cancelEditing = () => {
isEditing.value = false
userForm.value.password = ''
getUserInfo()
}

const handleSubmit = async () => {
try {
  const updateData = {}
  if (userForm.value.name) updateData.name = userForm.value.name
  if (userForm.value.email) updateData.email = userForm.value.email
  if (userForm.value.address) updateData.address = userForm.value.address
  if (userForm.value.password) updateData.password = userForm.value.password

  const token = store.state.token
  await axios.put('/user/me', updateData, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })

  showSuccess('保存成功')
  isEditing.value = false
  getUserInfo()
} catch (error) {
  console.error('更新失败:', error)
  showError(error.response?.data?.detail || '更新失败')
}
}

const confirmDelete = () => {
showDeleteConfirm.value = true
}

const deleteAccount = async () => {
try {
  const token = store.state.token
  await axios.delete('/user/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
  showSuccess('账号已注销')
  store.commit('clearUser')
  router.push('/login')
} catch (error) {
  console.error('注销失败:', error)
  showError('注销失败')
}
showDeleteConfirm.value = false
}

const showSuccess = (msg) => {
message.value = msg
messageType.value = 'success'
setTimeout(() => message.value = '', 3000)
}

const showError = (msg) => {
message.value = msg
messageType.value = 'error'
setTimeout(() => message.value = '', 3000)
}

onMounted(() => {
getUserInfo()
})
</script>
 
<style scoped>
.profile-container {
max-width: 800px;
margin: 40px auto;
padding: 20px;
}

.profile-header {
margin-bottom: 30px;
border-bottom: 1px solid #eee;
padding-bottom: 15px;
}

.profile-form {
display: flex;
flex-direction: column;
gap: 25px;
}

.form-group {
display: grid;
grid-template-columns: 120px 1fr;
align-items: start;
gap: 20px;
}

label {
font-weight: 500;
color: #333;
line-height: 32px;
}

.input-group {
display: flex;
flex-direction: column;
gap: 4px;
}

.input-tip {
font-size: 12px;
color: #999;
}

input {
padding: 8px 12px;
border: 1px solid #d9d9d9;
border-radius: 4px;
transition: all 0.3s;
}

input:focus {
border-color: #40a9ff;
box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
outline: none;
}

input:disabled {
background-color: #f5f5f5;
cursor: not-allowed;
}

.form-actions {
grid-column: 2;
display: flex;
gap: 12px;
}

button {
padding: 8px 16px;
border: none;
border-radius: 4px;
cursor: pointer;
transition: all 0.3s;
}

.edit-btn {
background-color: #1890ff;
color: white;
}

.save-btn {
background-color: #52c41a;
color: white;
}

.cancel-btn {
background-color: #f5f5f5;
color: #666;
}

.delete-btn {
background-color: #ff4d4f;
color: white;
}

button:hover {
opacity: 0.8;
}

.message {
position: fixed;
top: 20px;
right: 20px;
padding: 10px 20px;
border-radius: 4px;
animation: slideIn 0.3s ease;
}

.success {
background-color: #f6ffed;
border: 1px solid #b7eb8f;
color: #52c41a;
}

.error {
background-color: #fff2f0;
border: 1px solid #ffccc7;
color: #ff4d4f;
}

.modal-overlay {
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

.modal {
background: white;
padding: 24px;
border-radius: 8px;
min-width: 400px;
}

.modal h3 {
margin: 0 0 16px 0;
color: #333;
}

.modal p {
margin-bottom: 24px;
color: #666;
}

.modal-actions {
display: flex;
justify-content: flex-end;
gap: 12px;
}

.confirm-btn {
background-color: #ff4d4f;
color: white;
}

@keyframes slideIn {
from {
  transform: translateX(100%);
  opacity: 0;
}
to {
  transform: translateX(0);
  opacity: 1;
}
}

@media (max-width: 600px) {
.form-group {
  grid-template-columns: 1fr;
  gap: 8px;
}

.form-actions {
  grid-column: 1;
}
}
</style>