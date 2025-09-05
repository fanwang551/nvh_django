import request from '@/utils/request'

// 材料孔隙率流阻相关API
export const materialPorosityApi = {
  /**
   * 获取零件名称选项
   * @returns {Promise} 零件名称选项列表
   */
  getPartNameOptions() {
    return request.get('/sound-insulation/material-porosity/part-names/')
  },

  /**
   * 材料孔隙率流阻查询
   * @param {Object} params - 查询参数
   * @param {string} params.part_names - 零件名称列表，逗号分隔（可选）
   * @returns {Promise} 查询结果
   */
  queryMaterialPorosity(params = {}) {
    return request.get('/sound-insulation/material-porosity/query/', params)
  }
}

// 导出默认对象
export default materialPorosityApi
