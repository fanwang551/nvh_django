<template>
  <div class="material-porosity-query">
    <!-- 查询条件卡片 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">材料孔隙率和流阻查询</span>
        </div>
      </template>

      <el-form :model="store.searchCriteria" label-width="120px" class="search-form">
        <el-row :gutter="24">
          <!-- 零件选择 -->
          <el-col :span="16">
            <el-form-item label="零件名称" required>
              <el-select
                  v-model="store.searchCriteria.partNames"
                  placeholder="请选择零件名称"
                  :loading="store.partNamesLoading"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  @change="handlePartNameChange"
                  style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                      v-model="selectAllParts"
                      @change="handleSelectAllParts"
                      style="margin-left: 12px"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                    v-for="part in store.partNameOptions"
                    :key="part.value"
                    :label="part.label"
                    :value="part.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 操作按钮 -->
          <el-col :span="8">
            <el-form-item label=" ">
              <el-button
                  type="primary"
                  :icon="Search"
                  :loading="store.queryLoading"
                  :disabled="!store.canQuery"
                  @click="handleQuery"
              >
                查询
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 查询结果 -->
    <div v-if="store.hasResults" class="result-section">
      <!-- 结果表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">材料孔隙率和流阻数据表</span>
            <span class="card-subtitle">共 {{ store.queryResults.length }} 条记录</span>
          </div>
        </template>

        <div class="table-container">
          <el-table
              :data="store.queryResults"
              border
              stripe
              style="width: 100%"
              :header-cell-style="{ background: '#409eff', color: '#ffffff', fontWeight: '700', fontSize: '14px' }"
          >
            <el-table-column prop="part_name" label="零件名称" width="120" fixed="left" />
            <el-table-column prop="material_composition" label="材料组成" width="150" />
            <el-table-column prop="material_manufacturer" label="材料厂家" width="120" />
            <el-table-column prop="test_institution" label="测试机构" width="120" />
            <el-table-column prop="thickness_mm" label="厚度 (mm)" width="100" align="center" />
            <el-table-column prop="weight_per_area" label="克重 (g/m²)" width="110" align="center" />
            <el-table-column prop="density" label="密度 (kg/m³)" width="110" align="center" />
            <el-table-column prop="porosity_percent" label="孔隙率 (%)" width="110" align="center" />
            <el-table-column prop="porosity_deviation_percent" label="孔隙率偏差 (%)" width="130" align="center">
              <template #default="scope">
                <span v-if="scope.row.porosity_deviation_percent !== null">
                  {{ scope.row.porosity_deviation_percent }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="flow_resistance" label="流阻率 (Pa·s/m²)" width="140" align="center" />
            <el-table-column prop="flow_resistance_deviation" label="流阻率偏差 (Pa·s/m²)" width="160" align="center">
              <template #default="scope">
                <span v-if="scope.row.flow_resistance_deviation !== null">
                  {{ scope.row.flow_resistance_deviation }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!store.queryLoading" class="empty-state">
      <el-empty description="请选择零件名称并执行查询" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onDeactivated } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useMaterialPorosityQueryStore } from '@/store'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'MaterialPorosityFlowResistanceQuery'
})

// 使用Pinia store
const store = useMaterialPorosityQueryStore()

// UI状态管理（组件职责）
const selectAllParts = ref(false)

// UI交互处理：全选/反选零件
const handleSelectAllParts = (checked) => {
  if (checked) {
    store.setPartNames(store.partNameOptions.map(p => p.value))
  } else {
    store.setPartNames([])
  }
  selectAllParts.value = checked
}

// UI交互处理：零件名称变化
const handlePartNameChange = (partNames) => {
  // 更新全选状态
  selectAllParts.value = partNames.length === store.partNameOptions.length
}

// 执行查询
const handleQuery = async () => {
  if (!store.canQuery) {
    ElMessage.warning('请先加载零件名称选项')
    return
  }

  try {
    const result = await store.executeQuery()
    
    if (result.length > 0) {
      ElMessage.success(`查询成功，共找到 ${result.length} 条记录`)
    } else {
      ElMessage.warning('未找到匹配的数据')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  }
}

// UI交互处理：重置表单
const handleReset = () => {
  store.resetState()
  selectAllParts.value = false
}

onMounted(async () => {
  console.log('MaterialPorosityFlowResistanceQuery mounted - 初始化页面数据')
  await store.initializeData()
})

// keep-alive 激活时
onActivated(async () => {
  console.log('MaterialPorosityFlowResistanceQuery activated - 恢复组件状态')
  await store.initializeData()
})

// keep-alive 停用时
onDeactivated(() => {
  console.log('MaterialPorosityFlowResistanceQuery deactivated - 保存组件状态')
})
</script>

<style scoped>
.material-porosity-query {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 卡片样式 */
.search-card,
.table-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.search-card {
  background: #ffffff;
}

.table-card {
  background: #ffffff;
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

.card-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-left: auto;
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
.table-container {
  border-radius: 6px;
  overflow: hidden;
}

:deep(.el-table) {
  border: 1px solid #e7e7e7;
}

:deep(.el-table td),
:deep(.el-table th) {
  text-align: center;
  border-right: none;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 无数据样式 */
.no-data {
  color: #c0c4cc;
  font-style: italic;
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

/* 结果区域 */
.result-section {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
