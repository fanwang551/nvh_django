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

  const freqRaw = Array.isArray(parsedSignal.frequency) ? parsedSignal.frequency : null
  const dbRaw = Array.isArray(parsedSignal.dB)
    ? parsedSignal.dB
    : Array.isArray(parsedSignal.db)
      ? parsedSignal.db
      : null

  let frequencies = freqRaw
  let dBValues = dbRaw

  // 自动识别 frequency/dB 是否对调：
  // - 频率应在 [0, 300]，步长约 0.5，最大值通常 >= 100
  // - dB 幅值通常在 [-100, 100]（常见 [-30, 30] 区间）
  if (freqRaw && dbRaw) {
    const nFreq = freqRaw.map(Number).filter((v) => Number.isFinite(v))
    const nDb = dbRaw.map(Number).filter((v) => Number.isFinite(v))
    const fMax = nFreq.length ? Math.max(...nFreq) : -Infinity
    const fMin = nFreq.length ? Math.min(...nFreq) : Infinity
    const dMax = nDb.length ? Math.max(...nDb) : -Infinity
    const dMin = nDb.length ? Math.min(...nDb) : Infinity
    const fRange = fMax - fMin
    const dRange = dMax - dMin

    const looksLikeFreq = Number.isFinite(fMax) && fMax >= 80 && fMax <= 1000
    const looksLikeDb = Number.isFinite(dMax) && dRange <= 120 && dMax <= 120 && dMin >= -120

    const freqLooksDb = Number.isFinite(fMax) && fRange <= 120 && fMax <= 120 && fMin >= -120
    const dbLooksFreq = Number.isFinite(dMax) && dMax >= 80

    // 如果 frequency 像 dB 且 dB 像 frequency，则交换
    if (!looksLikeFreq && !looksLikeDb && freqLooksDb && dbLooksFreq) {
      frequencies = nDb
      dBValues = nFreq
    } else {
      frequencies = nFreq
      dBValues = nDb
    }
  }

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
      vehicleModelIds: []
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
      // 仅初始化车型列表，避免在未选择车型时自动加载数据
      await this.fetchVehicleModels()
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
      const { vehicleModelIds } = this.filters

      if (Array.isArray(vehicleModelIds) && vehicleModelIds.length > 0) {
        params.vehicle_model_ids = vehicleModelIds.join(',')
      }
      return params
    },

    async fetchRecords() {
      try {
        this.isLoading = true
        this.error = null

        // 未选择车型时，不发起请求并清空数据/曲线
        const { vehicleModelIds } = this.filters
        if (!Array.isArray(vehicleModelIds) || vehicleModelIds.length === 0) {
          this.records = []
          this.chartSeries = []
          return []
        }

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
        const rawPairs = normalizeForceTransferSignal(record.force_transfer_signal)
          .filter((pair) => Array.isArray(pair) && pair.length >= 2 && Number.isFinite(Number(pair[0])) && Number.isFinite(Number(pair[1])))

        // 若频率最大值在 30~40 之间，视为以 0.5 为步长但单位偏小，按 10 倍缩放到 0-300 区间
        let scaleFactor = 1
        try {
          const fMax = rawPairs.reduce((m, p) => (p[0] > m ? p[0] : m), -Infinity)
          if (Number.isFinite(fMax) && fMax > 0 && fMax <= 40) {
            scaleFactor = 10
          }
        } catch (e) {}

        const seriesData = rawPairs
          .map((p) => [Number(p[0]) * scaleFactor, Number(p[1])])
          .filter((p) => p[0] >= 0 && p[0] <= 300)
          .sort((a, b) => a[0] - b[0])
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
        vehicleModelIds: []
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






