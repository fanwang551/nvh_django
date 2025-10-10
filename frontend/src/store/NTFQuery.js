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
    measurementPointOptions: [],
    positionOptions: [],
    directionOptions: [],
    selectedVehicleIds: [],
    selectedPoints: [],
    selectedPositions: [],
    selectedDirections: [],
    vehicleCards: [],
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
    hasData: (state) => state.tableRows.length > 0
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
      this.seatColumns = []
      this.tableRows = []
      this.heatmap = { frequency: [], points: [], matrix: [] }
      this.vehicleCards = []
      this.error = null
    },

    async fetchFilters() {
      const params = {}
      if (Array.isArray(this.selectedVehicleIds) && this.selectedVehicleIds.length) {
        params.vehicle_ids = this.selectedVehicleIds.join(',')
      }
      // 注意：不要传入已选测点进行自我过滤，否则会导致测点选项被收缩为已选项，
      // 从而在界面上表现为“只能单选”的错觉。仅依据车型（及位置/方向）收敛可选项即可。
      if (Array.isArray(this.selectedPositions) && this.selectedPositions.length) {
        params.positions = this.selectedPositions.join(',')
      }
      if (Array.isArray(this.selectedDirections) && this.selectedDirections.length) {
        params.directions = this.selectedDirections.join(',')
      }
      try {
        const res = await NtfApi.getFilters(params)
        const data = res.data || {}
        this.measurementPointOptions = Array.isArray(data.measurement_points) ? data.measurement_points : []
        this.positionOptions = Array.isArray(data.positions) ? data.positions : []
        this.directionOptions = Array.isArray(data.directions) ? data.directions : []
        return data
      } catch (error) {
        console.error('加载过滤项失败', error)
        this.measurementPointOptions = []
        this.positionOptions = []
        this.directionOptions = []
        throw error
      }
    },

    async fetchMeasurementPoints() {
      const ids = Array.isArray(this.selectedVehicleIds) && this.selectedVehicleIds.length
        ? this.selectedVehicleIds.join(',')
        : ''
      try {
        const res = await NtfApi.getMeasurementPoints(ids ? { vehicle_ids: ids } : {})
        this.measurementPointOptions = Array.isArray(res.data) ? res.data : []
        return this.measurementPointOptions
      } catch (error) {
        console.error('加载测点列表失败', error)
        this.measurementPointOptions = []
        throw error
      }
    },

    async multiQuery() {
      if (!Array.isArray(this.selectedVehicleIds) || this.selectedVehicleIds.length === 0) {
        this.resetData()
        return null
      }
      try {
        this.isLoading = true
        this.error = null
        const params = { vehicle_ids: this.selectedVehicleIds.join(',') }
        if (Array.isArray(this.selectedPoints) && this.selectedPoints.length) {
          params.points = this.selectedPoints.join(',')
        }
        if (Array.isArray(this.selectedPositions) && this.selectedPositions.length) {
          params.positions = this.selectedPositions.join(',')
        }
        if (Array.isArray(this.selectedDirections) && this.selectedDirections.length) {
          params.directions = this.selectedDirections.join(',')
        }
        const res = await NtfApi.multiQuery(params)
        const data = res.data || {}
        this.seatColumns = Array.isArray(data.seat_columns) ? data.seat_columns : []
        this.tableRows = Array.isArray(data.results) ? data.results : []
        this.vehicleCards = Array.isArray(data.vehicles) ? data.vehicles : []
        const heatmap = data.heatmap || {}
        this.heatmap = {
          frequency: Array.isArray(heatmap.frequency) ? heatmap.frequency.map((x) => Number(x)) : [],
          points: Array.isArray(heatmap.points) ? heatmap.points : [],
          matrix: normalizeHeatmapMatrix(heatmap.matrix)
        }
        return data
      } catch (error) {
        console.error('加载NTF综合查询失败', error)
        this.error = error.message || '加载失败'
        this.resetData()
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})



