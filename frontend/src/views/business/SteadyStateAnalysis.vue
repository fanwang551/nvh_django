<template>
  <div class="steady-state-analysis">
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form label-width="100px" class="search-form">
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="车型">
              <el-select
                v-model="filters.vehicleModelIds"
                placeholder="请选择车型"
                multiple
                clearable
                collapse-tags
                collapse-tags-tooltip
                @change="onVehicleChange"
                style="width: 100%"
              >
                <el-option
                  class="vehicle-model-search-option"
                  :value="null"
                >
                  <div class="vehicle-model-search-input" @mousedown.stop>
                    <el-input
                      v-model="vehicleModelSearch"
                      placeholder="搜索车型..."
                      clearable
                      @click.stop
                      @keydown.stop
                    >
                      <template #prefix>
                        <el-icon><Search /></el-icon>
                      </template>
                    </el-input>
                  </div>
                </el-option>
                <el-option
                  v-for="item in filteredVehicleModels"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
                <el-option
                  v-if="!filteredVehicleModels.length"
                  :value="null"
                  disabled
                >
                  <span class="vehicle-model-empty">暂无匹配车型</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="工况">
              <el-select
                v-model="filters.workConditions"
                placeholder="请选择工况"
                multiple
                clearable
                collapse-tags
                collapse-tags-tooltip
                :disabled="!filters.vehicleModelIds.length"
                @change="onWorkConditionChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in workConditionOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="测点">
              <el-select
                v-model="filters.measurePoints"
                placeholder="请选择测点"
                multiple
                clearable
                collapse-tags
                collapse-tags-tooltip
                :disabled="!filters.workConditions.length"
                style="width: 100%"
              >
                <el-option
                  v-for="item in measurePointOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <span>{{ item.label }}</span>
                  <span v-if="item.measureType" class="option-tag">{{ MEASURE_TYPE_LABELS[item.measureType] }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <div class="form-actions">
              <el-button type="primary" @click="handleQuery" :loading="isLoading">查询</el-button>
              <el-button :disabled="isLoading" @click="handleReset">重置</el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>
      <el-alert
        v-if="error"
        class="error-alert"
        type="error"
        :closable="false"
        :description="error"
        show-icon
      />
    </el-card>

    <div class="charts-wrapper">
      <el-skeleton v-if="isLoading && !hasCharts" animated :rows="6" />
      <el-empty v-else-if="!hasCharts" description="请选择条件后进行查询" />
      <div v-else class="charts-grid">
        <el-card
          v-for="chart in charts"
          :key="chart.chartKey"
          class="chart-card"
          shadow="never"
        >
          <template #header>
            <div class="card-header">
              <div class="card-header-left">
                <span class="card-title">{{ chart.title }}</span>
                <span class="card-subtitle">单位：{{ chart.unit || '--' }}</span>
              </div>
            </div>
          </template>
          <div class="chart-body">
            <div
              v-show="chart.series?.length"
              class="echarts-container"
              :ref="(el) => registerChartRef(el, chart.chartKey)"
            />
            <el-empty v-show="!chart.series?.length" description="暂无数据" />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onMounted, onBeforeUnmount, nextTick, ref } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { Search } from '@element-plus/icons-vue'

import { useSteadyStateAnalysisStore } from '@/store/steadyStateAnalysis'

const MEASURE_TYPE_LABELS = {
  noise: '噪声',
  vibration: '振动',
  speed: '转速'
}

echarts.use([LineChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const store = useSteadyStateAnalysisStore()
const {
  filters,
  vehicleModels,
  workConditionOptions,
  measurePointOptions,
  charts,
  isLoading,
  error
} = storeToRefs(store)

const vehicleModelSearch = ref('')
const filteredVehicleModels = computed(() => {
  const keyword = vehicleModelSearch.value.trim().toLowerCase()
  const list = vehicleModels.value || []
  if (!keyword) return list
  return list.filter((item) => {
    const name = (item?.vehicle_model_name ?? '').toString().toLowerCase()
    return name.includes(keyword)
  })
})

const hasCharts = computed(() => charts.value.length > 0)
const containerMap = new Map()
const chartInstances = new Map()

const scheduleRender = (chartKey) => {
  nextTick(() => {
    const el = containerMap.get(chartKey)
    if (!el) return

    // 等待容器拿到实际尺寸后再初始化，避免 clientWidth/clientHeight 为 0
    if (!el.clientWidth || !el.clientHeight) {
      requestAnimationFrame(() => scheduleRender(chartKey))
      return
    }

    let instance = chartInstances.get(chartKey)
    if (!instance) {
      instance = echarts.init(el)
      chartInstances.set(chartKey, instance)
    }

    renderChart(chartKey)
    instance.resize()
  })
}

const registerChartRef = (el, key) => {
  if (!key) return
  if (!el) {
    const instance = chartInstances.get(key)
    if (instance) {
      instance.dispose()
      chartInstances.delete(key)
    }
    containerMap.delete(key)
    return
  }
  containerMap.set(key, el)
  scheduleRender(key)
}

const cleanupOrphanCharts = () => {
  const validKeys = new Set(charts.value.map((chart) => chart.chartKey))
  Array.from(chartInstances.keys()).forEach((key) => {
    if (!validKeys.has(key)) {
      chartInstances.get(key)?.dispose()
      chartInstances.delete(key)
      containerMap.delete(key)
    }
  })
}

const renderChart = (chartKey) => {
  const chartData = charts.value.find((item) => item.chartKey === chartKey)
  const instance = chartInstances.get(chartKey)
  if (!chartData || !instance) return
  const xAxisData = chartData.workConditions || []
  const series = (chartData.series || []).map((seriesItem) => ({
    name: seriesItem.name,
    type: 'line',
    symbol: 'circle',
    symbolSize: 6,
    connectNulls: false,
    data: (seriesItem.values || []).map((item) =>
      item === null || item === undefined ? null : Number(item)
    )
  }))
  instance.setOption({
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value) => (value == null ? '--' : value.toFixed ? value.toFixed(2) : value)
    },
    legend: { type: 'scroll', top: 0 },
    grid: { left: 50, right: 24, top: 70, bottom: 70 },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: { interval: 0, rotate: xAxisData.length > 6 ? 30 : 0 }
    },
    yAxis: { type: 'value', name: chartData.unit || '' },
    series
  })
}

watch(
  charts,
  async () => {
    cleanupOrphanCharts()
    await nextTick()
    charts.value.forEach((chart) => scheduleRender(chart.chartKey))
  },
  { deep: true }
)

const resize = () => {
  chartInstances.forEach((instance) => instance.resize())
}

const onVehicleChange = async () => {
  await store.fetchWorkConditions()
}

const onWorkConditionChange = async () => {
  await store.fetchMeasurePoints()
}

const handleQuery = async () => {
  try {
    await store.query()
  } catch (err) {
    // 错误信息通过状态提示给用户，这里无需额外处理
  }
}

const handleReset = () => {
  store.resetFilters()
}

onMounted(async () => {
  await store.initialize()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chartInstances.forEach((instance) => instance.dispose())
  chartInstances.clear()
  containerMap.clear()
})
</script>

<style scoped>
.steady-state-analysis {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-header-left {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
}
.card-subtitle {
  font-size: 12px;
  color: #909399;
}
.search-form {
  padding-top: 8px;
}
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 0;
}
.charts-wrapper {
  min-height: 300px;
}
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  gap: 16px;
}
.chart-body {
  width: 100%;
  min-height: 360px;
}
.echarts-container {
  width: 100%;
  height: 360px;
}
.error-alert {
  margin-top: 12px;
}
.option-tag {
  margin-left: 4px;
  font-size: 12px;
  color: #909399;
}
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  }
}

.vehicle-model-search-option {
  padding: 0;
  cursor: default;
}
.vehicle-model-search-input {
  width: 100%;
}
.vehicle-model-search-input .el-input,
.vehicle-model-search-input .el-input__wrapper {
  width: 100%;
  box-sizing: border-box;
}
.vehicle-model-search-input .el-input__wrapper {
  min-height: var(--el-select-option-height, 34px);
  padding: 0 12px;
  box-shadow: none;
  border-radius: 0;
}
.vehicle-model-empty {
  display: block;
  padding: 4px 12px;
  font-size: 12px;
  color: #909399;
}
</style>
