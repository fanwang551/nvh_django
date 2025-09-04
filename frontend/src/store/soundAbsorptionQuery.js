import { defineStore } from 'pinia'
import { soundAbsorptionApi } from '@/api/soundAbsorption'

export const useSoundAbsorptionQueryStore = defineStore('soundAbsorptionQuery', {
    state: () => ({
        // 查询条件
        searchCriteria: {
            partName: '',
            materialComposition: '',
            weight: null
        },

        // 业务数据
        partNames: [],
        materialCompositions: [],
        weights: [],
        queryResults: [],
        chartData: [],

        // 业务状态
        isLoading: false,
        error: null,
        partNamesLoading: false,
        materialCompositionsLoading: false,
        weightsLoading: false,
        queryLoading: false,
    }),

    getters: {
        // 业务验证：是否可以查询
        canQuery: (state) => {
            return state.searchCriteria.partName ||
                   state.searchCriteria.materialComposition ||
                   state.searchCriteria.weight !== null
        },

        // 业务状态：是否有查询结果
        hasResults: (state) => {
            return state.queryResults.length > 0
        },

        // 计算属性：格式化的图表数据
        formattedChartData: (state) => {
            return state.chartData
        },

        // 计算属性：当前查询条件描述
        queryDescription: (state) => {
            const conditions = []
            if (state.searchCriteria.partName) {
                conditions.push(`零件名称: ${state.searchCriteria.partName}`)
            }
            if (state.searchCriteria.materialComposition) {
                conditions.push(`材料组成: ${state.searchCriteria.materialComposition}`)
            }
            if (state.searchCriteria.weight !== null) {
                conditions.push(`克重: ${state.searchCriteria.weight}g/m²`)
            }
            return conditions.join(' | ')
        },

        // 业务状态：是否正在加载
        isLoadingAny: (state) => {
            return state.isLoading || state.partNamesLoading || state.materialCompositionsLoading || state.weightsLoading || state.queryLoading
        }
    },

    actions: {
        // API调用：加载零件名称选项
        async fetchPartNames() {
            try {
                this.partNamesLoading = true
                this.error = null

                const response = await soundAbsorptionApi.getPartNameOptions()
                this.partNames = response.data || []

                return this.partNames
            } catch (error) {
                this.error = '加载零件名称选项失败'
                console.error('加载零件名称选项失败:', error)
                throw error
            } finally {
                this.partNamesLoading = false
            }
        },

        // API调用：加载材料组成选项
        async fetchMaterialCompositions(partName = null) {
            try {
                this.materialCompositionsLoading = true
                this.error = null

                const params = {}
                if (partName) {
                    params.part_name = partName
                }
                const response = await soundAbsorptionApi.getMaterialCompositionOptions(params)
                this.materialCompositions = response.data || []

                return this.materialCompositions
            } catch (error) {
                this.error = '加载材料组成选项失败'
                console.error('加载材料组成选项失败:', error)
                throw error
            } finally {
                this.materialCompositionsLoading = false
            }
        },

        // API调用：加载克重选项
        async fetchWeights(partName = null, materialComposition = null) {
            try {
                this.weightsLoading = true
                this.error = null

                const params = {}
                if (partName) {
                    params.part_name = partName
                }
                if (materialComposition) {
                    params.material_composition = materialComposition
                }
                const response = await soundAbsorptionApi.getWeightOptions(params)
                this.weights = response.data || []

                return this.weights
            } catch (error) {
                this.error = '加载克重选项失败'
                console.error('加载克重选项失败:', error)
                throw error
            } finally {
                this.weightsLoading = false
            }
        },

        // API调用：查询吸声系数数据
        async queryData() {
            if (!this.canQuery) {
                const error = new Error('请至少选择一个查询条件')
                this.error = error.message
                throw error
            }

            try {
                this.queryLoading = true
                this.error = null

                const params = {}
                if (this.searchCriteria.partName) {
                    params.part_name = this.searchCriteria.partName
                }
                if (this.searchCriteria.materialComposition) {
                    params.material_composition = this.searchCriteria.materialComposition
                }
                if (this.searchCriteria.weight !== null) {
                    params.weight = this.searchCriteria.weight
                }

                const response = await soundAbsorptionApi.querySoundAbsorption(params)
                this.queryResults = response.data || []

                // 处理图表数据
                this.processChartData()

                return this.queryResults
            } catch (error) {
                this.error = '查询吸声系数数据失败'
                console.error('查询吸声系数数据失败:', error)
                throw error
            } finally {
                this.queryLoading = false
            }
        },

        // 业务逻辑：处理图表数据
        processChartData() {
            const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

            this.chartData = this.queryResults.map((item, index) => {
                // 测试值数据
                const testSeriesData = frequencies.map(freq => {
                    const fieldName = `test_value_${freq}`
                    const value = item.test_frequency_data[fieldName]
                    return value !== null && value !== undefined ? Number(value) : null
                })

                // 目标值数据
                const targetSeriesData = frequencies.map(freq => {
                    const fieldName = `target_value_${freq}`
                    const value = item.target_frequency_data[fieldName]
                    return value !== null && value !== undefined ? Number(value) : null
                })

                return {
                    name: `样本${index + 1}`,
                    testData: testSeriesData,
                    targetData: targetSeriesData,
                    itemData: item // 保存完整数据用于组件使用
                }
            })
        },

        // 业务逻辑：数据验证
        validateSearchCriteria() {
            if (!this.searchCriteria.partName && !this.searchCriteria.materialComposition && this.searchCriteria.weight === null) {
                throw new Error('请至少选择一个查询条件')
            }
            return true
        },

        // 业务逻辑：零件名称变化处理
        async handlePartNameChange(partName) {
            this.searchCriteria.partName = partName

            // 清空下级选项
            this.searchCriteria.materialComposition = ''
            this.searchCriteria.weight = null
            this.materialCompositions = []
            this.weights = []

            if (partName) {
                // 重新加载材料组成选项
                await this.fetchMaterialCompositions(partName)
            }
        },

        // 业务逻辑：材料组成变化处理
        async handleMaterialCompositionChange(materialComposition) {
            this.searchCriteria.materialComposition = materialComposition

            // 清空下级选项
            this.searchCriteria.weight = null
            this.weights = []

            if (materialComposition) {
                // 重新加载克重选项
                await this.fetchWeights(this.searchCriteria.partName, materialComposition)
            }
        },

        // 业务逻辑：克重变化处理
        handleWeightChange(weight) {
            this.searchCriteria.weight = weight
        },

        // 业务逻辑：设置查询条件
        setSearchCriteria(criteria) {
            this.searchCriteria = { ...this.searchCriteria, ...criteria }
        },

        // 业务逻辑：清除错误状态
        clearError() {
            this.error = null
        },

        // 业务逻辑：重置所有状态
        resetState() {
            this.searchCriteria = {
                partName: '',
                materialComposition: '',
                weight: null
            }
            this.queryResults = []
            this.chartData = []
            this.error = null
        },

        // 业务逻辑：初始化数据
        async initializeData() {
            if (this.partNames.length === 0) {
                await this.fetchPartNames()
            }
        }
    }
})