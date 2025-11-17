<template>
  <div class="acoustic-analysis">
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
                filterable
                @change="onVehicleChange"
                style="width: 100%"
              >
                <el-option
                  v-for="item in vehicleModels"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
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
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <div class="form-actions">
              <el-button type="primary" @click="handleQuery" :loading="isLoading">查询</el-button>
              <el-button @click="handleReset" :disabled="isLoading">重置</el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span class="card-title">{{ spectrumTitle }}</span>
            <span v-if="spectrumSubtitle" class="card-subtitle">{{ spectrumSubtitle }}</span>
          </div>
          <el-radio-group
            v-if="spectrumTypeOptions.length > 1"
            v-model="activeSpectrumType"
            size="small"
          >
            <el-radio-button
              v-for="item in spectrumTypeOptions"
              :key="item.value"
              :label="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="chart-body">
        <div ref="spectrumRef" class="echarts-container" v-show="currentSpectrumSeries.length"></div>
        <el-empty v-show="!currentSpectrumSeries.length" :description="spectrumEmptyText" />
      </div>
    </el-card>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span class="card-title">{{ oaTitle }}</span>
            <span v-if="oaSubtitle" class="card-subtitle">{{ oaSubtitle }}</span>
          </div>
          <el-radio-group
            v-if="oaTypeOptions.length > 1"
            v-model="activeOAType"
            size="small"
          >
            <el-radio-button
              v-for="item in oaTypeOptions"
              :key="item.value"
              :label="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="chart-body">
        <div ref="oaRef" class="echarts-container" v-show="currentOASeries.length"></div>
        <el-empty v-show="!currentOASeries.length" :description="oaEmptyText" />
      </div>
    </el-card>

    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span class="card-title">{{ tableTitle }}</span>
            <span class="card-subtitle">共 {{ currentTableRows.length }} 条</span>
          </div>
          <el-radio-group
            v-if="tableTypeOptions.length > 1"
            v-model="activeTableType"
            size="small"
          >
            <el-radio-button
              v-for="item in tableTypeOptions"
              :key="item.value"
              :label="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="currentTableRows" stripe border v-loading="isLoading" :empty-text="tableEmptyText">
        <el-table-column
          v-for="column in tableColumns"
          :key="column.prop"
          v-bind="column"
        />
      </el-table>
    </el-card>
  </div>
  
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { storeToRefs } from 'pinia'
import { useAcousticAnalysisStore } from '@/store/acousticAnalysis'

echarts.use([LineChart, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, CanvasRenderer])

const store = useAcousticAnalysisStore()
const { filters, vehicleModels, workConditionOptions, measurePointOptions, spectrumSeries, oaSeries, tableRows, isLoading } = storeToRefs(store)

const MEASURE_TYPE_LABELS = {
  noise: '噪声',
  vibration: '振动',
  speed: '转速'
}

const formatDecimal = (value, digits = 2) => {
  if (value === null || value === undefined || value === '') return '--'
  const num = Number(value)
  if (!Number.isFinite(num)) return '--'
  return num.toFixed(digits)
}

const decimalFormatter = (_row, _column, cellValue) => formatDecimal(cellValue)
const percentFormatter = (_row, _column, cellValue) => formatDecimal(cellValue)

const COMMON_COLUMNS = [
  { prop: 'vehicle_model_name', label: '车型', minWidth: 150 },
  { prop: 'work_condition', label: '工况', minWidth: 120 },
  { prop: 'measure_point', label: '测点', minWidth: 140 }
]

const TABLE_COLUMN_CONFIG = {
  noise: [
    ...COMMON_COLUMNS,
    { prop: 'speech_clarity', label: '语音清晰度 (%)', minWidth: 160, formatter: percentFormatter },
    { prop: 'rms_value', label: '有效值 RMS (dB)', minWidth: 160, formatter: decimalFormatter },
    { prop: 'test_date', label: '测试日期', minWidth: 140 }
  ],
  vibration: [
    ...COMMON_COLUMNS,
    { prop: 'rms_value', label: '有效值 RSS (m/s²)', minWidth: 180, formatter: decimalFormatter },
    { prop: 'test_date', label: '测试日期', minWidth: 140 }
  ],
  speed: [
    ...COMMON_COLUMNS,
    { prop: 'rms_value', label: '转速', minWidth: 140, formatter: decimalFormatter },
    { prop: 'test_date', label: '测试日期', minWidth: 140 }
  ],
  default: [
    ...COMMON_COLUMNS,
    { prop: 'speech_clarity', label: '语音清晰度', minWidth: 140, formatter: decimalFormatter },
    { prop: 'rms_value', label: '有效值', minWidth: 120, formatter: decimalFormatter },
    { prop: 'test_date', label: '测试日期', minWidth: 140 }
  ]
}

const TABLE_META = {
  noise: { title: '噪声测点数据', empty: '暂无噪声测点数据' },
  vibration: { title: '振动测点数据', empty: '暂无振动测点数据' },
  speed: { title: '转速测点数据', empty: '暂无转速测点数据' },
  default: { title: '数据表格', empty: '暂无数据' }
}

const CHART_META = {
  noise: {
    spectrum: { title: '噪声频谱图', subtitle: '纵轴：声压级 (dB)', yAxis: '声压级 (dB)', empty: '暂无噪声频谱数据' },
    oa: { title: '总声压级 (OA) 曲线', subtitle: '纵轴：声压级 (dB)', yAxis: '声压级 (dB)', empty: '暂无噪声OA数据' }
  },
  vibration: {
    spectrum: { title: '振动频谱图', subtitle: '纵轴：振动加速度 (m/s²)', yAxis: '加速度 (m/s²)', empty: '暂无振动频谱数据' },
    oa: { title: '振动时域曲线', subtitle: '纵轴：振动加速度 (m/s²)', yAxis: '加速度 (m/s²)', empty: '暂无振动时域数据' }
  }
}

const DEFAULT_SPECTRUM_META = { title: '频谱曲线', subtitle: '', yAxis: '幅值', empty: '当前测点类型暂无频谱数据' }
const DEFAULT_OA_META = { title: '总声压级 / 振动时域曲线', subtitle: '', yAxis: '幅值', empty: '当前测点类型暂无曲线数据' }
const TYPE_ORDER = ['noise', 'vibration', 'speed']

const spectrumRef = ref(null)
const oaRef = ref(null)
let spectrumChart = null
let oaChart = null

const spectrumTypeOptions = computed(() => {
  const present = new Set()
  spectrumSeries.value.forEach((series) => {
    if (series.measureType && ['noise', 'vibration'].includes(series.measureType) && series.data?.length) {
      present.add(series.measureType)
    }
  })
  return ['noise', 'vibration']
    .filter((type) => present.has(type))
    .map((type) => ({ value: type, label: MEASURE_TYPE_LABELS[type] }))
})

const oaTypeOptions = computed(() => {
  const present = new Set()
  oaSeries.value.forEach((series) => {
    if (series.measureType && ['noise', 'vibration'].includes(series.measureType) && series.data?.length) {
      present.add(series.measureType)
    }
  })
  return ['noise', 'vibration']
    .filter((type) => present.has(type))
    .map((type) => ({ value: type, label: MEASURE_TYPE_LABELS[type] }))
})

const tableTypeOptions = computed(() => {
  const present = new Set()
  tableRows.value.forEach((row) => {
    if (row.measureType) {
      present.add(row.measureType)
    }
  })
  return TYPE_ORDER.filter((type) => present.has(type)).map((type) => ({ value: type, label: MEASURE_TYPE_LABELS[type] }))
})

const activeSpectrumType = ref('')
const activeOAType = ref('')
const activeTableType = ref('')

const ensureActiveType = (options, targetRef) => {
  if (!options.length) {
    targetRef.value = ''
    return
  }
  if (!options.some((item) => item.value === targetRef.value)) {
    targetRef.value = options[0].value
  }
}

watch(spectrumTypeOptions, (options) => ensureActiveType(options, activeSpectrumType), { immediate: true })
watch(oaTypeOptions, (options) => ensureActiveType(options, activeOAType), { immediate: true })
watch(tableTypeOptions, (options) => ensureActiveType(options, activeTableType), { immediate: true })

const currentSpectrumSeries = computed(() =>
  activeSpectrumType.value ? spectrumSeries.value.filter((series) => series.measureType === activeSpectrumType.value) : []
)
const currentOASeries = computed(() =>
  activeOAType.value ? oaSeries.value.filter((series) => series.measureType === activeOAType.value) : []
)
const currentTableRows = computed(() =>
  activeTableType.value ? tableRows.value.filter((row) => row.measureType === activeTableType.value) : []
)

const spectrumMeta = computed(() => CHART_META[activeSpectrumType.value]?.spectrum ?? DEFAULT_SPECTRUM_META)
const spectrumTitle = computed(() => spectrumMeta.value.title)
const spectrumSubtitle = computed(() => spectrumMeta.value.subtitle)
const spectrumEmptyText = computed(() => spectrumMeta.value.empty)
const spectrumYAxisName = computed(() => spectrumMeta.value.yAxis)
const spectrumXAxisMax = computed(() => (activeSpectrumType.value === 'vibration' ? 800 : 12800))

const oaMeta = computed(() => CHART_META[activeOAType.value]?.oa ?? DEFAULT_OA_META)
const oaTitle = computed(() => oaMeta.value.title)
const oaSubtitle = computed(() => oaMeta.value.subtitle)
const oaEmptyText = computed(() => oaMeta.value.empty)
const oaYAxisName = computed(() => oaMeta.value.yAxis)

const tableColumns = computed(() => {
  if (activeTableType.value && TABLE_COLUMN_CONFIG[activeTableType.value]) {
    return TABLE_COLUMN_CONFIG[activeTableType.value]
  }
  return TABLE_COLUMN_CONFIG.default
})

const tableTitle = computed(() => {
  if (activeTableType.value && TABLE_META[activeTableType.value]) {
    return TABLE_META[activeTableType.value].title
  }
  return TABLE_META.default.title
})

const tableEmptyText = computed(() => {
  if (!activeTableType.value) {
    return tableRows.value.length ? '请选择测点类型' : TABLE_META.default.empty
  }
  return TABLE_META[activeTableType.value]?.empty ?? TABLE_META.default.empty
})

const initCharts = () => {
  if (spectrumRef.value && !spectrumChart) {
    spectrumChart = echarts.init(spectrumRef.value)
  }
  if (oaRef.value && !oaChart) {
    oaChart = echarts.init(oaRef.value)
  }
}

const renderSpectrum = () => {
  if (!spectrumChart) return
  if (!currentSpectrumSeries.value.length) {
    spectrumChart.clear()
    return
  }

  spectrumChart.setOption({
    tooltip: { trigger: 'axis' },
    // 将图例放到顶部，避免与图像重叠，便于点击
    legend: { type: 'scroll', top: 0 },
    // 给顶部留出更多空间以容纳图例，同时增大底部留白避免与缩放条重叠
    grid: { left: 40, right: 20, top: 70, bottom: 90 },
    // 限制频率横坐标最大值，并将轴标题上移一些避免与缩放条重叠
    xAxis: { type: 'value', name: '频率 (Hz)', nameLocation: 'middle', nameGap: 18, max: spectrumXAxisMax.value },
    yAxis: { type: 'value', name: spectrumYAxisName.value },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: currentSpectrumSeries.value.map((s) => ({
      name: s.name,
      type: 'line',
      symbol: 'none',
      sampling: 'lttb',
      lineStyle: { width: 2 },
      data: s.data
    }))
  })
}

const renderOA = () => {
  if (!oaChart) return
  if (!currentOASeries.value.length) {
    oaChart.clear()
    return
  }

  oaChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        // 展示该系列对应的统计信息
        const lines = []
        params.forEach((p) => {
          const s = currentOASeries.value.find((x) => x.name === p.seriesName)
          if (s?.stats) {
            const { max, min, avg } = s.stats
            lines.push(`${p.marker}${p.seriesName}: y=${p.value?.[1]} (Max:${max?.toFixed?.(2)} Min:${min?.toFixed?.(2)} Avg:${avg?.toFixed?.(2)})`)
          } else {
            lines.push(`${p.marker}${p.seriesName}: y=${p.value?.[1]}`)
          }
        })
        return lines.join('<br/>')
      }
    },
    legend: { type: 'scroll', top: 0 },
    grid: { left: 40, right: 20, top: 70, bottom: 60 },
    xAxis: { type: 'value', name: '时间', nameLocation: 'middle', nameGap: 25 },
    yAxis: { type: 'value', name: oaYAxisName.value },
    series: currentOASeries.value.map((s) => ({
      name: s.name,
      type: 'line',
      symbol: 'none',
      lineStyle: { width: 2 },
      data: s.data
    }))
  })
}

const onVehicleChange = async () => {
  await store.fetchWorkConditions()
}

const onWorkConditionChange = async () => {
  await store.fetchMeasurePoints()
}

const handleQuery = async () => {
  await store.query()
}

const handleReset = async () => {
  store.resetFilters()
}

onMounted(async () => {
  await store.initialize()
  initCharts()
})

watch([() => currentSpectrumSeries.value, () => spectrumYAxisName.value], async () => {
  await nextTick()
  initCharts()
  renderSpectrum()
}, { deep: true })

watch([() => currentOASeries.value, () => oaYAxisName.value], async () => {
  await nextTick()
  initCharts()
  renderOA()
}, { deep: true })

const resize = () => {
  spectrumChart?.resize()
  oaChart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (spectrumChart) { spectrumChart.dispose(); spectrumChart = null }
  if (oaChart) { oaChart.dispose(); oaChart = null }
})
</script>

<style scoped>
.acoustic-analysis { display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-header-left { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.card-title { font-size: 16px; font-weight: 600; }
.card-subtitle { font-size: 12px; color: #909399; }
.search-form { padding-top: 8px; }
.form-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 0; }
.chart-body { width: 100%; }
.echarts-container { width: 100%; height: 420px; }
</style>
