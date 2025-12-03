import { defineStore } from 'pinia'
import { nvhBenchmarkApi } from '@/api/nvhBenchmark'

const createDefaultFilters = () => ({
  mainVehicleId: null,
  benchmarkVehicleIds: [],
  showChassis: false,
  showAcousticPackage: false
})

export const useNvhBenchmarkStore = defineStore('nvhBenchmark', {
  state: () => ({
    vehicleOptions: [],
    filters: createDefaultFilters(),
    overview: null,
    loading: false,
    vehicleLoading: false,
    error: null
  }),

  getters: {
    hasOverview: (state) => !!state.overview,
    selectedVehicleCount: (state) => {
      if (!state.filters.mainVehicleId) return 0
      return 1 + (state.filters.benchmarkVehicleIds?.length || 0)
    }
  },

  actions: {
    async initialize() {
      await this.fetchVehicleOptions()
    },

    async fetchVehicleOptions() {
      this.vehicleLoading = true
      try {
        const response = await nvhBenchmarkApi.getVehicleModels()
        this.vehicleOptions = Array.isArray(response?.data) ? response.data : []
      } finally {
        this.vehicleLoading = false
      }
    },

    getDefaultBenchmarkIds(mainVehicleId) {
      if (!mainVehicleId) return []
      const found = this.vehicleOptions.find((item) => item?.id === mainVehicleId)
      if (!found) return []
      const defaults = found?.default_benchmark_ids
      return Array.isArray(defaults) ? [...defaults] : []
    },

    setFilters(patch) {
      this.filters = {
        ...this.filters,
        ...patch
      }
    },

    resetFilters() {
      this.filters = createDefaultFilters()
      this.overview = null
      this.error = null
    },

    async fetchOverview() {
      const { mainVehicleId, benchmarkVehicleIds, showChassis, showAcousticPackage } = this.filters
      if (!mainVehicleId) {
        this.overview = null
        return
      }
      this.loading = true
      this.error = null
      try {
        const payload = {
          main_vehicle_id: mainVehicleId,
          benchmark_vehicle_ids: Array.isArray(benchmarkVehicleIds) ? benchmarkVehicleIds : [],
          include_chassis: !!showChassis,
          include_acoustic_package: !!showAcousticPackage
        }
        const response = await nvhBenchmarkApi.getOverview(payload)
        this.overview = response?.data || null
      } catch (error) {
        this.error = error?.message || '查询失败'
        this.overview = null
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
