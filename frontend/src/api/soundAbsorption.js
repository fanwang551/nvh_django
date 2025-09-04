import request from '@/utils/request'

// 吸声系数相关API
export const soundAbsorptionApi = {
  /**
   * 获取零件名称选项列表
   * @returns {Promise} 零件名称选项列表
   */
  getPartNameOptions() {
    return request.get('/sound-insulation/sound-absorption/part-names/')
  },

  /**
   * 获取材料组成选项列表
   * @param {Object} params - 查询参数
   * @param {string} params.part_name - 零件名称（可选）
   * @returns {Promise} 材料组成选项列表
   */
  getMaterialCompositionOptions(params = {}) {
    return request.get('/sound-insulation/sound-absorption/material-compositions/', params)
  },

  /**
   * 获取克重选项列表
   * @param {Object} params - 查询参数
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.material_composition - 材料组成（可选）
   * @returns {Promise} 克重选项列表
   */
  getWeightOptions(params = {}) {
    return request.get('/sound-insulation/sound-absorption/weights/', params)
  },

  /**
   * 吸声系数查询
   * @param {Object} params - 查询参数
   * @param {string} params.part_name - 零件名称（可选）
   * @param {string} params.material_composition - 材料组成（可选）
   * @param {number} params.weight - 克重（可选）
   * @returns {Promise} 查询结果
   */
  querySoundAbsorption(params = {}) {
    return request.get('/sound-insulation/sound-absorption/query/', params)
  }
}

// 导出默认对象
export default soundAbsorptionApi