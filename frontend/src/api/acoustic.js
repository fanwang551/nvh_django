import request from '@/utils/request'

export const acousticApi = {
  getWorkConditions(params = {}) {
    return request.get('/acoustic-analysis/work-conditions/', params)
  },
  getMeasurePoints(params = {}) {
    return request.get('/acoustic-analysis/measure-points/', params)
  },
  query(data = {}) {
    return request.post('/acoustic-analysis/query/', data)
  }
}

export default acousticApi

