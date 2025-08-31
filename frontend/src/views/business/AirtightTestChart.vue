<template>
  <div class="airtight-test-chart">
    <!-- 搜索卡片 -->
    <el-card class="search-card" shadow="never">
      <div class="search-form">
        <div class="form-row">
          <div class="form-group">
            <span class="form-label">车型：</span>
            <el-select
              v-model="store.searchForm.vehicleModelId"
              placeholder="请选择车型"
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
          <div class="form-group">
            <span class="form-label">测试类型：</span>
            <el-select
              v-model="store.searchForm.testType"
              placeholder="请选择测试类型"
              clearable
              class="form-select"
              @change="handleTestTypeChange"
            >
              <el-option
                v-for="item in testTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </div>
          <div class="form-group">
            <span class="form-label">测试日期：</span>
            <el-date-picker
              v-model="store.searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="form-date-picker"
              @change="handleDateRangeChange"
            />
          </div>
          <div class="form-actions">
            <el-button
              type="primary"
              :icon="Search"
              @click="handleSearch"
              :loading="queryLoading"
              :disabled="!canQuery"
            >
              查询
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 图表展示卡片 -->
    <el-card class="result-card" shadow="never" v-if="hasResults">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>气密性测试图表</span>
        </div>
      </template>

      <!-- 图表容器 -->
      <div class="chart-container">
        <div ref="chartRef" class="chart" style="width: 100%; height: 400px;"></div>
      </div>

      <!-- 数据表格 -->
      <div class="table-container" v-if="chartDataList.length > 0">
        <el-table :data="chartDataList" stripe>
          <el-table-column prop="vehicle_model_name" label="车型" width="150" />
          <el-table-column prop="test_type" label="测试类型" width="120" />
          <el-table-column prop="test_date" label="测试日期" width="120" />
          <el-table-column prop="test_value" label="测试值" width="100" />
          <el-table-column prop="test_unit" label="单位" width="80" />
          <el-table-column prop="remarks" label="备注" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="handleViewDetails(row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="store.pagination.currentPage"
            v-model:page-size="store.pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="store.pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-card class="result-card" shadow="never" v-else-if="!queryLoading">
      <el-empty description="暂无气密性测试数据" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="store.imageDialogVisible"
      title="测试详情"
      width="60%"
      :before-close="handleCloseDialog"
    >
      <div v-if="store.currentImageData" class="dialog-content">
        <div class="detail-info">
          <p><strong>车型：</strong>{{ store.currentImageData.vehicle_model_name }}</p>
          <p><strong>测试类型：</strong>{{ store.currentImageData.test_type }}</p>
          <p><strong>测试日期：</strong>{{ store.currentImageData.test_date }}</p>
          <p><strong>测试值：</strong>{{ store.currentImageData.test_value }} {{ store.currentImageData.test_unit }}</p>
          <p><strong>备注：</strong>{{ store.currentImageData.remarks || '无' }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>
<script setup>
import { computed, ref, onMounted, onActivated, onDeactivated, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, TrendCharts } from '@element-plus/icons-vue'
import { useAirtightTestChartStore } from '@/store/airtightTestChart'
import * as echarts from 'echarts'

// 组件名称，用于keep-alive缓存
defineOptions({
  name: 'AirtightTestChart'
})

// 使用 Pinia store
const store = useAirtightTestChartStore()

// 图表引用
const chartRef = ref(null)

// 计算属性
const vehicleModelOptions = computed(() => store.vehicleModelOptions)
const vehicleModelsLoading = computed(() => store.vehicleModelsLoading)
const queryLoading = computed(() => store.queryLoading)
const chartDataList = computed(() => store.chartDataList)
const testTypeOptions = computed(() => store.testTypeOptions)
const hasResults = computed(() => store.hasResults)
const canQuery = computed(() => store.canQuery)

// 事件处理
const handleVehicleModelChange = () => {
  // 车型变化时可以自动查询或清空结果
}

const handleTestTypeChange = () => {
  // 测试类型变化时的处理
}

const handleDateRangeChange = () => {
  // 日期范围变化时的处理
}

const handleSearch = async () => {
  if (!store.canQuery) {
    ElMessage.warning('请选择车型和测试类型')
    return
  }

  try {
    await store.queryChartData()
    if (store.chartDataList.length > 0) {
      ElMessage.success('查询成功')
      // 等待DOM更新后渲染图表
      await nextTick()
      renderChart()
    } else {
      ElMessage.warning('未找到匹配的数据')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  }
}

const handleReset = () => {
  store.resetState()
  // 清空图表
  if (store.chartInstance) {
    store.chartInstance.dispose()
    store.setChartInstance(null)
  }
}

const handleViewDetails = (row) => {
  store.showImageDialog(row)
}

const handleCloseDialog = () => {
  store.closeImageDialog()
}

const handleSizeChange = (pageSize) => {
  store.changePageSize(pageSize)
}

const handleCurrentChange = (page) => {
  store.changePage(page)
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !store.chartDataList.length) return

  // 销毁现有图表实例
  if (store.chartInstance) {
    store.chartInstance.dispose()
  }

  // 创建新的图表实例
  const chartInstance = echarts.init(chartRef.value)
  store.setChartInstance(chartInstance)

  // 准备图表数据
  const xAxisData = store.chartDataList.map(item => item.test_date)
  const seriesData = store.chartDataList.map(item => parseFloat(item.test_value) || 0)

  const option = {
    title: {
      text: '气密性测试数据趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        const item = store.chartDataList[data.dataIndex]
        return `
          <div>
            <p><strong>日期：</strong>${item.test_date}</p>
            <p><strong>车型：</strong>${item.vehicle_model_name}</p>
            <p><strong>测试值：</strong>${item.test_value} ${item.test_unit}</p>
            <p><strong>备注：</strong>${item.remarks || '无'}</p>
          </div>
        `
      }
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: store.chartDataList[0]?.test_unit || ''
    },
    series: [{
      name: '测试值',
      type: 'line',
      data: seriesData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2
      },
      itemStyle: {
        color: '#409EFF'
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    }
  }

  chartInstance.setOption(option)

  // 响应式处理
  window.addEventListener('resize', () => {
    chartInstance.resize()
  })
}

// 生命周期
onMounted(async () => {
  // 初始化页面数据
  await store.initializePageData()
})

// 标签页激活时
onActivated(async () => {
  // 如果车型列表为空，重新加载
  if (store.vehicleModelOptions.length === 0) {
    await store.initializePageData()
  }

  // 如果有图表实例且有数据，重新渲染图表
  if (store.chartDataList.length > 0) {
    await nextTick()
    renderChart()
  }
})

// 标签页失活时保存状态
onDeactivated(() => {
  // 状态会自动保存在store中
})
</script>
<style scoped>
.airtight-test-chart {
  padding: 0;
  background-color: #f5f7fa;
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
  min-width: 200px;
}

.form-label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.form-select {
  flex: 1;
  max-width: 200px;
}

.form-date-picker {
  flex: 1;
  max-width: 300px;
}

.form-actions {
  display: flex;
  gap: 8px;
}

/* 图表容器 */
.chart-container {
  margin-bottom: 24px;
}

.chart {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

/* 表格容器 */
.table-container {
  margin-top: 16px;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* 弹窗内容 */
.dialog-content {
  padding: 16px 0;
}

.detail-info p {
  margin: 8px 0;
  line-height: 1.6;
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

  .form-select,
  .form-date-picker {
    max-width: none;
  }
}
</style>
