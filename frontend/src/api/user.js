import request from '@/utils/request'

// User API
export const userApi = {
  // Get user info
  getUserInfo() {
    return request.get('/users/info/')
  },

  // Get current user groups & permission flags
  getUserGroups() {
    return request.get('/users/groups/')
  },

  // Get user profile
  getUserProfile() {
    return request.get('/users/profile/')
  },

  // Health check
  healthCheck() {
    return request.get('/users/health/')
  },

  // Auth test
  authTest() {
    return request.get('/users/auth-test/')
  }
}
