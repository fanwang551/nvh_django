import { defineStore } from 'pinia'
import modalApi from '@/api/modal'

export const useModalDataQueryStore = defineStore('modalDataQuery', {
  state: () => ({
    // 业务数据状态 - 查询表单状态
    searchForm: {
      vehicleModelId: null,
      componentIds: []
    },

    // 业务数据状态 - 选项数据
    vehicleModelOptions: [],
    componentOptions: [],

    // 业务状态 - 加载状态
    vehicleModelsLoading: false,
    componentsLoading: false,
    loading: false, // 查询时的加载状态

    // 业务数据状态 - 查询结果
    modalDataResult: {
      count: 0,
      results: []
    },

    // 业务状态 - 分页状态
    currentPage: 1,
    pageSize: 10

    // UI状态已移除：modalShapeDialogVisible, currentModalData, activeTab
    // 这些状态现在由组件管理
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelId !== null
    },
    
    // 是否有查询结果
    hasResults: (state) => {
      return state.modalDataResult.results.length > 0
    },
    
    // 选中的零件数量
    selectedComponentCount: (state) => {
      return state.searchForm.componentIds.length
    },
    
    // 总结果数
    totalCount: (state) => {
      return state.modalDataResult.count || 0
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
    async loadComponents(vehicleModelId = null) {
      try {
        this.componentsLoading = true
        const params = vehicleModelId ? { vehicle_model_id: vehicleModelId } : {}
        const response = await modalApi.getComponents(params)
        this.componentOptions = response.data || []
        
        // 如果有车型选择，默认选中所有零件
        if (vehicleModelId && this.componentOptions.length > 0) {
          this.searchForm.componentIds = this.componentOptions.map(item => item.id)
        }
      } catch (error) {
        console.error('加载零件列表失败:', error)
        throw error
      } finally {
        this.componentsLoading = false
      }
    },
    
    // 车型变化处理
    async handleVehicleModelChange(vehicleModelId) {
      this.searchForm.vehicleModelId = vehicleModelId
      if (vehicleModelId) {
        await this.loadComponents(vehicleModelId)
      } else {
        this.componentOptions = []
        this.searchForm.componentIds = []
      }
      // 清空之前的查询结果
      this.modalDataResult = { count: 0, results: [] }
    },
    
    // 查询模态数据
    async queryModalData(page = null) {
      if (!this.canQuery) {
        throw new Error('请先选择车型')
      }
      
      try {
        this.loading = true
        
        const currentPageToUse = page || this.currentPage
        
        const params = {
          vehicle_model_id: this.searchForm.vehicleModelId,
          page: currentPageToUse,
          page_size: this.pageSize
        }
        
        // 如果选择了零件，添加到查询参数
        if (this.searchForm.componentIds.length > 0) {
          params.component_ids = this.searchForm.componentIds.join(',')
        }
        
        const response = await modalApi.queryModalData(params)
        this.modalDataResult = response
        
        if (page) {
          this.currentPage = page
        }
        
        return this.modalDataResult
      } catch (error) {
        console.error('查询模态数据失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 分页处理
    async handlePageChange(page) {
      this.currentPage = page
      if (this.searchForm.vehicleModelId) {
        await this.queryModalData(page)
      }
    },
    
    // 每页大小变化处理
    async handlePageSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      if (this.searchForm.vehicleModelId) {
        await this.queryModalData(1)
      }
    },
    
    // UI相关方法已移除：viewModalShape, closeModalShapeDialog, switchDialogTab
    // 这些方法现在由组件管理
    
    // 设置零件选择
    setComponentIds(componentIds) {
      this.searchForm.componentIds = componentIds
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
      
      // 如果已选择车型但零件列表为空，重新加载零件
      if (this.searchForm.vehicleModelId && this.componentOptions.length === 0) {
        await this.loadComponents(this.searchForm.vehicleModelId)
      }
    },
    
    // 业务逻辑：重置业务状态
    resetState() {
      this.searchForm = {
        vehicleModelId: null,
        componentIds: []
      }
      this.modalDataResult = {
        count: 0,
        results: []
      }
      this.currentPage = 1
      this.pageSize = 10
      // UI状态重置已移除，现在由组件管理
    }
  }
})
