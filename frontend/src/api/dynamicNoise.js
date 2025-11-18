import request from '@/utils/request'

export const dynamicNoiseApi = {
  getWorkConditions(params = {}) {
    return request.get('/acoustic-analysis/dynamic/work-conditions/', params)
  },
  getMeasurePoints(params = {}) {
    return request.get('/acoustic-analysis/dynamic/measure-points/', params)
  },
  query(data = {}) {
    return request.post('/acoustic-analysis/dynamic/query/', data)
  },
  getSpectrum(id) {
    return request.get(`/acoustic-analysis/dynamic/${id}/spectrum/`)
  }
}

export default dynamicNoiseApi
