import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstancesQueryStore = defineStore('substancesQuery', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      vehicle_model_id: null,
      part_names: [],
      statuses: [],
      development_stages: [],
      test_date_range: null,
      test_order_no: '',
      sample_no: '',
      page: 1,
      page_size: 10
    },

    // 选项数据
    vehicle_models: [],
    part_names: [],
    status_options: [],
    development_stage_options: [],

    // 业务数据
    all_test_data: [],
    filtered_test_data: [],
    current_test_details: [],

    // 分页
    pagination: {
      current_page: 1,
      total_pages: 0,
      total_count: 0,
      page_size: 10
    },

    // 业务状态
    isLoading: false,
    error: null,
    vehicle_models_loading: false,
    part_names_loading: false,
    status_options_loading: false,
    development_stage_loading: false,
    query_loading: false,
    detail_loading: false
  }),

  getters: {
    // 是否有查询结果
    hasResults: (state) => {
      return state.filtered_test_data.length > 0
    },

    // 是否有全谱明细
    hasDetails: (state) => {
      return state.current_test_details.length > 0
    },

    // 获取分页后的数据
    paginatedData: (state) => {
      const start = (state.pagination.current_page - 1) * state.pagination.page_size
      const end = start + state.pagination.page_size
      return state.filtered_test_data.slice(start, end)
    }
  },

  actions: {
    // 获取车型选项
    async fetchVehicleModelOptions() {
      try {
        this.vehicle_models_loading = true
        const response = await substancesApi.getVehicleModelOptions()
        const data = response.data || []
        
        // 按 vehicle_model_id 去重，只保留唯一车型
        const uniqueVehicles = new Map()
        data.forEach(item => {
          if (!uniqueVehicles.has(item.value)) {
            // 提取车型名称（去掉 "-状态-阶段" 部分）
            const vehicleName = item.label.split('-')[0]
            uniqueVehicles.set(item.value, {
              value: item.value,
              label: vehicleName
            })
          }
        })
        
        // 转换为数组
        this.vehicle_models = Array.from(uniqueVehicles.values())
      } catch (error) {
        this.error = error.message
        console.error('获取车型选项失败:', error)
      } finally {
        this.vehicle_models_loading = false
      }
    },

    // 从已加载数据中提取零件名称选项
    extractPartNameOptions() {
      const uniquePartNames = [...new Set(
        this.all_test_data
          .map(item => item.sample_info?.part_name)
          .filter(name => name)
      )].sort()
      
      this.part_names = uniquePartNames.map(name => ({
        label: name,
        value: name
      }))
    },

    // 从已加载数据中提取状态选项
    extractStatusOptions() {
      const uniqueStatuses = [...new Set(
        this.all_test_data
          .map(item => item.sample_info?.status)
          .filter(status => status)
      )].sort()
      
      this.status_options = uniqueStatuses.map(status => ({
        label: status,
        value: status
      }))
    },

    // 从已加载数据中提取开发阶段选项
    extractDevelopmentStageOptions() {
      const uniqueStages = [...new Set(
        this.all_test_data
          .map(item => item.sample_info?.development_stage)
          .filter(stage => stage)
      )].sort()
      
      this.development_stage_options = uniqueStages.map(stage => ({
        label: stage,
        value: stage
      }))
    },

    // 加载所有测试数据
    async loadAllTestData() {
      try {
        this.query_loading = true
        this.error = null
        
        const response = await substancesApi.getTestList({ page_size: 10000 })
        this.all_test_data = response.data.results || []
        
        // 提取唯一选项
        this.extractPartNameOptions()
        this.extractStatusOptions()
        this.extractDevelopmentStageOptions()
        
        this.filterTestData()
      } catch (error) {
        this.error = error.message
        console.error('加载全谱检测数据失败:', error)
      } finally {
        this.query_loading = false
      }
    },

    // 过滤测试数据
    filterTestData() {
      let filtered = [...this.all_test_data]

      if (this.searchCriteria.vehicle_model_id) {
        filtered = filtered.filter(item => 
          item.sample_info?.vehicle_model?.id === this.searchCriteria.vehicle_model_id
        )
      }

      if (this.searchCriteria.part_names.length > 0) {
        filtered = filtered.filter(item =>
          this.searchCriteria.part_names.includes(item.sample_info?.part_name)
        )
      }

      if (this.searchCriteria.statuses.length > 0) {
        filtered = filtered.filter(item =>
          this.searchCriteria.statuses.includes(item.sample_info?.status)
        )
      }

      if (this.searchCriteria.development_stages.length > 0) {
        filtered = filtered.filter(item =>
          this.searchCriteria.development_stages.includes(item.sample_info?.development_stage)
        )
      }

      if (this.searchCriteria.test_date_range && this.searchCriteria.test_date_range.length === 2) {
        const [startDate, endDate] = this.searchCriteria.test_date_range
        filtered = filtered.filter(item => {
          if (!item.test_date) return false
          const testDate = new Date(item.test_date)
          return testDate >= startDate && testDate <= endDate
        })
      }

      if (this.searchCriteria.test_order_no) {
        const searchValue = this.searchCriteria.test_order_no.toLowerCase()
        filtered = filtered.filter(item =>
          item.sample_info?.test_order_no?.toLowerCase().includes(searchValue)
        )
      }

      if (this.searchCriteria.sample_no) {
        const searchValue = this.searchCriteria.sample_no.toLowerCase()
        filtered = filtered.filter(item =>
          item.sample_info?.sample_no?.toLowerCase().includes(searchValue)
        )
      }

      this.filtered_test_data = filtered
      this.pagination.total_count = filtered.length
      this.pagination.current_page = 1
    },

    // 获取全谱明细
    async fetchTestDetail(testId) {
      try {
        this.detail_loading = true
        const response = await substancesApi.getTestDetail({ test_id: testId })
        this.current_test_details = response.data || []
      } catch (error) {
        this.error = error.message
        console.error('获取全谱明细失败:', error)
        this.current_test_details = []
      } finally {
        this.detail_loading = false
      }
    },

    // 重置查询条件
    resetSearchCriteria() {
      this.searchCriteria = {
        vehicle_model_id: null,
        part_names: [],
        statuses: [],
        development_stages: [],
        test_date_range: null,
        test_order_no: '',
        sample_no: '',
        page: 1,
        page_size: 10
      }
      this.filterTestData()
    },

    // 更新分页
    setPage(page) {
      this.pagination.current_page = page
    },

    // 设置每页数量
    setPageSize(pageSize) {
      this.pagination.page_size = pageSize
      this.pagination.current_page = 1
    }
  }
})
