import request from '@/utils/request'

// 隔声量系数相关API
export const soundInsulationCoefficientApi = {
  /**
   * 获取测试类型选项列表
   * @returns {Promise} 测试类型选项列表
   */
  getTestTypeOptions() {
    return request.get('/sound-insulation/sound-insulation-coefficient/test-types/')
  },

  /**
   * 获取零件名称选项列表
   * @param {Object} params - 查询参数
   * @param {string} params.test_type - 测试类型（可选）
   * @returns {Promise} 零件名称选项列表
   */
  getPartNameOptions(params = {}) {
    return request.get('/sound-insulation/sound-insulation-coefficient/part-names/', params)
  },

  /**
   * 获取材料组成选项列表
   * @param {Object} params - 查询参数
   * @param {string} params.test_type - 测试类型（可选）
   * @param {string} params.part_name - 零件名称（可选）
   * @returns {Promise} 材料组成选项列表
   */
  getMaterialCompositionOptions(params = {}) {
    return request.get('/sound-insulation/sound-insulation-coefficient/material-compositions/', params)
  },

  /**
   * 获取克重选项列表
   * @param {Object} params - 查询参数
   * @param {string} params.test_type - 测试类型（可选）
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.material_composition - 材料组成（可选）
   * @returns {Promise} 克重选项列表
   */
  getWeightOptions(params = {}) {
    return request.get('/sound-insulation/sound-insulation-coefficient/weights/', params)
  },

  /**
   * 隔声量系数查询
   * @param {Object} params - 查询参数
   * @param {string} params.test_type - 测试类型（可选）
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.material_composition - 材料组成（可选）
   * @param {number} params.weight - 克重（可选）
   * @returns {Promise} 查询结果
   */
  querySoundInsulationCoefficient(params = {}) {
    return request.get('/sound-insulation/sound-insulation-coefficient/query/', params)
  }
}

// 导出默认对象
export default soundInsulationCoefficientApi
