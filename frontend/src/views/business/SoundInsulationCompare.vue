<template>
  <div class="sound-insulation-compare">


    <!-- 查询条件卡片 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>

      <el-form :model="searchForm" label-width="120px" class="search-form">
        <el-row :gutter="24">
          <!-- 区域选择 -->
          <el-col :span="7">
            <el-form-item label="隔声区域" required>
              <el-select
                v-model="searchForm.areaId"
                placeholder="请选择区域"
                :loading="areasLoading"
                @change="handleAreaChange"
                style="width: 100%"
              >
                <el-option
                  v-for="area in areaOptions"
                  :key="area.id"
                  :label="area.area_name"
                  :value="area.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 车型选择 -->
          <el-col :span="11">
            <el-form-item label="对比车型" required>
              <el-select
                v-model="searchForm.vehicleModelIds"
                placeholder="请先选择区域，然后选择车型"
                :loading="vehicleModelsLoading"
                :disabled="!searchForm.areaId"
                multiple
                collapse-tags
                collapse-tags-tooltip
                style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                    v-model="selectAllVehicles"
                    @change="handleSelectAllVehicles"
                    style="margin-left: 12px"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                  v-for="vehicle in vehicleModelOptions"
                  :key="vehicle.id"
                  :label="vehicle.vehicle_model_name"
                  :value="vehicle.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 查询按钮 -->
          <el-col :span="6">
            <el-form-item>
              <el-button
                type="primary"
                :icon="TrendCharts"
                :loading="compareLoading"
                :disabled="!canQuery"
                @click="handleCompare"
                style="width: 100%; min-width: 120px;"
              >
                生成对比
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 对比结果 -->
    <div v-if="compareResult.length > 0" class="result-section">
      <!-- 对比表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">隔声量对比表格</span>
            <span class="card-subtitle">单位：dB</span>
          </div>
        </template>

        <div class="table-container">
          <el-table
            :data="compareResult"
            v-loading="compareLoading"
            class="result-table"
            stripe
            border
            :header-cell-style="{ backgroundColor: '#fafafa', color: '#606266', fontWeight: '600', fontSize: '14px' }"
            :scroll-x="true"
          >
            <el-table-column prop="vehicle_model_name" label="车型名称" width="180" fixed="left" />
            <el-table-column label="200Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_200) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="250Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_250) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="315Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_315) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="400Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_400) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="500Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_500) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="630Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_630) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="800Hz" width="80" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_800) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="1000Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_1000) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="1250Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_1250) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="1600Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_1600) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="2000Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_2000) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="2500Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_2500) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="3150Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_3150) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="4000Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_4000) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="5000Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_5000) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="6300Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_6300) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="8000Hz" width="90" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_8000) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="10000Hz" width="100" align="center">
              <template #default="scope">
                <span class="frequency-value">{{ formatFrequencyValue(scope.row.frequency_data.freq_10000) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 隔声量曲线图 -->
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">隔声量曲线图</span>
            <span class="card-subtitle">点击数据点查看测试图片</span>
          </div>
        </template>

        <div class="chart-container">
          <div ref="chartRef" class="echarts-container"></div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!compareLoading" class="empty-state">
      <el-empty description="请选择条件并生成对比数据" />
    </div>

    <!-- 测试图片弹窗 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="测试图片"
      width="600px"
      :before-close="handleCloseImageDialog"
      class="image-dialog"
    >
      <div v-if="currentImageData" class="image-content">
        <div class="image-info">
          <h4>{{ currentImageData.vehicle_model_name }} - {{ currentImageData.area_name }}</h4>
          <div class="test-details">
            <p><strong>测试日期：</strong>{{ currentImageData.test_date || '未知' }}</p>
            <p><strong>测试地点：</strong>{{ currentImageData.test_location || '未知' }}</p>
            <p><strong>测试工程师：</strong>{{ currentImageData.test_engineer || '未知' }}</p>
          </div>
        </div>
        
        <div class="image-wrapper">
          <div v-if="currentImageData.test_image_path" class="image-container">
            <img
              :src="getImageUrl(currentImageData.test_image_path)"
              :alt="`${currentImageData.vehicle_model_name}测试图片`"
              class="test-image"
              @error="handleImageError"
            />
          </div>
          <div v-else class="no-image">
            <el-empty description="暂无测试图片" />
          </div>
        </div>
        
        <div v-if="currentImageData.remarks" class="remarks">
          <p><strong>备注：</strong>{{ currentImageData.remarks }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import soundInsulationApi from '@/api/soundInsulation'

// 搜索表单
const searchForm = ref({
  areaId: null,
  vehicleModelIds: []
})

// 选项数据
const areaOptions = ref([])
const vehicleModelOptions = ref([])

// 加载状态
const areasLoading = ref(false)
const vehicleModelsLoading = ref(false)
const compareLoading = ref(false)

// 对比结果
const compareResult = ref([])

// 图表引用
const chartRef = ref(null)
let chartInstance = null

// 弹窗相关状态
const imageDialogVisible = ref(false)
const currentImageData = ref(null)

// 全选状态
const selectAllVehicles = ref(false)

// 计算属性
const canQuery = computed(() => {
  return searchForm.value.areaId && searchForm.value.vehicleModelIds.length > 0
})

// 频率标签映射
const frequencyLabels = {
  freq_200: '200Hz',
  freq_250: '250Hz',
  freq_315: '315Hz',
  freq_400: '400Hz',
  freq_500: '500Hz',
  freq_630: '630Hz',
  freq_800: '800Hz',
  freq_1000: '1000Hz',
  freq_1250: '1250Hz',
  freq_1600: '1600Hz',
  freq_2000: '2000Hz',
  freq_2500: '2500Hz',
  freq_3150: '3150Hz',
  freq_4000: '4000Hz',
  freq_5000: '5000Hz',
  freq_6300: '6300Hz',
  freq_8000: '8000Hz',
  freq_10000: '10000Hz'
}

// 频率数组（用于图表横轴）
const frequencies = [200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

// 加载区域列表
const loadAreas = async () => {
  try {
    areasLoading.value = true
    const response = await soundInsulationApi.getSoundInsulationAreas()
    areaOptions.value = response.data || []
  } catch (error) {
    console.error('加载区域列表失败:', error)
    ElMessage.error('加载区域列表失败')
  } finally {
    areasLoading.value = false
  }
}

// 根据区域加载车型列表
const loadVehiclesByArea = async (areaId) => {
  try {
    vehicleModelsLoading.value = true
    const response = await soundInsulationApi.getVehiclesByArea({ area_id: areaId })
    vehicleModelOptions.value = response.data || []

    // 重置车型选择
    searchForm.value.vehicleModelIds = []
    selectAllVehicles.value = false

    if (vehicleModelOptions.value.length === 0) {
      ElMessage.warning('该区域暂无车型数据')
    }
  } catch (error) {
    console.error('加载车型列表失败:', error)
    ElMessage.error('加载车型列表失败')
    vehicleModelOptions.value = []
  } finally {
    vehicleModelsLoading.value = false
  }
}

// 区域变化处理
const handleAreaChange = (areaId) => {
  if (areaId) {
    loadVehiclesByArea(areaId)
  } else {
    vehicleModelOptions.value = []
    searchForm.value.vehicleModelIds = []
    selectAllVehicles.value = false
  }

  // 清空对比结果
  compareResult.value = []
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

// 全选/反选车型
const handleSelectAllVehicles = (checked) => {
  if (checked) {
    searchForm.value.vehicleModelIds = vehicleModelOptions.value.map(v => v.id)
  } else {
    searchForm.value.vehicleModelIds = []
  }
}

// 监听车型选择变化，更新全选状态
watch(() => searchForm.value.vehicleModelIds, (newIds) => {
  if (newIds.length === 0) {
    selectAllVehicles.value = false
  } else if (newIds.length === vehicleModelOptions.value.length) {
    selectAllVehicles.value = true
  } else {
    selectAllVehicles.value = false
  }
})

// 格式化频率值
const formatFrequencyValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  return Number(value).toFixed(1)
}

// 生成对比数据
const handleCompare = async () => {
  if (!canQuery.value) {
    ElMessage.warning('请选择区域和车型')
    return
  }

  try {
    compareLoading.value = true

    const data = {
      area_id: searchForm.value.areaId,
      vehicle_model_ids: searchForm.value.vehicleModelIds.join(',')
    }

    const response = await soundInsulationApi.compareSoundInsulationData(data)
    compareResult.value = response.data || []

    if (compareResult.value.length > 0) {
      ElMessage.success('对比数据生成成功')
      // 等待DOM更新后渲染图表
      await nextTick()
      renderChart()
    } else {
      ElMessage.warning('未找到匹配的对比数据')
    }
  } catch (error) {
    console.error('生成对比数据失败:', error)
    ElMessage.error('生成对比数据失败')
  } finally {
    compareLoading.value = false
  }
}

// 图表渲染
const renderChart = () => {
  if (!chartRef.value || !compareResult.value.length) return

  // 销毁现有图表实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新的图表实例
  chartInstance = echarts.init(chartRef.value)

  // 准备图表数据
  const series = []
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']

  compareResult.value.forEach((item, index) => {
    const seriesData = []

    // 构建每个车型的数据点
    frequencies.forEach((freq, freqIndex) => {
      const fieldName = `freq_${freq}`
      const value = item.frequency_data[fieldName]

      // 确保数值有效，过滤null和undefined
      const numValue = value !== null && value !== undefined ? Number(value) : null

      seriesData.push({
        value: [freqIndex, numValue], // 使用频率索引和数值
        freq: freq, // 保存实际频率值
        freqLabel: `${freq}Hz`, // 保存频率标签
        itemData: item // 保存完整数据用于点击事件
      })
    })

    series.push({
      name: item.vehicle_model_name,
      type: 'line',
      data: seriesData,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3
      },
      itemStyle: {
        color: colors[index % colors.length]
      },
      emphasis: {
        focus: 'series',
        symbolSize: 12
      },
      connectNulls: false // 不连接空值点
    })
  })

  // 图表配置
  const option = {
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

        // 获取频率信息（从第一个数据点获取）
        const firstParam = params[0]
        const freqLabel = firstParam.data.freqLabel || `${frequencies[firstParam.dataIndex]}Hz`

        let result = `<div style="font-weight: bold; margin-bottom: 5px;">频率: ${freqLabel}</div>`

        // 遍历所有车型的数据
        params.forEach(param => {
          const value = param.value[1]
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
      data: frequencies,
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
        formatter: '{value} dB',
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

  chartInstance.setOption(option)

  // 添加点击事件
  chartInstance.on('click', function(params) {
    if (params.data && params.data.itemData) {
      showImageDialog(params.data.itemData)
    }
  })

  // 响应式处理
  const resizeHandler = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }

  // 移除之前的监听器，避免重复绑定
  window.removeEventListener('resize', resizeHandler)
  window.addEventListener('resize', resizeHandler)
}

// 显示图片弹窗
const showImageDialog = (data) => {
  currentImageData.value = data
  imageDialogVisible.value = true
}

// 关闭图片弹窗
const handleCloseImageDialog = () => {
  imageDialogVisible.value = false
  currentImageData.value = null
}

// 获取图片URL
const getImageUrl = (filePath) => {
  if (!filePath) return ''
  // 如果是相对路径，添加后端服务器地址
  if (filePath.startsWith('/')) {
    return `http://127.0.0.1:8000${filePath}`
  }
  return filePath
}

// 图片加载错误处理
const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  ElMessage.error('图片加载失败')
}

// 生命周期
onMounted(() => {
  loadAreas()
})

// 监听窗口大小变化
watch(() => compareResult.value, () => {
  if (compareResult.value.length > 0) {
    nextTick(() => {
      renderChart()
    })
  }
})
</script>

<style scoped>
.sound-insulation-compare {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

.search-form {
  margin: 0;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.table-card,
.chart-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.table-container {
  overflow-x: auto;
  overflow-y: hidden;
  width: 100%;
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.result-table {
  width: 100%;
  min-width: 1800px;
}

.frequency-value {
  font-weight: 500;
  color: #606266;
}

.chart-container {
  width: 100%;
  height: 500px;
  padding: 20px 10px;
  position: relative;
}

.echarts-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

/* 弹窗样式 */
.image-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
  }
}

.image-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-info h4 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.test-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.test-details p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.image-container {
  max-width: 100%;
  text-align: center;
}

.test-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-image {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.remarks {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.remarks p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-button--primary) {
  background-color: #0052d9;
  border-color: #0052d9;
}

:deep(.el-button--primary:hover) {
  background-color: #1890ff;
  border-color: #1890ff;
}

:deep(.el-table--border) {
  border: none;
}

:deep(.el-table--border::after) {
  display: none;
}

:deep(.el-table--border .el-table__inner-wrapper::before) {
  display: none;
}

:deep(.el-table .el-table__cell) {
  padding: 8px 0;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa !important;
}

/* 表格滚动条样式 */
.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .search-form .el-col {
    margin-bottom: 16px;
  }

  .chart-container {
    height: 400px;
  }

  .result-table {
    min-width: 1600px;
  }
}

@media (max-width: 768px) {
  .page-header h2 {
    font-size: 20px;
  }

  .result-table {
    min-width: 1400px;
  }

  .chart-container {
    height: 350px;
  }

  .test-details {
    grid-template-columns: 1fr;
  }

  .search-form .el-row {
    flex-direction: column;
  }

  .search-form .el-col {
    width: 100% !important;
    margin-bottom: 16px;
  }
}
</style>
