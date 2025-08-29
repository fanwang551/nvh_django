import request from './request'

// User API
export const userApi = {
  // Get user info
  getUserInfo() {
    return request({
      url: '/users/info/',
      method: 'get'
    })
  },
  
  // Get user profile
  getUserProfile() {
    return request({
      url: '/users/profile/',
      method: 'get'
    })
  },
  
  // Health check
  healthCheck() {
    return request({
      url: '/users/health/',
      method: 'get'
    })
  },

  // Auth test
  authTest() {
    return request({
      url: '/users/auth-test/',
      method: 'get'
    })
  }
}
