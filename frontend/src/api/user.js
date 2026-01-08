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

  // List users by Django auth Group name
  listUsersByGroup(groupName, keyword = '') {
    return request.get('/users/group-users/', {
      group_name: groupName,
      keyword: keyword || undefined
    })
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
