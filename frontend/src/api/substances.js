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
    return request.get('/vehicle-body/substances/test-list/', params)
  },

  /**
   * 获取全谱检测明细数据
   * @param {Object} params - 查询参数
   * @param {number} params.test_id - 测试ID
   * @returns {Promise} 明细数据
   */
  getTestDetail(params = {}) {
    return request.get('/vehicle-body/substances/test-detail/', params)
  },

  /**
   * 获取物质详细信息
   * @param {Object} params - 查询参数
   * @param {number} params.substance_id - 物质ID
   * @returns {Promise} 物质详细信息
   */
  getSubstanceDetail(params = {}) {
    return request.get('/vehicle-body/substances/substance-detail/', params)
  },

  /**
   * 获取车型选项列表（复用VOC接口）
   * @returns {Promise} 车型选项列表
   */
  getVehicleModelOptions() {
    return request.get('/vehicle-body/options/vehicle-models/')
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

  // ---- 污染物分项溯源（vehicle_body 版本） ----
  /**
   * 整车样品下拉选项
   */
  getVehicleSampleOptions() {
    return request.get('/vehicle-body/substance-traceability/vehicle-sample-options/')
  },

  /**
   * 获取某整车样品下的物质列表（下拉）
   * @param {Object} params
   * @param {string} params.project_name
   * @param {string} params.test_order_no
   * @param {string} params.sample_no
   */
  getTraceabilitySubstances(params = {}) {
    return request.get('/vehicle-body/substance-traceability/substances/', params)
  },

  /**
   * 获取溯源排名结果（按所选物质）
   * @param {Object} payload
   * @param {string} payload.project_name
   * @param {string} payload.test_order_no
   * @param {string} payload.sample_no
   * @param {Array<string>} payload.selected_substances
   */
  postSubstanceRanking(payload = {}) {
    return request.post('/vehicle-body/substance-traceability/ranking/', payload)
  }
}

export default substancesApi
