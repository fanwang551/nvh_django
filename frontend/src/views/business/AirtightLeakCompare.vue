<template>
  <div class="airtight-leak-compare">


    <!-- 车型选择卡片 -->
    <el-card class="search-card" shadow="never">
      <div class="search-form">
        <div class="form-row">
          <div class="form-group">
            <span class="form-label">选择车型：</span>
            <el-select
              v-model="selectedVehicleIds"
              placeholder="请选择要对比的车型（可多选）"
              class="form-select"
              multiple
              collapse-tags
              collapse-tags-tooltip
              clearable
              :loading="vehicleModelsLoading"
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
            <el-button
              type="primary"
              :icon="Search"
              @click="handleCompare"
              :loading="loading"
              :disabled="selectedVehicleIds.length === 0"
              class="search-btn"
            >
              对比
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 对比结果展示卡片 -->
    <el-card class="result-card" shadow="never" v-if="compareResult.vehicle_models.length > 0">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><List /></el-icon>
          <span>气密性泄漏量对比结果</span>
          <div class="header-extra">
            <span class="result-count">对比车型：{{ compareResult.vehicle_models.length }} 个</span>
          </div>
        </div>
      </template>

      <div class="table-container">
        <el-table
          :data="tableData"
          v-loading="loading"
          class="result-table"
          stripe
          border
          :header-cell-style="getHeaderCellStyle"
          :cell-style="getCellStyle"
          :span-method="spanMethod"
          table-layout="fixed"
          style="width: 100%"
        >
          <el-table-column
            prop="category"
            label="区域"
            :width="columnWidths.category"
            align="center"
            :resizable="false"
          />
          <el-table-column
            prop="item_name"
            label="泄漏量(SCFM)"
            :width="columnWidths.itemName"
            :resizable="false"
          />
          <el-table-column
            v-for="vehicle in compareResult.vehicle_models"
            :key="vehicle.id"
            :label="vehicle.name"
            :prop="`vehicle_${vehicle.id}`"
            :width="columnWidths.vehicle"
            align="center"
            :resizable="false"
          />
        </el-table>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-card class="result-card" shadow="never" v-else-if="!loading">
      <el-empty description="请选择车型进行对比" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, List } from '@element-plus/icons-vue'
import { modalApi } from '@/api/modal'

// 响应式数据
const loading = ref(false)
const vehicleModelsLoading = ref(false)
const selectedVehicleIds = ref([])
const vehicleModelOptions = ref([])
const compareResult = reactive({
  vehicle_models: [],
  leakage_data: []
})
const tableData = ref([])

// 动态列宽计算
const columnWidths = computed(() => {
  const vehicleCount = compareResult.vehicle_models.length

  if (vehicleCount === 0) {
    return {
      category: 150,
      itemName: 200,
      vehicle: 150
    }
  }

  // 基础列宽
  const categoryWidth = 150
  const itemNameWidth = 220

  // 根据车型数量动态计算车型列宽
  const minVehicleWidth = 140
  const maxVehicleWidth = 200

  // 计算可用宽度（假设容器最小宽度为800px）
  const containerMinWidth = 800
  const usedWidth = categoryWidth + itemNameWidth
  const availableWidth = containerMinWidth - usedWidth

  let vehicleWidth = Math.max(minVehicleWidth, Math.min(maxVehicleWidth, availableWidth / vehicleCount))

  // 如果车型数量较少，可以给更多空间
  if (vehicleCount <= 2) {
    vehicleWidth = maxVehicleWidth
  } else if (vehicleCount <= 4) {
    vehicleWidth = Math.max(160, vehicleWidth)
  }

  return {
    category: categoryWidth,
    itemName: itemNameWidth,
    vehicle: Math.round(vehicleWidth)
  }
})

// 获取车型列表
const loadVehicleModels = async () => {
  try {
    vehicleModelsLoading.value = true
    const response = await modalApi.getVehicleModels()
    if (response.success) {
      vehicleModelOptions.value = response.data
    } else {
      ElMessage.error(response.message || '获取车型列表失败')
    }
  } catch (error) {
    console.error('获取车型列表失败:', error)
    ElMessage.error('获取车型列表失败')
  } finally {
    vehicleModelsLoading.value = false
  }
}

// 处理对比操作
const handleCompare = async () => {
  if (selectedVehicleIds.value.length === 0) {
    ElMessage.warning('请至少选择一个车型')
    return
  }

  try {
    loading.value = true
    const response = await modalApi.compareAirtightnessData({
      vehicle_model_ids: selectedVehicleIds.value.join(',')
    })

    if (response.success) {
      compareResult.vehicle_models = response.data.vehicle_models
      compareResult.leakage_data = response.data.leakage_data
      buildTableData()
      ElMessage.success('对比数据获取成功')
    } else {
      ElMessage.error(response.message || '获取对比数据失败')
    }
  } catch (error) {
    console.error('获取对比数据失败:', error)
    ElMessage.error('获取对比数据失败')
  } finally {
    loading.value = false
  }
}

// 构建表格数据
const buildTableData = () => {
  const data = []

  compareResult.leakage_data.forEach(category => {
    category.items.forEach((item, itemIndex) => {
      const row = {
        category: itemIndex === 0 ? category.category : '',
        item_name: item.name,
        categoryRowspan: itemIndex === 0 ? category.items.length : 0
      }

      // 为每个车型添加对应的数值
      compareResult.vehicle_models.forEach((vehicle, vehicleIndex) => {
        row[`vehicle_${vehicle.id}`] = item.values[vehicleIndex] || '-'
      })

      data.push(row)
    })
  })

  tableData.value = data

  // 强制重新渲染表格以确保对齐
  nextTick(() => {
    // 触发表格重新计算布局
    window.dispatchEvent(new Event('resize'))
  })
}

// 表格合并单元格方法
const spanMethod = ({ row, column, rowIndex, columnIndex }) => {
  if (columnIndex === 0) { // 区域列
    if (row.categoryRowspan > 0) {
      return {
        rowspan: row.categoryRowspan,
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

// 表头样式方法
const getHeaderCellStyle = ({ row, column, rowIndex, columnIndex }) => {
  return {
    backgroundColor: '#409eff',
    color: '#ffffff',
    fontWeight: '700',
    fontSize: '16px',
    textAlign: 'center',
    padding: '16px 12px',
    borderBottom: '2px solid #337ecc'
  }
}

// 单元格样式方法
const getCellStyle = ({ row, column, rowIndex, columnIndex }) => {
  if (columnIndex === 0 && row.category) { // 区域列且有分类名称
    return {
      fontWeight: '600',
      color: '#303133',
      backgroundColor: '#fafbfc'
    }
  }
  return {}
}

// 组件挂载时加载数据
onMounted(() => {
  loadVehicleModels()
})
</script>

<style scoped>
.airtight-leak-compare {
  padding: 0;
}

.page-header {
  margin-bottom: 40px;
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

/* 搜索卡片样式 */
.search-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.search-form {
  padding: 8px 0;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
}

.form-select {
  min-width: 300px;
}

.search-btn {
  padding: 10px 24px;
  font-size: 14px;
  border-radius: 6px;
}

/* 结果卡片样式 */
.result-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-icon {
  margin-right: 8px;
  color: #409eff;
}

.result-count {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

/* 表格容器样式 */
.table-container {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
  width: 100%;
  min-width: 800px;
  overflow-x: auto;
}

.result-table {
  width: 100%;
  table-layout: fixed;
}

.result-table :deep(.el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.result-table :deep(.el-table__body-wrapper) {
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.result-table :deep(.el-table__header),
.result-table :deep(.el-table__body) {
  width: 100% !important;
  table-layout: fixed !important;
}

.result-table :deep(.el-table__header-wrapper .el-table__header thead tr th) {
  background-color: #409eff !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  padding: 16px 12px !important;
  border-bottom: 2px solid #337ecc !important;
  text-align: center !important;
  box-sizing: border-box !important;
}

.result-table :deep(.el-table__body-wrapper .el-table__body tbody tr td) {
  box-sizing: border-box !important;
  padding: 12px !important;
  text-align: center !important;
}

.result-table :deep(.el-table td),
.result-table :deep(.el-table th) {
  border-right: 1px solid #ebeef5;
  text-align: center;
}

.result-table :deep(.el-table td:last-child),
.result-table :deep(.el-table th:last-child) {
  border-right: none;
}

.result-table :deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 区域列特殊样式 */
.result-table :deep(.el-table__body td:first-child) {
  font-weight: 600 !important;
  color: #303133 !important;
  background-color: #fafbfc !important;
  border-right: 2px solid #e4e7ed !important;
}

.result-table :deep(.el-table__header th:first-child) {
  background-color: #337ecc !important;
  font-weight: 700 !important;
  color: #ffffff !important;
  border-right: 2px solid #2c6bb3 !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .table-container {
    min-width: 700px;
  }
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .form-group {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .form-select {
    min-width: auto;
    width: 100%;
  }

  .search-btn {
    width: 100%;
  }

  .table-container {
    min-width: 600px;
    overflow-x: auto;
  }

  .result-table :deep(.el-table__header-wrapper .el-table__header thead tr th) {
    font-size: 14px !important;
    padding: 12px 8px !important;
  }

  .result-table :deep(.el-table__body-wrapper .el-table__body tbody tr td) {
    padding: 10px 8px !important;
    font-size: 13px !important;
  }
}

@media (max-width: 480px) {
  .table-container {
    min-width: 500px;
  }

  .result-table :deep(.el-table__header-wrapper .el-table__header thead tr th) {
    font-size: 12px !important;
    padding: 10px 6px !important;
  }

  .result-table :deep(.el-table__body-wrapper .el-table__body tbody tr td) {
    padding: 8px 6px !important;
    font-size: 12px !important;
  }
}
</style>
