import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstancesQueryStore = defineStore('substancesQuery', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      project_name: null,
      part_names: [],
      statuses: [],
      development_stages: [],
      test_date_range: null,
      test_order_no: '',
      sample_no: [],  // 改为数组以支持多选
      page: 1,
      page_size: 10
    },

    // 选项数据
    vehicle_models: [],
    part_names: [],
    status_options: [],
    development_stage_options: [],
    sample_no_options: [],  // 样品编号选项（联动筛选）

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
    sample_no_options_loading: false,  // 样品编号选项加载状态
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
        // 直接使用后端返回（value 为项目名称，label 为 项目-委托单-样品）
        this.vehicle_models = data
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

    // 获取样品编号选项（根据项目名称联动筛选）
    async fetchSampleNoOptions(projectNames = []) {
      try {
        this.sample_no_options_loading = true
        const response = await substancesApi.getSampleNoOptions(projectNames)
        this.sample_no_options = response.data || []
      } catch (error) {
        this.error = error.message
        console.error('获取样品编号选项失败:', error)
        this.sample_no_options = []
      } finally {
        this.sample_no_options_loading = false
      }
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

      if (this.searchCriteria.project_name) {
        filtered = filtered.filter(item =>
          item.sample_info?.project_name === this.searchCriteria.project_name
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

      // 样品编号筛选：支持多选（数组）或手动输入（字符串）
      if (this.searchCriteria.sample_no) {
        if (Array.isArray(this.searchCriteria.sample_no) && this.searchCriteria.sample_no.length > 0) {
          // 多选模式：数组匹配
          filtered = filtered.filter(item =>
            this.searchCriteria.sample_no.includes(item.sample_info?.sample_no)
          )
        } else if (typeof this.searchCriteria.sample_no === 'string' && this.searchCriteria.sample_no.trim()) {
          // 手动输入模式：字符串包含匹配
          const searchValue = this.searchCriteria.sample_no.toLowerCase()
          filtered = filtered.filter(item =>
            item.sample_info?.sample_no?.toLowerCase().includes(searchValue)
          )
        }
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
        project_name: null,
        part_names: [],
        statuses: [],
        development_stages: [],
        test_date_range: null,
        test_order_no: '',
        sample_no: [],  // 改为数组以支持多选
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
