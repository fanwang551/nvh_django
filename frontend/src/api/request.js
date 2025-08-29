import axios from 'axios'
import keycloak from '@/utils/keycloak'

// Create axios instance
const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    // Add Authorization header if user is authenticated
    if (keycloak.authenticated && keycloak.token) {
      config.headers['Authorization'] = 'Bearer ' + keycloak.token
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)

    // Handle 401 Unauthorized
    if (error.response && error.response.status === 401) {
      console.log('Token expired or invalid, redirecting to login')
      keycloak.login()
      return Promise.reject(error)
    }

    // Handle other errors
    const message = error.response?.data?.message || error.message || 'Unknown error'
    return Promise.reject(new Error(message))
  }
)

export default service
