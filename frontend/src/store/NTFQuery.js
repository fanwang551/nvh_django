import { defineStore } from 'pinia'
import { NtfApi } from '@/api/NTF'
import { modalApi } from '@/api/modal'

function normalizeHeatmapMatrix(matrix = []) {
  if (!Array.isArray(matrix)) {
    return []
  }
  return matrix
    .map((row) => (Array.isArray(row) ? row.map((value) => Number(value)) : []))
}

export const useNTFQueryStore = defineStore('NTFQuery', {
  state: () => ({
    vehicleOptions: [],
    selectedVehicleId: null,
    detail: null,
    seatColumns: [],
    tableRows: [],
    heatmap: {
      frequency: [],
      points: [],
      matrix: []
    },
    isLoading: false,
    error: null
  }),

  getters: {
    hasData: (state) => Boolean(state.detail && state.tableRows.length > 0)
  },

  actions: {
    async fetchVehicleOptions() {
      try {
        const response = await modalApi.getVehicleModels()
        this.vehicleOptions = response.data || []
        return this.vehicleOptions
      } catch (error) {
        console.error('加载车型列表失败', error)
        this.vehicleOptions = []
        throw error
      }
    },

    resetData() {
      this.selectedVehicleId = null
      this.detail = null
      this.seatColumns = []
      this.tableRows = []
      this.heatmap = {
        frequency: [],
        points: [],
        matrix: []
      }
      this.error = null
    },

    async loadByVehicle(vehicleId) {
      if (!vehicleId) {
        this.selectedVehicleId = null
        this.resetData()
        return null
      }

      try {
        this.isLoading = true
        this.error = null
        this.selectedVehicleId = vehicleId

        const response = await NtfApi.getDetailByVehicle(vehicleId)
        const detail = response.data || null

        if (!detail) {
          this.resetData()
          return null
        }

        this.detail = detail
        this.seatColumns = Array.isArray(detail.seat_columns) ? detail.seat_columns : []
        this.tableRows = Array.isArray(detail.results) ? detail.results : []

        const heatmap = detail.heatmap || {}
        this.heatmap = {
          frequency: Array.isArray(heatmap.frequency) ? heatmap.frequency.map((item) => Number(item)) : [],
          points: Array.isArray(heatmap.points) ? heatmap.points : [],
          matrix: normalizeHeatmapMatrix(heatmap.matrix)
        }

        return detail
      } catch (error) {
        console.error('加载NTF详情失败', error)
        this.error = error.message || '加载失败'
        this.resetData()
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})



