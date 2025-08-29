<template>
  <div class="modal-data-query">
    <!-- 搜索卡片 -->
    <el-card class="search-card" shadow="never">
      <div class="search-form">
        <div class="form-row">
          <div class="form-group">
            <span class="form-label">车型：</span>
            <el-select
              v-model="searchForm.vehicleModelId"
              placeholder="请选择车型"
              class="form-select"
              clearable
              :loading="vehicleModelsLoading"
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
            <span class="form-label">零件：</span>
            <el-select
              v-model="searchForm.componentIds"
              placeholder="请选择零件（可多选）"
              class="form-select"
              multiple
              collapse-tags
              collapse-tags-tooltip
              clearable
              :loading="componentsLoading"
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
            <el-button
              type="primary"
              :icon="Search"
              @click="handleSearch"
              :loading="loading"
              class="search-btn"
            >
              查询
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 查询结果展示卡片 -->
    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><List /></el-icon>
          <span>查询结果展示</span>
          <div class="header-extra">
            <span class="result-count">共 {{ modalDataResult.count || 0 }} 条数据</span>
          </div>
        </div>
      </template>

      <el-table
        :data="modalDataResult.results || []"
        v-loading="loading"
        class="result-table"
        stripe
        :header-cell-style="{ backgroundColor: '#fafafa', color: '#606266', fontWeight: '600', fontSize: '14px' }"
      >
        <el-table-column prop="component_category" label="零件分类" width="120" />
        <el-table-column prop="component_name" label="零件名称" width="160" />
        <el-table-column prop="mode_shape_description" label="模态振型描述" width="200" />
        <el-table-column prop="frequency" label="频率(Hz)" width="130" align="center">
          <template #default="scope">
            <span class="frequency-value">{{ scope.row.frequency }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="damping_ratio" label="阻尼比" width="110" align="center" />
        <el-table-column label="操作" width="130" align="center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              text
              @click="viewModalShape(scope.row)"
            >
              查看振型
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页器 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="modalDataResult.count || 0"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

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
              <p class="image-caption">测试图片 - {{ currentModalData.component_name || '无名称' }}</p>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, List } from '@element-plus/icons-vue'
import modalApi from '@/api/modal'

// 搜索表单
const searchForm = ref({
  vehicleModelId: null,
  componentIds: []
})

// 加载状态
const loading = ref(false)
const vehicleModelsLoading = ref(false)
const componentsLoading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 数据选项
const vehicleModelOptions = ref([])
const componentOptions = ref([])

// 模态数据查询结果
const modalDataResult = ref({
  count: 0,
  results: []
})

// 弹窗相关状态
const modalShapeDialogVisible = ref(false)
const activeTab = ref('shape') // 'shape' 或 'photo'
const currentModalData = ref(null)

// API调用方法
const loadVehicleModels = async () => {
  try {
    vehicleModelsLoading.value = true
    const response = await modalApi.getVehicleModels()
    vehicleModelOptions.value = response.data || []
  } catch (error) {
    console.error('加载车型列表失败:', error)
    ElMessage.error('加载车型列表失败')
  } finally {
    vehicleModelsLoading.value = false
  }
}

const loadComponents = async (vehicleModelId = null) => {
  try {
    componentsLoading.value = true
    const params = vehicleModelId ? { vehicle_model_id: vehicleModelId } : {}
    const response = await modalApi.getComponents(params)
    componentOptions.value = response.data || []

    // 如果有车型选择，默认选中所有零件
    if (vehicleModelId && componentOptions.value.length > 0) {
      searchForm.value.componentIds = componentOptions.value.map(item => item.id)
    }
  } catch (error) {
    console.error('加载零件列表失败:', error)
    ElMessage.error('加载零件列表失败')
  } finally {
    componentsLoading.value = false
  }
}

// 车型变化处理
const handleVehicleModelChange = (vehicleModelId) => {
  if (vehicleModelId) {
    loadComponents(vehicleModelId)
  } else {
    componentOptions.value = []
    searchForm.value.componentIds = []
  }
  // 清空之前的查询结果
  modalDataResult.value = { count: 0, results: [] }
}

// 搜索处理
const handleSearch = async () => {
  if (!searchForm.value.vehicleModelId) {
    ElMessage.warning('请先选择车型')
    return
  }

  loading.value = true
  try {
    const params = {
      vehicle_model_id: searchForm.value.vehicleModelId,
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 如果选择了零件，添加到查询参数
    if (searchForm.value.componentIds.length > 0) {
      params.component_ids = searchForm.value.componentIds.join(',')
    }

    const response = await modalApi.queryModalData(params)
    modalDataResult.value = response
    ElMessage.success('查询完成')
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

// 查看振型
const viewModalShape = (row) => {
  currentModalData.value = row
  activeTab.value = 'shape' // 默认显示振型动画
  modalShapeDialogVisible.value = true
}

// 关闭弹窗
const handleCloseDialog = () => {
  modalShapeDialogVisible.value = false
  currentModalData.value = null
  activeTab.value = 'shape'
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

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  if (searchForm.value.vehicleModelId) {
    handleSearch()
  }
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  if (searchForm.value.vehicleModelId) {
    handleSearch()
  }
}

// 监听分页变化
watch([currentPage, pageSize], () => {
  if (searchForm.value.vehicleModelId && modalDataResult.value.results.length > 0) {
    handleSearch()
  }
})

onMounted(() => {
  // 初始化加载车型列表
  loadVehicleModels()
})
</script>

<style scoped>
.modal-data-query {
  padding: 0;
  background-color: #f5f7fa;
}

/* 卡片样式 */
.search-card,
.result-card {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #e7e7e7;
}

.search-card {
  background-color: #fff;
}

.result-card {
  background-color: #fff;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #1f2937;
}

.header-icon {
  color: #0052d9;
  font-size: 16px;
}

.header-extra {
  margin-left: auto;
}

.result-count {
  font-size: 14px;
  color: #6b7280;
}

/* 搜索表单 */
.search-form {
  padding: 0;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
  min-width: fit-content;
}

.form-select {
  width: 180px;
}

.search-btn {
  height: 32px;
  padding: 0 20px;
  border-radius: 3px;
  font-size: 14px;
  margin-left: 8px;
}

/* 表格样式 */
.result-table {
  border-radius: 6px;
  overflow: hidden;
}

:deep(.el-table) {
  border: 1px solid #e7e7e7;
}

:deep(.el-table th) {
  background-color: #f8f9fa !important;
  border-bottom: 1px solid #e7e7e7;
  font-weight: 600 !important;
  color: #374151 !important;
  font-size: 14px !important;
  padding: 12px 8px !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f1f3f4;
  padding: 10px 8px !important;
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: #f8f9fa;
}

:deep(.el-table .cell) {
  padding: 0 12px;
  line-height: 1.5;
}

.frequency-value {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 500;
  color: #0052d9;
}

/* 分页器 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f1f3f4;
}

:deep(.el-pagination) {
  --el-pagination-font-size: 14px;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  border-radius: 3px;
}

:deep(.el-pagination .el-pager li) {
  border-radius: 3px;
  margin: 0 2px;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #0052d9;
  color: white;
}

/* Element Plus 组件样式覆盖 */
:deep(.search-card .el-card__body) {
  padding: 20px;
}

:deep(.result-card .el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f3f4;
  background-color: #fafbfc;
}

:deep(.result-card .el-card__body) {
  padding: 20px;
}

:deep(.el-select) {
  --el-select-border-color-hover: #0052d9;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 3px;
}

:deep(.el-button--primary) {
  background-color: #0052d9;
  border-color: #0052d9;
}

:deep(.el-button--primary:hover) {
  background-color: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--text) {
  color: #0052d9;
}

:deep(.el-button--text:hover) {
  color: #1890ff;
  background-color: #f0f8ff;
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
