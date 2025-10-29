import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstanceTraceabilityStore = defineStore('substanceTraceability', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      vehicle_model_id: null,
      substance_ids: []
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
      return state.searchCriteria.substance_ids.length
    },

    // 是否可以查询
    canQuery: (state) => {
      return state.searchCriteria.vehicle_model_id && state.searchCriteria.substance_ids.length > 0
    }
  },

  actions: {
    // 获取车型选项
    async fetchVehicleModels() {
      try {
        this.vehicle_models_loading = true
        this.error = null
        const response = await substancesApi.getVehicleModelOptions()
        
        // 确保数据格式正确
        const data = response.data || []
        this.vehicle_models = Array.isArray(data) ? data : []
        
        console.log('车型选项加载成功:', this.vehicle_models.length, '个车型')
      } catch (error) {
        this.error = error.message
        console.error('获取车型选项失败:', error)
        this.vehicle_models = []
      } finally {
        this.vehicle_models_loading = false
      }
    },

    // 加载物质选项（从整车全谱数据获取，按浓度降序）
    async fetchSubstanceOptions(vehicleModelId) {
      if (!vehicleModelId) {
        this.substance_options = []
        return
      }

      try {
        this.substance_options_loading = true
        this.error = null

        // 获取该车型整车的全谱检测数据
        const response = await substancesApi.getTestList({
          vehicle_model_id: vehicleModelId,
          part_name: '整车',
          page_size: 1000
        })

        const testData = response.data.results || []
        
        if (testData.length === 0) {
          console.warn('未找到该车型的整车检测数据')
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

        const response = await substancesApi.getSubstanceTraceability({
          vehicle_model_id: this.searchCriteria.vehicle_model_id,
          substance_ids: this.searchCriteria.substance_ids
        })

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
        substance_ids: []
      }
      this.substance_options = []
      this.traceability_data = []
    },

    // 车型变化处理
    handleVehicleModelChange(vehicleModelId) {
      this.searchCriteria.vehicle_model_id = vehicleModelId
      this.searchCriteria.substance_ids = []
      this.traceability_data = []
      
      if (vehicleModelId) {
        this.fetchSubstanceOptions(vehicleModelId)
      } else {
        this.substance_options = []
      }
    }
  }
})
