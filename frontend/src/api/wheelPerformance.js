import request from '@/utils/request'

export const wheelPerformanceApi = {
  /**
   * 获取轮胎性能列表
   * @param {Object} params 查询条件
   * @returns {Promise}
   */
  getWheelPerformanceList(params = {}) {
    return request.get('/wheel-performance/', params)
  },

  /**
   * 创建轮胎性能数据
   * @param {Object} data 表单数据
   * @returns {Promise}
   */
  createWheelPerformance(data) {
    return request.post('/wheel-performance/', data)
  },


}

export default wheelPerformanceApi
