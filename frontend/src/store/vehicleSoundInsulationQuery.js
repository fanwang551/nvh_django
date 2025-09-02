import { defineStore } from 'pinia'
import { soundInsulationApi } from '@/api/soundInsulation'

export const useVehicleSoundInsulationQueryStore = defineStore('vehicleSoundInsulationQuery', {
    state: () => ({
        // 查询表单状态
        searchForm: {
            vehicleModelIds: []
        },

        // 数据状态
        vehicleModelOptions: [],
        compareResult: [],
        chartData: [], // 专门用于图表的数据

        // 加载状态
        vehicleModelsLoading: false,
        compareLoading: false,
    }),

    getters: {
        // 是否可以查询
        canQuery: (state) => {
            return state.searchForm.vehicleModelIds.length > 0
        },

        // 是否有查询结果
        hasResults: (state) => {
            return state.compareResult.length > 0
        },

        // 选中的车型数量
        selectedVehicleCount: (state) => {
            return state.searchForm.vehicleModelIds.length
        },

        // 获取图表数据（简化版，只返回数据）
        chartSeriesData: (state) => {
            return state.chartData
        },

        // 获取图片URL（统一处理）
        getImageUrl: () => (imagePath) => {
            if (!imagePath) return ''
            if (imagePath.startsWith('/')) {
                return `http://127.0.0.1:8000${imagePath}`
            }
            return imagePath
        }
    },

    actions: {
        // 加载有隔声量数据的车型列表
        async loadVehicleModels() {
            try {
                this.vehicleModelsLoading = true
                const response = await soundInsulationApi.getVehiclesWithSoundData()
                this.vehicleModelOptions = response.data || []
            } catch (error) {
                console.error('加载车型列表失败:', error)
                throw error
            } finally {
                this.vehicleModelsLoading = false
            }
        },

        // 生成对比数据
        async generateCompareData() {
            if (!this.canQuery) {
                throw new Error('请选择车型')
            }

            try {
                this.compareLoading = true

                const data = {
                    vehicle_model_ids: this.searchForm.vehicleModelIds.join(',')
                }

                const response = await soundInsulationApi.compareVehicleSoundInsulationData(data)
                this.compareResult = response.data || []

                // 生成图表数据
                this.generateChartData()

                return this.compareResult
            } catch (error) {
                console.error('生成对比数据失败:', error)
                throw error
            } finally {
                this.compareLoading = false
            }
        },

        // 生成图表数据（简化版，只处理数据转换）
        generateChartData() {
            const frequencies = [200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

            this.chartData = this.compareResult.map(item => {
                const seriesData = frequencies.map(freq => {
                    const fieldName = `freq_${freq}`
                    const value = item.frequency_data[fieldName]
                    return value !== null && value !== undefined ? Number(value) : null
                })

                return {
                    name: item.vehicle_model_name,
                    data: seriesData,
                    rawData: item // 保存完整数据供组件使用
                }
            })
        },

        // 设置车型选择
        setVehicleModels(vehicleIds) {
            this.searchForm.vehicleModelIds = vehicleIds
        },

        // 全选/反选车型（简化版，只处理数据）
        selectAllVehicles() {
            this.searchForm.vehicleModelIds = this.vehicleModelOptions.map(v => v.id)
        },

        // 清空车型选择
        clearVehicleSelection() {
            this.searchForm.vehicleModelIds = []
        },

        // 清空所有状态（只清空数据状态）
        resetState() {
            this.searchForm = {
                vehicleModelIds: []
            }
            this.compareResult = []
            this.chartData = []
        },

        // 初始化页面数据
        async initializePageData() {
            if (this.vehicleModelOptions.length === 0) {
                await this.loadVehicleModels()
            }
        }
    }
})
