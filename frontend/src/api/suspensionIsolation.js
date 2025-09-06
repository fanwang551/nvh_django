import request from '@/utils/request'

/**
 * 悬架隔振率相关API接口
 */

/**
 * 获取悬架隔振率测点列表
 * @param {Object} params - 查询参数
 * @param {number} params.vehicle_model_id - 车型ID（可选）
 * @returns {Promise} 接口响应
 */
export function getSuspensionMeasuringPoints(params = {}) {
  console.log('发送悬架隔振率测点列表请求:', params)
  return request.get('/dynamic-stiffness/suspension-isolation/measuring-points/', params)
}

/**
 * 查询悬架隔振率数据
 * @param {Object} params - 查询参数
 * @param {number} params.vehicle_model_id - 车型ID（必填）
 * @param {string} params.measuring_points - 测点列表，逗号分隔（可选）
 * @returns {Promise} 接口响应
 */
export function querySuspensionIsolationData(params) {
  return request.get('/dynamic-stiffness/suspension-isolation/data/', params)
}