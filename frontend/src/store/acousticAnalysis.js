import { defineStore } from 'pinia'
import { modalApi } from '@/api/modal'
import { acousticApi } from '@/api/acoustic'

function toNumberArray(arr) {
  return Array.isArray(arr)
    ? arr
        .map((x) => {
          if (typeof x === 'number' && Number.isFinite(x)) return x
          if (typeof x === 'string') {
            const text = x.trim()
            if (!text) return null
            const n = Number(text)
            return Number.isFinite(n) ? n : null
          }
          return null
        })
        .filter((v) => v !== null)
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
      if (Array.isArray(res.data)) {
        this.measurePointOptions = res.data.map((item) => {
          // 兼容历史后端仅返回字符串数组的情况
          if (typeof item === 'string') {
            return {
              label: item,
              value: item,
              measureType: null
            }
          }
          const label = item.label ?? item.measure_point ?? item.value ?? ''
          const value = item.value ?? item.measure_point ?? label
          const measureType = item.measureType ?? item.measure_type ?? null
          return {
            label,
            value,
            measureType
          }
        })
      } else {
        this.measurePointOptions = []
      }
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
          const frequencies = toNumberArray(s.frequency)
          const values = toNumberArray(s.values ?? s.dB ?? [])
          const len = Math.min(frequencies.length, values.length)
          const pairs = []
          for (let i = 0; i < len; i += 1) {
            pairs.push([frequencies[i], values[i]])
          }
          return {
            name: s.name || '未命名',
            data: pairs,
            measureType: s.measure_type || 'noise',
            unit: s.unit || (s.measure_type === 'vibration' ? 'm/s²' : 'dB')
          }
        })

        // OA 系列
        const oaSeries = Array.isArray(data.oa_series) ? data.oa_series : []
        this.oaSeries = oaSeries.map((s) => {
          const t = toNumberArray(s.time)
          const values = toNumberArray(s.values ?? s.OA ?? [])
          const len = Math.min(t.length, values.length)
          const pairs = []
          for (let i = 0; i < len; i += 1) {
            pairs.push([t[i], values[i]])
          }
          return {
            name: s.name || '未命名',
            data: pairs,
            stats: s.stats || null,
            measureType: s.measure_type || 'noise',
            unit: s.unit || (s.measure_type === 'vibration' ? 'm/s²' : 'dB')
          }
        })

        // 表格
        const tableData = Array.isArray(data.table) ? data.table : []
        this.tableRows = tableData.map((row) => ({
          ...row,
          measureType: row.measure_type || 'noise'
        }))
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
