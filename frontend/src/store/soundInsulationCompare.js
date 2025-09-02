import { defineStore } from 'pinia'
import soundInsulationApi from '@/api/soundInsulation'

export const useSoundInsulationCompareStore = defineStore('soundInsulationCompare', {
    state: () => ({
        // 查询表单状态
        searchForm: {
            areaId: null,
            vehicleModelIds: []
        },

        // 选项数据
        areaOptions: [],
        vehicleModelOptions: [],

        // 加载状态
        areasLoading: false,
        vehicleModelsLoading: false,
        compareLoading: false,

        // 查询结果
        compareResult: [],
        chartData: [], // 专门用于图表的数据

        // UI状态
        selectAllVehicles: false,

        // 弹窗状态
        imageDialogVisible: false,
        currentImageData: null,
    }),

    getters: {
        // 是否可以查询
        canQuery: (state) => {
            return state.searchForm.areaId && state.searchForm.vehicleModelIds.length > 0
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
        // 加载区域列表
        async loadAreas() {
            try {
                this.areasLoading = true
                const response = await soundInsulationApi.getSoundInsulationAreas()
                this.areaOptions = response.data || []
            } catch (error) {
                console.error('加载区域列表失败:', error)
                throw error
            } finally {
                this.areasLoading = false
            }
        },

        // 根据区域加载车型
        async loadVehiclesByArea(areaId) {
            if (!areaId) {
                this.vehicleModelOptions = []
                return
            }

            try {
                this.vehicleModelsLoading = true
                const response = await soundInsulationApi.getVehiclesByArea({ area_id: areaId })
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
                throw new Error('请选择区域和车型')
            }

            try {
                this.compareLoading = true

                const data = {
                    area_id: this.searchForm.areaId,
                    vehicle_model_ids: this.searchForm.vehicleModelIds.join(',')
                }

                const response = await soundInsulationApi.compareSoundInsulationData(data)
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
            const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']

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
                    text: '隔声量对比曲线',
                    left: 'center',
                    textStyle: {
                        fontSize: 16,
                        fontWeight: 'normal'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: {
                            backgroundColor: '#6a7985'
                        }
                    },
                    formatter: function(params) {
                        if (!params || params.length === 0) return ''

                        const dataIndex = params[0].dataIndex
                        const freq = frequencies[dataIndex]
                        let result = `<div style="font-weight: bold; margin-bottom: 5px;">频率: ${freq}Hz</div>`

                        params.forEach(param => {
                            const value = param.value
                            const seriesName = param.seriesName
                            const color = param.color

                            if (value !== null && value !== undefined) {
                                result += `<div style="margin: 2px 0;">
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${color}; margin-right: 5px;"></span>
                  ${seriesName}: <strong>${Number(value).toFixed(1)} dB</strong>
                </div>`
                            } else {
                                result += `<div style="margin: 2px 0; color: #999;">
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${color}; margin-right: 5px;"></span>
                  ${seriesName}: <span style="color: #999;">无数据</span>
                </div>`
                            }
                        })

                        result += '<br/>点击数据点查看测试详情'
                        return result
                    }
                },
                legend: {
                    top: 35,
                    type: 'scroll',
                    pageButtonItemGap: 5,
                    pageButtonGap: 30,
                    pageButtonPosition: 'end',
                    pageFormatter: '{current}/{total}',
                    pageIconColor: '#2f4554',
                    pageIconInactiveColor: '#aaa',
                    pageIconSize: 15,
                    pageTextStyle: {
                        color: '#666'
                    }
                },
                grid: {
                    left: '8%',
                    right: '5%',
                    bottom: '20%',
                    top: '18%',
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
                    min: 0,
                    max: 70,
                    interval: 10,
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

        // 设置区域
        setArea(areaId) {
            this.searchForm.areaId = areaId
            // 清空车型选择和结果
            this.searchForm.vehicleModelIds = []
            this.selectAllVehicles = false
            this.compareResult = []
            this.chartData = []

            // 加载对应区域的车型
            if (areaId) {
                this.loadVehiclesByArea(areaId)
            } else {
                this.vehicleModelOptions = []
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
                areaId: null,
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
            if (this.areaOptions.length === 0) {
                await this.loadAreas()
            }

            // 如果已选择区域但车型列表为空，重新加载车型
            if (this.searchForm.areaId && this.vehicleModelOptions.length === 0) {
                await this.loadVehiclesByArea(this.searchForm.areaId)
            }
        }
    }
})
