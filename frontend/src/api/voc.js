import request from '@/utils/request'

// VOC相关API
export const vocApi = {
  /**
   * 获取VOC数据列表
   * @param {Object} params - 查询参数
   * @param {number} params.vehicle_model_id - 车型ID（可选）
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.status - 状态（可选）
   * @param {string} params.test_order_no - 委托单号（可选）
   * @param {number} params.page - 页码（可选，默认1）
   * @param {number} params.page_size - 每页数量（可选，默认10）
   * @returns {Promise} VOC数据列表
   */
  getVocDataList(params = {}) {
    return request.get('/voc/data/', params)
  },

  /**
   * 获取零件名称选项列表
   * @returns {Promise} 零件名称选项列表
   */
  getPartNameOptions() {
    return request.get('/voc/options/part-names/')
  },

  /**
   * 获取车型选项列表
   * @returns {Promise} 车型选项列表
   */
  getVehicleModelOptions() {
    return request.get('/voc/options/vehicle-models/')
  },

  /**
   * 获取状态选项列表
   * @returns {Promise} 状态选项列表
   */
  getStatusOptions() {
    return request.get('/voc/options/status/')
  },

  /**
   * 获取开发阶段选项列表
   * @returns {Promise} 开发阶段选项列表
   */
  getDevelopmentStageOptions() {
    return request.get('/voc/options/development-stages/')
  },

  /**
   * 获取VOC图表数据
   * @param {Object} params - 查询参数
   * @param {string} params.main_group - 主分组（可选，默认part_name）
   * @param {string} params.sub_group - 副分组（可选，默认status）
   * @param {Array} params.compounds - 选择的VOC物质（可选）
   * @returns {Promise} 图表数据
   */
  getChartData(params = {}) {
    return request.get('/voc/chart-data/', params)
  },

  /**
   * 获取VOC统计数据
   * @returns {Promise} 统计数据
   */
  getStatistics() {
    return request.get('/voc/statistics/')
  },

  /**
   * 获取单行VOC数据的图表数据
   * @param {Object} params - 查询参数
   * @param {number} params.result_id - VOC结果ID
   * @returns {Promise} 图表数据
   */
  getRowChartData(params = {}) {
    return request.get('/voc/row-chart-data/', params)
  }
}

// 导出默认对象
export default vocApi
