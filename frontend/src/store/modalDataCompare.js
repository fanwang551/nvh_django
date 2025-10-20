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
    compareResult: [],
    
    // 全量模态数据
    allModalData: [],
    
    // 筛选后的表格数据
    filteredTableData: []

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
        
        const params = {
          component_id: this.compareForm.componentId,
          vehicle_model_ids: this.compareForm.vehicleModelIds.join(','),
          test_statuses: testStatusesArray.join(','),
          mode_types: this.compareForm.modeTypes.join(',')
        }

        const response = await modalApi.compareModalData(params)
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
      // 当选择零件时，加载对应的振型类型
      if (componentId) {
        this.loadModeTypesByComponent(componentId)
      } else {
        this.modeTypeOptions = []
      }
    },
    
    // 处理车型选择变化
    handleVehicleModelChange(vehicleModelIds) {
      this.compareForm.vehicleModelIds = vehicleModelIds
    },
    
    // 处理测试状态选择变化
    handleTestStatusChange(testStatuses) {
      this.compareForm.testStatuses = testStatuses
    },
    
    // 处理振型类型选择变化
    handleModeTypeChange(modeTypes) {
      this.compareForm.modeTypes = modeTypes
    },
    
    // UI相关方法已移除：showModalShapeDialog, closeModalShapeDialog, switchDialogTab
    // 图表相关方法已移除：setChartInstance, clearDialogState
    // 这些方法现在由组件管理
    
    // 加载所有模态数据（单请求）
    async loadAllModalData() {
      try {
        // 一次性获取所有模态数据（后端已支持 all=1 返回拍平数据、不分页）
        const modalResponse = await modalApi.queryModalData({ all: 1 })

        // 兼容两种返回结构：分页(results)与统一(data)
        const rawList = modalResponse?.results || modalResponse?.data || []

        // 规范化数据结构与类型
        const allData = rawList.map(item => ({
          id: item.id,
          component_id: Number(item.component_id),
          component_name: item.component_name || '',
          vehicle_model_id: Number(item.vehicle_model_id),
          vehicle_model_name: item.vehicle_model_name || '',
          test_status: item.test_status || '',
          mode_type: item.mode_type || item.mode_shape_description || '',
          frequency: typeof item.frequency === 'number' ? item.frequency : (parseFloat(item.frequency) || 0),
          mode_shape_file: item.mode_shape_file || null,
          test_photo_file: item.test_photo_file || null,
          notes: item.notes || ''
        }))

        this.allModalData = allData
        this.filteredTableData = [...allData]

        // 本地生成筛选选项，避免额外请求
        const componentMap = new Map()
        const vehicleMap = new Map()
        const statusSet = new Set()

        allData.forEach(d => {
          if (d.component_id && d.component_name && !componentMap.has(d.component_id)) {
            componentMap.set(d.component_id, { id: d.component_id, component_name: d.component_name })
          }
          if (d.vehicle_model_id && d.vehicle_model_name && !vehicleMap.has(d.vehicle_model_id)) {
            vehicleMap.set(d.vehicle_model_id, { id: d.vehicle_model_id, vehicle_model_name: d.vehicle_model_name })
          }
          if (d.test_status) statusSet.add(d.test_status)
        })

        // 仅当尚未加载到对应选项时才覆盖，避免与其它地方加载冲突
        if (this.componentOptions.length === 0) {
          this.componentOptions = Array.from(componentMap.values()).sort((a, b) => a.component_name.localeCompare(b.component_name))
        }
        if (this.vehicleModelOptions.length === 0) {
          this.vehicleModelOptions = Array.from(vehicleMap.values()).sort((a, b) => a.vehicle_model_name.localeCompare(b.vehicle_model_name))
        }
        this.testStatusOptions = Array.from(statusSet.values())
        // 振型选项按零件动态加载，这里不预填充
        this.modeTypeOptions = []

      } catch (error) {
        console.error('加载所有模态数据失败:', error)
        throw error
      }
    },
    
    // 根据零件加载振型类型
    async loadModeTypesByComponent(componentId) {
      try {
        this.modeTypesLoading = true
        const response = await modalApi.getModeTypesByComponent({ component_id: componentId })
        this.modeTypeOptions = response.data || []
      } catch (error) {
        console.error('根据零件加载振型类型失败:', error)
        this.modeTypeOptions = []
      } finally {
        this.modeTypesLoading = false
      }
    },
    
    // 筛选表格数据
    filterTableData() {
      let filtered = [...this.allModalData]
      
      // 按零件筛选
      if (this.compareForm.componentId) {
        filtered = filtered.filter(item => item.component_id === this.compareForm.componentId)
      }
      
      // 按车型筛选
      if (this.compareForm.vehicleModelIds.length > 0) {
        filtered = filtered.filter(item => 
          this.compareForm.vehicleModelIds.includes(item.vehicle_model_id)
        )
      }
      
      // 按测试状态筛选
      if (this.compareForm.testStatuses.length > 0) {
        filtered = filtered.filter(item => 
          this.compareForm.testStatuses.includes(item.test_status)
        )
      }
      
      // 按振型筛选
      if (this.compareForm.modeTypes.length > 0) {
        filtered = filtered.filter(item => 
          this.compareForm.modeTypes.includes(item.mode_type)
        )
      }
      
      this.filteredTableData = filtered
    },
    
    // 初始化页面数据（在onMounted或onActivated时调用）
    async initializePageData() {
      // 如果没有零件选项，加载零件列表
      if (this.componentOptions.length === 0) {
        await this.loadComponents()
      }
    }
  }
})
