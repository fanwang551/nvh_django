import { defineStore } from 'pinia'
import { soundAbsorptionApi } from '@/api/soundAbsorption'

export const useSoundAbsorptionQueryStore = defineStore('soundAbsorptionQuery', {
    state: () => ({
        // 查询表单状态
        searchForm: {
            partName: '',
            materialComposition: '',
            weight: null
        },

        // 选项数据
        partNameOptions: [],
        materialCompositionOptions: [],
        weightOptions: [],

        // 查询结果
        queryResult: [],
        chartData: [], // 专门用于图表的数据

        // 加载状态
        partNamesLoading: false,
        materialCompositionsLoading: false,
        weightsLoading: false,
        queryLoading: false,

        // 弹窗状态
        imageDialogVisible: false,
        currentImageData: null,
    }),

    getters: {
        // 是否可以查询
        canQuery: (state) => {
            return state.searchForm.partName || 
                   state.searchForm.materialComposition || 
                   state.searchForm.weight !== null
        },

        // 是否有查询结果
        hasResults: (state) => {
            return state.queryResult.length > 0
        },

        // 获取当前查询条件描述
        queryDescription: (state) => {
            const conditions = []
            if (state.searchForm.partName) {
                conditions.push(`零件名称: ${state.searchForm.partName}`)
            }
            if (state.searchForm.materialComposition) {
                conditions.push(`材料组成: ${state.searchForm.materialComposition}`)
            }
            if (state.searchForm.weight !== null) {
                conditions.push(`克重: ${state.searchForm.weight}g/m²`)
            }
            return conditions.join(' | ')
        }
    },

    actions: {
        // 加载零件名称选项
        async loadPartNameOptions() {
            try {
                this.partNamesLoading = true
                const response = await soundAbsorptionApi.getPartNameOptions()
                this.partNameOptions = response.data || []
            } catch (error) {
                console.error('加载零件名称选项失败:', error)
                throw error
            } finally {
                this.partNamesLoading = false
            }
        },

        // 加载材料组成选项
        async loadMaterialCompositionOptions(partName = null) {
            try {
                this.materialCompositionsLoading = true
                const params = {}
                if (partName) {
                    params.part_name = partName
                }
                const response = await soundAbsorptionApi.getMaterialCompositionOptions(params)
                this.materialCompositionOptions = response.data || []
            } catch (error) {
                console.error('加载材料组成选项失败:', error)
                throw error
            } finally {
                this.materialCompositionsLoading = false
            }
        },

        // 加载克重选项
        async loadWeightOptions(partName = null, materialComposition = null) {
            try {
                this.weightsLoading = true
                const params = {}
                if (partName) {
                    params.part_name = partName
                }
                if (materialComposition) {
                    params.material_composition = materialComposition
                }
                const response = await soundAbsorptionApi.getWeightOptions(params)
                this.weightOptions = response.data || []
            } catch (error) {
                console.error('加载克重选项失败:', error)
                throw error
            } finally {
                this.weightsLoading = false
            }
        },

        // 查询吸声系数数据
        async queryData() {
            if (!this.canQuery) {
                throw new Error('请至少选择一个查询条件')
            }

            try {
                this.queryLoading = true

                const data = {}
                if (this.searchForm.partName) {
                    data.part_name = this.searchForm.partName
                }
                if (this.searchForm.materialComposition) {
                    data.material_composition = this.searchForm.materialComposition
                }
                if (this.searchForm.weight !== null) {
                    data.weight = this.searchForm.weight
                }

                const response = await soundAbsorptionApi.querySoundAbsorption(data)
                this.queryResult = response.data || []

                // 生成图表数据
                this.generateChartData()

                return this.queryResult
            } catch (error) {
                console.error('查询吸声系数数据失败:', error)
                throw error
            } finally {
                this.queryLoading = false
            }
        },

        // 生成图表数据
        generateChartData() {
            const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

            this.chartData = this.queryResult.map((item, index) => {
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
                    itemData: item // 保存完整数据用于点击事件
                }
            })
        },

        // 获取图表配置
        getChartOption() {
            const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]
            const colors = ['#5470c6', '#ee6666', '#91cc75', '#fac858', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

            const series = []
            this.chartData.forEach((item, index) => {
                // 测试值曲线（实线）
                series.push({
                    name: `测试值`,
                    type: 'line',
                    data: item.testData.map((value, freqIndex) => ({
                        value: value,
                        freq: frequencies[freqIndex],
                        freqLabel: `${frequencies[freqIndex]}Hz`,
                        itemData: item.itemData
                    })),
                    symbol: 'circle',
                    symbolSize: 8,
                    lineStyle: {
                        width: 3,
                        color: colors[index % colors.length],
                        type: 'solid'
                    },
                    itemStyle: {
                        color: colors[index % colors.length]
                    },
                    emphasis: {
                        focus: 'series',
                        symbolSize: 12
                    },
                    connectNulls: false
                })

                // 目标值曲线（虚线）
                series.push({
                    name: `目标值`,
                    type: 'line',
                    data: item.targetData.map((value, freqIndex) => ({
                        value: value,
                        freq: frequencies[freqIndex],
                        freqLabel: `${frequencies[freqIndex]}Hz`,
                        itemData: item.itemData
                    })),
                    symbol: 'diamond',
                    symbolSize: 8,
                    lineStyle: {
                        width: 3,
                        color: colors[index % colors.length],
                        type: 'dashed'
                    },
                    itemStyle: {
                        color: colors[index % colors.length]
                    },
                    emphasis: {
                        focus: 'series',
                        symbolSize: 12
                    },
                    connectNulls: false
                })
            })

            return {
                title: {
                    text: '吸声系数曲线对比',
                    left: 'center',
                    textStyle: {
                        fontSize: 16,
                        fontWeight: 'normal'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    },
                    formatter: function(params) {
                        if (params.length === 0) return ''

                        const dataIndex = params[0].dataIndex
                        const freq = frequencies[dataIndex]
                        let result = `频率: ${freq}Hz<br/>`

                        params.forEach(param => {
                            if (param.value !== null && param.value !== undefined) {
                                result += `${param.seriesName}: ${param.value}<br/>`
                            }
                        })
                        result += '<br/>点击数据点查看测试详情'
                        return result
                    }
                },
                legend: {
                    top: 30,
                    type: 'scroll'
                },
                grid: {
                    left: '8%',
                    right: '4%',
                    bottom: '15%',
                    top: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    name: '频率 (Hz)',
                    nameLocation: 'middle',
                    nameGap: 30,
                    data: frequencies.map(freq => freq.toString()),
                    axisLabel: {
                        rotate: 45,
                        fontSize: 12
                    }
                },
                yAxis: {
                    type: 'value',
                    name: '吸声系数',
                    nameLocation: 'middle',
                    nameGap: 50,
                    min: 0,
                    max: 1,
                    axisLabel: {
                        formatter: '{value}',
                        fontSize: 12
                    },
                    splitLine: {
                        show: true,
                        lineStyle: {
                            color: '#e6e6e6',
                            type: 'dashed'
                        }
                    }
                },
                series: series,
                dataZoom: [
                    {
                        type: 'slider',
                        show: true,
                        xAxisIndex: [0],
                        start: 0,
                        end: 100,
                        bottom: '5%'
                    }
                ]
            }
        },

        // 零件名称变化处理
        async onPartNameChange(partName) {
            this.searchForm.partName = partName
            
            // 清空下级选项
            this.searchForm.materialComposition = ''
            this.searchForm.weight = null
            this.materialCompositionOptions = []
            this.weightOptions = []

            if (partName) {
                // 重新加载材料组成选项
                await this.loadMaterialCompositionOptions(partName)
            }
        },

        // 材料组成变化处理
        async onMaterialCompositionChange(materialComposition) {
            this.searchForm.materialComposition = materialComposition
            
            // 清空下级选项
            this.searchForm.weight = null
            this.weightOptions = []

            if (materialComposition) {
                // 重新加载克重选项
                await this.loadWeightOptions(this.searchForm.partName, materialComposition)
            }
        },

        // 克重变化处理
        onWeightChange(weight) {
            this.searchForm.weight = weight
        },

        // 显示图片弹窗
        showImageDialog(data) {
            if (data && data.test_image_path) {
                this.currentImageData = data
                this.imageDialogVisible = true
            }
        },

        // 关闭图片弹窗
        closeImageDialog() {
            this.imageDialogVisible = false
            this.currentImageData = null
        },

        // 清空所有状态
        resetState() {
            this.searchForm = {
                partName: '',
                materialComposition: '',
                weight: null
            }
            this.queryResult = []
            this.chartData = []
            this.imageDialogVisible = false
            this.currentImageData = null
        },

        // 初始化页面数据
        async initializePageData() {
            if (this.partNameOptions.length === 0) {
                await this.loadPartNameOptions()
            }
        }
    }
})