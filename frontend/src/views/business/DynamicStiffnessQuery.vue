<template>
  <div class="dynamic-stiffness-query">
    <!-- 查询条件区域 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">动刚度查询</span>
        </div>
      </template>

      <el-form :model="store.searchForm" label-width="100px" class="search-form">
        <el-row :gutter="24">
          <!-- 车型选择 -->
          <el-col :span="5">
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
                  v-for="item in vehicleModelOptions"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 零件名称选择 -->
          <el-col :span="5">
            <el-form-item label="零件名称">
              <el-select
                v-model="store.searchForm.partName"
                placeholder="请选择零件"
                clearable
                :loading="store.partNamesLoading"
                :disabled="!store.searchForm.vehicleModelId"
                @change="handlePartNameChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in partNameOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 子系统选择（改为多选） -->
          <el-col :span="5">
            <el-form-item label="子系统">
              <el-select
                v-model="store.searchForm.subsystem"
                placeholder="请选择子系统"
                multiple
                collapse-tags
                clearable
                :loading="store.subsystemsLoading"
                :disabled="!store.searchForm.partName"
                @change="handleSubsystemChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in subsystemOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 测点多选（随车型/零件加载，不再依赖子系统） -->
          <el-col :span="4">
            <el-form-item label="测点">
              <el-select
                v-model="store.searchForm.testPoints"
                placeholder="请选择测点"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :loading="store.testPointsLoading"
                :disabled="!store.searchForm.vehicleModelId || !store.searchForm.partName"
                style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                    v-model="selectAllTestPoints"
                    @change="handleSelectAllTestPoints"
                    style="margin-left: 12px"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                  v-for="item in testPointOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
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

      <div class="basic-info">
        <div class="info-banner">
          <div class="info-grid">
            <div class="info-chip">
              <span class="label">车型：</span>
              <span class="value">{{ basicInfo?.vehicleModelName || '-' }}</span>
            </div>
            <div class="info-chip">
              <span class="label">悬挂类型：</span>
              <span class="value">{{ basicInfo?.suspensionType || '-' }}</span>
            </div>
            <div class="info-chip">
              <span class="label">测试地点：</span>
              <span class="value">{{ basicInfo?.testLocation || '-' }}</span>
            </div>

            <div class="info-chip">
              <span class="label">测试时间：</span>
              <span class="value">{{ basicInfo?.testDate || '-' }}</span>
            </div>
            <div class="info-chip">
              <span class="label">测试人员：</span>
              <span class="value">{{ basicInfo?.testEngineer || '-' }}</span>
            </div>
            <div class="info-chip">
              <span class="label">分析人员：</span>
              <span class="value">{{ basicInfo?.analysisEngineer || '-' }}</span>
            </div>

            <div class="info-chip">
              <span class="label">测试图：</span>
              <template v-if="Array.isArray(basicInfo?.testPhotoList) && basicInfo.testPhotoList.length > 0">
                <el-button type="primary" link @click="viewTestPhotos">查看图片</el-button>
                <span class="photo-count">共 {{ basicInfo.testPhotoList.length }} 张</span>
              </template>
              <span v-else class="value">-</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 数据表格区域 -->
    <el-card v-if="store.hasResults" class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">动刚度数据 (共{{ transformedTableData.length }}条)</span>
        </div>
      </template>

      <el-table
        :data="transformedTableData"
        v-loading="store.loading"
        class="result-table"
        stripe
        :span-method="handleSpanMethod"
        :header-cell-style="{ backgroundColor: '#409EFF', color: '#ffffff', fontWeight: '600', fontSize: '14px' }"
      >
        <!-- 子系统列 -->
        <el-table-column prop="subsystem" label="子系统" width="100" align="center" />

        <!-- 测点列 -->
        <el-table-column prop="test_point" label="测点" width="120" align="center" />

        <!-- 方向列 -->
        <el-table-column prop="direction" label="方向" width="60" align="center" />

        <!-- 动刚度目标列 -->
        <el-table-column prop="target_stiffness" width="130" align="center">
          <template #header>
            <div>
              动刚度目标<br />
              <span>（N/mm）</span>
            </div>
          </template>
          <template #default="scope">
            <span>{{ formatTargetValue(scope.row.target_stiffness) }}</span>
          </template>
        </el-table-column>

        <!-- 50Hz -->
        <el-table-column prop="freq_50" label="50Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_50, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_50) }}
            </span>
          </template>
        </el-table-column>

        <!-- 63Hz -->
        <el-table-column prop="freq_63" label="63Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_63, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_63) }}
            </span>
          </template>
        </el-table-column>

        <!-- 80Hz -->
        <el-table-column prop="freq_80" label="80Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_80, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_80) }}
            </span>
          </template>
        </el-table-column>

        <!-- 100Hz -->
        <el-table-column prop="freq_100" label="100Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_100, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_100) }}
            </span>
          </template>
        </el-table-column>

        <!-- 125Hz -->
        <el-table-column prop="freq_125" label="125Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_125, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_125) }}
            </span>
          </template>
        </el-table-column>

        <!-- 160Hz -->
        <el-table-column prop="freq_160" label="160Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_160, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_160) }}
            </span>
          </template>
        </el-table-column>

        <!-- 200Hz -->
        <el-table-column prop="freq_200" label="200Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_200, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_200) }}
            </span>
          </template>
        </el-table-column>

        <!-- 250Hz -->
        <el-table-column prop="freq_250" label="250Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_250, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_250) }}
            </span>
          </template>
        </el-table-column>

        <!-- 315Hz -->
        <el-table-column prop="freq_315" label="315Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_315, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_315) }}
            </span>
          </template>
        </el-table-column>

        <!-- 400Hz -->
        <el-table-column prop="freq_400" label="400Hz" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: isValueBelowTarget(scope.row.freq_400, scope.row.target_stiffness) ? '#f56c6c' : '' }">
              {{ formatValue(scope.row.freq_400) }}
            </span>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="120" align="center">
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
    </el-card>

    <!-- 查看测试照片弹窗 -->
    <el-dialog
      v-model="testPhotoDialogVisible"
      title="查看测试照片"
      width="600px"
      :before-close="handleCloseTestPhotoDialog"
      class="test-photo-dialog"
    >
      <div class="test-photo-content">
        <div v-if="basicInfo?.testPhotoList && basicInfo.testPhotoList.length > 0" class="image-wrapper">
          <div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;">
            <img
              v-for="(imgPath, idx) in basicInfo.testPhotoList"
              :key="idx"
              :src="getImageUrl(imgPath)"
              alt="测试照片"
              class="test-photo-image"
              @error="handleImageError"
              style="max-width: 260px; max-height: 200px; object-fit: contain;"
            />
          </div>
        </div>
        <div v-else class="no-image">
          <el-empty description="暂无测试照片" />
        </div>
      </div>
    </el-dialog>

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
            测点布置图
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'curve' }"
            @click="switchTab('curve')"
          >
            测试曲线图
          </div>
        </div>

        <!-- 图片展示区域 -->
        <div class="image-display-area">
          <!-- 测点布置图 -->
          <div v-if="activeTab === 'layout'" class="image-container">
            <div v-if="currentRowData?.layout_image" class="image-wrapper">
              <img
                :src="getImageUrl(currentRowData.layout_image)"
                alt="测点布置图"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">测点布置图 - {{ currentRowData.subsystem }} - {{ currentRowData.test_point }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无测点布置图" />
            </div>
          </div>

          <!-- 测试曲线图 -->
          <div v-if="activeTab === 'curve'" class="image-container">
            <div v-if="currentRowData?.curve_image" class="image-wrapper">
              <img
                :src="getImageUrl(currentRowData.curve_image)"
                alt="测试曲线图"
                class="modal-image"
                @error="handleImageError"
              />
              <p class="image-caption">测试曲线图 - {{ currentRowData.subsystem }} - {{ currentRowData.test_point }}</p>
            </div>
            <div v-else class="no-image">
              <el-empty description="暂无测试曲线图" />
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useDynamicStiffnessQueryStore } from '@/store/dynamicStiffnessQuery'
import { getImageUrl, handleImageError } from '@/utils/imageService'

// 使用store
const store = useDynamicStiffnessQueryStore()

// 计算属性
const vehicleModelOptions = computed(() => store.vehicleModelOptions)
const partNameOptions = computed(() => store.partNameOptions)
const subsystemOptions = computed(() => store.subsystemOptions)
const testPointOptions = computed(() => store.testPointOptions)
const basicInfo = computed(() => store.basicInfo)
// 基本信息卡片数据
const basicInfoCards = computed(() => {
  const info = basicInfo.value
  if (!info) return []
  return [
    { key: 'vehicleModelName', label: '车型', value: info.vehicleModelName },
    { key: 'suspensionType', label: '悬挂类型', value: info.suspensionType },
    { key: 'testEngineer', label: '测试人员', value: info.testEngineer },
    { key: 'analysisEngineer', label: '分析人员', value: info.analysisEngineer },
    { key: 'testLocation', label: '测试地点', value: info.testLocation },
    { key: 'testDate', label: '测试时间', value: info.testDate },
    { key: 'testPhoto', label: '测试图', count: Array.isArray(info.testPhotoList) ? info.testPhotoList.length : 0 }
  ]
})

// UI状态管理（组件职责）
const testPhotoDialogVisible = ref(false)
const imageDialogVisible = ref(false)
const currentRowData = ref(null)
const activeTab = ref('layout')

// 全选测点状态
const selectAllTestPoints = computed({
  get() {
    return store.testPointOptions.length > 0 &&
           store.searchForm.testPoints.length === store.testPointOptions.length
  },
  set(value) {
    // 这里不需要处理，由handleSelectAllTestPoints处理
  }
})

// 转换表格数据 - 将原始数据按方向展开为行数据
const transformedTableData = computed(() => {
  if (!store.queryResult.results || store.queryResult.results.length === 0) {
    return []
  }

  const transformedData = []

  store.queryResult.results.forEach(item => {
    // X方向数据
    transformedData.push({
      subsystem: item.subsystem,
      test_point: item.test_point,
      direction: 'X',
      target_stiffness: item.target_stiffness_x,
      freq_50: item.freq_50_x,
      freq_63: item.freq_63_x,
      freq_80: item.freq_80_x,
      freq_100: item.freq_100_x,
      freq_125: item.freq_125_x,
      freq_160: item.freq_160_x,
      freq_200: item.freq_200_x,
      freq_250: item.freq_250_x,
      freq_315: item.freq_315_x,
      freq_400: item.freq_400_x,
      originalData: item, // 保存原始数据用于查看图片
      rowIndex: transformedData.length
    })

    // Y方向数据
    transformedData.push({
      subsystem: item.subsystem,
      test_point: item.test_point,
      direction: 'Y',
      target_stiffness: item.target_stiffness_y,
      freq_50: item.freq_50_y,
      freq_63: item.freq_63_y,
      freq_80: item.freq_80_y,
      freq_100: item.freq_100_y,
      freq_125: item.freq_125_y,
      freq_160: item.freq_160_y,
      freq_200: item.freq_200_y,
      freq_250: item.freq_250_y,
      freq_315: item.freq_315_y,
      freq_400: item.freq_400_y,
      originalData: item,
      rowIndex: transformedData.length
    })

    // Z方向数据
    transformedData.push({
      subsystem: item.subsystem,
      test_point: item.test_point,
      direction: 'Z',
      target_stiffness: item.target_stiffness_z,
      freq_50: item.freq_50_z,
      freq_63: item.freq_63_z,
      freq_80: item.freq_80_z,
      freq_100: item.freq_100_z,
      freq_125: item.freq_125_z,
      freq_160: item.freq_160_z,
      freq_200: item.freq_200_z,
      freq_250: item.freq_250_z,
      freq_315: item.freq_315_z,
      freq_400: item.freq_400_z,
      originalData: item,
      rowIndex: transformedData.length
    })
  })

  return transformedData
})

// 车型变化处理
const handleVehicleModelChange = async (vehicleModelId) => {
  try {
    await store.handleVehicleModelChange(vehicleModelId)
  } catch (error) {
    console.error('车型变化处理失败:', error)
    ElMessage.error('加载零件列表失败')
  }
}

// 零件名称变化处理
const handlePartNameChange = async (partName) => {
  try {
    await store.handlePartNameChange(partName)
  } catch (error) {
    console.error('零件名称变化处理失败:', error)
    ElMessage.error('加载子系统列表失败')
  }
}

// 子系统变化处理
const handleSubsystemChange = async (subsystem) => {
  try {
    await store.handleSubsystemChange(subsystem)
  } catch (error) {
    console.error('子系统变化处理失败:', error)
    ElMessage.error('加载测点列表失败')
  }
}

// 全选/反选测点处理
const handleSelectAllTestPoints = (checked) => {
  if (checked) {
    store.searchForm.testPoints = store.testPointOptions.map(option => option.value)
  } else {
    store.searchForm.testPoints = []
  }
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
  ElMessage.info('已重置查询条件')
}

// 合并单元格处理方法
const handleSpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  // 只对子系统和测点列进行合并
  if (columnIndex === 0 || columnIndex === 1) { // 子系统列或测点列
    // 每3行合并一次（X、Y、Z三个方向）
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

  // 操作列也需要合并，只在X方向显示按钮
  if (columnIndex === 14) { // 操作列的索引（新增63Hz后为第15列，从0开始计数）
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

// 数值格式化
const formatValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  return parseFloat(value).toFixed(1)
}

// 目标值格式化 - 显示为 ≥数值 的形式
const formatTargetValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  return `≥${parseFloat(value).toFixed(1)}`
}

// 检查数值是否小于目标值
const isValueBelowTarget = (value, targetValue) => {
  if (value === null || value === undefined || targetValue === null || targetValue === undefined) {
    return false
  }
  return parseFloat(value) < parseFloat(targetValue)
}

// 查看测试照片
const viewTestPhotos = () => {
  testPhotoDialogVisible.value = true
}

// 查看图片
const viewImages = (row) => {
  currentRowData.value = row
  activeTab.value = 'layout' // 默认显示测点布置图
  imageDialogVisible.value = true
}

// 关闭测试照片弹窗
const handleCloseTestPhotoDialog = () => {
  testPhotoDialogVisible.value = false
}

// 关闭图片弹窗
const handleCloseImageDialog = () => {
  imageDialogVisible.value = false
  currentRowData.value = null
  activeTab.value = 'layout'
}

// 切换图片标签页
const switchTab = (tab) => {
  activeTab.value = tab
}

// 组件生命周期处理
onMounted(async () => {
  try {
    await store.initializePageData()
  } catch (error) {
    console.error('组件初始化失败:', error)
    ElMessage.error('页面初始化失败')
  }
})
</script>

<style scoped>
.dynamic-stiffness-query {
  padding: 20px;
}

.search-card, .info-card, .table-card {
  margin-bottom: 20px;
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

.search-form {
  margin-bottom: 0;
}

/* 搜索按钮样式优化 */
.search-buttons-form-item {
  margin-bottom: 0 !important;
}

.search-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
}

.search-buttons .el-button {
  margin-left: 0;
}

/* 基本信息区域样式优化 */
.basic-info { padding: 12px 0; }


.info-banner {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #ffffff;
  padding: 14px 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px 24px;
  align-items: center;
}


.info-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}
.info-chip .label {
  color: #303133;
  font-size: 15px;
  font-weight: 550;
}
.info-chip .value {
  color: #606266;
  font-size: 15px;
  font-weight: 500;
  word-break: break-all;
}

.photo-count { color: #606266; font-size: 12px; margin-left: 6px; }

.result-table {
  width: 100%;
}

/* 优化表格样式 */
.result-table :deep(.el-table__cell) {
  padding: 12px 8px;
  font-size: 13px;
  font-weight: 600;
}

.result-table :deep(.cell) {
  white-space: nowrap;
  overflow: visible;
  text-overflow: clip;
}

.result-table :deep(.el-table__header-wrapper) {
  .el-table__header {
    th {
      background-color: #409EFF !important;
      color: #ffffff !important;
      border-right: 1px solid #ebeef5;
    }
  }
}

.result-table :deep(.el-table__body-wrapper) {
  .el-table__body {
    td {
      border-right: 1px solid #ebeef5;
    }
  }
}

/* 弹窗样式 */
.test-photo-dialog .test-photo-content {
  text-align: center;
}

.test-photo-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-dialog .image-content {
  padding: 0;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.tab-item {
  padding: 12px 20px;
  cursor: pointer;
  color: #606266;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
  font-weight: 600;
}

.image-display-area {
  min-height: 300px;
}

.image-container {
  text-align: center;
}

.image-wrapper {
  display: inline-block;
}

.modal-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-caption {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

.no-image {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .result-table {
    font-size: 12px;
  }

  .result-table :deep(.el-table__cell) {
    padding: 8px 0;
  }
}
</style>
