import { defineStore } from 'pinia'
import { wheelPerformanceApi } from '@/api/wheelPerformance'
import { modalApi } from '@/api/modal'

function normalizeForceTransferSignal(signal) {
  if (!signal) {
    return []
  }

  let parsedSignal = signal

  if (typeof parsedSignal === 'string') {
    try {
      parsedSignal = JSON.parse(parsedSignal)
    } catch (error) {
      console.warn('Failed to parse force_transfer_signal JSON', error)
      return []
    }
  }

  if (!parsedSignal || typeof parsedSignal !== 'object') {
    return []
  }

  const frequencies = Array.isArray(parsedSignal.frequency) ? parsedSignal.frequency : null
  const dBValues = Array.isArray(parsedSignal.dB)
    ? parsedSignal.dB
    : Array.isArray(parsedSignal.db)
      ? parsedSignal.db
      : null

  if (!frequencies || !dBValues) {
    return []
  }

  const length = Math.min(frequencies.length, dBValues.length)
  const result = []

  for (let i = 0; i < length; i += 1) {
    const frequency = Number(frequencies[i])
    const value = Number(dBValues[i])

    if (Number.isFinite(frequency) && Number.isFinite(value)) {
      result.push([frequency, value])
    }
  }

  return result
}


export const useWheelPerformanceQueryStore = defineStore('wheelPerformanceQuery', {
  state: () => ({
    filters: {
      vehicleModelId: null
    },
    vehicleModels: [],
    records: [],
    chartSeries: [],
    isLoading: false,
    error: null,
    rimModal: {
      visible: false,
      record: null,
      activeTab: 'curve'
    },
    forceModal: {
      visible: false,
      record: null
    }
  }),

  getters: {
    hasRecords: (state) => state.records.length > 0
  },

  actions: {
    async initialize() {
      await this.fetchVehicleModels()
      await this.fetchRecords()
    },

    async fetchVehicleModels() {
      try {
        const response = await modalApi.getVehicleModels()
        this.vehicleModels = response.data || []
        return this.vehicleModels
      } catch (error) {
        console.error('加载车型列表失败', error)
        this.vehicleModels = []
        throw error
      }
    },

    buildQueryParams() {
      const params = {}
      if (this.filters.vehicleModelId) {
        params.vehicle_model = this.filters.vehicleModelId
      }
      return params
    },

    async fetchRecords() {
      try {
        this.isLoading = true
        this.error = null

        const response = await wheelPerformanceApi.getWheelPerformanceList(
          this.buildQueryParams()
        )
        this.records = response.data || []
        this.buildChartSeries()
        return this.records
      } catch (error) {
        console.error('查询车轮性能数据失败', error)
        this.error = error.message || '数据获取失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    buildChartSeries() {
      this.chartSeries = this.records.map((record) => {
        const seriesData = normalizeForceTransferSignal(record.force_transfer_signal)
        const seriesName = [
          record.vehicle_model_name,
          record.tire_brand,
          record.tire_model
        ]
          .filter(Boolean)
          .join(' / ')
        return {
          name: seriesName || '未命名记录',
          data: seriesData
        }
      })
    },

    setFilters(patch) {
      this.filters = { ...this.filters, ...patch }
    },

    resetFilters() {
      this.filters = {
        vehicleModelId: null
      }
    },

    openRimModal(record) {
      this.rimModal = {
        visible: true,
        record,
        activeTab: 'curve'
      }
    },

    switchRimModalTab(tab) {
      this.rimModal = {
        ...this.rimModal,
        activeTab: tab
      }
    },

    closeRimModal() {
      this.rimModal = {
        visible: false,
        record: null,
        activeTab: 'curve'
      }
    },

    openForceModal(record) {
      this.forceModal = {
        visible: true,
        record
      }
    },

    closeForceModal() {
      this.forceModal = {
        visible: false,
        record: null
      }
    }
  }
})






