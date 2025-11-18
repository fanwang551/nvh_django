import { defineStore } from 'pinia'
import { modalApi } from '@/api/modal'
import { dynamicNoiseApi } from '@/api/dynamicNoise'

const createDefaultFilters = () => ({
  vehicleModelIds: [],
  workConditions: [],
  measurePoints: [],
  page: 1,
  pageSize: 10
})

export const useDynamicNoiseAnalysisStore = defineStore('dynamicNoiseAnalysis', {
  state: () => ({
    filters: createDefaultFilters(),
    vehicleModels: [],
    workConditionOptions: [],
    measurePointOptions: [],
    soundPressureSeries: [],
    speechClaritySeries: [],
    axisTypes: [],
    legend: [],
    table: {
      count: 0,
      page: 1,
      pageSize: 10,
      results: []
    },
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
      const res = await dynamicNoiseApi.getWorkConditions(params)
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
      const res = await dynamicNoiseApi.getMeasurePoints(params)
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
      const { vehicleModelIds, workConditions, measurePoints, page, pageSize } = this.filters
      if (!vehicleModelIds.length || !workConditions.length || !measurePoints.length) {
        this.soundPressureSeries = []
        this.speechClaritySeries = []
        this.axisTypes = []
        this.legend = []
        this.table = { count: 0, page: 1, pageSize: this.filters.pageSize, results: [] }
        return
      }
      const payload = {
        vehicle_model_ids: vehicleModelIds,
        work_conditions: workConditions,
        measure_points: measurePoints,
        page,
        page_size: pageSize
      }
      this.isLoading = true
      this.error = null
      try {
        const res = await dynamicNoiseApi.query(payload)
        const data = res?.data || {}
        this.soundPressureSeries = Array.isArray(data.sound_pressure) ? data.sound_pressure : []
        this.speechClaritySeries = Array.isArray(data.speech_clarity) ? data.speech_clarity : []
        this.axisTypes = Array.isArray(data.axis_types) ? data.axis_types : []
        this.legend = Array.isArray(data.legend) ? data.legend : []
        const table = data.table || {}
        const results = Array.isArray(table.results) ? table.results : []
        this.table = {
          count: Number(table.count) || results.length,
          page: Number(table.page) || page,
          pageSize: Number(table.page_size) || pageSize,
          results
        }
      } catch (error) {
        this.error = error?.message || '查询失败'
        this.soundPressureSeries = []
        this.speechClaritySeries = []
        this.axisTypes = []
        this.legend = []
        this.table = { count: 0, page: 1, pageSize: pageSize, results: [] }
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
      this.soundPressureSeries = []
      this.speechClaritySeries = []
      this.axisTypes = []
      this.legend = []
      this.table = { count: 0, page: 1, pageSize: 10, results: [] }
      this.error = null
    }
  }
})
