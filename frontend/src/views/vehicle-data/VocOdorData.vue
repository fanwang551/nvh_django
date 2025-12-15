<template>
  <el-config-provider :locale="locale">
    <div class="voc-query">
    <!-- 查询表单 -->
    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>VOC/气味数据查询</span>
        </div>
      </template>

      <el-form :model="store.searchCriteria" label-width="100px" class="search-form">
        <el-row :gutter="20">
          <!-- 项目名称选择（多选） -->
          <el-col :span="6">
            <el-form-item label="项目名称">
              <el-select
                v-model="store.searchCriteria.project_names"
                placeholder="请选择项目名称"
                multiple
                collapse-tags
                collapse-tags-tooltip
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
                @change="handlePartNamesChange"
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
      <!-- VOC检测结果表格 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>VOC检测结果</span>
            <div class="column-selector">
              <el-button size="small" type="success" @click="showFilteredChart" style="margin-right: 10px;">
                图表
              </el-button>
              <el-dropdown trigger="click" :hide-on-click="false">
                <el-button size="small" type="primary">
                  列选择<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item key="commission_number" @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes('commission_number')"
                        @change="(value) => toggleVocColumn('commission_number', value)"
                      >
                        委托单号
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="test_date" @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes('test_date')"
                        @change="(value) => toggleVocColumn('test_date', value)"
                      >
                        检测时间
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="development_stage" @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes('development_stage')"
                        @change="(value) => toggleVocColumn('development_stage', value)"
                      >
                        开发阶段
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="status" @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes('status')"
                        @change="(value) => toggleVocColumn('status', value)"
                      >
                        检测状态
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="sample_number" @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes('sample_number')"
                        @change="(value) => toggleVocColumn('sample_number', value)"
                      >
                        样品编号
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item v-for="compound in store.chart_config.compound_options"
                                     :key="compound.value"
                                     @click.stop>
                      <el-checkbox
                        :modelValue="vocVisibleColumns.includes(compound.value)"
                        @change="(value) => toggleVocColumn(compound.value, value)"
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
          <!-- 必选列 -->
          <el-table-column prop="sample_info.project_name" label="项目名称" width="120" align="center" />
          <el-table-column prop="sample_info.part_name" label="整车/零部件名称" width="160" align="center" />
          
          <!-- 可选列 -->
          <el-table-column
            v-if="vocVisibleColumns.includes('commission_number')"
            prop="sample_info.test_order_no"
            label="委托单号"
            width="150"
            align="center"
          />
          <el-table-column
            v-if="vocVisibleColumns.includes('test_date')"
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
            v-if="vocVisibleColumns.includes('development_stage')"
            prop="sample_info.development_stage"
            label="开发阶段"
            width="120"
            align="center"
          />
          <el-table-column
            v-if="vocVisibleColumns.includes('status')"
            prop="sample_info.status"
            label="检测状态"
            width="100"
            align="center"
          />
          <el-table-column
            v-if="vocVisibleColumns.includes('sample_number')"
            prop="sample_info.sample_no"
            label="样品编号"
            width="150"
            align="center"
          />

          <!-- VOC物质列 -->
          <el-table-column
            v-if="vocVisibleColumns.includes('benzene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>苯<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.benzene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('toluene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>甲苯<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.toluene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('ethylbenzene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>乙苯<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.ethylbenzene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('xylene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>二甲苯<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.xylene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('styrene')"
            width="90"
            align="center"
          >
            <template #header>
              <div>苯乙烯<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.styrene_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('formaldehyde')"
            width="90"
            align="center"
          >
            <template #header>
              <div>甲醛<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.formaldehyde_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('acetaldehyde')"
            width="90"
            align="center"
          >
            <template #header>
              <div>乙醛<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.acetaldehyde_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('acrolein')"
            width="90"
            align="center"
          >
            <template #header>
              <div>丙烯醛<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.acrolein_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('acetone')"
            width="90"
            align="center"
          >
            <template #header>
              <div>丙酮<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.acetone_formatted }}
            </template>
          </el-table-column>

          <el-table-column
            v-if="vocVisibleColumns.includes('tvoc')"
            width="90"
            align="center"
          >
            <template #header>
              <div>TVOC<br/>({{ vocUnit }})</div>
            </template>
            <template #default="scope">
              {{ scope.row.tvoc_formatted }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="showSampleImage(scope.row.sample_info?.sample_image_url)"
              >
                样品图
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

      <!-- 气味检测结果表格 -->
      <el-card v-if="store.hasOdorResults || store.query_loading" class="table-card" shadow="never" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>气味检测结果</span>
            <div class="column-selector">
              <el-button size="small" type="success" @click="showFilteredOdorChart" style="margin-right: 10px;">
                图表
              </el-button>
              <el-dropdown trigger="click" :hide-on-click="false">
                <el-button size="small" type="primary">
                  列选择<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item key="test_date" @click.stop>
                      <el-checkbox
                        :modelValue="odorVisibleColumns.includes('test_date')"
                        @change="(value) => toggleOdorColumn('test_date', value)"
                      >
                        检测时间
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="commission_number" @click.stop>
                      <el-checkbox
                        :modelValue="odorVisibleColumns.includes('commission_number')"
                        @change="(value) => toggleOdorColumn('commission_number', value)"
                      >
                        委托单号
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="development_stage" @click.stop>
                      <el-checkbox
                        :modelValue="odorVisibleColumns.includes('development_stage')"
                        @change="(value) => toggleOdorColumn('development_stage', value)"
                      >
                        开发阶段
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="status" @click.stop>
                      <el-checkbox
                        :modelValue="odorVisibleColumns.includes('status')"
                        @change="(value) => toggleOdorColumn('status', value)"
                      >
                        检测状态
                      </el-checkbox>
                    </el-dropdown-item>
                    <el-dropdown-item key="part_name" @click.stop>
                      <el-checkbox
                        :modelValue="odorVisibleColumns.includes('part_name')"
                        @change="(value) => toggleOdorColumn('part_name', value)"
                      >
                        整车/零部件名称
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
          :data="store.paginatedOdorData"
          style="width: 100%"
          stripe
          :header-cell-style="{ backgroundColor: '#67C23A', color: '#ffffff', fontWeight: '600', fontSize: '14px' }"
        >
          <!-- 必选列 -->
          <el-table-column prop="sample_info.project_name" label="项目名称" width="120" align="center" />
          
          <!-- 可选列 -->
          <el-table-column
            v-if="odorVisibleColumns.includes('test_date')"
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
            v-if="odorVisibleColumns.includes('commission_number')"
            prop="sample_info.test_order_no"
            label="委托单号"
            width="150"
            align="center"
          />
          <el-table-column
            v-if="odorVisibleColumns.includes('development_stage')"
            prop="sample_info.development_stage"
            label="开发阶段"
            width="120"
            align="center"
          />
          <el-table-column
            v-if="odorVisibleColumns.includes('status')"
            prop="sample_info.status"
            label="检测状态"
            width="100"
            align="center"
          />
          <el-table-column
            v-if="odorVisibleColumns.includes('part_name')"
            prop="sample_info.part_name"
            label="整车/零部件名称"
            width="160"
            align="center"
          />

          <!-- 气味数据列（必选） -->
          <el-table-column
            prop="static_front_formatted"
            label="静态-前排"
            width="110"
            align="center"
          >
            <template #default="scope">
              {{ scope.row.static_front_formatted || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="static_rear_formatted"
            label="静态-后排"
            width="110"
            align="center"
          >
            <template #default="scope">
              {{ scope.row.static_rear_formatted || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="dynamic_front_formatted"
            label="动态-前排"
            width="110"
            align="center"
          >
            <template #default="scope">
              {{ scope.row.dynamic_front_formatted || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="dynamic_rear_formatted"
            label="动态-后排"
            width="110"
            align="center"
          >
            <template #default="scope">
              {{ scope.row.dynamic_rear_formatted || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="odor_mean_formatted"
            label="气味均值"
            width="110"
            align="center"
          >
            <template #default="scope">
              {{ scope.row.odor_mean_formatted || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button
                type="success"
                size="small"
                @click="showSampleImage(scope.row.sample_info?.sample_image_url)"
              >
                样品图
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 气味表格分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="store.odor_pagination.current_page"
            v-model:page-size="store.odor_pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="store.odor_pagination.total_count"
            @size-change="handleOdorSizeChange"
            @current-change="handleOdorPageChange"
          />
        </div>
      </el-card>

      <!-- VOC图表展示 -->
      <el-card v-if="chartVisible" class="table-card" shadow="never" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>VOC数据图表分析</span>
            <el-button size="small" @click="chartVisible = false">关闭图表</el-button>
          </div>
        </template>
        <div v-loading="chartLoading" style="min-height: 400px;">
          <div v-if="chartData" style="padding: 10px;">
            <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
          </div>
        </div>
      </el-card>

      <!-- 气味图表展示 -->
      <el-card v-if="odorChartVisible" class="table-card" shadow="never" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>气味数据图表分析</span>
            <el-button size="small" @click="odorChartVisible = false">关闭图表</el-button>
          </div>
        </template>
        <div v-loading="odorChartLoading" style="min-height: 400px;">
          <div v-if="odorChartData" style="padding: 10px;">
            <div ref="odorChartContainer" style="width: 100%; height: 500px;"></div>
          </div>
        </div>
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

    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useVocQueryStore } from '@/store/vocQuery'
import { vocApi } from '@/api/voc'
import { ElMessage } from 'element-plus'
import { ArrowDown, Picture } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as echarts from 'echarts'

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

// 将“整车”选项置顶显示
const prioritizedPartNames = computed(() => {
  const options = store.part_names || []
  const idx = options.findIndex(opt => opt?.label === '整车' || opt?.value === '整车')
  if (idx > -1) {
    return [options[idx], ...options.slice(0, idx), ...options.slice(idx + 1)]
  }
  return options
})

// 根据当前筛选/结果动态确定VOC单位
const vocUnit = computed(() => {
  if (store.filtered_voc_data && store.filtered_voc_data.length > 0) {
    const partNames = Array.from(new Set(
      store.filtered_voc_data
        .map(item => item.sample_info?.part_name)
        .filter(Boolean)
    ))
    const hasWholeVehicle = partNames.includes('整车')
    const hasOtherParts = partNames.some(name => name !== '整车')
    if (hasWholeVehicle && !hasOtherParts) {
      return 'mg/m³'
    }
    return 'μg/m³'
  }

  const selectedParts = store.searchCriteria?.part_names || []
  if (selectedParts.length === 1 && selectedParts[0] === '整车') {
    return 'mg/m³'
  }
  return 'μg/m³'
})

// VOC表格可见列管理 - 默认选择所有物质和委托单号
const vocVisibleColumns = ref(['commission_number', 'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc', 'status','development_stage'])

// 气味表格可见列管理 - 默认选择检测时间、零部件、开发阶段
const odorVisibleColumns = ref(['test_date', 'part_name', 'development_stage', 'commission_number', 'status'])

// 样品图弹窗
const imageDialogVisible = ref(false)
const currentImageUrl = ref('')

// 记录零部件多选前一次值，用于判断“整车/非整车”切换行为
const previousPartNames = ref([...store.searchCriteria.part_names])

// VOC图表相关
const chartVisible = ref(false)
const chartLoading = ref(false)
const chartData = ref(null)
const chartContainer = ref(null)
let chartInstance = null

// 气味图表相关
const odorChartVisible = ref(false)
const odorChartLoading = ref(false)
const odorChartData = ref(null)
const odorChartContainer = ref(null)
let odorChartInstance = null

// 切换VOC列显示
const toggleVocColumn = (compound, visible) => {
  if (visible) {
    if (!vocVisibleColumns.value.includes(compound)) {
      vocVisibleColumns.value.push(compound)
    }
  } else {
    const index = vocVisibleColumns.value.indexOf(compound)
    if (index > -1) {
      vocVisibleColumns.value.splice(index, 1)
    }
  }
}

// 切换气味列显示
const toggleOdorColumn = (column, visible) => {
  if (visible) {
    if (!odorVisibleColumns.value.includes(column)) {
      odorVisibleColumns.value.push(column)
    }
  } else {
    const index = odorVisibleColumns.value.indexOf(column)
    if (index > -1) {
      odorVisibleColumns.value.splice(index, 1)
    }
  }
}

// 零部件多选变更：确保“整车”与其他零部件互斥
const handlePartNamesChange = (value) => {
  const newValue = Array.isArray(value) ? [...value] : []
  const prev = previousPartNames.value || []

  const hadWholeBefore = prev.includes('整车')
  const hadOtherBefore = prev.some(name => name !== '整车')

  const hasWholeNow = newValue.includes('整车')
  const hasOtherNow = newValue.some(name => name !== '整车')

  let resolved = newValue

  if (hasWholeNow && hasOtherNow) {
    if (!hadWholeBefore && hasWholeNow) {
      // 之前没有“整车”，本次新增“整车”：只保留“整车”
      resolved = ['整车']
    } else if (!hadOtherBefore && hasOtherNow) {
      // 之前只有“整车”，本次新增其他零部件：排除“整车”
      resolved = newValue.filter(name => name !== '整车')
    } else {
      // 不确定来源时，优先排除“整车”，与“选择非整车时排除整车”保持一致
      resolved = newValue.filter(name => name !== '整车')
    }
  }

  store.searchCriteria.part_names = resolved
  previousPartNames.value = [...resolved]
  handleFilterChange()
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

// 显示VOC图表（单行，保留旧逻辑）
const showChart = async (resultId) => {
  try {
    chartLoading.value = true
    chartVisible.value = true
    
    const response = await vocApi.getRowChartData({ result_id: resultId })
    chartData.value = response.data
    
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('获取图表数据失败:', error)
    ElMessage.error('获取图表数据失败')
    chartVisible.value = false
  } finally {
    chartLoading.value = false
  }
}

// 显示基于筛选条件的VOC图表
const showFilteredChart = async () => {
  try {
    // 检查是否有筛选结果
    if (store.filtered_voc_data.length === 0) {
      ElMessage.warning('当前筛选结果为空，无法生成图表')
      return
    }

    // 限制10条数据
    const dataToChart = store.filtered_voc_data.slice(0, 10)

    // 零部件分类校验：检查是否全部为"整车"或全部不为"整车"
    const partNames = [...new Set(dataToChart.map(item => item.sample_info?.part_name))]
    const hasWholeVehicle = partNames.includes('整车')
    const hasOtherParts = partNames.some(name => name !== '整车')

    if (hasWholeVehicle && hasOtherParts) {
      ElMessage.error('筛选结果中零部件分类不统一（整车和零件混合），无法生成图表')
      return
    }

    chartLoading.value = true
    chartVisible.value = true
    
    const response = await vocApi.getFilteredVocChartData({
      filters: store.searchCriteria,
      limit: 10
    })
    chartData.value = response.data
    
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('获取图表数据失败:', error)
    ElMessage.error('获取图表数据失败')
    chartVisible.value = false
  } finally {
    chartLoading.value = false
  }
}

// 显示气味图表（单行，保留旧逻辑）
const showOdorChart = async (resultId) => {
  try {
    odorChartLoading.value = true
    odorChartVisible.value = true
    
    const response = await vocApi.getOdorRowChartData({ result_id: resultId })
    odorChartData.value = response.data
    
    await nextTick()
    renderOdorChart()
  } catch (error) {
    console.error('获取气味图表数据失败:', error)
    ElMessage.error('获取气味图表数据失败')
    odorChartVisible.value = false
  } finally {
    odorChartLoading.value = false
  }
}

// 显示基于筛选条件的气味图表
const showFilteredOdorChart = async () => {
  try {
    // 检查是否有筛选结果
    if (store.filtered_odor_data.length === 0) {
      ElMessage.warning('当前筛选结果为空或无气味数据，无法生成图表')
      return
    }

    // 限制10条数据
    const dataToChart = store.filtered_odor_data.slice(0, 10)

    // 零部件分类校验：检查是否全部为"整车"或全部不为"整车"
    const partNames = [...new Set(dataToChart.map(item => item.sample_info?.part_name))]
    const hasWholeVehicle = partNames.includes('整车')
    const hasOtherParts = partNames.some(name => name !== '整车')

    if (hasWholeVehicle && hasOtherParts) {
      ElMessage.error('筛选结果中零部件分类不统一（整车和零件混合），无法生成图表')
      return
    }

    odorChartLoading.value = true
    odorChartVisible.value = true
    
    const response = await vocApi.getFilteredOdorChartData({
      filters: store.searchCriteria,
      limit: 10
    })
    odorChartData.value = response.data
    
    await nextTick()
    renderOdorChart()
  } catch (error) {
    console.error('获取气味图表数据失败:', error)
    ElMessage.error('获取气味图表数据失败')
    odorChartVisible.value = false
  } finally {
    odorChartLoading.value = false
  }
}

// 渲染VOC图表
const renderChart = () => {
  if (!chartContainer.value || !chartData.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartContainer.value)
  
  // 智能命名：检查是否需要隐藏相同字段
  const processedSeries = chartData.value.series.map(s => {
    const parts = s.raw_data || {}
    return {
      ...s,
      vehicleModel: parts.vehicle_model,
      sampleNo: parts.sample_no,
      status: parts.status,
      stage: parts.stage
    }
  })

  // 检测哪些字段完全相同
  const uniqueVehicles = new Set(processedSeries.map(s => s.vehicleModel))
  const uniqueSampleNos = new Set(processedSeries.map(s => s.sampleNo))
  const uniqueStatuses = new Set(processedSeries.map(s => s.status))
  const uniqueStages = new Set(processedSeries.map(s => s.stage))

  // 根据是否全部相同，动态生成系列名称（格式：车型-样品编号-检测状态-开发阶段）
  const newSeriesNames = processedSeries.map(s => {
    const parts = []
    if (uniqueVehicles.size > 1 && s.vehicleModel) parts.push(s.vehicleModel)
    if (uniqueSampleNos.size > 1 && s.sampleNo) parts.push(s.sampleNo)
    if (uniqueStatuses.size > 1 && s.status) parts.push(s.status)
    if (uniqueStages.size > 1 && s.stage) parts.push(s.stage)
    return parts.length > 0 ? parts.join('-') : (s.sampleNo || s.name || '未知')
  })

  // 检查是否全部为整车（用于单位显示）
  const isAllWholeVehicle = chartData.value.scenario === 'whole_vehicle' || 
    (chartData.value.series.length > 0 && chartData.value.series.every(s => s.part_name === '整车'))
  
  // 单位（整车：mg/m³；零部件：μg/m³），数值不再进行前端单位换算
  const unit = isAllWholeVehicle ? 'mg/m³' : 'μg/m³'

  const option = {
    title: {
      text: 'VOC物质浓度对比分析',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(item => {
          result += item.marker + ' ' + item.seriesName + ': ' + item.value + ' ' + unit + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: newSeriesNames,
      top: 40,
      type: 'scroll',
      selected: newSeriesNames.reduce((acc, name) => {
        acc[name] = true
        return acc
      }, {})
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      top: 100,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.value.xAxis,
      axisLabel: {
        interval: 0,
        rotate: 0,
        fontSize: 12
      },
      name: '物质名称',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: 'value',
      name: '浓度 (' + unit + ')',
      nameTextStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    series: chartData.value.series.map((s, idx) => ({
      name: newSeriesNames[idx],
      type: 'bar',
      data: s.data.map(v => Number(v).toFixed(3)),
      label: {
        show: true,
        position: 'top',
        formatter: '{c}',
        fontSize: 10
      },
      barMaxWidth: 50
    }))
  }
  
  chartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize()
  })
}

// 渲染气味图表
const renderOdorChart = () => {
  if (!odorChartContainer.value || !odorChartData.value) return
  
  if (odorChartInstance) {
    odorChartInstance.dispose()
  }
  
  odorChartInstance = echarts.init(odorChartContainer.value)
  
  // 智能命名：检查是否需要隐藏相同字段
  const processedSeries = odorChartData.value.series.map(s => {
    const parts = s.raw_data || {}
    return {
      ...s,
      vehicleModel: parts.vehicle_model,
      sampleNo: parts.sample_no,
      status: parts.status,
      stage: parts.stage
    }
  })

  // 检测哪些字段完全相同
  const uniqueVehicles = new Set(processedSeries.map(s => s.vehicleModel))
  const uniqueSampleNos = new Set(processedSeries.map(s => s.sampleNo))
  const uniqueStatuses = new Set(processedSeries.map(s => s.status))
  const uniqueStages = new Set(processedSeries.map(s => s.stage))

  // 根据是否全部相同，动态生成系列名称（格式：车型-样品编号-检测状态-开发阶段）
  const newSeriesNames = processedSeries.map(s => {
    const parts = []
    if (uniqueVehicles.size > 1 && s.vehicleModel) parts.push(s.vehicleModel)
    if (uniqueSampleNos.size > 1 && s.sampleNo) parts.push(s.sampleNo)
    if (uniqueStatuses.size > 1 && s.status) parts.push(s.status)
    if (uniqueStages.size > 1 && s.stage) parts.push(s.stage)
    return parts.length > 0 ? parts.join('-') : (s.sampleNo || s.name || '未知')
  })
  
  const option = {
    title: {
      text: '气味数据对比分析',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(item => {
          result += item.marker + ' ' + item.seriesName + ': ' + item.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: newSeriesNames,
      top: 40,
      type: 'scroll',
      selected: newSeriesNames.reduce((acc, name) => {
        acc[name] = true
        return acc
      }, {})
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      top: 100,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: odorChartData.value.xAxis,
      axisLabel: {
        interval: 0,
        rotate: 0,
        fontSize: 12
      },
      name: '位置',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: 'value',
      name: '气味',
      nameTextStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    series: odorChartData.value.series.map((s, idx) => ({
      name: newSeriesNames[idx],
      type: 'bar',
      data: s.data,
      label: {
        show: true,
        position: 'top',
        formatter: '{c}',
        fontSize: 10
      },
      barMaxWidth: 50
    }))
  }
  
  odorChartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    odorChartInstance && odorChartInstance.resize()
  })
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const handleFilterChange = () => {
  store.filterVocData()
}

const handleReset = () => {
  store.resetSearchCriteria()
  vocVisibleColumns.value = ['commission_number', 'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc']
  odorVisibleColumns.value = ['test_date', 'part_name', 'development_stage']
  previousPartNames.value = [...store.searchCriteria.part_names]
}

// VOC表格分页
const handleSizeChange = (val) => {
  store.setPageSize(val)
}

const handlePageChange = (val) => {
  store.setPage(val)
}

// 气味表格分页
const handleOdorSizeChange = (val) => {
  store.setOdorPageSize(val)
}

const handleOdorPageChange = (val) => {
  store.setOdorPage(val)
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
