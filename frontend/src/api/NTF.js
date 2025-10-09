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
  },

  /**
   * 获取过滤项（车型/测点/位置/方向）
   * @param {Object} params { vehicle_ids?: string, points?: string, positions?: string, directions?: string }
   */
  getFilters(params = {}) {
    return request.get('/NTF/filters/', params)
  },

  /**
   * 获取测点列表（兼容旧逻辑，建议改用 getFilters）
   * @param {Object} params { vehicle_ids?: string }
   */
  getMeasurementPoints(params = {}) {
    return request.get('/NTF/measurement-points/', params)
  },

  /**
   * 综合查询：多个车型、多个测点（可选位置/方向）
   * @param {Object} params { vehicle_ids: string, points?: string, positions?: string, directions?: string }
   */
  multiQuery(params = {}) {
    return request.get('/NTF/query/', params)
  }
}

export default NtfApi

