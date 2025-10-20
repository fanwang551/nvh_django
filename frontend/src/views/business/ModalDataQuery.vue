<template>
  <div class="modal-data-query">
    <!-- 搜索卡片 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>

      <el-form :model="searchForm" label-width="80px" class="search-form">
        <el-row :gutter="24">
          <!-- 车型选择 -->
          <el-col :span="8">
            <el-form-item label="车型" required>
              <el-select
                v-model="searchForm.vehicleModelId"
                placeholder="请选择车型"
                clearable
                :loading="vehicleModelsLoading"
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

          <!-- 零件选择 -->
          <el-col :span="10">
            <el-form-item label="零件">
              <el-select
                v-model="searchForm.componentIds"
                placeholder="请选择零件（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                :loading="componentsLoading"
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

          <!-- 查询按钮 -->
          <el-col :span="6">
            <el-form-item>
              <el-button
                type="primary"
                :icon="Search"
                @click="handleSearch"
                :loading="loading"
                style="width: 100%; min-width: 120px;"
              >
                查询
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
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
        :header-cell-style="{ backgroundColor: '#409EFF', color: '#ffffff', fontWeight: '600', fontSize: '14px' }"
      >
        <el-table-column prop="component_category" label="零件分类" min-width="120" />
        <el-table-column prop="component_name" label="零件名称" min-width="160" />
        <el-table-column prop="mode_shape_description" label="模态振型描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="frequency" label="频率(Hz)" min-width="130" align="center">
          <template #default="scope">
            <span class="frequency-value">{{ scope.row.frequency }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="damping_ratio" label="阻尼比" min-width="110" align="center" />
        <el-table-column label="操作" width="130" align="center" fixed="right">
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
import { ref, computed, onMounted, onActivated, onDeactivated } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, List } from '@element-plus/icons-vue'
import { useModalDataQueryStore } from '@/store/modalDataQuery'
import { getImageUrl, handleImageError } from '@/utils/imageService'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'ModalDataQuery'
})

// 使用Pinia store
const store = useModalDataQueryStore()

// 从store中获取响应式状态
const searchForm = computed(() => store.searchForm)
const loading = computed(() => store.loading)
const vehicleModelsLoading = computed(() => store.vehicleModelsLoading)
const componentsLoading = computed(() => store.componentsLoading)
const currentPage = computed({
  get: () => store.currentPage,
  set: (value) => { store.currentPage = value }
})
const pageSize = computed({
  get: () => store.pageSize,
  set: (value) => { store.pageSize = value }
})
const vehicleModelOptions = computed(() => store.vehicleModelOptions)
const componentOptions = computed(() => store.componentOptions)
const modalDataResult = computed(() => store.modalDataResult)
// UI状态管理（组件职责）
const modalShapeDialogVisible = ref(false)
const currentModalData = ref(null)
const activeTab = ref('shape')

// 车型变化处理
const handleVehicleModelChange = async (vehicleModelId) => {
  try {
    await store.handleVehicleModelChange(vehicleModelId)
  } catch (error) {
    console.error('车型变化处理失败:', error)
    ElMessage.error('加载零件列表失败')
  }
}

// 搜索处理
const handleSearch = async () => {
  if (!store.canQuery) {
    ElMessage.warning('请先选择车型')
    return
  }

  try {
    await store.queryModalData()
    ElMessage.success('查询完成')
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  }
}

// UI交互处理：查看振型（组件职责）
const viewModalShape = (row) => {
  currentModalData.value = row
  activeTab.value = 'shape' // 默认显示振型动画
  modalShapeDialogVisible.value = true
}

// UI交互处理：关闭弹窗（组件职责）
const handleCloseDialog = () => {
  modalShapeDialogVisible.value = false
  currentModalData.value = null
  activeTab.value = 'shape'
}

// UI交互处理：切换弹窗标签页（组件职责）
const switchDialogTab = (tab) => {
  activeTab.value = tab
}

// 图片相关功能已移至 @/utils/imageService

// 分页处理
const handleSizeChange = async (val) => {
  try {
    await store.handlePageSizeChange(val)
  } catch (error) {
    console.error('页面大小变化失败:', error)
    ElMessage.error('操作失败')
  }
}

const handleCurrentChange = async (val) => {
  try {
    await store.handlePageChange(val)
  } catch (error) {
    console.error('页面切换失败:', error)
    ElMessage.error('操作失败')
  }
}

// 组件生命周期处理
onMounted(async () => {
  try {
    await store.initializePageData()
    // 如果已有数据且有查询条件，重新查询以确保数据最新
    if (store.hasResults && store.canQuery) {
      await store.queryModalData()
    }
  } catch (error) {
    console.error('组件初始化失败:', error)
    ElMessage.error('页面初始化失败')
  }
})

// 组件被激活时（从keep-alive缓存中恢复）
onActivated(async () => {
  try {
    await store.initializePageData()
    // 如果已有数据且有查询条件，确保数据是最新的
    if (store.hasResults && store.canQuery) {
      // 可以选择是否重新查询，这里保持数据不变以保持用户状态
      // await store.queryModalData()
    }
  } catch (error) {
    console.error('组件激活失败:', error)
  }
})

// 组件被停用时（被keep-alive缓存）
onDeactivated(() => {
  // 清理UI状态，避免状态残留（组件职责）
  if (modalShapeDialogVisible.value) {
    handleCloseDialog()
  }
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

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
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
  margin: 0;
}

:deep(.search-form .el-form-item) {
  margin-bottom: 0;
}

:deep(.search-form .el-form-item__label) {
  font-weight: 500;
  color: #374151;
}
/* 表格样式 */
.result-table {
  border-radius: 6px;
  overflow: hidden;
  width: 100%;
}

:deep(.result-table .el-table__body-wrapper) {
  overflow-x: auto;
}

:deep(.result-table .el-table) {
  width: 100% !important;
  min-width: 100%;
}

:deep(.el-table) {
  border: 1px solid #e7e7e7;
}

:deep(.el-table th) {
  background-color: #409EFF !important;
  border-bottom: 1px solid #409EFF;
  font-weight: 600 !important;
  color: #ffffff !important;
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
  color: #409EFF;
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
