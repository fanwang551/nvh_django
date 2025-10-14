import request from '@/utils/request'

export const experienceApi = {
  /**
   * 获取经验数据列表
   * @param {Object} params { q, category, page, page_size }
   */
  list(params = {}) {
    return request.get('/experience/', params)
  },

  /**
   * 获取经验详情
   * @param {number} id 经验ID
   */
  detail(id) {
    return request.get(`/experience/${id}/`)
  },

  /**
   * 新增经验
   * @param {Object} data 表单数据
   */
  create(data) {
    return request.post('/experience/', data)
  }
}

export default experienceApi

