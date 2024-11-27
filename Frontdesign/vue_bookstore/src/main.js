
import axios from 'axios'



// axios 配置
axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.withCredentials = true

// axios 请求拦截器
axios.interceptors.request.use(
  config => {
    const token = store.state.token || localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// axios 响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.commit('clearUser')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

// main.js
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 500) {
      // 统一处理500错误
      console.error('服务器错误')
    }
    if (error.response?.status === 404) {
      // 统一处理404错误
      console.error('请求的资源不存在')
    }
    return Promise.reject(error)
  }
)
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createApp } from 'vue';



import App from './App.vue'
import router from './router'
import store from './stores/store'

const app=createApp(App)
app.use(ElementPlus)
app.use(router)
app.use(store)
app.mount('#app')


