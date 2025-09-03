<template>
  <div class="vehicle-reverberation-query">
    <!-- 查询条件卡片 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>

      <el-form :model="store.searchForm" label-width="120px" class="search-form">
        <el-row :gutter="24">
          <!-- 车型选择 -->
          <el-col :span="16">
            <el-form-item label="对比车型" required>
              <el-select
                  v-model="store.searchForm.vehicleModelIds"
                  placeholder="请选择要对比的车型"
                  :loading="store.vehicleModelsLoading"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  @change="handleVehicleModelChange"
                  style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                      v-model="store.selectAllVehicles"
                      @change="handleSelectAllVehicles"
                      style="margin-left: 12px"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                    v-for="vehicle in store.vehicleModelOptions"
                    :key="vehicle.id"
                    :label="vehicle.vehicle_model_name"
                    :value="vehicle.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 操作按钮 -->
          <el-col :span="8">
            <el-form-item label=" ">
              <el-button
                  type="primary"
                  :icon="TrendCharts"
                  :loading="store.compareLoading"
                  :disabled="!store.canQuery"
                  @click="handleCompare"
              >
                生成对比
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 对比结果 -->
    <div v-if="store.hasResults" class="result-section">
      <!-- 对比表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">车辆混响时间对比表</span>
            <span class="card-subtitle">单位：s</span>
          </div>
        </template>

        <div class="table-container">
          <el-table
              :data="store.compareResult"
              border
              stripe
              style="width: 100%"
              :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column prop="vehicle_model_name" label="车型名称" width="120" fixed="left" />

            <!-- 频率列 -->
            <el-table-column
                v-for="freq in frequencies"
                :key="freq"
                :prop="`frequency_data.freq_${freq}`"
                :label="`${freq}Hz`"
                width="85"
                align="center"
            >
              <template #default="scope">
                <span v-if="scope.row.frequency_data[`freq_${freq}`] !== null">
                  {{ scope.row.frequency_data[`freq_${freq}`] }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>

            <el-table-column label="测试信息" width="120" fixed="right">
              <template #default="scope">
                <el-button
                    type="primary"
                    size="small"
                    text
                    @click="store.showImageDialog(scope.row)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 混响时间曲线图 -->
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">车辆混响时间曲线图</span>
            <span class="card-subtitle">点击数据点查看测试图片</span>
          </div>
        </template>

        <div class="chart-container">
          <div ref="chartRef" class="echarts-container"></div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!store.compareLoading" class="empty-state">
      <el-empty description="请选择车型并生成对比数据" />
    </div>

    <!-- 测试图片弹窗 -->
    <el-dialog
        v-model="store.imageDialogVisible"
        title="测试详情"
        width="600px"
        @close="handleCloseImageDialog"
    >
      <div v-if="store.currentImageData" class="image-dialog-content">
        <!-- 基本信息 -->
        <div class="info-section">
          <h4>基本信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="车型名称">
              {{ store.currentImageData.vehicle_model_name }}
            </el-descriptions-item>
            <el-descriptions-item label="备注">
              {{ store.currentImageData.remarks || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 测试图片 -->
        <div v-if="store.currentImageData.test_image_path" class="image-section">
          <h4>测试图片</h4>
          <div class="image-container">
            <img
                :src="getImageUrl(store.currentImageData.test_image_path)"
                alt="测试图片"
                class="test-image"
                @error="handleImageError"
            />
          </div>
        </div>
        <div v-else class="no-image">
          <el-empty description="暂无测试图片" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onDeactivated, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useVehicleReverberationQueryStore } from '@/store'
import { getImageUrl, handleImageError } from '@/utils/imageService'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'VehicleReverberationQuery'
})

// 使用Pinia store
const store = useVehicleReverberationQueryStore()

// 图表相关
const chartRef = ref(null)
let chartInstance = null
let resizeHandler = null

// 频率数组（用于图表横轴，混响时间频率范围：400-10000Hz）
const frequencies = [400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

// 全选/反选车型
const handleSelectAllVehicles = (checked) => {
  store.toggleSelectAllVehicles(checked)
}

// 车型选择变化处理
const handleVehicleModelChange = (vehicleIds) => {
  store.setVehicleModels(vehicleIds)
}

// 生成对比数据
const handleCompare = async () => {
  if (!store.canQuery) {
    ElMessage.warning('请选择车型')
    return
  }

  try {
    const result = await store.generateCompareData()

    if (result.length > 0) {
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
  }
}

// 重置表单
const handleReset = () => {
  store.resetState()
  destroyChart()
}

// 图片相关功能已移至 @/utils/imageService

// 销毁图表实例
const destroyChart = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
}

// 渲染ECharts图表
const renderChart = () => {
  console.log('开始渲染混响时间图表，容器存在:', !!chartRef.value, '数据长度:', store.chartData.length)

  if (!chartRef.value || !store.chartData.length) {
    console.warn('图表渲染条件不满足')
    return
  }

  // 检查容器是否可见和有尺寸
  const containerRect = chartRef.value.getBoundingClientRect()
  if (containerRect.width === 0 || containerRect.height === 0) {
    console.warn('图表容器尺寸为0，延迟渲染')
    setTimeout(() => {
      if (chartRef.value && store.chartData.length) {
        renderChart()
      }
    }, 100)
    return
  }

  // 销毁现有图表实例
  destroyChart()

  // 创建新的图表实例
  console.log('创建新的混响时间图表实例，容器尺寸:', containerRect.width, 'x', containerRect.height)
  chartInstance = echarts.init(chartRef.value)

  // 使用store中的图表配置
  const option = store.getChartOption()

  chartInstance.setOption(option)

  // 强制调整图表大小
  setTimeout(() => {
    if (chartInstance) {
      chartInstance.resize()
      console.log('图表大小已调整')
    }
  }, 100)

  // 添加点击事件
  chartInstance.on('click', function(params) {
    if (params.data && params.data.itemData) {
      store.showImageDialog(params.data.itemData)
    }
  })

  // 响应式处理
  resizeHandler = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }
  window.addEventListener('resize', resizeHandler)
}

// 关闭图片弹窗
const handleCloseImageDialog = () => {
  store.closeImageDialog()
}

onMounted(async () => {
  console.log('VehicleReverberationQuery mounted - 初始化页面数据')
  await store.initializePageData()

  // 如果已有数据，重新渲染图表
  if (store.hasResults) {
    console.log('检测到已有数据，准备渲染图表')
    await nextTick()
    renderChart()
  }
})

// keep-alive 激活时
onActivated(async () => {
  console.log('VehicleReverberationQuery activated - 恢复组件状态')

  // 初始化页面数据
  await store.initializePageData()

  // 强制重新渲染图表（如果有数据）
  if (store.hasResults) {
    await nextTick()
    if (chartRef.value) {
      console.log('标签切换回来，重新渲染混响时间图表')
      renderChart()
    }
  }
})

// keep-alive 停用时
onDeactivated(() => {
  console.log('VehicleReverberationQuery deactivated - 保存组件状态')

  // 销毁图表实例，避免内存泄漏
  destroyChart()

  // 关闭可能打开的弹窗
  if (store.imageDialogVisible) {
    store.closeImageDialog()
  }
})

// 组件卸载时
onBeforeUnmount(() => {
  destroyChart()
})
</script>

<style scoped>
.vehicle-reverberation-query {
  padding: 0;
  background-color: #f5f7fa;
}

/* 卡片样式 */
.search-card,
.table-card,
.chart-card {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #e7e7e7;
  background-color: #fff;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 500;
  color: #1f2937;
}

.card-title {
  font-size: 16px;
  color: #303133;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

/* 搜索表单 */
.search-form {
  margin: 0;
}

/* 表格容器 */
.table-container {
  max-height: 400px;
  overflow: auto;
}

.no-data {
  color: #c0c4cc;
  font-style: italic;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 500px;
  padding: 20px 0;
}

.echarts-container {
  width: 100%;
  height: 100%;
}

/* 空状态 */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* 弹窗样式 */
.image-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 20px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.image-section h4 {
  margin: 20px 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.image-container {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.test-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-image {
  padding: 40px 0;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form .el-col {
    margin-bottom: 16px;
  }

  .chart-container {
    height: 400px;
  }

  .table-container {
    max-height: 300px;
  }
}
</style>