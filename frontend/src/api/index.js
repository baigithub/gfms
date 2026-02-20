import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response

      if (status === 401) {
        // 如果是登录接口，不在这里处理，让登录页面自行处理
        if (!error.config.url.includes('/auth/login')) {
          ElMessage.error('登录已过期，请重新登录')
          const authStore = useAuthStore()
          authStore.logout()
          window.location.href = '/login'
        }
      } else if (status === 403) {
        ElMessage.error('登录已失效，请重新登录')
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/login'
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status === 500) {
        ElMessage.error('服务器错误')
      } else {
        // 只对非登录接口显示通用错误提示
        if (!error.config.url.includes('/auth/login')) {
          ElMessage.error(data.detail || '请求失败')
        }
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default request