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

        // UI状态
        selectAllVehicles: false,

        // 弹窗状态
        imageDialogVisible: false,
        currentImageData: null,
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

        // 全选状态
        isAllVehiclesSelected: (state) => {
            return state.vehicleModelOptions.length > 0 &&
                state.searchForm.vehicleModelIds.length === state.vehicleModelOptions.length
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

        // 生成图表数据
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
                    itemData: item // 保存完整数据用于点击事件
                }
            })
        },

        // 获取图表配置
        getChartOption() {
            const frequencies = [200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]
            const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

            const series = this.chartData.map((item, index) => ({
                name: item.name,
                type: 'line',
                data: item.data.map((value, freqIndex) => ({
                    value: value,
                    freq: frequencies[freqIndex],
                    freqLabel: `${frequencies[freqIndex]}Hz`,
                    itemData: item.itemData
                })),
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {
                    width: 3,
                    color: colors[index % colors.length]
                },
                itemStyle: {
                    color: colors[index % colors.length]
                },
                emphasis: {
                    focus: 'series',
                    symbolSize: 12
                },
                connectNulls: false
            }))

            return {
                title: {
                    text: '车型隔声量对比曲线',
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
                                result += `${param.seriesName}: ${param.value}dB<br/>`
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
                    name: '隔声量 (dB)',
                    nameLocation: 'middle',
                    nameGap: 50,
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

        // 设置车型选择
        setVehicleModels(vehicleIds) {
            this.searchForm.vehicleModelIds = vehicleIds
            this.updateSelectAllState()
        },

        // 全选/反选车型
        toggleSelectAllVehicles(checked) {
            if (checked) {
                this.searchForm.vehicleModelIds = this.vehicleModelOptions.map(v => v.id)
            } else {
                this.searchForm.vehicleModelIds = []
            }
            this.selectAllVehicles = checked
        },

        // 更新全选状态
        updateSelectAllState() {
            if (this.searchForm.vehicleModelIds.length === 0) {
                this.selectAllVehicles = false
            } else if (this.searchForm.vehicleModelIds.length === this.vehicleModelOptions.length) {
                this.selectAllVehicles = true
            } else {
                this.selectAllVehicles = false
            }
        },

        // 显示图片弹窗
        showImageDialog(data) {
            this.currentImageData = data
            this.imageDialogVisible = true
        },

        // 关闭图片弹窗
        closeImageDialog() {
            this.imageDialogVisible = false
            this.currentImageData = null
        },

        // 清空所有状态
        resetState() {
            this.searchForm = {
                vehicleModelIds: []
            }
            this.compareResult = []
            this.chartData = []
            this.selectAllVehicles = false
            this.imageDialogVisible = false
            this.currentImageData = null
        },

        // 初始化页面数据
        async initializePageData() {
            if (this.vehicleModelOptions.length === 0) {
                await this.loadVehicleModels()
            }
        }
    }
})
