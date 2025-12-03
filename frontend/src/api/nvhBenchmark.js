import request from '@/utils/request'

export const nvhBenchmarkApi = {
  getVehicleModels(params = {}) {
    return request.get('/nvh-benchmark/vehicle-models/', params)
  },

  getOverview(data = {}) {
    return request.post('/nvh-benchmark/overview/', data)
  }
}

export default nvhBenchmarkApi
