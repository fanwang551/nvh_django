<template>
  <div class="modal-data-compare">
    <div class="page-header">
      <h2>模态数据对比</h2>
      <p class="page-description">对比不同模态测试结果</p>
    </div>

    <!-- 选择控件区域 -->
    <el-card class="selection-card" shadow="never">
      <div class="selection-form">
        <div class="form-row">
          <div class="form-group">
            <span class="form-label">零件：</span>
            <el-select
              v-model="compareForm.componentId"
              placeholder="请选择零件"
              class="form-select"
              clearable
              :loading="componentsLoading"
              @change="handleComponentChange"
            >
              <el-option
                v-for="item in componentOptions"
                :key="item.id"
                :label="item.component_name"
                :value="item.id"
              />
            </el-select>
          </div>

          <div class="form-group">
            <span class="form-label">车型：</span>
            <el-select
              v-model="compareForm.vehicleModelIds"
              placeholder="请选择车型（可多选）"
              class="form-select"
              multiple
              collapse-tags
              collapse-tags-tooltip
              clearable
              :loading="vehicleModelsLoading"
              :disabled="!compareForm.componentId"
              @change="handleVehicleModelChange"
            >
              <el-option
                v-for="item in vehicleModelOptions"
                :key="item.id"
                :label="item.vehicle_model_name"
                :value="item.id"
              />
            </el-select>
          </div>

          <div class="form-group">
            <span class="form-label">测试状态：</span>
            <el-select
              v-model="compareForm.testStatuses"
              placeholder="请选择测试状态"
              class="form-select"
              :multiple="isTestStatusMultiple"
              collapse-tags
              collapse-tags-tooltip
              clearable
              :loading="testStatusesLoading"
              :disabled="!compareForm.vehicleModelIds.length"
              @change="handleTestStatusChange"
            >
              <el-option
                v-for="item in testStatusOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>

          <div class="form-group">
            <span class="form-label">振型：</span>
            <el-select
              v-model="compareForm.modeTypes"
              placeholder="请选择振型（可多选）"
              class="form-select"
              multiple
              collapse-tags
              collapse-tags-tooltip
              clearable
              :loading="modeTypesLoading"
              :disabled="!compareForm.testStatuses.length"
              @change="handleModeTypeChange"
            >
              <el-option
                v-for="item in modeTypeOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>

          <div class="form-group">
            <el-button
              type="primary"
              :icon="TrendCharts"
              @click="handleCompare"
              :loading="compareLoading"
              :disabled="!canCompare"
              class="compare-btn"
            >
              生成对比
            </el-button>
          </div>
        </div>
      </div>
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
          <div ref="chartRef" class="echarts-container"></div>
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
            @click="activeTab = 'shape'"
          >
            振型动画
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'photo' }"
            @click="activeTab = 'photo'"
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
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import modalApi from '@/api/modal'

// 表单数据
const compareForm = ref({
  componentId: null,
  vehicleModelIds: [],
  testStatuses: [],
  modeTypes: []
})

// 选项数据
const componentOptions = ref([])
const vehicleModelOptions = ref([])
const testStatusOptions = ref([])
const modeTypeOptions = ref([])

// 加载状态
const componentsLoading = ref(false)
const vehicleModelsLoading = ref(false)
const testStatusesLoading = ref(false)
const modeTypesLoading = ref(false)
const compareLoading = ref(false)

// 对比结果
const compareResult = ref([])

// 图表引用
const chartRef = ref(null)
let chartInstance = null

// 弹窗相关状态
const modalShapeDialogVisible = ref(false)
const activeTab = ref('shape') // 'shape' 或 'photo'
const currentModalData = ref(null)

// 计算属性
const isTestStatusMultiple = computed(() => {
  // 业务规则：多车型时测试状态单选，单车型时可多选
  return compareForm.value.vehicleModelIds.length === 1
})

const canCompare = computed(() => {
  return compareForm.value.componentId &&
         compareForm.value.vehicleModelIds.length > 0 &&
         compareForm.value.testStatuses.length > 0 &&
         compareForm.value.modeTypes.length > 0
})

// 表格数据处理
const tableData = computed(() => {
  if (!compareResult.value.length) return []

  // 按振型类型分组
  const groupedData = {}
  compareResult.value.forEach(item => {
    if (!groupedData[item.mode_type]) {
      groupedData[item.mode_type] = { modeType: item.mode_type }
    }
    groupedData[item.mode_type][item.display_name] = item.frequency
  })

  return Object.values(groupedData)
})

// 车型列数据
const vehicleColumns = computed(() => {
  if (!compareResult.value.length) return []

  const uniqueVehicles = [...new Set(compareResult.value.map(item => item.display_name))]
  return uniqueVehicles.map(name => ({
    key: name,
    label: name
  }))
})

// API调用方法
const loadComponents = async () => {
  try {
    componentsLoading.value = true
    const response = await modalApi.getComponents()
    componentOptions.value = response.data || []
  } catch (error) {
    console.error('加载零件列表失败:', error)
    ElMessage.error('加载零件列表失败')
  } finally {
    componentsLoading.value = false
  }
}

const loadRelatedVehicleModels = async (componentId) => {
  try {
    vehicleModelsLoading.value = true
    const response = await modalApi.getRelatedVehicleModels({ component_id: componentId })
    vehicleModelOptions.value = response.data || []
  } catch (error) {
    console.error('加载相关车型失败:', error)
    ElMessage.error('加载相关车型失败')
  } finally {
    vehicleModelsLoading.value = false
  }
}

const loadTestStatuses = async () => {
  try {
    testStatusesLoading.value = true
    const params = {
      component_id: compareForm.value.componentId,
      vehicle_model_ids: compareForm.value.vehicleModelIds.join(',')
    }
    const response = await modalApi.getTestStatuses(params)
    testStatusOptions.value = response.data || []
  } catch (error) {
    console.error('加载测试状态失败:', error)
    ElMessage.error('加载测试状态失败')
  } finally {
    testStatusesLoading.value = false
  }
}

const loadModeTypes = async () => {
  try {
    modeTypesLoading.value = true

    // 处理testStatuses，确保它是数组格式
    const testStatusesArray = Array.isArray(compareForm.value.testStatuses)
      ? compareForm.value.testStatuses
      : [compareForm.value.testStatuses]

    const params = {
      component_id: compareForm.value.componentId,
      vehicle_model_ids: compareForm.value.vehicleModelIds.join(','),
      test_statuses: testStatusesArray.join(',')
    }
    const response = await modalApi.getModeTypes(params)
    modeTypeOptions.value = response.data || []
  } catch (error) {
    console.error('加载振型类型失败:', error)
    ElMessage.error('加载振型类型失败')
  } finally {
    modeTypesLoading.value = false
  }
}

// 事件处理方法
const handleComponentChange = (componentId) => {
  // 重置后续选择
  compareForm.value.vehicleModelIds = []
  compareForm.value.testStatuses = []
  compareForm.value.modeTypes = []
  vehicleModelOptions.value = []
  testStatusOptions.value = []
  modeTypeOptions.value = []
  compareResult.value = []

  if (componentId) {
    loadRelatedVehicleModels(componentId)
  }
}

const handleVehicleModelChange = (vehicleModelIds) => {
  // 重置后续选择
  compareForm.value.testStatuses = []
  compareForm.value.modeTypes = []
  testStatusOptions.value = []
  modeTypeOptions.value = []
  compareResult.value = []

  if (vehicleModelIds.length > 0) {
    loadTestStatuses()
  }

  // 根据业务规则调整测试状态选择模式
  if (!isTestStatusMultiple.value && compareForm.value.testStatuses.length > 1) {
    // 从多选变为单选时，只保留第一个选项
    compareForm.value.testStatuses = [compareForm.value.testStatuses[0]]
  }
}

const handleTestStatusChange = (testStatuses) => {
  // 重置后续选择
  compareForm.value.modeTypes = []
  modeTypeOptions.value = []
  compareResult.value = []

  if (testStatuses.length > 0) {
    loadModeTypes()
  }
}

const handleModeTypeChange = () => {
  // 清空对比结果
  compareResult.value = []
}

// 生成对比数据
const handleCompare = async () => {
  if (!canCompare.value) {
    ElMessage.warning('请完善选择条件')
    return
  }

  try {
    compareLoading.value = true

    // 处理testStatuses，确保它是数组格式
    const testStatusesArray = Array.isArray(compareForm.value.testStatuses)
      ? compareForm.value.testStatuses
      : [compareForm.value.testStatuses]

    const data = {
      component_id: compareForm.value.componentId,
      vehicle_model_ids: compareForm.value.vehicleModelIds.join(','),
      test_statuses: testStatusesArray.join(','),
      mode_types: compareForm.value.modeTypes.join(',')
    }

    const response = await modalApi.compareModalData(data)
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
  const seriesData = {}
  const xAxisData = [...new Set(compareResult.value.map(item => item.display_name))]

  // 按振型类型分组数据，同时保存完整的模态数据信息
  compareResult.value.forEach(item => {
    if (!seriesData[item.mode_type]) {
      seriesData[item.mode_type] = []
    }

    const xIndex = xAxisData.indexOf(item.display_name)
    seriesData[item.mode_type].push({
      value: [xIndex, item.frequency],
      modalData: item // 保存完整的模态数据，用于点击事件
    })
  })

  // 生成系列数据
  const series = Object.keys(seriesData).map((modeType, index) => ({
    name: modeType,
    type: 'scatter',
    data: seriesData[modeType],
    symbolSize: 8,
    itemStyle: {
      color: `hsl(${index * 60}, 70%, 50%)`
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
      formatter: (params) => {
        const vehicleName = xAxisData[params.data.value[0]]
        const frequency = params.data.value[1]
        return `${params.seriesName}<br/>${vehicleName}: ${frequency} Hz<br/>点击查看振型图`
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
        rotate: 45,
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
        color: '#606266'
      }
    },
    series: series
  }

  chartInstance.setOption(option)

  // 添加点击事件
  chartInstance.on('click', (params) => {
    if (params.data && params.data.modalData) {
      viewModalShape(params.data.modalData)
    }
  })

  // 响应式调整
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
}

// 弹窗相关方法
const viewModalShape = (modalData) => {
  currentModalData.value = modalData
  activeTab.value = 'shape' // 默认显示振型动画
  modalShapeDialogVisible.value = true
}

const handleCloseDialog = () => {
  modalShapeDialogVisible.value = false
  currentModalData.value = null
  activeTab.value = 'shape'
}

const getImageUrl = (filePath) => {
  if (!filePath) return ''
  // 如果是相对路径，添加后端服务器地址
  if (filePath.startsWith('/')) {
    return `http://127.0.0.1:8000${filePath}`
  }
  return filePath
}

const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  ElMessage.error('图片加载失败')
}

// 生命周期
onMounted(() => {
  loadComponents()
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
.modal-data-compare {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 选择控件区域 */
.selection-card {
  margin-bottom: 24px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.selection-form {
  padding: 8px;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 0;
  align-items: center;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
  min-width: 60px;
}

.form-select {
  min-width: 180px;
}

.compare-btn {
  padding: 10px 24px;
  font-size: 14px;
  border-radius: 6px;
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
  .form-row {
    flex-wrap: wrap;
    gap: 16px;
  }

  .form-select {
    min-width: 180px;
  }
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .form-group {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }

  .form-label {
    min-width: auto;
    text-align: left;
  }

  .form-select {
    min-width: auto;
    width: 100%;
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
