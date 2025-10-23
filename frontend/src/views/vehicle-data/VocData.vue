<template>
  <el-config-provider :locale="locale">
    <div class="voc-query">
    <!-- 查询表单 -->
    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>VOC数据查询</span>
        </div>
      </template>

      <el-form :model="store.searchCriteria" label-width="100px" class="search-form">
        <el-row :gutter="20">
          <!-- 项目名称选择 -->
          <el-col :span="6">
            <el-form-item label="项目名称">
              <el-select
                v-model="store.searchCriteria.vehicle_model_id"
                placeholder="请选择项目名称"
                clearable
                filterable
                :loading="store.vehicle_models_loading"
                style="width: 100%"
              >
                <el-option
                  v-for="option in store.vehicle_models"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 零件名称选择（多选） -->
          <el-col :span="6">
            <el-form-item label="零件名称">
              <el-select
                v-model="store.searchCriteria.part_names"
                placeholder="请选择零件名称（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                filterable
                :loading="store.part_names_loading"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="option in store.part_names"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 检测状态选择（多选） -->
          <el-col :span="6">
            <el-form-item label="检测状态">
              <el-select
                v-model="store.searchCriteria.statuses"
                placeholder="请选择检测状态（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                filterable
                :loading="store.status_options_loading"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="option in store.status_options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 开发阶段选择（多选） -->
          <el-col :span="6">
            <el-form-item label="开发阶段">
              <el-select
                v-model="store.searchCriteria.development_stages"
                placeholder="请选择开发阶段（可多选）"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                filterable
                :loading="store.development_stage_loading"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="option in store.development_stage_options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <!-- 检测时间 -->
          <el-col :span="6">
            <el-form-item label="检测时间">
              <el-date-picker
                v-model="store.searchCriteria.test_date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                clearable
                style="width: 100%"
                @change="handleFilterChange"
              />
            </el-form-item>
          </el-col>

          <!-- 委托单号 -->
          <el-col :span="6">
            <el-form-item label="委托单号">
              <el-input
                v-model="store.searchCriteria.test_order_no"
                placeholder="请输入委托单号"
                clearable
                @change="handleFilterChange"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <!-- 样品编号 -->
          <el-col :span="6">
            <el-form-item label="样品编号">
              <el-input
                v-model="store.searchCriteria.sample_no"
                placeholder="请输入样品编号"
                clearable
                @change="handleFilterChange"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <!-- 重置筛选按钮 -->
          <el-col :span="6">
            <el-form-item label=" " label-width="20px">
              <el-button type="primary" @click="handleReset">重置筛选</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 查询结果 -->
    <div v-if="store.hasResults || store.query_loading" class="results-section">
      <!-- 数据表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>检测结果</span>
            <div class="column-selector">
              <el-dropdown trigger="click">
                <el-button size="small" type="primary">
                  列选择<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item key="commission_number">
                      <el-checkbox
                        :modelValue="visibleColumns.includes('commission_number')"
                        @change="(value) => toggleColumn('commission_number', value)"
                      >
                        委托单号
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="sample_number">
                      <el-checkbox
                        :modelValue="visibleColumns.includes('sample_number')"
                        @change="(value) => toggleColumn('sample_number', value)"
                      >
                        样品编号
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item v-for="compound in store.chart_config.compound_options"
                                     :key="compound.value">
                      <el-checkbox
                        :modelValue="visibleColumns.includes(compound.value)"
                        @change="(value) => toggleColumn(compound.value, value)"
                      >
                        {{ compound.label }}
                      </el-checkbox>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>

        <el-table
          v-loading="store.query_loading"
          :data="store.paginatedData"
          style="width: 100%"
          stripe
          :header-cell-style="{ backgroundColor: '#409EFF', color: '#ffffff', fontWeight: '600', fontSize: '14px' }"
        >
          <el-table-column prop="sample_info.vehicle_model.vehicle_model_name" label="项目名称" width="120" align="center" />
          <el-table-column prop="test_date" label="检测时间" width="150" align="center">
            <template #default="scope">
              {{ formatDate(scope.row.test_date) }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="visibleColumns.includes('commission_number')"
            prop="sample_info.test_order_no"
            label="委托单号"
            width="150"
            align="center"
          />
          <el-table-column
            v-if="visibleColumns.includes('sample_number')"
            prop="sample_info.sample_no"
            label="样品编号"
            width="150"
            align="center"
          />
          <el-table-column prop="sample_info.part_name" label="零部件名称" width="120" align="center" />
          <el-table-column prop="sample_info.status" label="检测状态" width="100" align="center" />
          <el-table-column prop="sample_info.development_stage" label="开发阶段" width="120" align="center" />

          <!-- VOC物质列 -->
          <el-table-column
            v-if="visibleColumns.includes('benzene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>苯<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.benzene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('toluene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>甲苯<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.toluene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('ethylbenzene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>乙苯<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.ethylbenzene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('xylene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>二甲苯<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.xylene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('styrene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>苯乙烯<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.styrene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('formaldehyde')"
            width="90"
            align="center"
          >
            <template #header>
              <div>甲醛<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.formaldehyde_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('acetaldehyde')"
            width="90"
            align="center"
          >
            <template #header>
              <div>乙醛<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.acetaldehyde_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('acrolein')"
            width="90"
            align="center"
          >
            <template #header>
              <div>丙烯醛<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.acrolein_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="visibleColumns.includes('tvoc')"
            width="90"
            align="center"
          >
            <template #header>
              <div>TVOC<br/>(mg/m³)</div>
            </template>
            <template #default="scope">
              {{ scope.row.tvoc_formatted }}
            </template>
          </el-table-column>

        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="store.pagination.current_page"
            v-model:page-size="store.pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="store.pagination.total_count"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>


    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useVocQueryStore } from '@/store/vocQuery'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 配置中文语言，自定义星期显示
const locale = ref({
  ...zhCn,
  el: {
    ...zhCn.el,
    datepicker: {
      ...zhCn.el.datepicker,
      weeks: {
        sun: '日',
        mon: '一',
        tue: '二',
        wed: '三',
        thu: '四',
        fri: '五',
        sat: '六'
      }
    }
  }
})

// Store
const store = useVocQueryStore()

// 可见列管理 - 默认选择所有物质和委托单号、样品编号
const visibleColumns = ref(['commission_number', 'sample_number', 'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc'])

// 切换列显示
const toggleColumn = (compound, visible) => {
  if (visible) {
    if (!visibleColumns.value.includes(compound)) {
      visibleColumns.value.push(compound)
    }
  } else {
    const index = visibleColumns.value.indexOf(compound)
    if (index > -1) {
      visibleColumns.value.splice(index, 1)
    }
  }
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const handleFilterChange = () => {
  store.filterVocData()
}

const handleReset = () => {
  store.resetSearchCriteria()
  visibleColumns.value = ['commission_number', 'sample_number', 'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc']
}

const handleSizeChange = (val) => {
  store.setPageSize(val)
}

const handlePageChange = (val) => {
  store.setPage(val)
}

// 生命周期
onMounted(async () => {
  try {
    // 首先加载车型选项
    await store.fetchVehicleModelOptions()
    
    // 加载所有VOC数据，并自动提取唯一选项
    await store.loadAllVocData()
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('页面初始化失败')
  }
})
</script>

<style scoped>
.voc-query {
  padding: 20px;
  background-color: #f5f7fa;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.search-form {
  background-color: #fff;
}

.results-section {
  margin-top: 20px;
}

.table-card {
  margin-bottom: 20px;
  background-color: #fff;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table__header-wrapper) {
  background-color: #f5f7fa;
}

:deep(.el-table__body-wrapper) {
  overflow-x: auto;
}
</style>
