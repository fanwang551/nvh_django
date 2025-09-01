import { defineStore } from 'pinia'
import { modalApi } from '@/api/modal'

export const useAirtightLeakCompareStore = defineStore('airtightLeakCompare', {
  state: () => ({
    // 查询表单状态
    selectedVehicleIds: [],
    
    // 选项数据
    vehicleModelOptions: [],
    
    // 加载状态
    vehicleModelsLoading: false,
    loading: false,
    
    // 对比结果
    compareResult: {
      vehicle_models: [],
      leakage_data: []
    },
    
    // 表格数据
    tableData: [],
    
    // 弹窗状态（在切换标签时需要清理）
    detailDialogVisible: false,
    currentDetailData: null
  }),
  
  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.selectedVehicleIds.length > 0
    },
    
    // 是否有查询结果
    hasResults: (state) => {
      return state.compareResult.vehicle_models.length > 0
    },
    
    // 选中的车型数量
    selectedVehicleCount: (state) => {
      return state.selectedVehicleIds.length
    },
    
    // 动态列宽计算
    columnWidths: (state) => {
      const vehicleCount = state.compareResult.vehicle_models.length

      if (vehicleCount === 0) {
        return {
          category: 150,
          itemName: 200,
          vehicle: 150
        }
      }

      // 基础列宽
      const categoryWidth = 150
      const itemNameWidth = 220

      // 根据车型数量动态计算车型列宽
      const minVehicleWidth = 140
      const maxVehicleWidth = 200

      // 计算可用宽度（假设容器最小宽度为800px）
      const containerMinWidth = 800
      const usedWidth = categoryWidth + itemNameWidth
      const availableWidth = containerMinWidth - usedWidth

      let vehicleWidth = Math.max(minVehicleWidth, Math.min(maxVehicleWidth, availableWidth / vehicleCount))

      // 如果车型数量较少，可以给更多空间
      if (vehicleCount <= 2) {
        vehicleWidth = maxVehicleWidth
      } else if (vehicleCount <= 4) {
        vehicleWidth = Math.max(160, vehicleWidth)
      }

      return {
        category: categoryWidth,
        itemName: itemNameWidth,
        vehicle: Math.round(vehicleWidth)
      }
    }
  },
  
  actions: {
    // 加载车型列表
    async loadVehicleModels() {
      try {
        this.vehicleModelsLoading = true
        const response = await modalApi.getVehicleModels()
        if (response.success) {
          this.vehicleModelOptions = response.data || []
        } else {
          throw new Error(response.message || '获取车型列表失败')
        }
      } catch (error) {
        console.error('加载车型列表失败:', error)
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },

    // 执行气密性对比
    async handleCompare() {
      if (!this.canQuery) {
        throw new Error('请至少选择一个车型')
      }

      try {
        this.loading = true
        const response = await modalApi.compareAirtightnessData({
          vehicle_model_ids: this.selectedVehicleIds.join(',')
        })

        if (response.success) {
          this.compareResult.vehicle_models = response.data.vehicle_models || []
          this.compareResult.leakage_data = response.data.leakage_data || []
          this.buildTableData()
          return this.compareResult
        } else {
          throw new Error(response.message || '获取对比数据失败')
        }
      } catch (error) {
        console.error('获取对比数据失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 构建表格数据
    buildTableData() {
      const data = []

      this.compareResult.leakage_data.forEach(category => {
        category.items.forEach((item, itemIndex) => {
          const row = {
            category: itemIndex === 0 ? category.category : '',
            item_name: item.name,
            categoryRowspan: itemIndex === 0 ? category.items.length : 0
          }

          // 为每个车型添加对应的数值
          this.compareResult.vehicle_models.forEach((vehicle, vehicleIndex) => {
            row[`vehicle_${vehicle.id}`] = item.values[vehicleIndex] || '-'
          })

          data.push(row)
        })
      })

      this.tableData = data
    },
    
    // 设置车型选择
    setSelectedVehicleIds(vehicleIds) {
      this.selectedVehicleIds = vehicleIds
    },
    
    // 显示详情弹窗
    showDetailDialog(data) {
      this.currentDetailData = data
      this.detailDialogVisible = true
    },
    
    // 关闭详情弹窗
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.currentDetailData = null
    },
    
    // 清理弹窗状态（在标签切换时调用）
    clearDialogState() {
      this.detailDialogVisible = false
      this.currentDetailData = null
    },
    
    // 初始化页面数据
    async initializePageData() {
      // 只在没有车型选项时加载，避免重复请求
      if (this.vehicleModelOptions.length === 0) {
        await this.loadVehicleModels()
      }
    }
  }
})
