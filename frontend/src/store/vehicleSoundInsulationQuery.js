import { defineStore } from 'pinia'
import { soundInsulationApi } from '@/api/soundInsulation'

export const useVehicleSoundInsulationQueryStore = defineStore('vehicleSoundInsulationQuery', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelIds: []
    },
    
    // 数据状态
    vehicleModelOptions: [],
    compareResult: [],
    
    // 加载状态
    vehicleModelsLoading: false,
    compareLoading: false,
    
    // UI状态
    selectAllVehicles: false,
    
    // 弹窗状态
    imageDialogVisible: false,
    currentImageData: null,
    
    // 图表状态
    chartInstance: null,
    chartInitialized: false
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelIds.length > 0
    },
    
    // 是否有查询结果
    hasResults: (state) => {
      return state.compareResult.length > 0
    },
    
    // 选中的车型数量
    selectedVehicleCount: (state) => {
      return state.searchForm.vehicleModelIds.length
    },
    
    // 全选状态
    isAllVehiclesSelected: (state) => {
      return state.vehicleModelOptions.length > 0 && 
             state.searchForm.vehicleModelIds.length === state.vehicleModelOptions.length
    }
  },
  
  actions: {
    // 加载有隔声量数据的车型列表
    async loadVehicleModels() {
      try {
        this.vehicleModelsLoading = true
        const response = await soundInsulationApi.getVehiclesWithSoundData()
        this.vehicleModelOptions = response.data || []
      } catch (error) {
        console.error('加载车型列表失败:', error)
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },
    
    // 生成对比数据
    async generateCompareData() {
      if (!this.canQuery) {
        throw new Error('请选择车型')
      }
      
      try {
        this.compareLoading = true
        
        const data = {
          vehicle_model_ids: this.searchForm.vehicleModelIds.join(',')
        }
        
        const response = await soundInsulationApi.compareVehicleSoundInsulationData(data)
        this.compareResult = response.data || []
        
        return this.compareResult
      } catch (error) {
        console.error('生成对比数据失败:', error)
        throw error
      } finally {
        this.compareLoading = false
      }
    },
    
    // 设置车型选择
    setVehicleModels(vehicleIds) {
      this.searchForm.vehicleModelIds = vehicleIds
      this.updateSelectAllState()
    },
    
    // 全选/反选车型
    toggleSelectAllVehicles(checked) {
      if (checked) {
        this.searchForm.vehicleModelIds = this.vehicleModelOptions.map(v => v.id)
      } else {
        this.searchForm.vehicleModelIds = []
      }
      this.selectAllVehicles = checked
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
    
    // 显示图片弹窗
    showImageDialog(data) {
      this.currentImageData = data
      this.imageDialogVisible = true
    },
    
    // 关闭图片弹窗
    closeImageDialog() {
      this.imageDialogVisible = false
      this.currentImageData = null
    },
    
    // 设置图表实例
    setChartInstance(instance) {
      this.chartInstance = instance
      this.chartInitialized = !!instance
    },
    
    // 清空所有状态
    resetState() {
      this.searchForm = {
        vehicleModelIds: []
      }
      this.compareResult = []
      this.selectAllVehicles = false
      this.imageDialogVisible = false
      this.currentImageData = null
      this.chartInitialized = false
      this.chartInstance = null
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
    }
  }
})
