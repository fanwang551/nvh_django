import { defineStore } from 'pinia'
import mountIsolationApi from '@/api/mountIsolation'
import { ElMessage } from 'element-plus'

export const useVehicleMountIsolationQueryStore = defineStore('vehicleMountIsolationQuery', {
  state: () => ({
    // 查询条件
    selectedVehicles: [], // [{id, name, energy_type}]
    selectedPoints: [], // ["左前悬置", ...]
    selectedDirections: ['X', 'Y', 'Z'],

    // 选项
    vehicleOptions: [],
    measuringPointOptions: [],

    // 加载状态
    loadingVehicles: false,
    loadingPoints: false,
    loadingQuery: false,

    // 查询结果
    queryResult: null, // { energy_type, x_axis_label, data: [...] }
    testInfoCards: [] // [{ vehicle_id, vehicle_name, test_engineer, test_location, test_condition, test_date }]
  }),

  getters: {
    canQuery(state) {
      return state.selectedVehicles.length > 0 && state.selectedDirections.length > 0
    }
  },

  actions: {
    // 加载车型（去重，含能源类型）
    async loadVehicleModels() {
      this.loadingVehicles = true
      try {
        const res = await mountIsolationApi.getIsolationVehicleModels()
        this.vehicleOptions = res?.data || []
      } catch (e) {
        console.error('加载车型失败', e)
        this.vehicleOptions = []
        throw e
      } finally {
        this.loadingVehicles = false
      }
    },

    // 加载测点（基于多车型）
    async loadMeasuringPoints() {
      this.loadingPoints = true
      try {
        const ids = this.selectedVehicles.map(v => v.id)
        const res = await mountIsolationApi.getIsolationMeasuringPoints(ids)
        this.measuringPointOptions = res?.data || []
      } catch (e) {
        console.error('加载测点失败', e)
        this.measuringPointOptions = []
        throw e
      } finally {
        this.loadingPoints = false
      }
    },

    // 校验能源类型是否一致
    validateEnergyType() {
      if (this.selectedVehicles.length <= 1) return true
      const types = new Set(this.selectedVehicles.map(v => v.energy_type))
      if (types.size > 1) {
        ElMessage.error('只能选择相同能源类型的车型（燃油车或纯电/混动车）')
        return false
      }
      return true
    },

    // 查询曲线数据 + 测试卡片
    async queryData() {
      if (!this.canQuery) {
        ElMessage.warning('请先选择车型与方向')
        return
      }
      if (!this.validateEnergyType()) {
        return
      }

      this.loadingQuery = true
      try {
        const payload = {
          vehicle_ids: this.selectedVehicles.map(v => v.id),
          measuring_points: this.selectedPoints,
          directions: this.selectedDirections
        }
        const [curveRes, infoRes] = await Promise.all([
          mountIsolationApi.queryIsolationData(payload),
          mountIsolationApi.getIsolationTestInfo(payload.vehicle_ids)
        ])

        this.queryResult = curveRes?.data || null
        this.testInfoCards = infoRes?.data || []
      } catch (e) {
        console.error('查询失败', e)
        this.queryResult = null
        this.testInfoCards = []
        throw e
      } finally {
        this.loadingQuery = false
      }
    },

    // 状态变更
    setSelectedVehicles(list) {
      this.selectedVehicles = list || []
    },
    setSelectedPoints(list) {
      this.selectedPoints = list || []
    },
    setSelectedDirections(list) {
      this.selectedDirections = list || []
    },

    reset() {
      this.selectedVehicles = []
      this.selectedPoints = []
      this.selectedDirections = ['X', 'Y', 'Z']
      this.measuringPointOptions = []
      this.queryResult = null
      this.testInfoCards = []
    },

    async initialize() {
      try {
        await this.loadVehicleModels()
      } catch (e) {
        console.error('初始化失败', e)
      }
    }
  }
})
