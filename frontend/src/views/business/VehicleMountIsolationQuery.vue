<template>
  <div class="vehicle-mount-isolation-query">
    <!-- 查询条件区域 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">整车悬置隔振率查询</span>
        </div>
      </template>

      <el-form :model="store.searchForm" label-width="100px" class="search-form">
        <el-row :gutter="24">
          <!-- 车型选择 -->
          <el-col :span="6">
            <el-form-item label="车型" required>
              <el-select
                v-model="store.searchForm.vehicleModelId"
                placeholder="请选择车型"
                clearable
                :loading="store.vehicleModelsLoading"
                @change="handleVehicleModelChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in store.vehicleModelOptions"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 测点多选 -->
          <el-col :span="8">
            <el-form-item label="测点">
              <el-select
                v-model="store.searchForm.measuringPoints"
                placeholder="请选择测点"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :loading="store.measuringPointsLoading"
                :disabled="!store.searchForm.vehicleModelId"
                style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                    v-model="selectAllMeasuringPoints"
                    @change="handleSelectAllMeasuringPoints"
                    style="margin-left: 12px"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                  v-for="item in store.measuringPointOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 查询按钮 -->
          <el-col :span="6">
            <el-form-item label=" " class="search-buttons-form-item">
              <div class="search-buttons">
                <el-button
                  type="primary"
                  @click="handleSearch"
                  :loading="store.loading"
                  :disabled="!store.canQuery"
                >
                  查询
                </el-button>
                <el-button @click="handleReset">重置</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 基础信息区域 -->
    <el-card v-if="store.hasResults" class="info-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">基础信息</span>
        </div>
      </template>

      <div class="basic-info-content">
        <!-- 基本信息部分 -->
        <div class="basic-info-section">
          <el-row :gutter="24">
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">车型名称：</span>
                <span class="info-value">{{ store.basicInfo?.vehicleModelName || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">测试时间：</span>
                <span class="info-value">{{ store.basicInfo?.testDate || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">测试地点：</span>
                <span class="info-value">{{ store.basicInfo?.testLocation || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">测试人员：</span>
                <span class="info-value">{{ store.basicInfo?.testEngineer || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">悬挂形式：</span>
                <span class="info-value">{{ store.basicInfo?.suspensionType || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">实测胎压：</span>
                <span class="info-value">{{ store.basicInfo?.tirePressure || '-' }}</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 振动数据卡片部分 -->
        <div class="vibration-cards-section">
          <el-row :gutter="24">
            <!-- 座椅导轨振动卡片 -->
            <el-col :span="8">
              <div class="vibration-card">
                <div class="vibration-card-header">
                  <span class="vibration-card-title">驾驶员座椅导轨振动 (m/s²)</span>
                </div>
                <div class="vibration-card-content">
                  <el-table
                    :data="seatVibrationData"
                    size="small"
                    border
                    class="vibration-table"
                  >
                    <el-table-column prop="axis" label="" width="40" align="center" />
                    <el-table-column prop="acOff" label="AC OFF (N档)" align="center" />
                    <el-table-column prop="acOn" label="AC ON (N档)" align="center" />
                  </el-table>
                </div>
              </div>
            </el-col>

            <!-- 方向盘振动卡片 -->
            <el-col :span="8">
              <div class="vibration-card">
                <div class="vibration-card-header">
                  <span class="vibration-card-title">方向盘振动 (m/s²)</span>
                </div>
                <div class="vibration-card-content">
                  <el-table
                    :data="steeringVibrationData"
                    size="small"
                    border
                    class="vibration-table"
                  >
                    <el-table-column prop="axis" label="" width="40" align="center" />
                    <el-table-column prop="acOff" label="AC OFF (N档)" align="center" />
                    <el-table-column prop="acOn" label="AC ON (N档)" align="center" />
                  </el-table>
                </div>
              </div>
            </el-col>

            <!-- 内噪声卡片 -->
            <el-col :span="8">
              <div class="vibration-card">
                <div class="vibration-card-header">
                  <span class="vibration-card-title">内噪声 (dB)</span>
                </div>
                <div class="vibration-card-content">
                  <el-table
                    :data="cabinNoiseData"
                    size="small"
                    border
                    class="vibration-table"
                  >
                    <el-table-column prop="position" label="位置" width="60" align="center" />
                    <el-table-column prop="acOff" label="AC OFF" align="center" />
                    <el-table-column prop="acOn" label="AC ON" align="center" />
                  </el-table>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>

    <!-- 试验结果区域 -->
    <el-card v-if="store.hasResults" class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">试验结果</span>
          <div class="header-extra">
            <span class="result-count">共 {{ store.queryResult.count || 0 }} 条数据</span>
          </div>
        </div>
      </template>

      <div class="table-container">
        <el-table
          :data="transformedTableData"
          v-loading="store.loading"
          class="result-table"
          stripe
          border
          :span-method="handleSpanMethod"
          :header-cell-style="{ backgroundColor: '#fafafa', color: '#606266', fontWeight: '600', fontSize: '14px' }"
          style="width: 100%"
        >
        <!-- 测点列 - 弹性宽度，最小宽度保证内容显示 -->
        <el-table-column
          prop="measuring_point"
          label="测点"
          min-width="120"
          align="center"
          show-overflow-tooltip
        />

        <!-- 方向列 - 固定较小宽度 -->
        <el-table-column
          prop="direction"
          label="方向"
          width="80"
          align="center"
        />

        <!-- AC OFF (N档) - 弹性分组列 -->
        <el-table-column label="AC OFF (N档)" align="center" header-align="center">
          <el-table-column
            prop="ac_off_isolation"
            label="隔振率(dB)"
            min-width="140"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.ac_off_isolation) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="ac_off_vibration"
            label="2阶被动端振动(m/s²)"
            min-width="180"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.ac_off_vibration) }}</span>
            </template>
          </el-table-column>
        </el-table-column>

        <!-- AC ON (N档) - 弹性分组列 -->
        <el-table-column label="AC ON (N档)" align="center" header-align="center">
          <el-table-column
            prop="ac_on_isolation"
            label="隔振率(dB)"
            min-width="140"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.ac_on_isolation) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="ac_on_vibration"
            label="2阶被动端振动(m/s²)"
            min-width="180"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.ac_on_vibration) }}</span>
            </template>
          </el-table-column>
        </el-table-column>

        <!-- 操作列 - 固定宽度 -->
        <el-table-column
          label="操作"
          width="120"
          align="center"
          fixed="right"
        >
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="viewImages(scope.row.originalData)"
              v-if="scope.row.direction === 'X'"
            >
              查看图片
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
    </el-card>

    <!-- 查看图片弹窗 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="查看图片"
      width="800px"
      :before-close="handleCloseImageDialog"
      class="image-dialog"
    >
      <div class="image-content">
        <!-- Tab 切换按钮 -->
        <div class="tab-header">
          <div
            class="tab-item"
            :class="{ active: activeTab === 'layout' }"
            @click="switchTab('layout')"
          >
            测试布置图
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'curve' }"
            @click="switchTab('curve')"
          >
            测试数据曲线图
          </div>
        </div>

        <!-- 图片展示区域 -->
        <div class="image-display-area">
          <!-- 测试布置图 -->
          <div v-if="activeTab === 'layout'" class="image-container">
            <div v-if="currentRowData?.layout_image_path" class="image-wrapper">
              <img
                :src="getImageUrl(currentRowData.layout_image_path)"
                alt="测试布置图"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">测试布置图 - {{ currentRowData.measuring_point }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无测试布置图" />
            </div>
          </div>

          <!-- 测试数据曲线图 -->
          <div v-if="activeTab === 'curve'" class="image-container">
            <div v-if="currentRowData?.curve_image_path" class="image-wrapper">
              <img
                :src="getImageUrl(currentRowData.curve_image_path)"
                alt="测试数据曲线图"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">测试数据曲线图 - {{ currentRowData.measuring_point }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无测试数据曲线图" />
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useVehicleMountIsolationQueryStore } from '@/store/vehicleMountIsolationQuery'

// 组件名称（用于keep-alive缓存）
defineOptions({
  name: 'VehicleMountIsolationQuery'
})

// 使用Pinia store
const store = useVehicleMountIsolationQueryStore()

// UI状态管理（组件职责）
const selectAllMeasuringPoints = ref(false)
const imageDialogVisible = ref(false)
const currentRowData = ref(null)
const activeTab = ref('layout')

// 监听测点选择变化，更新全选状态
watch(() => store.searchForm.measuringPoints, (newVal) => {
  selectAllMeasuringPoints.value = newVal.length === store.measuringPointOptions.length && store.measuringPointOptions.length > 0
}, { deep: true })

// 监听车型选择变化，加载测点列表
watch(() => store.searchForm.vehicleModelId, async (newVal) => {
  if (newVal) {
    try {
      await store.loadMeasuringPoints(newVal)
    } catch (error) {
      ElMessage.error('加载测点列表失败')
    }
  } else {
    store.measuringPointOptions = []
  }
})

// 车型变化处理
const handleVehicleModelChange = (value) => {
  store.setVehicleModelId(value)
}

// 全选/反选测点处理
const handleSelectAllMeasuringPoints = (checked) => {
  if (checked) {
    store.setMeasuringPoints(store.measuringPointOptions.map(p => p.value))
  } else {
    store.setMeasuringPoints([])
  }
  selectAllMeasuringPoints.value = checked
}

// 搜索处理
const handleSearch = async () => {
  if (!store.canQuery) {
    ElMessage.warning('请先选择车型')
    return
  }

  try {
    await store.queryData()
    ElMessage.success('查询完成')
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  }
}

// 重置处理
const handleReset = () => {
  store.resetSearchForm()
  selectAllMeasuringPoints.value = false
  ElMessage.info('已重置查询条件')
}

// 数值格式化
const formatValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  return parseFloat(value).toFixed(3)
}

// 座椅导轨振动数据
const seatVibrationData = computed(() => {
  if (!store.basicInfo) return []
  return [
    {
      axis: 'X',
      acOff: formatValue(store.basicInfo.seatVibXAcOff),
      acOn: formatValue(store.basicInfo.seatVibXAcOn)
    },
    {
      axis: 'Y',
      acOff: formatValue(store.basicInfo.seatVibYAcOff),
      acOn: formatValue(store.basicInfo.seatVibYAcOn)
    },
    {
      axis: 'Z',
      acOff: formatValue(store.basicInfo.seatVibZAcOff),
      acOn: formatValue(store.basicInfo.seatVibZAcOn)
    }
  ]
})

// 方向盘振动数据
const steeringVibrationData = computed(() => {
  if (!store.basicInfo) return []
  return [
    {
      axis: 'X',
      acOff: formatValue(store.basicInfo.steeringVibXAcOff),
      acOn: formatValue(store.basicInfo.steeringVibXAcOn)
    },
    {
      axis: 'Y',
      acOff: formatValue(store.basicInfo.steeringVibYAcOff),
      acOn: formatValue(store.basicInfo.steeringVibYAcOn)
    },
    {
      axis: 'Z',
      acOff: formatValue(store.basicInfo.steeringVibZAcOff),
      acOn: formatValue(store.basicInfo.steeringVibZAcOn)
    }
  ]
})

// 内噪声数据
const cabinNoiseData = computed(() => {
  if (!store.basicInfo) return []
  return [
    {
      position: '前排',
      acOff: formatValue(store.basicInfo.cabinNoiseFrontAcOff),
      acOn: formatValue(store.basicInfo.cabinNoiseFrontAcOn)
    },
    {
      position: '后排',
      acOff: formatValue(store.basicInfo.cabinNoiseRearAcOff),
      acOn: formatValue(store.basicInfo.cabinNoiseRearAcOn)
    }
  ]
})

// 表格数据转换 - 将每个测点的X/Y/Z方向数据展开为多行
const transformedTableData = computed(() => {
  const result = []

  store.queryResult.results.forEach(item => {
    // X方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'X',
      ac_off_isolation: item.x_ac_off_isolation,
      ac_off_vibration: item.x_ac_off_vibration,
      ac_on_isolation: item.x_ac_on_isolation,
      ac_on_vibration: item.x_ac_on_vibration,
      originalData: item
    })

    // Y方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'Y',
      ac_off_isolation: item.y_ac_off_isolation,
      ac_off_vibration: item.y_ac_off_vibration,
      ac_on_isolation: item.y_ac_on_isolation,
      ac_on_vibration: item.y_ac_on_vibration,
      originalData: item
    })

    // Z方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'Z',
      ac_off_isolation: item.z_ac_off_isolation,
      ac_off_vibration: item.z_ac_off_vibration,
      ac_on_isolation: item.z_ac_on_isolation,
      ac_on_vibration: item.z_ac_on_vibration,
      originalData: item
    })
  })

  return result
})

// 表格行合并处理
const handleSpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  // 测点列需要合并（每3行合并为1行，因为每个测点有X/Y/Z三个方向）
  if (columnIndex === 0) { // 测点列
    if (rowIndex % 3 === 0) {
      return {
        rowspan: 3,
        colspan: 1
      }
    } else {
      return {
        rowspan: 0,
        colspan: 0
      }
    }
  }

  // 操作列也需要合并
  if (columnIndex === 6) { // 操作列
    if (rowIndex % 3 === 0) {
      return {
        rowspan: 3,
        colspan: 1
      }
    } else {
      return {
        rowspan: 0,
        colspan: 0
      }
    }
  }
}

// 查看图片
const viewImages = (row) => {
  currentRowData.value = row
  activeTab.value = 'layout' // 默认显示测试布置图
  imageDialogVisible.value = true
}

// 切换Tab
const switchTab = (tab) => {
  activeTab.value = tab
}

// 关闭图片弹窗
const handleCloseImageDialog = () => {
  imageDialogVisible.value = false
  currentRowData.value = null
}

// 获取图片URL（复用统一工具，避免硬编码主机名）
import { getImageUrl as buildImageUrl } from '@/utils/imageService'
const getImageUrl = (imagePath) => buildImageUrl(imagePath)

// 图片加载错误处理
const handleImageError = (event) => {
  console.warn('图片加载失败:', event.target.src)
  event.target.style.display = 'none'
}

// 组件挂载时初始化
onMounted(async () => {
  try {
    await store.initialize()
  } catch (error) {
    console.error('组件初始化失败:', error)
    ElMessage.error('初始化失败')
  }
})
</script>

<style scoped>
.vehicle-mount-isolation-query {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 卡片样式 */
.search-card,
.info-card,
.result-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.header-extra {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-count {
  font-size: 14px;
  color: #909399;
}

/* 搜索表单样式 */
.search-form {
  padding: 10px 0;
}

.search-buttons-form-item :deep(.el-form-item__label) {
  visibility: hidden;
}

.search-buttons {
  display: flex;
  gap: 12px;
}

/* 基础信息样式 */
.basic-info-content {
  padding: 10px 0;
}

.basic-info-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-label {
  font-weight: 500;
  color: #606266;
  min-width: 120px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  flex: 1;
}

/* 振动数据卡片样式 */
.vibration-cards-section {
  margin-top: 20px;
}

.vibration-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
  height: 100%;
}

.vibration-card-header {
  background: #409eff;
  color: white;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

.vibration-card-title {
  font-size: 13px;
  font-weight: 600;
}

.vibration-card-content {
  padding: 0;
}

.vibration-table {
  margin: 0;
}

.vibration-table :deep(.el-table__header-wrapper) {
  background: #f5f7fa;
}

.vibration-table :deep(.el-table th) {
  background: #f5f7fa !important;
  color: #606266;
  font-weight: 600;
  font-size: 12px;
  padding: 6px 8px;
  text-align: center;
}

.vibration-table :deep(.el-table__body-wrapper) {
  border-radius: 0;
}

.vibration-table :deep(.el-table td) {
  padding: 6px 8px;
  font-size: 12px;
  text-align: center;
}

.vibration-table :deep(.el-table__row:hover > td) {
  background-color: #ecf5ff !important;
}

/* 表格样式 - 弹性布局优化 */
.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.result-table {
  width: 100%;
  min-width: 1000px; /* 增加最小宽度以适应弹性列 */
  table-layout: auto; /* 允许表格自动调整列宽 */
}

.result-table :deep(.el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}

.result-table :deep(.el-table__body-wrapper) {
  border-radius: 0 0 8px 8px;
}

.result-table :deep(.el-table th) {
  text-align: center;
  padding: 12px 8px;
  font-weight: 600;
  white-space: nowrap;
  background-color: #fafafa !important;
}

.result-table :deep(.el-table td) {
  text-align: center;
  padding: 10px 8px;
  white-space: nowrap;
}

.result-table :deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 表格滚动条样式优化 */
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

/* 图片弹窗样式 */
.image-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.image-content {
  min-height: 500px;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fafafa;
}

.tab-item {
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
  background-color: #ecf5ff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
  background-color: #fff;
}

.image-display-area {
  padding: 20px;
  min-height: 450px;
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
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-caption {
  margin-top: 12px;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #909399;
}

/* 响应式设计 - 弹性布局优化 */
@media (max-width: 1400px) {
  .result-table {
    min-width: 1200px;
  }

  .result-table :deep(.el-table th),
  .result-table :deep(.el-table td) {
    padding: 10px 6px;
    font-size: 13px;
  }
}

@media (max-width: 1200px) {
  .vehicle-mount-isolation-query {
    padding: 15px;
  }

  .basic-info-content .el-col {
    margin-bottom: 20px;
  }

  .vibration-cards-section .el-col {
    margin-bottom: 16px;
  }

  .result-table {
    min-width: 1100px;
  }

  .result-table :deep(.el-table th),
  .result-table :deep(.el-table td) {
    padding: 8px 4px;
    font-size: 12px;
  }
}

@media (max-width: 992px) {
  .result-table {
    min-width: 1000px;
  }

  .table-container {
    border-radius: 6px;
  }

  .result-table :deep(.el-table__header-wrapper) {
    border-radius: 6px 6px 0 0;
  }

  .result-table :deep(.el-table__body-wrapper) {
    border-radius: 0 0 6px 6px;
  }
}

@media (max-width: 768px) {
  .vehicle-mount-isolation-query {
    padding: 10px;
  }

  .search-form .el-col {
    margin-bottom: 15px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .result-table {
    min-width: 900px;
    font-size: 11px;
  }

  .result-table :deep(.el-table th) {
    padding: 8px 4px;
    font-size: 11px;
  }

  .result-table :deep(.el-table td) {
    padding: 6px 4px;
    font-size: 11px;
  }

  /* 移动端振动卡片单列显示 */
  .vibration-cards-section .el-col {
    width: 100% !important;
    margin-bottom: 16px;
  }

  .vibration-card-header {
    font-size: 12px;
    padding: 6px 10px;
  }

  .vibration-table :deep(.el-table td) {
    padding: 4px 6px;
    font-size: 11px;
  }

  /* 移动端表格容器优化 */
  .table-container {
    border-radius: 4px;
    margin: 0 -10px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
}
</style>
