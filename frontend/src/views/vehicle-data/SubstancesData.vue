<template>
  <el-config-provider :locale="locale">
    <div class="substances-query">
      <!-- 查询表单 -->
      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>全谱物质数据查询</span>
          </div>
        </template>

        <el-form :model="store.searchCriteria" label-width="100px" class="search-form">
          <el-row :gutter="20">
            <!-- 项目名称选择 -->
            <el-col :span="6">
              <el-form-item label="项目名称">
                <el-select
                  v-model="store.searchCriteria.project_name"
                  placeholder="请选择项目名称"
                  clearable
                  filterable
                  :loading="store.vehicle_models_loading"
                  style="width: 100%"
                  @change="handleFilterChange"
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

            <!-- 整车/零部件名称选择（多选） -->
            <el-col :span="6">
              <el-form-item label="整车/零部件">
                <el-select
                  v-model="store.searchCriteria.part_names"
                  placeholder="请选择整车/零部件"
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
                    v-for="option in prioritizedPartNames"
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
                  placeholder="请选择检测状态"
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
                  placeholder="请选择开发阶段"
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
        <!-- 测试信息表格 -->
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>测试信息</span>
              <div class="column-selector">
                <el-dropdown trigger="click" :hide-on-click="false">
                  <el-button size="small" type="primary">
                    列选择<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item key="test_date" @click.stop>
                        <el-checkbox
                          :modelValue="visibleColumns.includes('test_date')"
                          @change="(value) => toggleColumn('test_date', value)"
                        >
                          检测时间
                        </el-checkbox>
                      </el-dropdown-item>
                      <el-dropdown-item key="status" @click.stop>
                        <el-checkbox
                          :modelValue="visibleColumns.includes('status')"
                          @change="(value) => toggleColumn('status', value)"
                        >
                          检测状态
                        </el-checkbox>
                      </el-dropdown-item>
                      <el-dropdown-item key="development_stage" @click.stop>
                        <el-checkbox
                          :modelValue="visibleColumns.includes('development_stage')"
                          @change="(value) => toggleColumn('development_stage', value)"
                        >
                          开发阶段
                        </el-checkbox>
                      </el-dropdown-item>
                      <el-dropdown-item key="test_order_no" @click.stop>
                        <el-checkbox
                          :modelValue="visibleColumns.includes('test_order_no')"
                          @change="(value) => toggleColumn('test_order_no', value)"
                        >
                          委托单号
                        </el-checkbox>
                      </el-dropdown-item>
                      <el-dropdown-item key="sample_no" @click.stop>
                        <el-checkbox
                          :modelValue="visibleColumns.includes('sample_no')"
                          @change="(value) => toggleColumn('sample_no', value)"
                        >
                          样品编号
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
            <!-- 必选列 -->
            <el-table-column prop="sample_info.project_name" label="项目名称" width="120" align="center" />
            <el-table-column prop="sample_info.part_name" label="整车/零部件名称" width="160" align="center" />
            
            <!-- 可选列 -->
            <el-table-column
              v-if="visibleColumns.includes('test_date')"
              prop="test_date"
              label="检测时间"
              width="150"
              align="center"
            >
              <template #default="scope">
                {{ formatDate(scope.row.test_date) }}
              </template>
            </el-table-column>
            <el-table-column
              v-if="visibleColumns.includes('status')"
              prop="sample_info.status"
              label="检测状态"
              width="100"
              align="center"
            />
            <el-table-column
              v-if="visibleColumns.includes('development_stage')"
              prop="sample_info.development_stage"
              label="开发阶段"
              width="120"
              align="center"
            />
            <el-table-column
              v-if="visibleColumns.includes('test_order_no')"
              prop="sample_info.test_order_no"
              label="委托单号"
              width="150"
              align="center"
            />
            <el-table-column
              v-if="visibleColumns.includes('sample_no')"
              prop="sample_info.sample_no"
              label="样品编号"
              width="150"
              align="center"
            />

            <!-- 指标列（Goi/Vi/Gvi 已删除，根据新表结构不再展示） -->

            <el-table-column label="详情" width="200" align="center">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  @click="showSampleImage(scope.row.sample_info?.sample_image_url)"
                >
                  样品图
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  @click="showSpectrum(scope.row.id)"
                  style="margin-left: 5px;"
                >
                  全谱
                </el-button>
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

        <!-- 全谱物质信息表 -->
        <el-card v-if="spectrumVisible" class="table-card" shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>全谱物质信息</span>
              <el-button size="small" @click="spectrumVisible = false">关闭</el-button>
            </div>
          </template>

          <el-table
            v-loading="store.detail_loading"
            :data="store.current_test_details"
            style="width: 100%"
            stripe
            :header-cell-style="{ backgroundColor: '#67C23A', color: '#ffffff', fontWeight: '600', fontSize: '14px' }"
          >
            <el-table-column label="物质名称" min-width="180" align="center">
              <template #default="scope">
                <el-button
                  type="text"
                  @click="showSubstanceDetail(scope.row.substance, scope.row.substance_info)"
                  style="color: #409EFF; font-weight: 600;"
                >
                  {{ scope.row.substance_name_cn }}
                </el-button>
              </template>
            </el-table-column>

            <el-table-column
              prop="substance_name_en"
              label="物质英文名"
              min-width="200"
              align="center"
            >
              <template #default="scope">
                {{ scope.row.substance_name_en || '-' }}
              </template>
            </el-table-column>

            <el-table-column
              prop="cas_no"
              label="CAS号"
              min-width="120"
              align="center"
            />

            <el-table-column
              prop="match_degree_formatted"
              label="匹配度"
              min-width="100"
              align="center"
            >
              <template #default="scope">
                {{ scope.row.match_degree_formatted || '-' }}
              </template>
            </el-table-column>

            <el-table-column
              prop="retention_time_formatted"
              label="保留时间(分钟)"
              min-width="140"
              align="center"
            >
              <template #default="scope">
                {{ scope.row.retention_time_formatted || '-' }}
              </template>
            </el-table-column>

            <el-table-column
              prop="concentration_ratio_formatted"
              label="浓度占比(%)"
              min-width="130"
              align="center"
            >
              <template #default="scope">
                {{ scope.row.concentration_ratio_formatted || '-' }}
              </template>
            </el-table-column>

            <el-table-column
              prop="concentration_formatted"
              label="浓度(μg/m³)"
              min-width="140"
              align="center"
            >
              <template #default="scope">
                {{ scope.row.concentration_formatted || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 样品图预览对话框 -->
      <el-dialog
        v-model="imageDialogVisible"
        title="样品图"
        width="60%"
        center
      >
        <div style="text-align: center;">
          <el-image
            :src="currentImageUrl"
            fit="contain"
            style="max-width: 100%; max-height: 70vh;"
          >
            <template #error>
              <div style="padding: 50px; color: #909399;">
                <el-icon :size="60"><Picture /></el-icon>
                <p>图片加载失败</p>
              </div>
            </template>
          </el-image>
        </div>
      </el-dialog>

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
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useSubstancesQueryStore } from '@/store/substancesQuery'
import { substancesApi } from '@/api/substances'
import { ElMessage } from 'element-plus'
import { ArrowDown, Picture } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 配置中文语言
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
const store = useSubstancesQueryStore()

// 将“整车”选项置顶显示
const prioritizedPartNames = computed(() => {
  const options = store.part_names || []
  const idx = options.findIndex(opt => opt?.label === '整车' || opt?.value === '整车')
  if (idx > -1) {
    return [options[idx], ...options.slice(0, idx), ...options.slice(idx + 1)]
  }
  return options
})

// 表格可见列管理 - 默认选择检测时间、检测状态、开发阶段
const visibleColumns = ref(['test_date', 'status', 'development_stage'])

// 样品图弹窗
const imageDialogVisible = ref(false)
const currentImageUrl = ref('')

// 全谱信息显示
const spectrumVisible = ref(false)

// 物质详情弹窗
const substanceDialogVisible = ref(false)
const currentSubstance = ref(null)

// 切换列显示
const toggleColumn = (column, visible) => {
  if (visible) {
    if (!visibleColumns.value.includes(column)) {
      visibleColumns.value.push(column)
    }
  } else {
    const index = visibleColumns.value.indexOf(column)
    if (index > -1) {
      visibleColumns.value.splice(index, 1)
    }
  }
}

// 显示样品图
const showSampleImage = (imageUrl) => {
  if (imageUrl) {
    currentImageUrl.value = imageUrl
    imageDialogVisible.value = true
  } else {
    ElMessage.warning('该样品暂无图片')
  }
}

// 显示全谱信息
const showSpectrum = async (testId) => {
  try {
    await store.fetchTestDetail(testId)
    spectrumVisible.value = true
  } catch (error) {
    console.error('获取全谱信息失败:', error)
    ElMessage.error('获取全谱信息失败')
  }
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

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 筛选条件变化
const handleFilterChange = () => {
  store.filterTestData()
}

// 重置筛选
const handleReset = () => {
  store.resetSearchCriteria()
  visibleColumns.value = ['test_date', 'status', 'development_stage']
}

// 分页
const handleSizeChange = (val) => {
  store.setPageSize(val)
}

const handlePageChange = (val) => {
  store.setPage(val)
}

// 生命周期
onMounted(async () => {
  try {
    await store.fetchVehicleModelOptions()
    await store.loadAllTestData()
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('页面初始化失败')
  }
})
</script>

<style scoped>
.substances-query {
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
