import { defineStore } from 'pinia'
import modalApi from '@/api/modal'
import mountIsolationApi from '@/api/mountIsolation'

export const useVehicleMountIsolationQueryStore = defineStore('vehicleMountIsolationQuery', {
  state: () => ({
    // 业务数据状态 - 查询表单状态
    searchForm: {
      vehicleModelId: null,
      measuringPoints: []
    },

    // 业务数据状态 - 选项数据
    vehicleModelOptions: [],
    measuringPointOptions: [],

    // 业务状态 - 加载状态
    vehicleModelsLoading: false,
    measuringPointsLoading: false,
    loading: false, // 查询时的加载状态

    // 业务数据状态 - 查询结果
    queryResult: {
      count: 0,
      results: []
    }
  }),

  getters: {
    // 业务逻辑：是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelId !== null
    },

    // 业务逻辑：是否有查询结果
    hasResults: (state) => {
      return state.queryResult.results.length > 0
    },

    // 业务逻辑：获取基本信息（从第一条数据中提取）
    basicInfo: (state) => {
      if (state.queryResult.results.length === 0) return null
      
      const firstResult = state.queryResult.results[0]
      return {
        vehicleModelName: firstResult.vehicle_model_name,
        testDate: firstResult.test_date,
        testLocation: firstResult.test_location,
        testEngineer: firstResult.test_engineer,
        suspensionType: firstResult.suspension_type,
        tirePressure: firstResult.tire_pressure,
        // 座椅导轨振动 AC OFF/ON
        seatVibXAcOff: firstResult.seat_vib_x_ac_off,
        seatVibYAcOff: firstResult.seat_vib_y_ac_off,
        seatVibZAcOff: firstResult.seat_vib_z_ac_off,
        seatVibXAcOn: firstResult.seat_vib_x_ac_on,
        seatVibYAcOn: firstResult.seat_vib_y_ac_on,
        seatVibZAcOn: firstResult.seat_vib_z_ac_on,
        // 方向盘振动 AC OFF/ON
        steeringVibXAcOff: firstResult.steering_vib_x_ac_off,
        steeringVibYAcOff: firstResult.steering_vib_y_ac_off,
        steeringVibZAcOff: firstResult.steering_vib_z_ac_off,
        steeringVibXAcOn: firstResult.steering_vib_x_ac_on,
        steeringVibYAcOn: firstResult.steering_vib_y_ac_on,
        steeringVibZAcOn: firstResult.steering_vib_z_ac_on,
        // 内噪声 AC OFF/ON
        cabinNoiseFrontAcOff: firstResult.cabin_noise_front_ac_off,
        cabinNoiseRearAcOff: firstResult.cabin_noise_rear_ac_off,
        cabinNoiseFrontAcOn: firstResult.cabin_noise_front_ac_on,
        cabinNoiseRearAcOn: firstResult.cabin_noise_rear_ac_on
      }
    }
  },

  actions: {
    // 业务逻辑：加载车型列表
    async loadVehicleModels() {
      this.vehicleModelsLoading = true
      try {
        const response = await modalApi.getVehicleModels()
        if (response.success) {
          this.vehicleModelOptions = response.data || []
        } else {
          throw new Error(response.message || '获取车型列表失败')
        }
      } catch (error) {
        console.error('加载车型列表失败:', error)
        this.vehicleModelOptions = []
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },

    // 业务逻辑：加载测点列表
    async loadMeasuringPoints(vehicleModelId = null) {
      this.measuringPointsLoading = true
      try {
        const params = {}
        if (vehicleModelId) {
          params.vehicle_model_id = vehicleModelId
        }
        
        const response = await mountIsolationApi.getMeasuringPoints(params)
        if (response.success) {
          this.measuringPointOptions = response.data || []
        } else {
          throw new Error(response.message || '获取测点列表失败')
        }
      } catch (error) {
        console.error('加载测点列表失败:', error)
        this.measuringPointOptions = []
        throw error
      } finally {
        this.measuringPointsLoading = false
      }
    },

    // 业务逻辑：查询数据
    async queryData() {
      if (!this.canQuery) {
        throw new Error('请先选择车型')
      }

      this.loading = true
      try {
        const params = {
          vehicle_model_id: this.searchForm.vehicleModelId
        }

        // 处理测点参数
        if (this.searchForm.measuringPoints.length > 0) {
          params.measuring_points = this.searchForm.measuringPoints.join(',')
        }

        const response = await mountIsolationApi.queryMountIsolationData(params)
        if (response.success) {
          this.queryResult = response.data || { count: 0, results: [] }
        } else {
          throw new Error(response.message || '查询失败')
        }
      } catch (error) {
        console.error('查询数据失败:', error)
        this.queryResult = { count: 0, results: [] }
        throw error
      } finally {
        this.loading = false
      }
    },

    // UI状态管理：设置车型ID
    setVehicleModelId(vehicleModelId) {
      this.searchForm.vehicleModelId = vehicleModelId
      // 车型变化时清空测点选择
      this.searchForm.measuringPoints = []
      // 清空查询结果
      this.queryResult = { count: 0, results: [] }
    },

    // UI状态管理：设置测点列表
    setMeasuringPoints(measuringPoints) {
      this.searchForm.measuringPoints = measuringPoints
    },

    // UI状态管理：重置搜索表单
    resetSearchForm() {
      this.searchForm = {
        vehicleModelId: null,
        measuringPoints: []
      }
      this.queryResult = { count: 0, results: [] }
    },

    // 初始化：组件挂载时调用
    async initialize() {
      try {
        await this.loadVehicleModels()
      } catch (error) {
        console.error('初始化失败:', error)
      }
    }
  }
})
