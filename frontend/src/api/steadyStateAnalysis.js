import request from '@/utils/request'

export const steadyStateApi = {
  query(data = {}) {
    return request.post('/acoustic-analysis/steady-state/query/', data)
  }
}

export default steadyStateApi
