import request from '@/utils/request'

/**
 * 悬置隔振率查询相关API（重构版）
 */

// ---------------- 重构版 API ----------------
// 车型列表（去重，含能源类型）
export const getIsolationVehicleModels = () => {
  return request.get('/dynamic-stiffness/vehicle-models/')
}

// 根据多车型获取测点
export const getIsolationMeasuringPoints = (vehicleIds = []) => {
  const params = {}
  if (Array.isArray(vehicleIds) && vehicleIds.length) {
    params.vehicle_ids = vehicleIds.join(',')
  }
  return request.get('/dynamic-stiffness/measuring-points/', params)
}

// 测试信息卡片
export const getIsolationTestInfo = (vehicleIds = []) => {
  const params = {}
  if (Array.isArray(vehicleIds) && vehicleIds.length) {
    params.vehicle_ids = vehicleIds.join(',')
  }
  return request.get('/dynamic-stiffness/test-info/', params)
}

// 曲线数据查询（POST）
export const queryIsolationData = (payload = {}) => {
  return request.post('/dynamic-stiffness/isolation-data/query/', payload)
}

export default {
  getIsolationVehicleModels,
  getIsolationMeasuringPoints,
  getIsolationTestInfo,
  queryIsolationData
}
