import { defineStore } from 'pinia'
import modalApi from '@/api/modal'

export const useAirtightnessImageQueryStore = defineStore('airtightnessImageQuery', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelIds: []
    },

    // 选项数据
    vehicleModelOptions: [],

    // 加载状态
    vehicleModelsLoading: false,
    queryLoading: false,

    // 查询结果
    imageDataList: [],

    // UI状态
    selectAllVehicles: false
  }),
  
  getters: {
    // 是否可以查询（允许查询全部或按车型筛选）
    canQuery: (state) => {
      return true
    },

    // 是否有查询结果
    hasResults: (state) => {
      return state.imageDataList.length > 0
    },

    // 选中的车型数量
    selectedVehicleCount: (state) => {
      return state.searchForm.vehicleModelIds.length
    },

    // 获取选中的车型名称
    selectedVehicleNames: (state) => {
      if (state.searchForm.vehicleModelIds.length === 0) return []
      return state.vehicleModelOptions
        .filter(item => state.searchForm.vehicleModelIds.includes(item.id))
        .map(item => item.vehicle_model_name)
    }
  },
  
  actions: {
    // 加载车型列表
    async loadVehicleModels() {
      try {
        this.vehicleModelsLoading = true
        const response = await modalApi.getVehicleModels()
        this.vehicleModelOptions = response.data || []
      } catch (error) {
        console.error('加载车型列表失败:', error)
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },

    // 查询气密性图片数据
    async queryImageData(vehicleModelIds = []) {
      try {
        this.queryLoading = true
        const params = {}

        // 如果选择了车型，添加到查询参数
        if (vehicleModelIds.length > 0) {
          params.vehicle_model_ids = vehicleModelIds.join(',')
        }

        const response = await modalApi.getAirtightnessImages(params)
        this.imageDataList = response.data || []

        return this.imageDataList
      } catch (error) {
        console.error('查询气密性图片数据失败:', error)
        throw error
      } finally {
        this.queryLoading = false
      }
    },
    
    // 设置车型选择
    setVehicleModels(vehicleIds) {
      this.searchForm.vehicleModelIds = vehicleIds
      this.updateSelectAllState()
    },
    
    // 更新全选状态
    updateSelectAllState() {
      if (this.searchForm.vehicleModelIds.length === 0) {
        this.selectAllVehicles = false
      } else if (this.searchForm.vehicleModelIds.length === this.vehicleModelOptions.length) {
        this.selectAllVehicles = true
      } else {
        this.selectAllVehicles = false
      }
    },
    
    // 清空所有状态
    resetState() {
      this.searchForm = {
        vehicleModelIds: []
      }
      this.imageDataList = []
      this.selectAllVehicles = false
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
    }
  }
})
