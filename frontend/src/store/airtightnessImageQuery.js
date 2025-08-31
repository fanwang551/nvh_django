import { defineStore } from 'pinia'
// 注意：这里暂时使用modal API，实际项目中需要创建对应的airtight API
import modalApi from '@/api/modal'

export const useAirtightnessImageQueryStore = defineStore('airtightnessImageQuery', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelIds: [],
      testType: null,
      dateRange: []
    },
    
    // 选项数据
    vehicleModelOptions: [],
    testTypeOptions: [
      { value: 'leak_test', label: '泄漏量测试' },
      { value: 'pressure_test', label: '压力测试' },
      { value: 'flow_test', label: '流量测试' }
    ],
    
    // 加载状态
    vehicleModelsLoading: false,
    queryLoading: false,
    
    // 查询结果
    imageDataList: [],
    
    // 分页状态
    pagination: {
      currentPage: 1,
      pageSize: 12, // 图片展示通常用更大的页面大小
      total: 0
    },
    
    // UI状态
    selectAllVehicles: false,
    viewMode: 'grid', // 'grid' 或 'list'
    
    // 弹窗状态
    previewDialogVisible: false,
    currentPreviewImages: [],
    currentImageIndex: 0
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelIds.length > 0 && state.searchForm.testType
    },
    
    // 是否有查询结果
    hasResults: (state) => {
      return state.imageDataList.length > 0
    },
    
    // 选中的车型数量
    selectedVehicleCount: (state) => {
      return state.searchForm.vehicleModelIds.length
    },
    
    // 全选状态
    isAllVehiclesSelected: (state) => {
      return state.vehicleModelOptions.length > 0 && 
             state.searchForm.vehicleModelIds.length === state.vehicleModelOptions.length
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

    // 查询测试图片数据
    async queryImageData(page = 1) {
      if (!this.canQuery) {
        throw new Error('请选择车型和测试类型')
      }

      try {
        this.queryLoading = true

        const params = {
          vehicle_model_ids: this.searchForm.vehicleModelIds.join(','),
          test_type: this.searchForm.testType,
          page: page,
          page_size: this.pagination.pageSize
        }

        // 添加日期范围参数
        if (this.searchForm.dateRange && this.searchForm.dateRange.length === 2) {
          params.start_date = this.searchForm.dateRange[0]
          params.end_date = this.searchForm.dateRange[1]
        }

        // 注意：这里暂时使用modal API，实际项目中需要创建对应的方法
        const response = await modalApi.queryModalData(params)
        this.imageDataList = response.data.results || []
        this.pagination.total = response.data.count || 0
        this.pagination.currentPage = page
        
        return this.imageDataList
      } catch (error) {
        console.error('查询测试图片数据失败:', error)
        throw error
      } finally {
        this.queryLoading = false
      }
    },
    
    // 设置车型选择
    setVehicleModels(vehicleIds) {
      this.searchForm.vehicleModelIds = vehicleIds
      this.updateSelectAllState()
      // 清空结果
      this.imageDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
    },
    
    // 设置测试类型
    setTestType(testType) {
      this.searchForm.testType = testType
      // 清空结果
      this.imageDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
    },
    
    // 设置日期范围
    setDateRange(dateRange) {
      this.searchForm.dateRange = dateRange
      // 清空结果
      this.imageDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
    },
    
    // 全选/反选车型
    toggleSelectAllVehicles(checked) {
      if (checked) {
        this.searchForm.vehicleModelIds = this.vehicleModelOptions.map(v => v.id)
      } else {
        this.searchForm.vehicleModelIds = []
      }
      this.selectAllVehicles = checked
      // 清空结果
      this.imageDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
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
    
    // 切换页码
    changePage(page) {
      this.queryImageData(page)
    },
    
    // 改变页面大小
    changePageSize(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.currentPage = 1
      this.queryImageData(1)
    },
    
    // 切换视图模式
    switchViewMode(mode) {
      this.viewMode = mode
    },
    
    // 显示图片预览弹窗
    showPreviewDialog(images, startIndex = 0) {
      this.currentPreviewImages = images
      this.currentImageIndex = startIndex
      this.previewDialogVisible = true
    },
    
    // 关闭图片预览弹窗
    closePreviewDialog() {
      this.previewDialogVisible = false
      this.currentPreviewImages = []
      this.currentImageIndex = 0
    },
    
    // 切换预览图片
    switchPreviewImage(index) {
      if (index >= 0 && index < this.currentPreviewImages.length) {
        this.currentImageIndex = index
      }
    },
    
    // 上一张图片
    previousImage() {
      if (this.currentImageIndex > 0) {
        this.currentImageIndex--
      }
    },
    
    // 下一张图片
    nextImage() {
      if (this.currentImageIndex < this.currentPreviewImages.length - 1) {
        this.currentImageIndex++
      }
    },
    
    // 清空所有状态
    resetState() {
      this.searchForm = {
        vehicleModelIds: [],
        testType: null,
        dateRange: []
      }
      this.imageDataList = []
      this.pagination = {
        currentPage: 1,
        pageSize: 12,
        total: 0
      }
      this.selectAllVehicles = false
      this.viewMode = 'grid'
      this.previewDialogVisible = false
      this.currentPreviewImages = []
      this.currentImageIndex = 0
    },
    
    // 初始化页面数据
    async initializePageData() {
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
    }
  }
})
