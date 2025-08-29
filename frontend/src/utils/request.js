import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import keycloak from '@/utils/keycloak'

// 创建axios实例
const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    // 添加认证token
    if (keycloak.authenticated && keycloak.token) {
      config.headers['Authorization'] = `Bearer ${keycloak.token}`
    }
    
    // 请求日志
    console.log(`🚀 [${config.method?.toUpperCase()}] ${config.url}`, {
      params: config.params,
      data: config.data
    })
    
    return config
  },
  error => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    const { data } = response
    
    // 响应日志
    console.log(`✅ [${response.config.method?.toUpperCase()}] ${response.config.url}`, data)
    
    // 统一处理后端响应格式
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    
    return data
  },
  error => {
    console.error('❌ Response Error:', error)
    
    // 处理不同的错误状态
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('认证失败，请重新登录')
          keycloak.login()
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error(error.message || '未知错误')
    }
    
    return Promise.reject(error)
  }
)

// 封装常用的请求方法
const request = {
  // GET请求
  get(url, params = {}, config = {}) {
    return http.get(url, { params, ...config })
  },
  
  // POST请求
  post(url, data = {}, config = {}) {
    return http.post(url, data, config)
  },
  
  // PUT请求
  put(url, data = {}, config = {}) {
    return http.put(url, data, config)
  },
  
  // DELETE请求
  delete(url, config = {}) {
    return http.delete(url, config)
  },
  
  // PATCH请求
  patch(url, data = {}, config = {}) {
    return http.patch(url, data, config)
  }
}

// 导出实例和封装方法
export { http }
export default request
