import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstanceTraceabilityStore = defineStore('substanceTraceability', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      project_name: null,
      test_order_no: null,
      sample_no: null,
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
    // 获取整车样品选项：按 project_name - test_order_no - sample_no 唯一标识
    async fetchVehicleModels() {
      try {
        this.vehicle_models_loading = true
        this.error = null

        const resp = await substancesApi.getVehicleSampleOptions()
        const list = resp?.data || []
        // 直接沿用 vehicle_models 命名，语义为“整车样品选项”
        this.vehicle_models = list.map((v, idx) => ({
          key: v.key || `key_${idx}`,
          value: v.key || `key_${idx}`,
          label: v.label,
          project_name: v.project_name,
          status: v.status || null,
          test_order_no: v.test_order_no,
          sample_no: v.sample_no
        }))

        console.log('整车样品选项加载成功:', this.vehicle_models.length, '个选项')
        if (this.vehicle_models.length > 0) {
          console.log('示例选项:', this.vehicle_models[0])
        }
      } catch (error) {
        this.error = error.message
        console.error('获取整车样品选项失败:', error)
        this.vehicle_models = []
      } finally {
        this.vehicle_models_loading = false
      }
    },

    // 加载物质选项（从所选的整车样品获取，按浓度降序）
    async fetchSubstanceOptions(selectedOption) {
      if (!selectedOption) {
        this.substance_options = []
        return
      }

      try {
        this.substance_options_loading = true
        this.error = null

        const { project_name, test_order_no, sample_no } = selectedOption
        if (!project_name || !test_order_no || !sample_no) {
          console.warn('选项缺少必要字段')
          this.substance_options = []
          return
        }

        const listResp = await substancesApi.getTraceabilitySubstances({ project_name, test_order_no, sample_no })
        const details = listResp.data || []

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
          value: item.cas_no,
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

        const payload = {
          project_name: this.searchCriteria.project_name,
          test_order_no: this.searchCriteria.test_order_no,
          sample_no: this.searchCriteria.sample_no,
          selected_substances: this.searchCriteria.cas_nos
        }

        const response = await substancesApi.postSubstanceRanking(payload)
        this.traceability_data = (response?.data?.substances) || []
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
        project_name: null,
        test_order_no: null,
        sample_no: null,
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
          this.searchCriteria.project_name = selectedOption.project_name
          this.searchCriteria.test_order_no = selectedOption.test_order_no
          this.searchCriteria.sample_no = selectedOption.sample_no
          
          // 加载该选项对应的物质列表
          this.fetchSubstanceOptions(selectedOption)
        }
      } else {
        // 清空选择
        this.searchCriteria.selected_key = null
        this.searchCriteria.project_name = null
        this.searchCriteria.test_order_no = null
        this.searchCriteria.sample_no = null
        this.substance_options = []
      }
    }
  }
})
