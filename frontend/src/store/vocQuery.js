import { defineStore } from 'pinia'
import { vocApi } from '@/api/voc'

export const useVocQueryStore = defineStore('vocQuery', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      vehicle_model_ids: [],  // 改为多选
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
    all_voc_data: [],
    filtered_voc_data: [],
    filtered_odor_data: [],
    chart_data: [],
    statistics_data: null,

    // VOC表格分页
    pagination: {
      current_page: 1,
      total_pages: 0,
      total_count: 0,
      page_size: 10
    },

    // 气味表格独立分页
    odor_pagination: {
      current_page: 1,
      total_pages: 0,
      total_count: 0,
      page_size: 10
    },

    // 图表配置
    chart_config: {
      group_by: 'part_name',
      compound_options: [
        { value: 'benzene', label: '苯' },
        { value: 'toluene', label: '甲苯' },
        { value: 'ethylbenzene', label: '乙苯' },
        { value: 'xylene', label: '二甲苯' },
        { value: 'styrene', label: '苯乙烯' },
        { value: 'formaldehyde', label: '甲醛' },
        { value: 'acetaldehyde', label: '乙醛' },
        { value: 'acrolein', label: '丙烯醛' },
        { value: 'acetone', label: '丙酮' },
        { value: 'tvoc', label: 'TVOC' }
      ]
    },

    // 业务状态
    isLoading: false,
    error: null,
    vehicle_models_loading: false,
    part_names_loading: false,
    status_options_loading: false,
    development_stage_loading: false,
    query_loading: false,
    chart_data_loading: false
  }),

  getters: {
    // 是否有查询结果
    hasResults: (state) => {
      return state.filtered_voc_data.length > 0
    },

    // 是否有气味数据
    hasOdorResults: (state) => {
      return state.filtered_odor_data.length > 0
    },

    // 是否有图表数据
    hasChartData: (state) => {
      return state.chart_data.length > 0
    },

    // 获取VOC表格分页后的数据
    paginatedData: (state) => {
      const start = (state.pagination.current_page - 1) * state.pagination.page_size
      const end = start + state.pagination.page_size
      return state.filtered_voc_data.slice(start, end)
    },

    // 获取气味表格分页后的数据
    paginatedOdorData: (state) => {
      const start = (state.odor_pagination.current_page - 1) * state.odor_pagination.page_size
      const end = start + state.odor_pagination.page_size
      return state.filtered_odor_data.slice(start, end)
    }
  },

  actions: {
    // 获取车型选项
    async fetchVehicleModelOptions() {
      try {
        this.vehicle_models_loading = true
        const response = await vocApi.getVehicleModelOptions()
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

    // 获取零件名称选项 - 从已加载数据中提取唯一值
    extractPartNameOptions() {
      const uniquePartNames = [...new Set(
        this.all_voc_data
          .map(item => item.sample_info?.part_name)
          .filter(name => name)
      )].sort()
      
      this.part_names = uniquePartNames.map(name => ({
        label: name,
        value: name
      }))
    },

    // 获取状态选项 - 从已加载数据中提取唯一值
    extractStatusOptions() {
      const uniqueStatuses = [...new Set(
        this.all_voc_data
          .map(item => item.sample_info?.status)
          .filter(status => status)
      )].sort()
      
      this.status_options = uniqueStatuses.map(status => ({
        label: status,
        value: status
      }))
    },

    // 获取开发阶段选项 - 从已加载数据中提取唯一值
    extractDevelopmentStageOptions() {
      const uniqueStages = [...new Set(
        this.all_voc_data
          .map(item => item.sample_info?.development_stage)
          .filter(stage => stage)
      )].sort()
      
      this.development_stage_options = uniqueStages.map(stage => ({
        label: stage,
        value: stage
      }))
    },

    // 获取零件名称选项 - 保留API调用作为备用
    async fetchPartNameOptions() {
      try {
        this.part_names_loading = true
        const response = await vocApi.getPartNameOptions()
        this.part_names = response.data
      } catch (error) {
        this.error = error.message
        console.error('获取零件名称选项失败:', error)
      } finally {
        this.part_names_loading = false
      }
    },

    // 获取状态选项 - 保留API调用作为备用
    async fetchStatusOptions() {
      try {
        this.status_options_loading = true
        const response = await vocApi.getStatusOptions()
        this.status_options = response.data
      } catch (error) {
        this.error = error.message
        console.error('获取状态选项失败:', error)
      } finally {
        this.status_options_loading = false
      }
    },

    // 获取开发阶段选项 - 保留API调用作为备用
    async fetchDevelopmentStageOptions() {
      try {
        this.development_stage_loading = true
        const response = await vocApi.getDevelopmentStageOptions()
        this.development_stage_options = response.data
      } catch (error) {
        this.error = error.message
        console.error('获取开发阶段选项失败:', error)
      } finally {
        this.development_stage_loading = false
      }
    },

    // 加载所有VOC数据
    async loadAllVocData() {
      try {
        this.query_loading = true
        this.error = null
        
        const response = await vocApi.getVocDataList({ page_size: 10000 })
        this.all_voc_data = response.data.results || []
        
        // 提取唯一选项
        this.extractPartNameOptions()
        this.extractStatusOptions()
        this.extractDevelopmentStageOptions()
        
        this.filterVocData()
      } catch (error) {
        this.error = error.message
        console.error('加载VOC数据失败:', error)
      } finally {
        this.query_loading = false
      }
    },

    // 过滤VOC和气味数据
    filterVocData() {
      let filtered = [...this.all_voc_data]

      if (this.searchCriteria.vehicle_model_ids.length > 0) {
        filtered = filtered.filter(item => 
          this.searchCriteria.vehicle_model_ids.includes(item.sample_info?.vehicle_model?.id)
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

      this.filtered_voc_data = filtered
      this.pagination.total_count = filtered.length
      this.pagination.current_page = 1

      // 过滤气味数据：只显示至少有一个气味字段不为空的记录
      const odorFiltered = filtered.filter(item => {
        return item.static_front !== null || 
               item.static_rear !== null || 
               item.dynamic_front !== null || 
               item.dynamic_rear !== null || 
               item.odor_mean !== null
      })
      
      this.filtered_odor_data = odorFiltered
      this.odor_pagination.total_count = odorFiltered.length
      this.odor_pagination.current_page = 1
    },

    // 生成图表数据
    generateChartData(groupBy) {
      const groupedData = {}
      const compounds = this.chart_config.compound_options.map(c => c.value)

      this.filtered_voc_data.forEach(item => {
        const groupValue = groupBy === 'part_name' 
          ? item.sample_info?.part_name 
          : item.sample_info?.status

        if (!groupValue) return

        if (!groupedData[groupValue]) {
          groupedData[groupValue] = {}
          compounds.forEach(compound => {
            groupedData[groupValue][compound] = { total: 0, count: 0 }
          })
        }

        compounds.forEach(compound => {
          const value = item[`${compound}_formatted`] || item[compound] || 0
          const numValue = typeof value === 'string' ? parseFloat(value) : value
          if (!isNaN(numValue)) {
            groupedData[groupValue][compound].total += numValue
            groupedData[groupValue][compound].count += 1
          }
        })
      })

      this.chart_data = Object.entries(groupedData).map(([groupValue, compoundData]) => ({
        groupValue,
        ...Object.fromEntries(
          compounds.map(compound => [
            compound,
            compoundData[compound].count > 0 
              ? (compoundData[compound].total / compoundData[compound].count).toFixed(2)
              : 0
          ])
        )
      }))
    },

    // 重置查询条件
    resetSearchCriteria() {
      this.searchCriteria = {
        vehicle_model_ids: [],  // 改为多选
        part_names: [],
        statuses: [],
        development_stages: [],
        test_date_range: null,
        test_order_no: '',
        sample_no: '',
        page: 1,
        page_size: 10
      }
      this.filterVocData()
    },

    // 更新VOC表格分页
    setPage(page) {
      this.pagination.current_page = page
    },

    // 设置VOC表格每页数量
    setPageSize(pageSize) {
      this.pagination.page_size = pageSize
      this.pagination.current_page = 1
    },

    // 更新气味表格分页
    setOdorPage(page) {
      this.odor_pagination.current_page = page
    },

    // 设置气味表格每页数量
    setOdorPageSize(pageSize) {
      this.odor_pagination.page_size = pageSize
      this.odor_pagination.current_page = 1
    }
  }
})
