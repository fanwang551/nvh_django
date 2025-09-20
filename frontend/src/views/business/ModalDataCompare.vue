<template>
  <div class="modal-data-compare">
    <!-- 选择控件区域 -->
    <el-card class="selection-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">对比条件</span>
        </div>
      </template>

      <el-form :model="compareForm" label-width="80px" class="selection-form">
        <el-row :gutter="4">
          <!-- 零件选择 -->
          <el-col :span="5">
            <el-form-item label="零件" required>
              <el-select
                v-model="compareForm.componentId"
                placeholder="请选择零件"
                clearable
                :loading="componentsLoading"
                @change="handleComponentChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in componentOptions"
                  :key="item.id"
                  :label="item.component_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 车型选择 -->
          <el-col :span="5">
            <el-form-item label="车型" required>
              <el-select
                v-model="compareForm.vehicleModelIds"
                placeholder="请选择车型（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                :loading="vehicleModelsLoading"
                :disabled="!compareForm.componentId"
                @change="handleVehicleModelChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in vehicleModelOptions"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 测试状态选择 -->
          <el-col :span="5">
            <el-form-item label="测试状态">
              <el-select
                v-model="compareForm.testStatuses"
                placeholder="请选择测试状态"
                :multiple="isTestStatusMultiple"
                collapse-tags
                collapse-tags-tooltip
                clearable
                :loading="testStatusesLoading"
                :disabled="!compareForm.vehicleModelIds.length"
                @change="handleTestStatusChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in testStatusOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 振型选择 -->
          <el-col :span="5">
            <el-form-item label="振型">
              <el-select
                v-model="compareForm.modeTypes"
                placeholder="请选择振型（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                :loading="modeTypesLoading"
                :disabled="!compareForm.testStatuses.length"
                @change="handleModeTypeChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in modeTypeOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 生成对比按钮 -->
          <el-col :span="2">
            <el-form-item>
              <el-button
                type="primary"
                :icon="TrendCharts"
                @click="handleCompare"
                :loading="compareLoading"
                :disabled="!canCompare"
                style="width: 100%; min-width: 100px;"
              >
                生成对比
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 对比结果展示区域 -->
    <div v-if="compareResult.length > 0" class="result-section">
      <!-- 对比表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">对比表格</span>
          </div>
        </template>

        <div class="table-container">
          <el-table
            :data="tableData"
            class="compare-table"
            border
            stripe
            :header-cell-style="{ backgroundColor: '#f1f3f5', fontWeight: 'bold', textAlign: 'center' }"
            :cell-style="{ textAlign: 'center' }"
          >
            <el-table-column prop="modeType" label="振型类型" width="200" fixed="left" />
            <el-table-column
              v-for="vehicle in vehicleColumns"
              :key="vehicle.key"
              :prop="vehicle.key"
              :label="vehicle.label"
              width="150"
            >
              <template #default="scope">
                <span v-if="scope.row[vehicle.key]" class="frequency-value">
                  {{ scope.row[vehicle.key] }} Hz
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 散点图 -->
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">散点图对比</span>
          </div>
        </template>

        <div class="chart-container">
          <div ref="chartContainer" class="echarts-container"></div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!compareLoading" class="empty-state">
      <el-empty description="请选择条件并生成对比数据" />
    </div>

    <!-- 查看振型弹窗 -->
    <el-dialog
      v-model="modalShapeDialogVisible"
      title="查看振型"
      width="800px"
      :before-close="handleCloseDialog"
      class="modal-shape-dialog"
    >
      <div class="modal-shape-content">
        <!-- Tab 切换按钮 -->
        <div class="tab-header">
          <div
            class="tab-item"
            :class="{ active: activeTab === 'shape' }"
            @click="switchDialogTab('shape')"
          >
            振型动画
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'photo' }"
            @click="switchDialogTab('photo')"
          >
            测试图片
          </div>
        </div>

        <!-- 图片展示区域 -->
        <div class="image-display-area">
          <!-- 振型动画 -->
          <div v-if="activeTab === 'shape'" class="image-container">
            <div v-if="currentModalData?.mode_shape_file" class="image-wrapper">
              <img
                :src="getImageUrl(currentModalData.mode_shape_file)"
                alt="振型动画"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">振型动画 - {{ currentModalData.mode_shape_description || '无描述' }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无振型动画数据" />
            </div>
          </div>

          <!-- 测试图片 -->
          <div v-if="activeTab === 'photo'" class="image-container">
            <div v-if="currentModalData?.test_photo_file" class="image-wrapper">
              <img
                :src="getImageUrl(currentModalData.test_photo_file)"
                alt="测试图片"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">测试图片 - {{ currentModalData.display_name || '无名称' }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无测试图片数据" />
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, onDeactivated, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useModalDataCompareStore } from '@/store/modalDataCompare'
import { getImageUrl } from '@/utils/imageService'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'ModalDataCompare'
})

// 使用Pinia store
const store = useModalDataCompareStore()

// 从store中获取响应式状态
const compareForm = computed({
  get: () => store.compareForm,
  set: (value) => store.compareForm = value
})

const componentOptions = computed(() => store.componentOptions)
const vehicleModelOptions = computed(() => store.vehicleModelOptions)
const testStatusOptions = computed(() => store.testStatusOptions)
const modeTypeOptions = computed(() => store.modeTypeOptions)

const componentsLoading = computed(() => store.componentsLoading)
const vehicleModelsLoading = computed(() => store.vehicleModelsLoading)
const testStatusesLoading = computed(() => store.testStatusesLoading)
const modeTypesLoading = computed(() => store.modeTypesLoading)
const compareLoading = computed(() => store.compareLoading)

const compareResult = computed(() => store.compareResult)
const tableData = computed(() => store.tableData)
const vehicleColumns = computed(() => store.vehicleColumns)
const canCompare = computed(() => store.canCompare)
const isTestStatusMultiple = computed(() => store.isTestStatusMultiple)

// UI状态管理（组件职责）
const modalShapeDialogVisible = ref(false)
const currentModalData = ref(null)
const activeTab = ref('shape')

// 图表状态管理（组件职责）
const chartContainer = ref(null)
let chartInstance = null

// 事件处理方法
const handleComponentChange = (componentId) => {
  store.handleComponentChange(componentId)
}

const handleVehicleModelChange = (vehicleModelIds) => {
  store.handleVehicleModelChange(vehicleModelIds)
}

const handleTestStatusChange = (testStatuses) => {
  store.handleTestStatusChange(testStatuses)
}

const handleModeTypeChange = (modeTypes) => {
  store.handleModeTypeChange(modeTypes)
}

// 生成对比数据
const handleCompare = async () => {
  if (!canCompare.value) {
    ElMessage.warning('请完善选择条件')
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

// 图表渲染
const renderChart = () => {
  if (!chartContainer.value || !compareResult.value.length) return

  // 检查容器是否可见和有尺寸
  const containerRect = chartContainer.value.getBoundingClientRect()
  if (containerRect.width === 0 || containerRect.height === 0) {
    // 容器尺寸为0，延迟渲染
    console.warn('图表容器尺寸为0，延迟渲染')
    setTimeout(() => {
      renderChart()
    }, 100)
    return
  }

  // 销毁现有图表实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新的图表实例
  chartInstance = echarts.init(chartContainer.value)

  // 准备图表数据
  const seriesData = {}
  const xAxisData = [...new Set(compareResult.value.map(item => item.display_name))]

  // 按振型类型分组数据，使用正确的数据格式
  compareResult.value.forEach(item => {
    if (!seriesData[item.mode_type]) {
      seriesData[item.mode_type] = []
    }

    const xIndex = xAxisData.indexOf(item.display_name)
    seriesData[item.mode_type].push({
      value: item.frequency, // 对于category类型的xAxis，使用简单数值格式
      modalData: item, // 保存完整的模态数据，用于点击事件
      itemStyle: {
        shadowBlur: 0
      }
    })
  })

  // 生成系列数据
  const series = Object.keys(seriesData).map((modeType, index) => ({
    name: modeType,
    type: 'scatter',
    data: seriesData[modeType],
    symbolSize: 8,
    itemStyle: {
      color: `hsl(${index * 60}, 70%, 50%)`,
      shadowBlur: 3,
      shadowColor: 'rgba(0, 0, 0, 0.2)'
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.3)'
      },
      symbolSize: 14
    }
  }))

  // 图表配置
  const option = {
    title: {
      text: '模态频率对比散点图',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: {
        color: '#303133',
        fontSize: 13
      },
      padding: [12, 16],
      extraCssText: 'box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);',
      formatter: (params) => {
        const vehicleName = xAxisData[params.dataIndex]
        const frequency = params.data.value
        const seriesColor = params.color
        
        if (!frequency) {
          return `<div style="color: #909399;">无数据</div>`
        }
        
        return `
          <div style="margin-bottom: 8px; font-weight: 600; color: #303133;">
            <span style="display: inline-block; width: 8px; height: 8px; background: ${seriesColor}; border-radius: 50%; margin-right: 6px;"></span>
            ${params.seriesName}
          </div>
          <div style="margin-bottom: 4px; color: #606266;">
            <strong>车型：</strong>${vehicleName}
          </div>
          <div style="margin-bottom: 8px; color: #606266;">
            <strong>频率：</strong><span style="color: #409eff; font-weight: 600;">${frequency.toFixed(1)} Hz</span>
          </div>
          <div style="color: #909399; font-size: 12px;">
            💡 点击数据点查看振型图
          </div>
        `
      }
    },
    legend: {
      type: 'scroll',
      bottom: 10,
      data: Object.keys(seriesData)
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: '车型/测试状态',
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#303133'
      },
      axisLabel: {
        rotate: 0,
        interval: 0,
        fontSize: 14,
        fontWeight: 'bold',
        color: '#606266'
      }
    },
    yAxis: {
      type: 'value',
      name: '频率 (Hz)',
      nameLocation: 'middle',
      nameGap: 50,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#303133'
      },
      axisLabel: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#606266',
        formatter: (value) => `${value.toFixed(1)}`
      }
    },
    series: series
  }

  chartInstance.setOption(option)

  // 渲染完成后强制调用resize()方法确保图表大小正确
  setTimeout(() => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }, 100)

  // 添加点击事件
  chartInstance.on('click', (params) => {
    if (params.data && params.data.modalData) {
      viewModalShape(params.data.modalData)
    }
  })

  // 响应式调整监听器
  const resizeListener = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }
  
  window.addEventListener('resize', resizeListener)
  
  // 保存监听器引用，用于清理
  chartInstance._resizeListener = resizeListener
}

// UI交互处理：弹窗相关方法（组件职责）
const viewModalShape = (modalData) => {
  currentModalData.value = modalData
  modalShapeDialogVisible.value = true
  activeTab.value = 'shape'
}

const handleCloseDialog = () => {
  modalShapeDialogVisible.value = false
  currentModalData.value = null
  activeTab.value = 'shape'
}

// UI交互处理：切换弹窗标签页（组件职责）
const switchDialogTab = (tab) => {
  activeTab.value = tab
}

// 图片URL生成功能已移至 @/utils/imageService

const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  ElMessage.error('图片加载失败')
}

// 生命周期钩子 - 按照Vue组件生命周期处理模式
onMounted(async () => {
  // 初始化基础数据
  await store.initializePageData()
})

// 保持活跃时 - 确保基础数据最新，但保持用户状态不变
onActivated(async () => {
  // 如果没有零件选项，重新加载
  if (store.componentOptions.length === 0) {
    await store.initializePageData()
  }
  
  // 如果有对比结果，重新渲染图表
  if (store.compareResult.length > 0) {
    await nextTick()
    // 等待容器完成渲染
    setTimeout(() => {
      if (chartContainer.value) {
        renderChart()
      }
    }, 200)
  }
})

// 失活时 - 清理UI状态，避免状态残留（组件职责）
onDeactivated(() => {
  // 清理弹窗状态
  if (modalShapeDialogVisible.value) {
    handleCloseDialog()
  }

  // 清理图表监听器，避免内存泄漏
  if (chartInstance && chartInstance._resizeListener) {
    window.removeEventListener('resize', chartInstance._resizeListener)
    chartInstance._resizeListener = null
  }
})

// 监听对比结果变化
watch(() => store.compareResult, (newResult) => {
  if (newResult && newResult.length > 0) {
    nextTick(() => {
      // 等待DOM更新完成后再渲染
      setTimeout(() => {
        if (chartContainer.value) {
          renderChart()
        }
      }, 100)
    })
  }
}, { immediate: true })
</script>

<style scoped>
.modal-data-compare {
  padding: 0;
}

/* 选择控件区域 */
.selection-card {
  margin-bottom: 24px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.selection-form {
  margin: 0;
}

:deep(.selection-form .el-form-item) {
  margin-bottom: 0;
}

:deep(.selection-form .el-form-item__label) {
  font-weight: 500;
  color: #374151;
}

/* 结果展示区域 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.table-card,
.chart-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 表格样式 */
.table-container {
  border-radius: 8px;
  overflow: hidden;
}

.compare-table {
  border-radius: 8px;
}

:deep(.compare-table .el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}

:deep(.compare-table .el-table__header th) {
  background-color: #f1f3f5 !important;
  color: #303133;
  font-weight: bold;
  border-bottom: 2px solid #dcdfe6;
}

:deep(.compare-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}

:deep(.compare-table .el-table__body td) {
  border-bottom: 1px solid #ebeef5;
}

.frequency-value {
  font-weight: 600;
  color: #409eff;
}

.no-data {
  color: #c0c4cc;
  font-style: italic;
}

/* 图表样式 */
.chart-container {
  padding: 16px;
}

.echarts-container {
  width: 100%;
  height: 400px;
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  :deep(.selection-form .el-row) {
    flex-wrap: wrap;
  }

  :deep(.selection-form .el-col) {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  :deep(.selection-form .el-col) {
    flex: 0 0 100%;
    max-width: 100%;
    margin-bottom: 12px;
  }

  .echarts-container {
    height: 300px;
  }
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

/* 弹窗样式 */
.modal-shape-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.modal-shape-content {
  .tab-header {
    display: flex;
    border-bottom: 1px solid #e4e7ed;
    background-color: #fafafa;
  }

  .tab-item {
    flex: 1;
    padding: 16px 20px;
    text-align: center;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #606266;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;

    &:hover {
      background-color: #f0f2f5;
      color: #409eff;
    }

    &.active {
      color: #409eff;
      border-bottom-color: #409eff;
      background-color: #fff;
    }
  }

  .image-display-area {
    padding: 20px;
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .image-container {
    width: 100%;
    text-align: center;
  }

  .image-wrapper {
    display: inline-block;
    max-width: 100%;
  }

  .modal-image {
    max-width: 100%;
    max-height: 500px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;

    &:hover {
      transform: scale(1.02);
    }
  }

  .image-caption {
    margin-top: 12px;
    font-size: 14px;
    color: #606266;
    font-weight: 500;
  }

  .no-image {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: #909399;
  }
}
</style>
