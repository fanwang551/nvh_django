import request from '@/utils/request'

// 模态数据相关API
export const modalApi = {
  /**
   * 获取车型列表
   * @param {Object} params - 查询参数
   * @param {string} params.search - 搜索关键词（可选）
   * @returns {Promise} 车型列表
   */
  getVehicleModels(params = {}) {
    return request.get('/modal/vehicle-models/', params)
  },

  /**
   * 获取零件列表
   * @param {Object} params - 查询参数
   * @param {number} params.vehicle_model_id - 车型ID（可选，用于筛选）
   * @param {string} params.search - 搜索关键词（可选）
   * @returns {Promise} 零件列表
   */
  getComponents(params = {}) {
    return request.get('/modal/components/', params)
  },

  /**
   * 查询模态数据（分页）
   * @param {Object} params - 查询参数
   * @param {number} params.vehicle_model_id - 车型ID（必需）
   * @param {string} params.component_ids - 零件ID列表，逗号分隔（可选）
   * @param {string} params.test_type - 测试类型（可选）
   * @param {number} params.page - 页码（可选，默认1）
   * @param {number} params.page_size - 每页数量（可选，默认10）
   * @returns {Promise} 模态数据分页结果
   */
  queryModalData(params = {}) {
    return request.get('/modal/modal-data/', params)
  },

  /**
   * 获取模态数据统计信息
   * @param {Object} params - 查询参数
   * @param {number} params.vehicle_model_id - 车型ID（必需）
   * @param {string} params.component_ids - 零件ID列表，逗号分隔（可选）
   * @returns {Promise} 统计信息
   */
  getModalDataStatistics(params = {}) {
    return request.get('/modal/modal-data/statistics/', params)
  },

  /**
   * 根据零件ID获取相关的车型列表
   * @param {Object} params - 查询参数
   * @param {number} params.component_id - 零件ID（必需）
   * @returns {Promise} 相关车型列表
   */
  getRelatedVehicleModels(params = {}) {
    return request.get('/modal/modal-data/related-vehicles/', params)
  },

  /**
   * 获取测试状态选项
   * @param {Object} params - 查询参数
   * @param {number} params.component_id - 零件ID（必需）
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（可选）
   * @returns {Promise} 测试状态列表
   */
  getTestStatuses(params = {}) {
    return request.get('/modal/modal-data/test-statuses/', params)
  },

  /**
   * 获取振型类型选项
   * @param {Object} params - 查询参数
   * @param {number} params.component_id - 零件ID（必需）
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（可选）
   * @param {string} params.test_statuses - 测试状态列表，逗号分隔（可选）
   * @returns {Promise} 振型类型列表
   */
  getModeTypes(params = {}) {
    return request.get('/modal/modal-data/mode-types/', params)
  },

  /**
   * 模态数据对比
   * @param {Object} params - 对比参数
   * @param {number} params.component_id - 零件ID（必需）
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（必需）
   * @param {string} params.test_statuses - 测试状态列表，逗号分隔（可选）
   * @param {string} params.mode_types - 振型类型列表，逗号分隔（可选）
   * @returns {Promise} 对比数据
   */
  compareModalData(params = {}) {
    return request.get('/modal/modal-data/compare/', params)
  },

  /**
   * 气密性数据对比
   * @param {Object} params - 对比参数
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（必需）
   * @returns {Promise} 气密性对比数据
   */
  compareAirtightnessData(params = {}) {
    return request.get('/modal/airtightness-data/compare/', params)
  },

  /**
   * 获取气密性测试图片
   * @param {Object} params - 查询参数
   * @param {string} params.vehicle_model_ids - 车型ID列表，逗号分隔（可选）
   * @returns {Promise} 气密性图片列表
   */
  getAirtightnessImages(params = {}) {
    return request.get('/modal/airtightness-images/', params)
  }
}

// 导出默认对象
export default modalApi
