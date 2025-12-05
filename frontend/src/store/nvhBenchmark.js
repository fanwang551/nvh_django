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
    error: null,
    // 缓存控制
    vehicleOptionsLoaded: false,
    lastOverviewQueryKey: null
  }),

  getters: {
    hasOverview: (state) => !!(state.overview && Object.keys(state.overview).length > 0),
    
    selectedVehicleCount: (state) => {
      if (!state.filters.mainVehicleId) return 0
      return 1 + (state.filters.benchmarkVehicleIds?.length || 0)
    }
  },

  actions: {
    async initialize() {
      // 首次进入时才加载车型列表，后续切换标签复用缓存
      if (!this.vehicleOptionsLoaded || !this.vehicleOptions.length) {
        await this.fetchVehicleOptions()
      }
    },

    async fetchVehicleOptions({ force = false } = {}) {
      if (!force && this.vehicleOptionsLoaded && this.vehicleOptions.length) {
        return
      }

      this.vehicleLoading = true
      try {
        const response = await nvhBenchmarkApi.getVehicleModels()
        this.vehicleOptions = Array.isArray(response?.data) ? response.data : []
        this.vehicleOptionsLoaded = true
      } catch (err) {
        console.error('Failed to load vehicle options:', err)
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
      this.lastOverviewQueryKey = null
      this.error = null
    },

    /**
     * 获取概览数据
     * @param {boolean} force - 是否强制刷新，忽略缓存
     */
    async fetchOverview(force = false) {
      const { mainVehicleId, benchmarkVehicleIds, showChassis, showAcousticPackage } = this.filters
      
      if (!mainVehicleId) {
        this.overview = null
        this.lastOverviewQueryKey = null
        return
      }

      // 1. 构建 Payload
      // 注意：对数组进行排序，确保 [1,2] 和 [2,1] 生成相同的 Key
      const sortedBenchmarkIds = Array.isArray(benchmarkVehicleIds) 
        ? [...benchmarkVehicleIds].sort((a, b) => a - b) 
        : []

      const payload = {
        main_vehicle_id: mainVehicleId,
        benchmark_vehicle_ids: sortedBenchmarkIds,
        include_chassis: !!showChassis,
        include_acoustic_package: !!showAcousticPackage
      }

      // 2. 生成缓存 Key
      const queryKey = JSON.stringify(payload)

      // 3. 检查缓存
      // 如果不强制刷新，且有数据，且 Key 一致，则直接返回缓存
      if (!force && this.overview && this.lastOverviewQueryKey === queryKey) {
        return this.overview
      }

      // 4. 发起请求
      this.loading = true
      this.error = null
      try {
        const response = await nvhBenchmarkApi.getOverview(payload)
        this.overview = response?.data || null
        // 只有请求成功才更新 Key
        this.lastOverviewQueryKey = queryKey
        return this.overview
      } catch (error) {
        this.error = error?.message || '查询失败'
        // 请求失败不清除旧数据，或者根据业务需求决定是否清除
        // this.overview = null 
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
