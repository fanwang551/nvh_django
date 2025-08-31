import { defineStore } from 'pinia'
import modalApi from '@/api/modal'

export const useModalDataQueryStore = defineStore('modalDataQuery', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelId: null,
      partIds: []
    },
    
    // 选项数据
    vehicleModelOptions: [],
    partOptions: [],
    
    // 加载状态
    vehicleModelsLoading: false,
    partsLoading: false,
    queryLoading: false,
    
    // 查询结果
    modalDataList: [],
    
    // 分页状态
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    
    // UI状态
    selectAllParts: false,
    
    // 弹窗状态
    modeShapeDialogVisible: false,
    currentModeShapeData: null,
    activeTab: 'animation' // 'animation' 或 'photo'
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelId && state.searchForm.partIds.length > 0
    },
    
    // 是否有查询结果
    hasResults: (state) => {
      return state.modalDataList.length > 0
    },
    
    // 选中的零件数量
    selectedPartCount: (state) => {
      return state.searchForm.partIds.length
    },
    
    // 全选状态
    isAllPartsSelected: (state) => {
      return state.partOptions.length > 0 && 
             state.searchForm.partIds.length === state.partOptions.length
    },
    
    // 分页信息
    paginationInfo: (state) => {
      const start = (state.pagination.currentPage - 1) * state.pagination.pageSize + 1
      const end = Math.min(state.pagination.currentPage * state.pagination.pageSize, state.pagination.total)
      return {
        start,
        end,
        total: state.pagination.total
      }
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
    
    // 根据车型加载零件
    async loadPartsByVehicle(vehicleModelId) {
      if (!vehicleModelId) {
        this.partOptions = []
        return
      }
      
      try {
        this.partsLoading = true
        const response = await modalApi.getPartsByVehicle(vehicleModelId)
        this.partOptions = response.data || []
        
        // 默认选择所有零件
        this.searchForm.partIds = this.partOptions.map(part => part.id)
        this.selectAllParts = true
      } catch (error) {
        console.error('加载零件列表失败:', error)
        throw error
      } finally {
        this.partsLoading = false
      }
    },
    
    // 查询模态数据
    async queryModalData(page = 1) {
      if (!this.canQuery) {
        throw new Error('请选择车型和零件')
      }
      
      try {
        this.queryLoading = true
        
        const params = {
          vehicle_model_id: this.searchForm.vehicleModelId,
          part_ids: this.searchForm.partIds.join(','),
          page: page,
          page_size: this.pagination.pageSize
        }
        
        const response = await modalApi.queryModalData(params)
        this.modalDataList = response.data.results || []
        this.pagination.total = response.data.count || 0
        this.pagination.currentPage = page
        
        return this.modalDataList
      } catch (error) {
        console.error('查询模态数据失败:', error)
        throw error
      } finally {
        this.queryLoading = false
      }
    },
    
    // 设置车型
    setVehicleModel(vehicleModelId) {
      this.searchForm.vehicleModelId = vehicleModelId
      // 清空零件选择和结果
      this.searchForm.partIds = []
      this.selectAllParts = false
      this.modalDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
      
      // 加载对应车型的零件
      if (vehicleModelId) {
        this.loadPartsByVehicle(vehicleModelId)
      } else {
        this.partOptions = []
      }
    },
    
    // 设置零件选择
    setParts(partIds) {
      this.searchForm.partIds = partIds
      this.updateSelectAllState()
    },
    
    // 全选/反选零件
    toggleSelectAllParts(checked) {
      if (checked) {
        this.searchForm.partIds = this.partOptions.map(p => p.id)
      } else {
        this.searchForm.partIds = []
      }
      this.selectAllParts = checked
    },
    
    // 更新全选状态
    updateSelectAllState() {
      if (this.searchForm.partIds.length === 0) {
        this.selectAllParts = false
      } else if (this.searchForm.partIds.length === this.partOptions.length) {
        this.selectAllParts = true
      } else {
        this.selectAllParts = false
      }
    },
    
    // 切换页码
    changePage(page) {
      this.queryModalData(page)
    },
    
    // 改变页面大小
    changePageSize(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.currentPage = 1
      this.queryModalData(1)
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
    
    // 清空所有状态
    resetState() {
      this.searchForm = {
        vehicleModelId: null,
        partIds: []
      }
      this.modalDataList = []
      this.pagination = {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
      this.selectAllParts = false
      this.modeShapeDialogVisible = false
      this.currentModeShapeData = null
      this.activeTab = 'animation'
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
      
      // 如果已选择车型但零件列表为空，重新加载零件
      if (this.searchForm.vehicleModelId && this.partOptions.length === 0) {
        await this.loadPartsByVehicle(this.searchForm.vehicleModelId)
      }
    }
  }
})
