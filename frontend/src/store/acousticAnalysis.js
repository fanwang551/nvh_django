import { defineStore } from 'pinia'
import { modalApi } from '@/api/modal'
import { acousticApi } from '@/api/acoustic'

function toNumberArray(arr) {
  return Array.isArray(arr)
    ? arr
        .map((x) => Number(x))
        .filter((v) => Number.isFinite(v))
    : []
}

export const useAcousticAnalysisStore = defineStore('acousticAnalysis', {
  state: () => ({
    filters: {
      vehicleModelIds: [],
      workConditions: [],
      measurePoints: []
    },
    vehicleModels: [],
    workConditionOptions: [],
    measurePointOptions: [],
    spectrumSeries: [],
    oaSeries: [],
    tableRows: [],
    isLoading: false,
    error: null
  }),

  actions: {
    async initialize() {
      await this.fetchVehicleModels()
    },

    async fetchVehicleModels() {
      const res = await modalApi.getVehicleModels()
      this.vehicleModels = res.data || []
    },

    async fetchWorkConditions() {
      this.workConditionOptions = []
      this.measurePointOptions = []
      this.filters.workConditions = []
      this.filters.measurePoints = []
      if (!this.filters.vehicleModelIds?.length) return

      const params = { vehicle_model_ids: this.filters.vehicleModelIds.join(',') }
      const res = await acousticApi.getWorkConditions(params)
      this.workConditionOptions = Array.isArray(res.data) ? res.data : []
    },

    async fetchMeasurePoints() {
      this.measurePointOptions = []
      this.filters.measurePoints = []
      if (!this.filters.vehicleModelIds?.length || !this.filters.workConditions?.length) return

      const params = {
        vehicle_model_ids: this.filters.vehicleModelIds.join(','),
        work_conditions: this.filters.workConditions.join(',')
      }
      const res = await acousticApi.getMeasurePoints(params)
      this.measurePointOptions = Array.isArray(res.data) ? res.data : []
    },

    async query() {
      try {
        this.isLoading = true
        this.error = null

        const { vehicleModelIds, workConditions, measurePoints } = this.filters
        if (!vehicleModelIds.length || !workConditions.length || !measurePoints.length) {
          this.spectrumSeries = []
          this.oaSeries = []
          this.tableRows = []
          return
        }

        const payload = {
          vehicle_model_ids: vehicleModelIds,
          work_conditions: workConditions,
          measure_points: measurePoints
        }
        const res = await acousticApi.query(payload)
        const data = res?.data || {}

        // 频谱系列
        const specSeries = Array.isArray(data.spectrum_series) ? data.spectrum_series : []
        this.spectrumSeries = specSeries.map((s) => {
          const f = toNumberArray(s.frequency)
          const v = toNumberArray(s.dB)
          const len = Math.min(f.length, v.length)
          const pairs = []
          for (let i = 0; i < len; i += 1) {
            pairs.push([f[i], v[i]])
          }
          return { name: s.name || '未命名', data: pairs }
        })

        // OA 系列
        const oaSeries = Array.isArray(data.oa_series) ? data.oa_series : []
        this.oaSeries = oaSeries.map((s) => {
          const t = toNumberArray(s.time)
          const v = toNumberArray(s.OA)
          const len = Math.min(t.length, v.length)
          const pairs = []
          for (let i = 0; i < len; i += 1) {
            pairs.push([t[i], v[i]])
          }
          return { name: s.name || '未命名', data: pairs, stats: s.stats || null }
        })

        // 表格
        this.tableRows = Array.isArray(data.table) ? data.table : []
      } finally {
        this.isLoading = false
      }
    },

    setFilters(patch) {
      this.filters = { ...this.filters, ...patch }
    },

    resetFilters() {
      this.filters = { vehicleModelIds: [], workConditions: [], measurePoints: [] }
      this.workConditionOptions = []
      this.measurePointOptions = []
      this.spectrumSeries = []
      this.oaSeries = []
      this.tableRows = []
    }
  }
})

