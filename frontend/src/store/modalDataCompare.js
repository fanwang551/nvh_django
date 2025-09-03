import { defineStore } from 'pinia'
import modalApi from '@/api/modal'

export const useModalDataCompareStore = defineStore('modalDataCompare', {
  state: () => ({
    // 对比表单状态 - 需要保持的状态
    compareForm: {
      componentId: null,
      vehicleModelIds: [],
      testStatuses: [],
      modeTypes: []
    },
    
    // 选项数据 - 需要保持的状态
    componentOptions: [],
    vehicleModelOptions: [],
    testStatusOptions: [],
    modeTypeOptions: [],
    
    // 加载状态
    componentsLoading: false,
    vehicleModelsLoading: false,
    testStatusesLoading: false,
    modeTypesLoading: false,
    compareLoading: false,
    
    // 业务数据状态 - 对比结果
    compareResult: []

    // UI状态已移除：modalShapeDialogVisible, currentModalData, activeTab
    // 图表状态已移除：chartInstance, chartInitialized
    // 这些状态现在由组件管理
  }),
  
  getters: {
    // 是否可以执行对比
    canCompare: (state) => {
      return state.compareForm.componentId &&
             state.compareForm.vehicleModelIds.length > 0 &&
             state.compareForm.testStatuses.length > 0 &&
             state.compareForm.modeTypes.length > 0
    },
    
    // 是否有对比结果
    hasResults: (state) => {
      return state.compareResult.length > 0
    },
    
    // 测试状态是否为多选模式（单车型时可多选，多车型时单选）
    isTestStatusMultiple: (state) => {
      return state.compareForm.vehicleModelIds.length === 1
    },
    
    // 表格数据处理
    tableData: (state) => {
      if (!state.compareResult.length) return []
      
      // 按振型类型分组
      const groupedData = {}
      state.compareResult.forEach(item => {
        if (!groupedData[item.mode_type]) {
          groupedData[item.mode_type] = { modeType: item.mode_type }
        }
        groupedData[item.mode_type][item.display_name] = item.frequency
      })
      
      return Object.values(groupedData)
    },
    
    // 车型列数据
    vehicleColumns: (state) => {
      if (!state.compareResult.length) return []
      
      const uniqueVehicles = [...new Set(state.compareResult.map(item => item.display_name))]
      return uniqueVehicles.map(name => ({
        key: name,
        label: name
      }))
    }
  },
  
  actions: {
    // 加载零件列表
    async loadComponents() {
      try {
        this.componentsLoading = true
        const response = await modalApi.getComponents()
        this.componentOptions = response.data || []
      } catch (error) {
        console.error('加载零件列表失败:', error)
        throw error
      } finally {
        this.componentsLoading = false
      }
    },
    
    // 加载相关车型列表
    async loadRelatedVehicleModels(componentId) {
      try {
        this.vehicleModelsLoading = true
        const response = await modalApi.getRelatedVehicleModels({ component_id: componentId })
        this.vehicleModelOptions = response.data || []
      } catch (error) {
        console.error('加载相关车型失败:', error)
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },
    
    // 加载测试状态列表
    async loadTestStatuses() {
      try {
        this.testStatusesLoading = true
        const params = {
          component_id: this.compareForm.componentId,
          vehicle_model_ids: this.compareForm.vehicleModelIds.join(',')
        }
        const response = await modalApi.getTestStatuses(params)
        this.testStatusOptions = response.data || []
      } catch (error) {
        console.error('加载测试状态失败:', error)
        throw error
      } finally {
        this.testStatusesLoading = false
      }
    },
    
    // 加载振型类型列表
    async loadModeTypes() {
      try {
        this.modeTypesLoading = true
        
        // 处理testStatuses，确保它是数组格式
        const testStatusesArray = Array.isArray(this.compareForm.testStatuses)
          ? this.compareForm.testStatuses
          : [this.compareForm.testStatuses]
        
        const params = {
          component_id: this.compareForm.componentId,
          vehicle_model_ids: this.compareForm.vehicleModelIds.join(','),
          test_statuses: testStatusesArray.join(',')
        }
        const response = await modalApi.getModeTypes(params)
        this.modeTypeOptions = response.data || []
      } catch (error) {
        console.error('加载振型类型失败:', error)
        throw error
      } finally {
        this.modeTypesLoading = false
      }
    },
    
    // 生成对比数据
    async generateCompareData() {
      if (!this.canCompare) {
        throw new Error('请完善选择条件')
      }
      
      try {
        this.compareLoading = true
        
        // 处理testStatuses，确保它是数组格式
        const testStatusesArray = Array.isArray(this.compareForm.testStatuses)
          ? this.compareForm.testStatuses
          : [this.compareForm.testStatuses]
        
        const data = {
          component_id: this.compareForm.componentId,
          vehicle_model_ids: this.compareForm.vehicleModelIds.join(','),
          test_statuses: testStatusesArray.join(','),
          mode_types: this.compareForm.modeTypes.join(',')
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
    
    // 处理零件选择变化
    handleComponentChange(componentId) {
      this.compareForm.componentId = componentId
      // 重置后续选择
      this.compareForm.vehicleModelIds = []
      this.compareForm.testStatuses = []
      this.compareForm.modeTypes = []
      this.vehicleModelOptions = []
      this.testStatusOptions = []
      this.modeTypeOptions = []
      this.compareResult = []
      
      if (componentId) {
        this.loadRelatedVehicleModels(componentId)
      }
    },
    
    // 处理车型选择变化
    handleVehicleModelChange(vehicleModelIds) {
      this.compareForm.vehicleModelIds = vehicleModelIds
      // 重置后续选择
      this.compareForm.testStatuses = []
      this.compareForm.modeTypes = []
      this.testStatusOptions = []
      this.modeTypeOptions = []
      this.compareResult = []
      
      if (vehicleModelIds.length > 0) {
        this.loadTestStatuses()
      }
      
      // 根据业务规则调整测试状态选择模式
      if (!this.isTestStatusMultiple && this.compareForm.testStatuses.length > 1) {
        // 从多选变为单选时，只保留第一个选项
        this.compareForm.testStatuses = [this.compareForm.testStatuses[0]]
      }
    },
    
    // 处理测试状态选择变化
    handleTestStatusChange(testStatuses) {
      this.compareForm.testStatuses = testStatuses
      // 重置后续选择
      this.compareForm.modeTypes = []
      this.modeTypeOptions = []
      this.compareResult = []
      
      if (testStatuses.length > 0) {
        this.loadModeTypes()
      }
    },
    
    // 处理振型类型选择变化
    handleModeTypeChange(modeTypes) {
      this.compareForm.modeTypes = modeTypes
      // 清空对比结果
      this.compareResult = []
    },
    
    // UI相关方法已移除：showModalShapeDialog, closeModalShapeDialog, switchDialogTab
    // 图表相关方法已移除：setChartInstance, clearDialogState
    // 这些方法现在由组件管理
    
    // 初始化页面数据（在onMounted或onActivated时调用）
    async initializePageData() {
      // 如果没有零件选项，加载零件列表
      if (this.componentOptions.length === 0) {
        await this.loadComponents()
      }
    }
  }
})
