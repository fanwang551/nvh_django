import request from '@/utils/request'

export const substancesApi = {
  /**
   * 获取全谱检测测试信息列表
   * @param {Object} params - 查询参数
   * @param {number} params.vehicle_model_id - 车型ID（可选）
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.status - 状态（可选）
   * @param {string} params.development_stage - 开发阶段（可选）
   * @param {string} params.test_order_no - 委托单号（可选）
   * @param {string} params.sample_no - 样品编号（可选）
   * @param {string} params.test_date_start - 开始日期（可选）
   * @param {string} params.test_date_end - 结束日期（可选）
   * @param {number} params.page - 页码（可选，默认1）
   * @param {number} params.page_size - 每页数量（可选，默认10）
   * @returns {Promise} 测试信息列表
   */
  getTestList(params = {}) {
    return request.get('/voc/substances/test-list/', params)
  },

  /**
   * 获取全谱检测明细数据
   * @param {Object} params - 查询参数
   * @param {number} params.test_id - 测试ID
   * @returns {Promise} 明细数据
   */
  getTestDetail(params = {}) {
    return request.get('/voc/substances/test-detail/', params)
  },

  /**
   * 获取物质详细信息
   * @param {Object} params - 查询参数
   * @param {number} params.substance_id - 物质ID
   * @returns {Promise} 物质详细信息
   */
  getSubstanceDetail(params = {}) {
    return request.get('/voc/substances/substance-detail/', params)
  },

  /**
   * 获取车型选项列表（复用VOC接口）
   * @returns {Promise} 车型选项列表
   */
  getVehicleModelOptions() {
    return request.get('/voc/options/vehicle-models/')
  },

  /**
   * 获取状态选项列表（复用VOC接口）
   * @returns {Promise} 状态选项列表
   */
  getStatusOptions() {
    return request.get('/voc/options/status/')
  },

  /**
   * 获取开发阶段选项列表（复用VOC接口）
   * @returns {Promise} 开发阶段选项列表
   */
  getDevelopmentStageOptions() {
    return request.get('/voc/options/development-stages/')
  },

  /**
   * 获取物质分项溯源数据
   * @param {Object} params - 查询参数
   * @param {number} [params.vehicle_test_id] - 整车全谱测试ID（推荐，唯一定位样品）
   * @param {number} [params.vehicle_model_id] - 车型ID（兼容旧方式）
   * @param {Array<string>} params.cas_nos - CAS号数组
   * @returns {Promise} 溯源数据
   */
  getSubstanceTraceability(params = {}) {
    return request.get('/voc/substances/item-traceability/', params)
  }
}

export default substancesApi
