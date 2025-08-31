import { defineStore } from 'pinia'
// 注意：这里暂时使用modal API，实际项目中需要创建对应的airtight API
import modalApi from '@/api/modal'

export const useAirtightTestChartStore = defineStore('airtightTestChart', {
  state: () => ({
    // 查询表单状态
    searchForm: {
      vehicleModelId: null,
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
    chartDataList: [],
    
    // 分页状态
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    
    // 图表状态
    chartInstance: null,
    chartInitialized: false,
    
    // 弹窗状态
    imageDialogVisible: false,
    currentImageData: null
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelId && state.searchForm.testType
    },

    // 是否有查询结果
    hasResults: (state) => {
      return state.chartDataList.length > 0
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

    // 查询测试图表数据
    async queryChartData(page = 1) {
      if (!this.canQuery) {
        throw new Error('请选择车型和测试类型')
      }

      try {
        this.queryLoading = true

        const params = {
          vehicle_model_id: this.searchForm.vehicleModelId,
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
        this.chartDataList = response.data.results || []
        this.pagination.total = response.data.count || 0
        this.pagination.currentPage = page
        
        return this.chartDataList
      } catch (error) {
        console.error('查询测试图表数据失败:', error)
        throw error
      } finally {
        this.queryLoading = false
      }
    },
    
    // 设置车型
    setVehicleModel(vehicleModelId) {
      this.searchForm.vehicleModelId = vehicleModelId
      // 清空结果
      this.chartDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
      this.chartInitialized = false
    },
    
    // 设置测试类型
    setTestType(testType) {
      this.searchForm.testType = testType
      // 清空结果
      this.chartDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
      this.chartInitialized = false
    },
    
    // 设置日期范围
    setDateRange(dateRange) {
      this.searchForm.dateRange = dateRange
      // 清空结果
      this.chartDataList = []
      this.pagination.currentPage = 1
      this.pagination.total = 0
      this.chartInitialized = false
    },
    
    // 切换页码
    changePage(page) {
      this.queryChartData(page)
    },
    
    // 改变页面大小
    changePageSize(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.currentPage = 1
      this.queryChartData(1)
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
        vehicleModelId: null,
        testType: null,
        dateRange: []
      }
      this.chartDataList = []
      this.pagination = {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
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
