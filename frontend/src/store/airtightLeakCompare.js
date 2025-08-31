import { defineStore } from 'pinia'
// 注意：这里暂时使用modal API，实际项目中需要创建对应的airtight API
import modalApi from '@/api/modal'

export const useAirtightLeakCompareStore = defineStore('airtightLeakCompare', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelIds: [],
      testCondition: null
    },
    
    // 选项数据
    vehicleModelOptions: [],
    testConditionOptions: [
      { value: 'normal', label: '常规测试' },
      { value: 'extreme', label: '极限测试' }
    ],
    
    // 加载状态
    vehicleModelsLoading: false,
    compareLoading: false,
    
    // 对比结果
    compareResult: [],
    
    // UI状态
    selectAllVehicles: false,
    
    // 图表状态
    chartInstance: null,
    chartInitialized: false,
    
    // 弹窗状态
    detailDialogVisible: false,
    currentDetailData: null
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelIds.length > 0 && state.searchForm.testCondition
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

    // 生成对比数据
    async generateCompareData() {
      if (!this.canQuery) {
        throw new Error('请选择车型和测试条件')
      }

      try {
        this.compareLoading = true

        const data = {
          vehicle_model_ids: this.searchForm.vehicleModelIds.join(','),
          test_condition: this.searchForm.testCondition
        }

        // 注意：这里暂时使用modal API，实际项目中需要创建对应的方法
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
    
    // 设置测试条件
    setTestCondition(condition) {
      this.searchForm.testCondition = condition
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
    
    // 显示详情弹窗
    showDetailDialog(data) {
      this.currentDetailData = data
      this.detailDialogVisible = true
    },
    
    // 关闭详情弹窗
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.currentDetailData = null
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
        testCondition: null
      }
      this.compareResult = []
      this.selectAllVehicles = false
      this.detailDialogVisible = false
      this.currentDetailData = null
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
