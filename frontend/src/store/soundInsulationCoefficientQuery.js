import { defineStore } from 'pinia'
import { soundInsulationCoefficientApi } from '@/api/soundInsulationCoefficient'

export const useSoundInsulationCoefficientQueryStore = defineStore('soundInsulationCoefficientQuery', {
    state: () => ({
        // 查询条件
        searchCriteria: {
            testType: '',
            partName: '',
            materialComposition: '',
            weight: null
        },

        // 业务数据
        testTypes: [],
        partNames: [],
        materialCompositions: [],
        weights: [],
        queryResults: [],
        chartData: [],

        // 业务状态
        isLoading: false,
        error: null,
        testTypesLoading: false,
        partNamesLoading: false,
        materialCompositionsLoading: false,
        weightsLoading: false,
        queryLoading: false,
    }),

    getters: {
        // 是否有查询结果
        hasResults: (state) => state.queryResults.length > 0,

        // 格式化的图表数据
        formattedChartData: (state) => state.chartData,

        // 查询条件是否有效
        isValidQuery: (state) => {
            return !!(state.searchCriteria.testType || 
                     state.searchCriteria.partName || 
                     state.searchCriteria.materialComposition || 
                     state.searchCriteria.weight !== null)
        }
    },

    actions: {
        // 初始化数据
        async initializeData() {
            try {
                this.isLoading = true
                this.error = null

                // 加载测试类型选项
                await this.loadTestTypes()

            } catch (error) {
                this.error = '初始化数据失败'
                console.error('初始化数据失败:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        // 加载测试类型选项
        async loadTestTypes() {
            try {
                this.testTypesLoading = true
                const response = await soundInsulationCoefficientApi.getTestTypeOptions()
                this.testTypes = response.data || []
            } catch (error) {
                console.error('加载测试类型选项失败:', error)
                throw error
            } finally {
                this.testTypesLoading = false
            }
        },

        // 加载零件名称选项
        async loadPartNames(testType = null) {
            try {
                this.partNamesLoading = true
                const params = {}
                if (testType) {
                    params.test_type = testType
                }

                const response = await soundInsulationCoefficientApi.getPartNameOptions(params)
                this.partNames = response.data || []
            } catch (error) {
                console.error('加载零件名称选项失败:', error)
                throw error
            } finally {
                this.partNamesLoading = false
            }
        },

        // 加载材料组成选项
        async loadMaterialCompositions(testType = null, partName = null) {
            try {
                this.materialCompositionsLoading = true
                const params = {}
                if (testType) {
                    params.test_type = testType
                }
                if (partName) {
                    params.part_name = partName
                }

                const response = await soundInsulationCoefficientApi.getMaterialCompositionOptions(params)
                this.materialCompositions = response.data || []
            } catch (error) {
                console.error('加载材料组成选项失败:', error)
                throw error
            } finally {
                this.materialCompositionsLoading = false
            }
        },

        // 加载克重选项
        async loadWeights(testType = null, partName = null, materialComposition = null) {
            try {
                this.weightsLoading = true
                const params = {}
                if (testType) {
                    params.test_type = testType
                }
                if (partName) {
                    params.part_name = partName
                }
                if (materialComposition) {
                    params.material_composition = materialComposition
                }

                const response = await soundInsulationCoefficientApi.getWeightOptions(params)
                this.weights = response.data || []
            } catch (error) {
                console.error('加载克重选项失败:', error)
                throw error
            } finally {
                this.weightsLoading = false
            }
        },

        // 处理测试类型变化
        async handleTestTypeChange(testType) {
            this.searchCriteria.testType = testType
            
            // 清空下级选项
            this.searchCriteria.partName = ''
            this.searchCriteria.materialComposition = ''
            this.searchCriteria.weight = null
            this.partNames = []
            this.materialCompositions = []
            this.weights = []

            // 重新加载零件名称选项
            if (testType) {
                await this.loadPartNames(testType)
            }
        },

        // 处理零件名称变化
        async handlePartNameChange(partName) {
            this.searchCriteria.partName = partName
            
            // 清空下级选项
            this.searchCriteria.materialComposition = ''
            this.searchCriteria.weight = null
            this.materialCompositions = []
            this.weights = []

            // 重新加载材料组成选项
            if (partName) {
                await this.loadMaterialCompositions(this.searchCriteria.testType, partName)
            }
        },

        // 处理材料组成变化
        async handleMaterialCompositionChange(materialComposition) {
            this.searchCriteria.materialComposition = materialComposition
            
            // 清空下级选项
            this.searchCriteria.weight = null
            this.weights = []

            // 重新加载克重选项
            if (materialComposition) {
                await this.loadWeights(
                    this.searchCriteria.testType, 
                    this.searchCriteria.partName, 
                    materialComposition
                )
            }
        },

        // 处理克重变化
        handleWeightChange(weight) {
            this.searchCriteria.weight = weight
        },

        // 查询数据
        async queryData() {
            if (!this.isValidQuery) {
                throw new Error('至少需要提供一个查询条件')
            }

            try {
                this.queryLoading = true
                this.error = null

                const params = {}
                if (this.searchCriteria.testType) {
                    params.test_type = this.searchCriteria.testType
                }
                if (this.searchCriteria.partName) {
                    params.part_name = this.searchCriteria.partName
                }
                if (this.searchCriteria.materialComposition) {
                    params.material_composition = this.searchCriteria.materialComposition
                }
                if (this.searchCriteria.weight !== null) {
                    params.weight = this.searchCriteria.weight
                }

                const response = await soundInsulationCoefficientApi.querySoundInsulationCoefficient(params)
                this.queryResults = response.data || []

                // 处理图表数据
                this.processChartData()

                return this.queryResults
            } catch (error) {
                this.error = '查询隔声量系数数据失败'
                console.error('查询隔声量系数数据失败:', error)
                throw error
            } finally {
                this.queryLoading = false
            }
        },

        // 处理图表数据
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

        // 重置状态
        resetState() {
            this.searchCriteria = {
                testType: '',
                partName: '',
                materialComposition: '',
                weight: null
            }
            this.partNames = []
            this.materialCompositions = []
            this.weights = []
            this.queryResults = []
            this.chartData = []
            this.error = null
        }
    }
})
