<template>
  <div class="nvh-benchmark">
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">筛选条件</span>
          <span class="card-subtitle">已选择 {{ selectedVehicleCount }} 台车型</span>
        </div>
      </template>
      <el-form label-width="96px" class="filter-form">
        <el-row :gutter="20">
          <el-col :md="8" :sm="24">
            <el-form-item label="主车型">
              <el-select
                v-model="selectedMainVehicle"
                filterable
                clearable
                placeholder="请选择主车型"
                :loading="vehicleLoading"
                @change="handleMainVehicleChange"
              >
                <el-option
                  v-for="item in vehicleOptions"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :md="8" :sm="24">
            <el-form-item label="对标车型">
              <el-select
                v-model="selectedBenchmarkVehicles"
                multiple
                clearable
                collapse-tags
                collapse-tags-tooltip
                filterable
                placeholder="请选择对标车型"
                :disabled="!selectedMainVehicle"
              >
                <el-option
                  v-for="item in vehicleOptions"
                  :key="`benchmark-${item.id}`"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                  :disabled="item.id === selectedMainVehicle"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :md="8" :sm="24">
            <el-form-item label="扩展模块">
              <el-space wrap>
                <el-button
                  :type="filters.showChassis ? 'primary' : 'default'"
                  @click="toggleSection('showChassis')"
                >
                  底盘详细分析
                </el-button>
                <el-button
                  :type="filters.showAcousticPackage ? 'primary' : 'default'"
                  @click="toggleSection('showAcousticPackage')"
                >
                  声学包分析
                </el-button>
              </el-space>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-actions">
          <el-button type="primary" @click="handleQuery" :loading="loading">查询</el-button>
          <el-button @click="handleReset" :disabled="loading">重置</el-button>
        </div>
      </el-form>
    </el-card>

    <el-alert
      v-if="error"
      type="error"
      :closable="false"
      class="error-alert"
      :description="error"
      show-icon
    />

    <div v-if="!overview && !loading" class="empty-wrapper">
      <el-empty description="请选择主车型并点击查询获取对标数据" />
    </div>

    <div v-else class="overview-section" v-loading="loading">
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">匀速工况噪声对比（RMS雷达图）</span>
          </div>
        </template>
        <div class="chart-row">
          <div class="chart-panel">
            <div class="panel-title">匀速前排驾驶员右耳</div>
            <div class="panel-body">
              <div v-if="hasRadarData(radarCards[0].dataset)" ref="radarFrontRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
          <div class="chart-panel">
            <div class="panel-title">匀速二排驾驶员左耳</div>
            <div class="panel-body">
              <div v-if="hasRadarData(radarCards[1].dataset)" ref="radarRearRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">加速工况声压曲线</span>
          </div>
        </template>
        <div class="chart-row">
          <div class="chart-panel">
            <div class="panel-title">加速前排驾驶员右耳</div>
            <div class="panel-body">
              <div v-if="hasSeries(accelerationCards[0].dataset)" ref="accelFrontRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据或单位不一致" />
            </div>
          </div>
          <div class="chart-panel">
            <div class="panel-title">加速后排驾驶员左耳</div>
            <div class="panel-body">
              <div v-if="hasSeries(accelerationCards[1].dataset)" ref="accelRearRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据或单位不一致" />
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">空调全档位噪声趋势</span>
          </div>
        </template>
        <div class="chart-row">
          <div class="chart-panel">
            <div class="panel-title">驾驶员右耳（空调1-9档）</div>
            <div class="panel-body">
              <div v-if="hasSeries(airConditionCards[0].dataset)" ref="airFrontRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
          <div class="chart-panel">
            <div class="panel-title">后排左耳（空调1-9档）</div>
            <div class="panel-body">
              <div v-if="hasSeries(airConditionCards[1].dataset)" ref="airRearRef" class="chart-container"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
        </div>
      </el-card>

      <el-card
        v-if="filters.showChassis"
        class="chart-card"
        shadow="never"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">底盘详细分析</span>
          </div>
        </template>
        <div v-if="hasChassisTable" class="table-wrapper">
          <el-table :data="chassisParameters" border stripe size="small">
            <el-table-column prop="vehicle_model_name" label="车型" min-width="160" />
            <el-table-column prop="suspension_type" label="悬架形式" min-width="120" />
            <el-table-column prop="subframe_type" label="副车架形式" min-width="120" />
            <el-table-column prop="tire_brand" label="轮胎品牌" min-width="120" />
            <el-table-column prop="tire_model" label="轮胎型号" min-width="140" />
            <el-table-column label="是否静音胎" min-width="120">
              <template #default="{ row }">
                <span>{{ formatBoolean(row.is_silent) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="rim_lateral_stiffness" label="轮辋侧向刚度 (kN/mm)" min-width="160" />
          </el-table>
        </div>
        <el-empty v-else description="暂无底盘参数数据" />
        <div class="chart-row chart-row--top-gap">
          <div class="chart-panel">
            <div class="panel-title">车轮力传递率</div>
            <div class="panel-body">
              <div v-if="hasSeries(chassisForceTransfer)" ref="forceTransferRef" class="chart-container"></div>
              <el-empty v-else description="暂无曲线数据" />
            </div>
          </div>
          <div class="chart-panel">
            <div class="panel-title">悬架隔振率（测点-方向）</div>
            <div class="panel-body">
              <div v-if="hasSeries(chassisSuspension)" ref="suspensionRef" class="chart-container"></div>
              <el-empty v-else description="暂无隔振数据" />
            </div>
          </div>
        </div>
      </el-card>

      <el-card
        v-if="filters.showAcousticPackage"
        class="chart-card"
        shadow="never"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">声学包分析</span>
          </div>
        </template>
        <div v-if="hasAcousticTable" class="table-wrapper">
          <el-table :data="acousticTable" border stripe size="small">
            <el-table-column prop="vehicle_model_name" label="车型" min-width="160" />
            <el-table-column prop="suspension_type" label="悬架形式" min-width="120" />
            <el-table-column prop="front_windshield" label="前挡玻璃" min-width="150" />
            <el-table-column prop="side_door_glass" label="侧门玻璃" min-width="150" />
            <el-table-column prop="sound_insulation_performance" label="隔声性能" min-width="120" />
            <el-table-column prop="uncontrolled_leakage" label="气密性泄漏量 (SCFM)" min-width="160" />
            <el-table-column prop="speech_clarity_100" label="100km/h语音清晰度" min-width="170" />
            <el-table-column prop="speech_clarity_120" label="120km/h语音清晰度" min-width="170" />
          </el-table>
        </div>
        <el-empty v-else description="暂无声学包表格数据" />
        <div class="chart-panel chart-panel--single chart-row--top-gap">
          <div class="panel-title">整车隔声量曲线（400Hz-10kHz）</div>
          <div class="panel-body">
            <div v-if="hasSeries(acousticCurve)" ref="insulationRef" class="chart-container"></div>
            <el-empty v-else description="暂无隔声曲线" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts/core'
import { LineChart, RadarChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useNvhBenchmarkStore } from '@/store/nvhBenchmark'

echarts.use([LineChart, RadarChart, GridComponent, LegendComponent, TitleComponent, TooltipComponent, CanvasRenderer])

const store = useNvhBenchmarkStore()
const { filters, vehicleOptions, overview, loading, vehicleLoading, error, selectedVehicleCount } = storeToRefs(store)

const selectedMainVehicle = computed({
  get: () => filters.value.mainVehicleId,
  set: (value) => {
    store.setFilters({ mainVehicleId: value })
  }
})

const selectedBenchmarkVehicles = computed({
  get: () => filters.value.benchmarkVehicleIds,
  set: (value) => {
    const list = Array.isArray(value) ? value.filter((item) => item !== selectedMainVehicle.value) : []
    store.setFilters({ benchmarkVehicleIds: list })
  }
})

const handleMainVehicleChange = (value) => {
  const defaults = store.getDefaultBenchmarkIds(value)
  store.setFilters({ benchmarkVehicleIds: defaults })
}

const handleQuery = async () => {
  await store.fetchOverview()
  await nextTick()
  renderAllCharts()
}

const handleReset = () => {
  store.resetFilters()
  clearAllCharts()
}

const toggleSection = (key) => {
  store.setFilters({ [key]: !filters.value[key] })
  if (overview.value) {
    handleQuery().catch(() => {})
  }
}

const formatBoolean = (value) => {
  if (value === true) return '是'
  if (value === false) return '否'
  return '-'
}

const radarCards = computed(() => [
  { key: 'front_right', dataset: overview.value?.cruise_radar?.front_right },
  { key: 'rear_left', dataset: overview.value?.cruise_radar?.rear_left }
])

const accelerationCards = computed(() => [
  { key: 'front_right', dataset: overview.value?.acceleration?.front_right },
  { key: 'rear_left', dataset: overview.value?.acceleration?.rear_left }
])

const airConditionCards = computed(() => [
  { key: 'front_right', dataset: overview.value?.air_condition?.front_right },
  { key: 'rear_left', dataset: overview.value?.air_condition?.rear_left }
])

const chassisParameters = computed(() => overview.value?.chassis?.parameters || [])
const chassisForceTransfer = computed(() => overview.value?.chassis?.force_transfer || [])
const chassisSuspension = computed(() => overview.value?.chassis?.suspension_isolation || null)
const acousticTable = computed(() => overview.value?.acoustic_package?.table || [])
const acousticCurve = computed(() => overview.value?.acoustic_package?.insulation_curve || null)

const hasChassisTable = computed(() => !!(chassisParameters.value && chassisParameters.value.length))
const hasAcousticTable = computed(() => !!(acousticTable.value && acousticTable.value.length))

const hasRadarData = (dataset) => {
  if (!dataset || !Array.isArray(dataset.series)) return false
  return dataset.series.some((item) => Array.isArray(item?.values) && item.values.some((value) => typeof value === 'number'))
}

const hasSeries = (dataset) => {
  if (!dataset) return false
  if (Array.isArray(dataset.series)) {
    return dataset.series.some((item) => {
      const data = item?.data || item?.values
      return Array.isArray(data) && data.some((point) => {
        if (Array.isArray(point)) return typeof point[1] === 'number'
        return typeof point === 'number'
      })
    })
  }
  if (Array.isArray(dataset)) {
    return dataset.length > 0
  }
  return false
}

const chartRefs = {
  radarFrontRef: ref(null),
  radarRearRef: ref(null),
  accelFrontRef: ref(null),
  accelRearRef: ref(null),
  airFrontRef: ref(null),
  airRearRef: ref(null),
  forceTransferRef: ref(null),
  suspensionRef: ref(null),
  insulationRef: ref(null)
}

const chartInstances = reactive({
  radarFrontRef: null,
  radarRearRef: null,
  accelFrontRef: null,
  accelRearRef: null,
  airFrontRef: null,
  airRearRef: null,
  forceTransferRef: null,
  suspensionRef: null,
  insulationRef: null
})

const initChart = (key) => {
  const el = chartRefs[key]?.value
  if (!el) return null
  if (!chartInstances[key]) {
    chartInstances[key] = echarts.init(el)
  }
  return chartInstances[key]
}

const clearChart = (key) => {
  if (chartInstances[key]) {
    chartInstances[key].clear()
  }
}

const clearAllCharts = () => {
  Object.keys(chartInstances).forEach((key) => {
    if (chartInstances[key]) {
      chartInstances[key].clear()
    }
  })
}

const renderRadarChart = (key, dataset, title) => {
  if (!hasRadarData(dataset)) {
    clearChart(key)
    return
  }
  const chart = initChart(key)
  if (!chart) return
  const allValues = dataset.series.flatMap((item) => (item.values || [])).filter((value) => typeof value === 'number')
  const maxValue = allValues.length ? Math.max(...allValues) * 1.1 : 10
  const indicators = dataset.indicators?.map((indicator) => ({
    name: indicator.label,
    max: maxValue || 10
  })) || []
  const series = dataset.series.map((item) => ({
    name: item.vehicle_model_name || `车型${item.vehicle_id}`,
    value: (item.values || []).map((value) => (typeof value === 'number' ? value : null))
  }))
  chart.setOption({
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    legend: { type: 'scroll', bottom: 0 },
    tooltip: { trigger: 'item' },
    radar: {
      indicator: indicators,
      radius: '62%',
      splitNumber: 5
    },
    series: [
      {
        type: 'radar',
        data: series,
        areaStyle: { opacity: 0.12 },
        lineStyle: { width: 2 }
      }
    ]
  })
}

const renderLinePairsChart = (key, dataset, config = {}) => {
  if (!hasSeries(dataset)) {
    clearChart(key)
    return
  }
  const chart = initChart(key)
  if (!chart) return
  const series = dataset.series.map((item) => ({
    name: item.vehicle_model_name || `车型${item.vehicle_id}`,
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: item.data || []
  }))
  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      type: 'scroll',
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: 40,
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: config.xName || '',
      axisLabel: { formatter: (value) => Number(value).toFixed(1) }
    },
    yAxis: {
      type: 'value',
      name: config.yName || 'dB(A)'
    },
    series
  })
}

const renderCategoryLineChart = (key, dataset, config = {}) => {
  if (!hasSeries(dataset)) {
    clearChart(key)
    return
  }
  const chart = initChart(key)
  if (!chart) return
  const categories = dataset.labels?.map((item, index) => item?.label || `测点${index + 1}`) || dataset.points || []
  const series = dataset.series.map((item) => ({
    name: item.vehicle_model_name || `车型${item.vehicle_id}`,
    type: 'line',
    smooth: true,
    data: item.values || []
  }))
  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      type: 'scroll',
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: 40,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      name: config.xName || ''
    },
    yAxis: {
      type: 'value',
      name: config.yName || 'dB(A)'
    },
    series
  })
}

const renderSuspensionChart = (dataset) => {
  if (!hasSeries(dataset)) {
    clearChart('suspensionRef')
    return
  }
  const chart = initChart('suspensionRef')
  if (!chart) return
  const series = (dataset.series || []).map((item) => ({
    name: item.vehicle_model_name || `车型${item.vehicle_id}`,
    type: 'line',
    data: item.data
  }))
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll', bottom: 0 },
    grid: { left: '3%', right: '3%', bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: dataset.categories || [] },
    yAxis: { type: 'value', name: '隔振率 (dB)' },
    series
  })
}

const renderInsulationChart = (dataset) => {
  if (!hasSeries(dataset)) {
    clearChart('insulationRef')
    return
  }
  const chart = initChart('insulationRef')
  if (!chart) return
  const freqs = dataset.frequencies || []
  const series = (dataset.series || []).map((item) => ({
    name: item.vehicle_model_name || `车型${item.vehicle_id}`,
    type: 'line',
    smooth: true,
    data: item.values || []
  }))
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll', bottom: 0 },
    grid: { left: '3%', right: '3%', bottom: 50, containLabel: true },
    xAxis: { type: 'category', name: '频率 (Hz)', data: freqs },
    yAxis: { type: 'value', name: '隔声量 (dB)' },
    series
  })
}

const renderAllCharts = () => {
  renderRadarChart('radarFrontRef', radarCards.value[0].dataset, '匀速前排驾驶员右耳')
  renderRadarChart('radarRearRef', radarCards.value[1].dataset, '匀速二排驾驶员左耳')
  renderLinePairsChart('accelFrontRef', accelerationCards.value[0].dataset, { xName: '车速/转速', yName: 'dB(A)' })
  renderLinePairsChart('accelRearRef', accelerationCards.value[1].dataset, { xName: '车速/转速', yName: 'dB(A)' })
  renderCategoryLineChart('airFrontRef', airConditionCards.value[0].dataset, { xName: '测点', yName: 'dB(A)' })
  renderCategoryLineChart('airRearRef', airConditionCards.value[1].dataset, { xName: '测点', yName: 'dB(A)' })
  renderLinePairsChart('forceTransferRef', { series: chassisForceTransfer.value }, { xName: '频率 (Hz)', yName: 'dB' })
  renderSuspensionChart(chassisSuspension.value)
  renderInsulationChart(acousticCurve.value)
}

const handleResize = () => {
  Object.values(chartInstances).forEach((instance) => {
    if (instance) {
      instance.resize()
    }
  })
}

watch(
  () => overview.value,
  async () => {
    await nextTick()
    renderAllCharts()
  },
  { deep: true }
)

onMounted(async () => {
  await store.initialize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  Object.keys(chartInstances).forEach((key) => {
    if (chartInstances[key]) {
      chartInstances[key].dispose()
      chartInstances[key] = null
    }
  })
})
</script>

<style scoped>
.nvh-benchmark {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-form {
  padding-top: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.overview-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-card {
  width: 100%;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.chart-row--top-gap {
  margin-top: 16px;
}

.chart-panel {
  display: flex;
  flex-direction: column;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background-color: #fdfdfd;
  min-height: 360px;
}

.chart-panel--single {
  min-height: 420px;
}

.panel-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.panel-body {
  flex: 1;
  min-height: 320px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.table-wrapper {
  margin-bottom: 16px;
}

.error-alert {
  margin-top: -4px;
}

.empty-wrapper {
  padding: 40px 0;
}
</style>
