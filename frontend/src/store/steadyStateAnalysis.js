import { defineStore } from 'pinia'
import { modalApi } from '@/api/modal'
import { acousticApi } from '@/api/acoustic'
import { steadyStateApi } from '@/api/steadyStateAnalysis'

const createDefaultFilters = () => ({
  vehicleModelIds: [],
  workConditions: [],
  measurePoints: []
})

const normalizeNumericValue = (value) => {
  if (value === null || value === undefined || value === '') return null
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

const normalizeValueList = (values) => (Array.isArray(values) ? values.map((item) => normalizeNumericValue(item)) : [])

export const useSteadyStateAnalysisStore = defineStore('steadyStateAnalysis', {
  state: () => ({
    filters: createDefaultFilters(),
    vehicleModels: [],
    workConditionOptions: [],
    measurePointOptions: [],
    charts: [],
    isLoading: false,
    error: null
  }),

  actions: {
    async initialize() {
      await this.fetchVehicleModels()
    },

    async fetchVehicleModels() {
      const res = await modalApi.getVehicleModels()
      this.vehicleModels = res?.data || []
    },

    async fetchWorkConditions() {
      this.workConditionOptions = []
      this.measurePointOptions = []
      this.filters.workConditions = []
      this.filters.measurePoints = []
      if (!this.filters.vehicleModelIds?.length) return

      const params = { vehicle_model_ids: this.filters.vehicleModelIds.join(',') }
      const res = await acousticApi.getWorkConditions(params)
      this.workConditionOptions = Array.isArray(res?.data) ? res.data : []
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
      if (!Array.isArray(res?.data)) {
        this.measurePointOptions = []
        return
      }
      this.measurePointOptions = res.data.map((item) => {
        if (typeof item === 'string') {
          return { label: item, value: item, measureType: null }
        }
        const label = item.label ?? item.measure_point ?? item.value ?? ''
        const value = item.value ?? item.measure_point ?? label
        const measureType = item.measureType ?? item.measure_type ?? null
        return { label, value, measureType }
      })
    },

    async query() {
      const { vehicleModelIds, workConditions, measurePoints } = this.filters
      if (!vehicleModelIds.length || !workConditions.length || !measurePoints.length) {
        this.charts = []
        return
      }

      const payload = {
        vehicle_model_ids: vehicleModelIds,
        work_conditions: workConditions,
        measure_points: measurePoints
      }

      this.isLoading = true
      this.error = null
      try {
        const res = await steadyStateApi.query(payload)
        const charts = Array.isArray(res?.data?.charts) ? res.data.charts : []
        this.charts = charts.map((chart) => ({
          chartKey: chart.chart_key || `${chart.measure_type || 'chart'}_${chart.metric || 'metric'}`,
          title: chart.title || '对比图',
          unit: chart.unit || '',
          measureType: chart.measure_type || '',
          metric: chart.metric || '',
          workConditions: Array.isArray(chart.work_conditions) ? chart.work_conditions : [],
          series: Array.isArray(chart.series)
            ? chart.series.map((series) => ({
                name: series.name || '未命名',
                vehicleModelName: series.vehicle_model_name || '',
                measurePoint: series.measure_point || '',
                measureType: series.measure_type || '',
                metric: series.metric || '',
                values: normalizeValueList(series.values)
              }))
            : []
        }))
      } catch (error) {
        this.error = error?.message ?? '查询失败'
        this.charts = []
        throw error
      } finally {
        this.isLoading = false
      }
    },

    setFilters(patch) {
      this.filters = { ...this.filters, ...patch }
    },

    resetFilters() {
      this.filters = createDefaultFilters()
      this.workConditionOptions = []
      this.measurePointOptions = []
      this.charts = []
      this.error = null
    }
  }
})
