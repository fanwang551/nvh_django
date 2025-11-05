import { defineStore } from 'pinia'
import { substancesApi } from '@/api/substances'

export const useSubstanceTraceabilityStore = defineStore('substanceTraceability', {
  state: () => ({
    // 查询条件
    searchCriteria: {
      vehicle_model_id: null,
      vehicle_test_id: null, // 唯一整车测试ID
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
    // 获取样品选项（整车）：按 车型-委托单号-样品编号 唯一标识
    async fetchVehicleModels() {
      try {
        this.vehicle_models_loading = true
        this.error = null

        // 仅从整车测试中构造选项
        const testsResp = await substancesApi.getTestList({ part_name: '整车', page_size: 10000 })
        const allTests = (testsResp?.data?.results || [])
          .filter(r => r?.sample_info?.vehicle_model?.id)

        // 用 (vmId, test_order_no, sample_no) 作为唯一组合，保留最新测试
        const latestByCombo = new Map()
        for (const t of allTests) {
          const vmId = t.sample_info.vehicle_model.id
          const vmName = t.sample_info.vehicle_model.vehicle_model_name || '未知车型'
          const orderNo = t.sample_info.test_order_no || '-'
          const sampleNo = t.sample_info.sample_no || '-'
          const comboKey = `${vmId}||${orderNo}||${sampleNo}`
          const existed = latestByCombo.get(comboKey)
          const curDate = new Date(t.test_date || 0).getTime()
          const oldDate = existed ? new Date(existed.test_date || 0).getTime() : -1
          if (!existed || curDate > oldDate) {
            latestByCombo.set(comboKey, {
              test_id: t.id,
              vehicle_model_id: vmId,
              vehicle_model_name: vmName,
              test_order_no: orderNo,
              sample_no: sampleNo,
              label: `${vmName}-${orderNo}-${sampleNo}`
            })
          }
        }

        // 转换为下拉选项
        let idx = 0
        this.vehicle_models = Array.from(latestByCombo.values()).map(v => ({
          key: `key_${idx++}_${v.test_id}`,
          value: v.test_id,
          label: v.label,
          vehicle_test_id: v.test_id,
          vehicle_model_id: v.vehicle_model_id,
          vehicle_model_name: v.vehicle_model_name,
          test_order_no: v.test_order_no,
          sample_no: v.sample_no
        }))

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

    // 加载物质选项（从所选唯一样品的整车全谱数据获取，按浓度降序）
    async fetchSubstanceOptions(selectedOption) {
      if (!selectedOption) {
        this.substance_options = []
        return
      }

      try {
        this.substance_options_loading = true
        this.error = null

        const testId = selectedOption.vehicle_test_id || selectedOption.value
        if (!testId) {
          console.warn('未获取到车辆整车测试ID')
          this.substance_options = []
          return
        }

        const detailResponse = await substancesApi.getTestDetail({ test_id: testId })

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
          vehicle_test_id: this.searchCriteria.vehicle_test_id,
          vehicle_model_id: this.searchCriteria.vehicle_model_id, // 备用
          cas_nos: this.searchCriteria.cas_nos
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
        vehicle_test_id: null,
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
          this.searchCriteria.vehicle_test_id = selectedOption.vehicle_test_id || selectedOption.value
          
          // 加载该选项对应的物质列表
          this.fetchSubstanceOptions(selectedOption)
        }
      } else {
        // 清空选择
        this.searchCriteria.selected_key = null
        this.searchCriteria.vehicle_model_id = null
        this.searchCriteria.vehicle_test_id = null
        this.substance_options = []
      }
    }
  }
})
