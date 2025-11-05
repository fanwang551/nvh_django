import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstanceTraceabilityStore = defineStore('substanceTraceability', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      vehicle_model_id: null,
      status: null,
      development_stage: null,
      cas_nos: [],
      selected_key: null  // 用于存储选中的唯一标识
    },

    // 选项数据
    vehicle_models: [],
    substance_options: [],

    // 溯源结果数据
    traceability_data: [],

    // 列显示配置
    column_visibility: {
      show_qij: false,
      show_wih: false,
      show_concentration: false
    },

    // 加载状态
    vehicle_models_loading: false,
    substance_options_loading: false,
    query_loading: false,
    error: null
  }),

  getters: {
    // 是否有查询结果
    hasResults: (state) => {
      return state.traceability_data.length > 0
    },

    // 已选物质数量
    selectedSubstanceCount: (state) => {
      return state.searchCriteria.cas_nos.length
    },

    // 是否可以查询
    canQuery: (state) => {
      return state.searchCriteria.selected_key && state.searchCriteria.cas_nos.length > 0
    }
  },

  actions: {
    // 获取车型选项
    async fetchVehicleModels() {
      try {
        this.vehicle_models_loading = true
        this.error = null
        const response = await substancesApi.getVehicleModelOptions()
        
        // 数据格式: {label, vehicle_model_id, status, development_stage}
        const data = response.data || []
        
        // 为每个选项生成唯一的key
        this.vehicle_models = (Array.isArray(data) ? data : []).map((item, index) => {
          // 确保status和development_stage有值
          const status = item.status || '未知状态'
          const stage = item.development_stage || '未知阶段'
          // 使用索引作为key，避免特殊字符问题
          const key = `key_${index}_${item.vehicle_model_id}`
          return {
            value: item.vehicle_model_id,
            label: item.label,
            vehicle_model_id: item.vehicle_model_id,
            status: status,
            development_stage: stage,
            key: key
          }
        })
        
        console.log('车型选项加载成功:', this.vehicle_models.length, '个选项')
        console.log('第一个选项示例:', this.vehicle_models[0])
      } catch (error) {
        this.error = error.message
        console.error('获取车型选项失败:', error)
        this.vehicle_models = []
      } finally {
        this.vehicle_models_loading = false
      }
    },

    // 加载物质选项（从整车全谱数据获取，按浓度降序）
    async fetchSubstanceOptions(selectedOption) {
      if (!selectedOption) {
        this.substance_options = []
        return
      }

      try {
        this.substance_options_loading = true
        this.error = null

        // 获取该车型+状态+开发阶段的整车全谱检测数据
        const queryParams = {
          vehicle_model_id: selectedOption.vehicle_model_id,
          part_name: '整车',
          page_size: 1000
        }
        
        // 添加状态和开发阶段过滤
        if (selectedOption.status && selectedOption.status !== '未知状态') {
          queryParams.status = selectedOption.status
        }
        if (selectedOption.development_stage && selectedOption.development_stage !== '未知阶段') {
          queryParams.development_stage = selectedOption.development_stage
        }

        const response = await substancesApi.getTestList(queryParams)

        const testData = response.data.results || []
        
        if (testData.length === 0) {
          console.warn('未找到匹配的整车检测数据')
          this.substance_options = []
          return
        }

        // 取最新的整车检测数据
        const latestTest = testData.sort((a, b) => {
          const dateA = new Date(a.test_date || 0)
          const dateB = new Date(b.test_date || 0)
          return dateB - dateA || b.id - a.id
        })[0]

        console.log('选择的整车测试数据:', latestTest)

        // 获取该测试的详细物质数据
        const detailResponse = await substancesApi.getTestDetail({
          test_id: latestTest.id
        })

        const details = detailResponse.data || []

        // 按浓度降序排序，构建选项列表
        const sortedDetails = details
          .filter(item => {
            const concentration = parseFloat(item.concentration)
            return !isNaN(concentration) && concentration > 0
          })
          .sort((a, b) => {
            const concA = parseFloat(a.concentration) || 0
            const concB = parseFloat(b.concentration) || 0
            return concB - concA
          })

        this.substance_options = sortedDetails.map(item => ({
          value: item.substance,
          label: `${item.substance_name_cn} (${item.substance_name_en || 'N/A'}, ${item.cas_no})`,
          substance_name_cn: item.substance_name_cn,
          substance_name_en: item.substance_name_en,
          cas_no: item.cas_no,
          concentration: parseFloat(item.concentration)
        }))

        console.log(`成功加载${this.substance_options.length}种物质`)

      } catch (error) {
        this.error = error.message
        console.error('获取物质选项失败:', error)
        this.substance_options = []
      } finally {
        this.substance_options_loading = false
      }
    },

    // 查询溯源数据
    async fetchTraceabilityData() {
      if (!this.canQuery) {
        return
      }

      try {
        this.query_loading = true
        this.error = null

        const params = {
          vehicle_model_id: this.searchCriteria.vehicle_model_id,
          cas_nos: this.searchCriteria.cas_nos
        }
        
        // 添加状态和开发阶段参数
        if (this.searchCriteria.status) {
          params.status = this.searchCriteria.status
        }
        if (this.searchCriteria.development_stage) {
          params.development_stage = this.searchCriteria.development_stage
        }

        const response = await substancesApi.getSubstanceTraceability(params)

        this.traceability_data = response.data.substances || []
      } catch (error) {
        this.error = error.message
        console.error('获取溯源数据失败:', error)
        this.traceability_data = []
      } finally {
        this.query_loading = false
      }
    },

    // 切换列显示
    toggleColumnVisibility(column, visible) {
      if (column === 'qij') {
        this.column_visibility.show_qij = visible
      } else if (column === 'wih') {
        this.column_visibility.show_wih = visible
      } else if (column === 'concentration') {
        this.column_visibility.show_concentration = visible
      }

      // 保存到localStorage
      this.saveColumnVisibility()
    },

    // 全部显示
    showAllColumns() {
      this.column_visibility.show_qij = true
      this.column_visibility.show_wih = true
      this.column_visibility.show_concentration = true
      this.saveColumnVisibility()
    },

    // 全部隐藏
    hideAllColumns() {
      this.column_visibility.show_qij = false
      this.column_visibility.show_wih = false
      this.column_visibility.show_concentration = false
      this.saveColumnVisibility()
    },

    // 保存列显示配置到localStorage
    saveColumnVisibility() {
      try {
        localStorage.setItem(
          'substance_traceability_column_visibility',
          JSON.stringify(this.column_visibility)
        )
      } catch (error) {
        console.error('保存列显示配置失败:', error)
      }
    },

    // 从localStorage加载列显示配置
    loadColumnVisibility() {
      try {
        const saved = localStorage.getItem('substance_traceability_column_visibility')
        if (saved) {
          const config = JSON.parse(saved)
          this.column_visibility = {
            ...this.column_visibility,
            ...config
          }
        }
      } catch (error) {
        console.error('加载列显示配置失败:', error)
      }
    },

    // 重置查询条件
    resetSearchCriteria() {
      this.searchCriteria = {
        vehicle_model_id: null,
        status: null,
        development_stage: null,
        cas_nos: [],
        selected_key: null
      }
      this.substance_options = []
      this.traceability_data = []
    },

    // 车型变化处理
    handleVehicleModelChange(selectedKey) {
      // 清空之前的选择
      this.searchCriteria.cas_nos = []
      this.traceability_data = []
      
      if (selectedKey) {
        // 根据key找到完整的选项信息
        const selectedOption = this.vehicle_models.find(item => item.key === selectedKey)
        
        if (selectedOption) {
          this.searchCriteria.selected_key = selectedKey
          this.searchCriteria.vehicle_model_id = selectedOption.vehicle_model_id
          this.searchCriteria.status = selectedOption.status
          this.searchCriteria.development_stage = selectedOption.development_stage
          
          // 加载该选项对应的物质列表
          this.fetchSubstanceOptions(selectedOption)
        }
      } else {
        // 清空选择
        this.searchCriteria.selected_key = null
        this.searchCriteria.vehicle_model_id = null
        this.searchCriteria.status = null
        this.searchCriteria.development_stage = null
        this.substance_options = []
      }
    }
  }
})
