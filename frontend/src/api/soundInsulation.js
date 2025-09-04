import request from '@/utils/request'

// 隔声量相关API
export const soundInsulationApi = {
  /**
   * 获取隔声区域列表
   * @param {Object} params - 查询参数
   * @param {string} params.search - 搜索关键词（可选）
   * @returns {Promise} 区域列表
   */
  getSoundInsulationAreas(params = {}) {
    return request.get('/sound-insulation/areas/', params)
  },

  /**
   * 根据区域ID获取有数据的车型列表
   * @param {Object} params - 查询参数
   * @param {number} params.area_id - 区域ID（必需）
   * @returns {Promise} 车型列表
   */
  getVehiclesByArea(params = {}) {
    return request.get('/sound-insulation/vehicles/', params)
  },

  /**
   * 隔声量数据对比
   * @param {Object} params - 对比参数
   * @param {number} params.area_id - 区域ID（必需）
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（必需）
   * @returns {Promise} 对比数据
   */
  compareSoundInsulationData(params = {}) {
    return request.get('/sound-insulation/compare/', params)
  },

  /**
   * 获取有车型隔声量数据的车型列表
   * @param {Object} params - 查询参数
   * @param {string} params.search - 搜索关键词（可选）
   * @returns {Promise} 车型列表
   */
  getVehiclesWithSoundData(params = {}) {
    return request.get('/sound-insulation/vehicle-sound-data/', params)
  },

  /**
   * 车型隔声量数据对比
   * @param {Object} params - 对比参数
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（必需）
   * @returns {Promise} 对比数据
   */
  compareVehicleSoundInsulationData(params = {}) {
    return request.get('/sound-insulation/vehicle-sound-compare/', params)
  },

  /**
   * 获取有车辆混响时间数据的车型列表
   * @param {Object} params - 查询参数
   * @param {string} params.search - 搜索关键词（可选）
   * @returns {Promise} 车型列表
   */
  getVehiclesWithReverberationData(params = {}) {
    return request.get('/sound-insulation/vehicle-reverberation-data/', params)
  },

  /**
   * 车辆混响时间数据对比
   * @param {Object} params - 对比参数
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（必需）
   * @returns {Promise} 对比数据
   */
  compareVehicleReverberationData(params = {}) {
    return request.get('/sound-insulation/vehicle-reverberation-compare/', params)
  }
}

// 导出默认对象
export default soundInsulationApi
