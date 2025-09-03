import { defineStore } from 'pinia'
import { soundInsulationApi } from '@/api/soundInsulation'

export const useVehicleReverberationQueryStore = defineStore('vehicleReverberationQuery', {
    state: () => ({
        // 查询条件
        searchCriteria: {
            vehicleModelIds: []
        },

        // 业务数据
        vehicleModels: [],
        compareResults: [],
        chartData: [],

        // 业务状态
        isLoading: false,
        error: null,
        vehicleModelsLoading: false,
        compareLoading: false,
    }),

    getters: {
        // 业务验证：是否可以查询
        canQuery: (state) => {
            return state.searchCriteria.vehicleModelIds.length > 0
        },

        // 业务状态：是否有查询结果
        hasResults: (state) => {
            return state.compareResults.length > 0
        },

        // 计算属性：选中的车型数量
        selectedVehicleCount: (state) => {
            return state.searchCriteria.vehicleModelIds.length
        },

        // 计算属性：格式化的图表数据
        formattedChartData: (state) => {
            return state.chartData
        },

        // 业务状态：是否正在加载
        isLoadingAny: (state) => {
            return state.isLoading || state.vehicleModelsLoading || state.compareLoading
        }
    },

    actions: {
        // API调用：加载有混响时间数据的车型列表
        async fetchVehicleModels() {
            try {
                this.vehicleModelsLoading = true
                this.error = null

                const response = await soundInsulationApi.getVehiclesWithReverberationData()
                this.vehicleModels = response.data || []

                return this.vehicleModels
            } catch (error) {
                this.error = '加载车型列表失败'
                console.error('加载车型列表失败:', error)
                throw error
            } finally {
                this.vehicleModelsLoading = false
            }
        },

        // API调用：生成对比数据
        async generateCompareData() {
            if (!this.canQuery) {
                const error = new Error('请选择车型')
                this.error = error.message
                throw error
            }

            try {
                this.compareLoading = true
                this.error = null

                const data = {
                    vehicle_model_ids: this.searchCriteria.vehicleModelIds.join(',')
                }

                const response = await soundInsulationApi.compareVehicleReverberationData(data)
                this.compareResults = response.data || []

                // 处理图表数据
                this.processChartData()

                return this.compareResults
            } catch (error) {
                this.error = '生成对比数据失败'
                console.error('生成对比数据失败:', error)
                throw error
            } finally {
                this.compareLoading = false
            }
        },

        // 业务逻辑：处理图表数据
        processChartData() {
            const frequencies = [400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

            this.chartData = this.compareResults.map(item => {
                const seriesData = frequencies.map(freq => {
                    const fieldName = `freq_${freq}`
                    const value = item.frequency_data[fieldName]
                    return value !== null && value !== undefined ? Number(value) : null
                })

                return {
                    name: item.vehicle_model_name,
                    data: seriesData,
                    itemData: item // 保存完整数据用于组件使用
                }
            })
        },

        // 业务逻辑：数据验证
        validateSearchCriteria() {
            if (!this.searchCriteria.vehicleModelIds.length) {
                throw new Error('请选择至少一个车型')
            }
            return true
        },

        // 业务逻辑：设置查询条件
        setSearchCriteria(criteria) {
            this.searchCriteria = { ...this.searchCriteria, ...criteria }
        },

        // 业务逻辑：设置车型选择
        setVehicleModelIds(vehicleIds) {
            this.searchCriteria.vehicleModelIds = vehicleIds
        },

        // 业务逻辑：清除错误状态
        clearError() {
            this.error = null
        },

        // 业务逻辑：重置所有状态
        resetState() {
            this.searchCriteria = {
                vehicleModelIds: []
            }
            this.compareResults = []
            this.chartData = []
            this.error = null
        },

        // 业务逻辑：初始化数据
        async initializeData() {
            if (this.vehicleModels.length === 0) {
                await this.fetchVehicleModels()
            }
        }
    }
})