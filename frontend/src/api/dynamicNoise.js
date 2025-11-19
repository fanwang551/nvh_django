import request, { http } from '@/utils/request'

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
  getSpectrum(id, config = {}) {
    // 直接下载/预览 PPTX 文件，返回 Blob 数据
    return http.get(`/acoustic-analysis/dynamic/${id}/spectrum/`, {
      responseType: 'blob',
      ...config
    })
  }
}

export default dynamicNoiseApi
