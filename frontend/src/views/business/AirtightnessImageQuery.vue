<template>
  <div class="airtightness-image-query">


    <!-- 搜索卡片 -->
    <el-card class="search-card" shadow="never">
      <div class="search-form">
        <div class="form-row">
          <div class="form-group">
            <span class="form-label">车型：</span>
            <el-select
              v-model="searchForm.vehicleModelIds"
              placeholder="请选择车型（可多选，默认显示全部）"
              multiple
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              clearable
              filterable
              class="form-select"
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
          <div class="form-actions">
            <el-button 
              type="primary" 
              :icon="Search" 
              @click="handleSearch"
              :loading="loading"
            >
              查询
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 图片展示卡片 -->
    <el-card class="result-card" shadow="never" v-if="imageDataList.length > 0">
      <template #header>
        <div class="card-header">
          <el-icon><Picture /></el-icon>
          <span>气密性测试图片 ({{ imageDataList.length }}个车型)</span>
        </div>
      </template>

      <div class="image-display-container">
        <!-- 按车型分组显示图片 -->
        <div 
          v-for="imageData in imageDataList" 
          :key="imageData.id"
          class="vehicle-image-group"
        >
          <!-- 车型标题 -->
          <div class="vehicle-title">
            <h3>{{ imageData.vehicle_model_name }}</h3>
          </div>

          <!-- 三个位置的图片 -->
          <div class="image-grid">
            <!-- 前舱图片 -->
            <div class="image-item">
              <div class="image-title">前舱</div>
              <el-image
                v-if="imageData.front_compartment_image"
                :src="getImageUrl(imageData.front_compartment_image)"
                :preview-src-list="[getImageUrl(imageData.front_compartment_image)]"
                :preview-teleported="true"
                fit="cover"
                class="airtightness-image"
                lazy
                @error="handleImageError"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="image-placeholder">
                <el-icon><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </div>

            <!-- 车门图片 -->
            <div class="image-item">
              <div class="image-title">车门</div>
              <el-image
                v-if="imageData.door_image"
                :src="getImageUrl(imageData.door_image)"
                :preview-src-list="[getImageUrl(imageData.door_image)]"
                :preview-teleported="true"
                fit="cover"
                class="airtightness-image"
                lazy
                @error="handleImageError"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="image-placeholder">
                <el-icon><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </div>

            <!-- 尾门图片 -->
            <div class="image-item">
              <div class="image-title">尾门</div>
              <el-image
                v-if="imageData.tailgate_image"
                :src="getImageUrl(imageData.tailgate_image)"
                :preview-src-list="[getImageUrl(imageData.tailgate_image)]"
                :preview-teleported="true"
                fit="cover"
                class="airtightness-image"
                lazy
                @error="handleImageError"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="image-placeholder">
                <el-icon><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-card class="result-card" shadow="never" v-else-if="!loading">
      <el-empty description="暂无气密性测试图片数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Picture } from '@element-plus/icons-vue'
import modalApi from '@/api/modal'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'AirtightnessImageQuery'
})

// 搜索表单
const searchForm = ref({
  vehicleModelIds: []
})

// 数据状态
const vehicleModelOptions = ref([])
const vehicleModelsLoading = ref(false)
const imageDataList = ref([])
const loading = ref(false)

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

const loadAirtightnessImages = async (vehicleModelIds = []) => {
  try {
    loading.value = true
    const params = {}
    
    // 如果选择了车型，添加到查询参数
    if (vehicleModelIds.length > 0) {
      params.vehicle_model_ids = vehicleModelIds.join(',')
    }

    const response = await modalApi.getAirtightnessImages(params)
    imageDataList.value = response.data || []
  } catch (error) {
    console.error('加载气密性图片失败:', error)
    ElMessage.error('加载气密性图片失败')
  } finally {
    loading.value = false
  }
}

// 事件处理
const handleVehicleModelChange = () => {
  // 车型选择变化时自动查询
  handleSearch()
}

const handleSearch = () => {
  loadAirtightnessImages(searchForm.value.vehicleModelIds)
}

const handleReset = () => {
  searchForm.value.vehicleModelIds = []
  loadAirtightnessImages()
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
}

// 生命周期
onMounted(async () => {
  // 初始化加载车型列表和所有图片
  await loadVehicleModels()
  await loadAirtightnessImages()
})
</script>

<style scoped>
.airtightness-image-query {
  padding: 0;
  background-color: #f5f7fa;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 500;
  color: #1f2937;
}

.page-description {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

/* 卡片样式 */
.search-card,
.result-card {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #e7e7e7;
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

/* 搜索表单 */
.search-form {
  padding: 4px 0;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.form-label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.form-select {
  flex: 1;
  max-width: 400px;
}

.form-actions {
  display: flex;
  gap: 8px;
}

/* 图片展示容器 */
.image-display-container {
  padding: 8px 0;
}

.vehicle-image-group {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.vehicle-image-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

/* 车型标题 */
.vehicle-title {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f3f4f6;
  text-align: center;
}

.vehicle-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* 图片网格 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
}

@media (min-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.image-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-title {
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

/* 图片样式 */
.airtightness-image {
  width: 200px;
  height: 150px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.3s ease;
}

.airtightness-image:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

/* 图片错误和占位符 */
.image-error,
.image-placeholder {
  width: 200px;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  color: #9ca3af;
}

.image-error .el-icon,
.image-placeholder .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.image-error span,
.image-placeholder span {
  font-size: 12px;
}



/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .form-group {
    min-width: auto;
  }

  .form-actions {
    justify-content: center;
  }


}

/* 图片预览弹窗全局样式修复 */
:deep(.el-image-viewer__wrapper) {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 9999 !important;
  background-color: rgba(0, 0, 0, 0.8) !important;
}

:deep(.el-image-viewer__canvas) {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 控制弹窗内的图片大小 - 使用更高优先级覆盖内联样式 */
:deep(.el-image-viewer__img) {
  max-width: 80vw !important;   /* 最大宽度为视窗宽度的80% */
  max-height: 80vh !important;  /* 最大高度为视窗高度的80% */
  width: auto !important;       /* 保持宽高比 */
  height: auto !important;      /* 保持宽高比 */
  object-fit: contain !important; /* 确保图片完整显示且不变形 */
}

/* 针对具体的内联样式进行覆盖 */
:deep(.el-image-viewer__canvas .el-image-viewer__img[style*="max-height: 100%"]) {
  max-height: 80vh !important;
}

:deep(.el-image-viewer__canvas .el-image-viewer__img[style*="max-width: 100%"]) {
  max-width: 80vw !important;
}

:deep(.el-image-viewer__actions) {
  position: fixed !important;
  bottom: 30px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 10000 !important;
}

:deep(.el-image-viewer__close) {
  position: fixed !important;
  top: 30px !important;
  right: 30px !important;
  z-index: 10000 !important;
}

/* 确保预览弹窗不被父容器限制 */
:deep(.el-image-viewer__mask) {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9998 !important;
}

/* 修复可能的容器overflow限制 */
.airtightness-image-query,
.image-display-container,
.vehicle-image-group,
.image-grid,
.image-item {
  overflow: visible !important;
}

/* 全局样式 - 更强力的图片预览样式覆盖 */
</style>

<!-- 全局样式，不使用scoped，确保能覆盖Element Plus的内联样式 -->
<style>
/* 气密性图片预览弹窗样式优化 */
.el-image-viewer__wrapper .el-image-viewer__canvas .el-image-viewer__img {
  max-width: 80vw !important;
  max-height: 80vh !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
}

/* 使用属性选择器强制覆盖内联样式 */
.el-image-viewer__img[style] {
  max-width: 80vw !important;
  max-height: 80vh !important;
  width: auto !important;
  height: auto !important;
}

/* 确保图片居中显示 */
.el-image-viewer__canvas {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  padding: 20px !important;
}

/* 响应式设计 - 小屏幕上进一步限制大小 */
@media (max-width: 768px) {
  .el-image-viewer__wrapper .el-image-viewer__canvas .el-image-viewer__img,
  .el-image-viewer__img[style] {
    max-width: 90vw !important;
    max-height: 70vh !important;
  }
}
</style>
