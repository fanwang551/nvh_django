import request from '@/utils/request'

/**
 * 悬置隔振率查询相关API
 */

// 获取测点列表
export const getMeasuringPoints = (params = {}) => {
  return request.get('/dynamic-stiffness/measuring-points/', params)
}

// 悬置隔振率数据查询
export const queryMountIsolationData = (params = {}) => {
  return request.get('/dynamic-stiffness/mount-isolation-data/', params)
}

export default {
  getMeasuringPoints,
  queryMountIsolationData
}
