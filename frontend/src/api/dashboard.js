import request from '@/utils/request'

export const dashboardApi = {
  /**
   * 获取 NVH 首页大屏数据
   * @returns {Promise}
   */
  getHomeDashboard() {
    return request.get('/nvh-dashboard/home/')
  }
}

export default dashboardApi

