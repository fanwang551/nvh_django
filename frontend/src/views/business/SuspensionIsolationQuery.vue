<template>
  <div class="suspension-isolation-query">
    <!-- 查询条件区域 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">整车悬架隔振率查询</span>
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
        <el-row :gutter="24" style="margin-top: 12px">
          <el-col :span="24">
            <div class="info-item">
              <span class="info-label">测试工况：</span>
              <span class="info-value">{{ store.basicInfo?.testCondition || '-' }}</span>
            </div>
          </el-col>
        </el-row>
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
          <!-- 测点列 -->
          <el-table-column
            prop="measuring_point"
            label="测点"
            min-width="120"
            align="center"
            show-overflow-tooltip
          />

          <!-- 方向列 -->
          <el-table-column
            prop="direction"
            label="方向"
            width="80"
            align="center"
          />

          <!-- 主动端列 -->
          <el-table-column
            prop="active_value"
            label="主动端(m/s²)"
            min-width="140"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.active_value) }}</span>
            </template>
          </el-table-column>

          <!-- 被动端列 -->
          <el-table-column
            prop="passive_value"
            label="被动端(m/s²)"
            min-width="140"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.passive_value) }}</span>
            </template>
          </el-table-column>

          <!-- 隔振率列 -->
          <el-table-column
            prop="isolation_rate"
            label="隔振率(dB)"
            min-width="120"
            align="center"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row.isolation_rate) }}</span>
            </template>
          </el-table-column>

          <!-- 操作列 -->
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
                查看按钮
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
import { useSuspensionIsolationQueryStore } from '@/store/suspensionIsolationQuery'

// 组件名称（用于keep-alive缓存）
defineOptions({
  name: 'SuspensionIsolationQuery'
})

// 使用Pinia store
const store = useSuspensionIsolationQueryStore()

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
watch(() => store.searchForm.vehicleModelId, async (newVal, oldVal) => {
  console.log('车型变化:', { newVal, oldVal })
  if (newVal) {
    try {
      console.log('开始加载测点列表，车型ID:', newVal)
      await store.loadMeasuringPoints(newVal)
      console.log('测点列表加载成功，数量:', store.measuringPointOptions.length)
    } catch (error) {
      console.error('加载测点列表失败详情:', error)
      ElMessage.error('加载测点列表失败')
    }
  } else {
    store.measuringPointOptions = []
    console.log('车型清空，清空测点列表')
  }
})

// 车型变化处理 - 直接设置值，让watch监听器处理后续逻辑
const handleVehicleModelChange = (value) => {
  console.log('handleVehicleModelChange 被调用，值:', value)
  // 直接设置车型ID，清空测点选择和查询结果
  store.searchForm.vehicleModelId = value
  store.searchForm.measuringPoints = []
  store.clearResults()
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

// 数值格式化（保留两位小数）
const formatValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  return parseFloat(value).toFixed(2)
}

// 表格数据转换 - 将每个测点的X/Y/Z方向数据展开为多行
const transformedTableData = computed(() => {
  const result = []

  store.queryResult.results.forEach(item => {
    // X方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'X',
      active_value: item.x_active_value,
      passive_value: item.x_passive_value,
      isolation_rate: item.x_isolation_rate,
      originalData: item
    })

    // Y方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'Y',
      active_value: item.y_active_value,
      passive_value: item.y_passive_value,
      isolation_rate: item.y_isolation_rate,
      originalData: item
    })

    // Z方向数据
    result.push({
      measuring_point: item.measuring_point,
      direction: 'Z',
      active_value: item.z_active_value,
      passive_value: item.z_passive_value,
      isolation_rate: item.z_isolation_rate,
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
  if (columnIndex === 5) { // 操作列
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
.suspension-isolation-query {
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
  padding: 8px 0;
}

.info-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 15px;
}

.info-label {
  color: #303133;
  font-size: 15px;
  font-weight: 550;
  min-width: auto;
  flex-shrink: 0;
}

.info-value {
  color: #606266;
  font-size: 15px;
  font-weight: 500;
  flex: 1;
  word-break: break-all;
}

/* 表格样式 */
.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.result-table {
  width: 100%;
  min-width: 900px;
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .suspension-isolation-query {
    padding: 15px;
  }

  .basic-info-content .el-col {
    margin-bottom: 20px;
  }

  .result-table {
    min-width: 800px;
  }
}

@media (max-width: 768px) {
  .suspension-isolation-query {
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
    min-width: 700px;
    font-size: 12px;
  }
}
</style>
