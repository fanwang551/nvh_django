<template>
  <div class="substance-traceability">
    <!-- 筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form class="filter-form">
        <el-form-item label="车型选择">
          <el-select
            v-model="store.searchCriteria.selected_key"
            placeholder="请选择车型"
            clearable
            filterable
            :loading="store.vehicle_models_loading"
            style="width: 280px"
            @change="handleVehicleModelChange"
          >
            <el-option
              v-for="option in store.vehicle_models"
              :key="option.key"
              :label="option.label"
              :value="option.key"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="物质选择">
          <el-select
            v-model="store.searchCriteria.cas_nos"
            placeholder="请选择物质（可多选）"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            filterable
            :loading="store.substance_options_loading"
            :disabled="!store.searchCriteria.selected_key"
            style="width: 400px"
          >
            <template #footer>
              <div style="padding: 8px; text-align: center; border-top: 1px solid #e4e7ed;">
                已选择 {{ store.selectedSubstanceCount }} 种物质
                <el-button 
                  type="text" 
                  size="small" 
                  @click="clearSubstances"
                  style="margin-left: 10px;"
                >
                  清空
                </el-button>
              </div>
            </template>
            <el-option
              v-for="option in store.substance_options"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ option.label }}</span>
                <span style="color: #909399; font-size: 12px;">
                  {{ formatConcentration(option.concentration) }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            :disabled="!store.canQuery"
            :loading="store.query_loading"
            @click="handleQuery"
          >
            查询溯源结果
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果表格 -->
    <el-card v-if="store.hasResults" class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            {{ getCurrentVehicleModelName() }} 整车溯源分析结果（共{{ store.traceability_data.length }}种物质）
          </span>
          <el-dropdown trigger="click" :hide-on-click="false">
            <el-button size="small" type="primary">
              显示列设置 <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click.stop>
                  <el-checkbox
                    :model-value="store.column_visibility.show_qij"
                    @change="(val) => store.toggleColumnVisibility('qij', val)"
                  >
                    Qij值
                  </el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item @click.stop>
                  <el-checkbox
                    :model-value="store.column_visibility.show_wih"
                    @change="(val) => store.toggleColumnVisibility('wih', val)"
                  >
                    Wih值
                  </el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item @click.stop>
                  <el-checkbox
                    :model-value="store.column_visibility.show_concentration"
                    @change="(val) => store.toggleColumnVisibility('concentration', val)"
                  >
                    浓度值
                  </el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <el-button-group size="small" style="width: 100%;">
                    <el-button @click="store.showAllColumns()">全部显示</el-button>
                    <el-button @click="store.hideAllColumns()">全部隐藏</el-button>
                  </el-button-group>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>

      <div class="table-container">
        <el-table
          :data="store.traceability_data"
          border
          style="width: 100%"
          :row-class-name="getRowClassName"
        >
          <!-- 固定列区域 -->
          <el-table-column
            prop="substance_name_cn"
            label="物质中文名"
            width="120"
            fixed
            align="center"
            :class-name="'fixed-column'"
          >
            <template #header>
              <span>物质名称</span>
            </template>
            <template #default="scope">
              <el-button
                type="text"
                @click="showSubstanceDetail(scope.row.substance_id, scope.row.substance_info)"
                style="color: #409EFF; font-weight: 600;"
              >
                {{ scope.row.substance_name_cn }}
              </el-button>
            </template>
          </el-table-column>

          <el-table-column
            prop="retention_time"
            label="保留时间"
            width="100"
            align="center"
          >
            <template #default="scope">
              <span class="number-cell">{{ formatNumber(scope.row.retention_time, 2) }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="match_degree"
            label="匹配度"
            width="80"
            align="center"
          >
            <template #default="scope">
              <span class="number-cell">{{ formatNumber(scope.row.match_degree, 1) }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="concentration_ratio"
            label="浓度占比"
            width="90"
            align="center"
          >
            <template #default="scope">
              <span class="number-cell">{{ formatNumber(scope.row.concentration_ratio, 1) }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="concentration"
            label="浓度(μg/m³)"
            width="100"
            align="center"
          >
            <template #default="scope">
              <span class="number-cell">{{ formatNumber(scope.row.concentration, 3) }}</span>
            </template>
          </el-table-column>

          <!-- 气味污染物来源区域 -->
          <el-table-column label="气味污染物可能来源 (按Qij排序)" align="center" header-align="center">
            <el-table-column
              v-for="rank in 5"
              :key="'odor-' + rank"
              :label="'TOP' + rank"
              align="center"
              header-align="center"
            >
              <!-- 零件名列 -->
              <el-table-column
                label="零件"
                align="center"
                width="100"
              >
                <template #default="scope">
                  <span class="part-name">
                    {{ scope.row.odor_top5[rank - 1]?.part_name || '-' }}
                  </span>
                </template>
              </el-table-column>
              
              <!-- Qij列 -->
              <el-table-column
                v-if="store.column_visibility.show_qij"
                label="Qij"
                align="center"
                width="80"
              >
                <template #default="scope">
                  <span class="number-cell">
                    {{ scope.row.odor_top5[rank - 1]?.qij !== null && scope.row.odor_top5[rank - 1]?.qij !== undefined 
                       ? formatNumber(scope.row.odor_top5[rank - 1].qij, 3) 
                       : '-' }}
                  </span>
                </template>
              </el-table-column>
              
              <!-- 浓度列 -->
              <el-table-column
                v-if="store.column_visibility.show_concentration"
                label="浓度"
                align="center"
                width="90"
              >
                <template #default="scope">
                  <span class="number-cell">
                    {{ scope.row.odor_top5[rank - 1]?.concentration !== null && scope.row.odor_top5[rank - 1]?.concentration !== undefined
                       ? formatNumber(scope.row.odor_top5[rank - 1].concentration, 3)
                       : '-' }}
                  </span>
                </template>
              </el-table-column>
            </el-table-column>
          </el-table-column>

          <!-- 有机污染物来源区域 -->
          <el-table-column label="挥发性有机污染物可能来源 (按Wih排序)" align="center" header-align="center">
            <el-table-column
              v-for="rank in 5"
              :key="'organic-' + rank"
              :label="'TOP' + rank"
              align="center"
              header-align="center"
            >
              <!-- 零件名列 -->
              <el-table-column
                label="零件"
                align="center"
                width="100"
              >
                <template #default="scope">
                  <span class="part-name">
                    {{ scope.row.organic_top5[rank - 1]?.part_name || '-' }}
                  </span>
                </template>
              </el-table-column>
              
              <!-- Wih列 -->
              <el-table-column
                v-if="store.column_visibility.show_wih"
                label="Wih"
                align="center"
                width="80"
              >
                <template #default="scope">
                  <span class="number-cell">
                    {{ scope.row.organic_top5[rank - 1]?.wih !== null && scope.row.organic_top5[rank - 1]?.wih !== undefined 
                       ? formatNumber(scope.row.organic_top5[rank - 1].wih, 3) 
                       : '-' }}
                  </span>
                </template>
              </el-table-column>
              
              <!-- 浓度列 -->
              <el-table-column
                v-if="store.column_visibility.show_concentration"
                label="浓度"
                align="center"
                width="90"
              >
                <template #default="scope">
                  <span class="number-cell">
                    {{ scope.row.organic_top5[rank - 1]?.concentration !== null && scope.row.organic_top5[rank - 1]?.concentration !== undefined
                       ? formatNumber(scope.row.organic_top5[rank - 1].concentration, 3)
                       : '-' }}
                  </span>
                </template>
              </el-table-column>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty
      v-else-if="!store.query_loading"
      description="请选择车型和物质后查询"
      :image-size="200"
    />

    <!-- 加载状态 -->
    <div v-if="store.query_loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 物质详情对话框 -->
    <el-dialog
      v-model="substanceDialogVisible"
      title="物质详细信息"
      width="50%"
      center
    >
      <el-card v-if="currentSubstance" shadow="never" style="border: none;">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="物质中文名">
            {{ currentSubstance.substance_name_cn || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="物质英文名">
            {{ currentSubstance.substance_name_en || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="CAS号">
            {{ currentSubstance.cas_no || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="嗅阈值(μg/m³)">
            {{ currentSubstance.odor_threshold || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="有机物阈值(μg/m³)">
            {{ currentSubstance.organic_threshold || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="限值(μg/m³)">
            {{ currentSubstance.limit_value || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="气味特性">
            {{ currentSubstance.odor_character || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="主要用途">
            {{ currentSubstance.main_usage || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注">
            {{ currentSubstance.remark || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSubstanceTraceabilityStore } from '@/store/substanceTraceability'
import { substancesApi } from '@/api/substances'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const store = useSubstanceTraceabilityStore()

// 物质详情弹窗
const substanceDialogVisible = ref(false)
const currentSubstance = ref(null)

// 车型变化处理
const handleVehicleModelChange = (selectedKey) => {
  console.log('车型选择变化:', selectedKey)
  console.log('可用选项:', store.vehicle_models)
  store.handleVehicleModelChange(selectedKey)
}

// 清空物质选择
const clearSubstances = () => {
  store.searchCriteria.cas_nos = []
}

// 查询
const handleQuery = async () => {
  try {
    await store.fetchTraceabilityData()
    if (store.traceability_data.length === 0) {
      ElMessage.warning('未查询到溯源数据')
    }
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

// 获取当前车型名称
const getCurrentVehicleModelName = () => {
  const currentModel = store.vehicle_models.find(
    (m) => m.key === store.searchCriteria.selected_key
  )
  return currentModel ? currentModel.label : '未知车型'
}

// 格式化数字
const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return '-'
  return Number(value).toFixed(decimals)
}

// 格式化浓度显示
const formatConcentration = (concentration) => {
  if (!concentration) return ''
  const num = typeof concentration === 'number' ? concentration : parseFloat(concentration)
  if (isNaN(num)) return ''
  return num.toFixed(3) + ' μg/m³'
}



// 显示物质详情
const showSubstanceDetail = async (substanceId, substanceInfo) => {
  try {
    if (substanceInfo) {
      currentSubstance.value = substanceInfo
      substanceDialogVisible.value = true
    } else {
      const response = await substancesApi.getSubstanceDetail({ substance_id: substanceId })
      currentSubstance.value = response.data
      substanceDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取物质详情失败:', error)
    ElMessage.error('获取物质详情失败')
  }
}

// 表格行类名
const getRowClassName = ({ rowIndex }) => {
  return rowIndex % 2 === 0 ? 'even-row' : 'odd-row'
}

// 生命周期
onMounted(async () => {
  console.log('SubstanceTraceability 组件挂载')
  try {
    store.loadColumnVisibility()
    await store.fetchVehicleModels()
    console.log('初始化完成，车型数量:', store.vehicle_models?.length || 0)
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error(`页面初始化失败: ${error.message || '未知错误'}`)
  }
})
</script>

<style scoped>
.substance-traceability {
  padding: 20px;
  background-color: #f5f7fa;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: nowrap;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
  flex-shrink: 0;
}

.filter-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.result-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.table-container {
  overflow-x: auto;
}

/* 表头样式 */
:deep(.el-table__header-wrapper) {
  background-color: #f5f7fa;
}

:deep(.el-table th) {
  background-color: #1890ff !important;
  color: #ffffff !important;
  font-weight: 600;
  font-size: 14px;
  line-height: 22px;
  padding: 12px 0;
}

/* 固定列样式 */
:deep(.el-table .fixed-column) {
  /* 移除背景色，与其他列保持一致 */
}

/* 行样式 */
:deep(.el-table .even-row) {
  background-color: #fafafa;
}

:deep(.el-table .odd-row) {
  background-color: #ffffff;
}

:deep(.el-table tbody tr:hover) {
  background-color: #e6f7ff !important;
}

/* 单元格样式 */
:deep(.el-table td) {
  padding: 8px 12px;
  line-height: 20px;
}

.substance-name {
  font-weight: 500;
  color: #1f2937;
}

.number-cell {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  color: #374151;
}

.part-name {
  color: #1f2937;
  font-weight: 500;
}

.loading-container {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

/* 表头分组样式 */
.header-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
}

.header-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.header-subtitle {
  font-size: 12px;
  color: #6b7280;
  font-weight: normal;
}



/* 响应式 */
@media (max-width: 1600px) {
  .filter-form :deep(.el-form-item) {
    margin-bottom: 10px;
  }
}
</style>
