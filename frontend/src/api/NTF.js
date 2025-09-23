import request from '@/utils/request'

export const NtfApi = {
  /**
   * 获取NTF测试信息列表
   * @param {Object} params
   */
  getInfos(params = {}) {
    return request.get('/NTF/infos/', params)
  },

  /**
   * 获取NTF测试详情
   * @param {number|string} id
   */
  getDetail(id) {
    return request.get(`/NTF/infos/${id}/`)
  },

  /**
   * 根据车型获取最新NTF测试详情
   * @param {number|string} vehicleId
   */
  getDetailByVehicle(vehicleId) {
    return request.get(`/NTF/infos/by-vehicle/${vehicleId}/`)
  }
}

export default NtfApi
