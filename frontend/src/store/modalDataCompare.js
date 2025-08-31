import { defineStore } from 'pinia'
import modalApi from '@/api/modal'

export const useModalDataCompareStore = defineStore('modalDataCompare', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelIds: [],
      partId: null,
      orderNumber: null
    },
    
    // 选项数据
    vehicleModelOptions: [],
    partOptions: [],
    
    // 加载状态
    vehicleModelsLoading: false,
    partsLoading: false,
    compareLoading: false,
    
    // 对比结果
    compareResult: [],
    
    // UI状态
    selectAllVehicles: false,
    
    // 弹窗状态
    modeShapeDialogVisible: false,
    currentModeShapeData: null,
    activeTab: 'animation', // 'animation' 或 'photo'
    
    // 图表状态
    chartInstance: null,
    chartInitialized: false
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelIds.length > 0 && 
             state.searchForm.partId && 
             state.searchForm.orderNumber
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
    
    // 加载零件列表
    async loadParts() {
      try {
        this.partsLoading = true
        const response = await modalApi.getParts()
        this.partOptions = response.data || []
      } catch (error) {
        console.error('加载零件列表失败:', error)
        throw error
      } finally {
        this.partsLoading = false
      }
    },
    
    // 生成对比数据
    async generateCompareData() {
      if (!this.canQuery) {
        throw new Error('请选择车型、零件和阶次')
      }
      
      try {
        this.compareLoading = true
        
        const data = {
          vehicle_model_ids: this.searchForm.vehicleModelIds.join(','),
          part_id: this.searchForm.partId,
          order_number: this.searchForm.orderNumber
        }
        
        const response = await modalApi.compareModalData(data)
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
      // 清空对比结果
      this.compareResult = []
      this.chartInitialized = false
    },
    
    // 设置零件
    setPart(partId) {
      this.searchForm.partId = partId
      // 清空对比结果
      this.compareResult = []
      this.chartInitialized = false
    },
    
    // 设置阶次
    setOrderNumber(orderNumber) {
      this.searchForm.orderNumber = orderNumber
      // 清空对比结果
      this.compareResult = []
      this.chartInitialized = false
    },
    
    // 全选/反选车型
    toggleSelectAllVehicles(checked) {
      if (checked) {
        this.searchForm.vehicleModelIds = this.vehicleModelOptions.map(v => v.id)
      } else {
        this.searchForm.vehicleModelIds = []
      }
      this.selectAllVehicles = checked
      // 清空对比结果
      this.compareResult = []
      this.chartInitialized = false
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
    
    // 显示模态振型弹窗
    showModeShapeDialog(data) {
      this.currentModeShapeData = data
      this.modeShapeDialogVisible = true
      this.activeTab = 'animation'
    },
    
    // 关闭模态振型弹窗
    closeModeShapeDialog() {
      this.modeShapeDialogVisible = false
      this.currentModeShapeData = null
      this.activeTab = 'animation'
    },
    
    // 切换弹窗标签页
    switchTab(tab) {
      this.activeTab = tab
    },
    
    // 设置图表实例
    setChartInstance(instance) {
      this.chartInstance = instance
      this.chartInitialized = !!instance
    },
    
    // 清空所有状态
    resetState() {
      this.searchForm = {
        vehicleModelIds: [],
        partId: null,
        orderNumber: null
      }
      this.compareResult = []
      this.selectAllVehicles = false
      this.modeShapeDialogVisible = false
      this.currentModeShapeData = null
      this.activeTab = 'animation'
      this.chartInitialized = false
      this.chartInstance = null
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
      
      if (this.partOptions.length === 0) {
        await this.loadParts()
      }
    }
  }
})
