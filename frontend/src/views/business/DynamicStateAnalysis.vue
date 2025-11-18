<template>
  <div class="dynamic-noise-analysis">
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form label-width="96px" class="search-form">
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
                style="width: 100%"
                @change="handleVehicleChange"
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
                style="width: 100%"
                @change="handleWorkConditionChange"
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
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <div class="form-actions">
              <el-button type="primary" :loading="isLoading" @click="handleQuery">查询</el-button>
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

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span class="card-title">声压级曲线</span>
            <span class="card-subtitle">单位：dB(A)</span>
          </div>
          <el-radio-group
            v-if="axisTypeOptions.length > 1"
            v-model="activeSoundAxisType"
            size="small"
          >
            <el-radio-button
              v-for="option in axisTypeOptions"
              :key="option.value"
              :label="option.value"
            >
              {{ option.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="chart-body">
        <div v-show="soundSeries.length" ref="soundChartRef" class="echarts-container" />
        <el-empty v-show="!soundSeries.length" description="暂无曲线数据" />
      </div>
    </el-card>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span class="card-title">语音清晰度曲线</span>
            <span class="card-subtitle">单位：%AI</span>
          </div>
          <el-radio-group
            v-if="axisTypeOptions.length > 1"
            v-model="activeClarityAxisType"
            size="small"
          >
            <el-radio-button
              v-for="option in axisTypeOptions"
              :key="option.value"
              :label="option.value"
            >
              {{ option.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="chart-body">
        <div v-show="speechSeries.length" ref="speechChartRef" class="echarts-container" />
        <el-empty v-show="!speechSeries.length" description="暂无曲线数据" />
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">数据列表</span>
          <span class="card-subtitle">仅在查询后展示</span>
        </div>
      </template>
      <el-table
        ref="tableRef"
        v-loading="isLoading"
        :data="tableRows"
        row-key="id"
        :expand-row-keys="expandedRowKeys"
        class="dynamic-table"
        empty-text="暂无数据"
      >
        <el-table-column type="expand" width="1">
          <template #default="{ row }">
            <div class="audio-player-panel">
              <audio v-if="row.audio_url" controls :src="row.audio_url" style="width: 100%" />
              <el-empty v-else description="暂无音频文件" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vehicle_model_name" label="车型" width="140" show-overflow-tooltip />
        <el-table-column prop="work_condition" label="工况" width="160" show-overflow-tooltip />
        <el-table-column prop="measure_point" label="测点" width="160" show-overflow-tooltip />
        <el-table-column prop="x_axis_type" label="横轴类型" width="100">
          <template #default="{ row }">
            {{ axisTypeLabel[row.x_axis_type] || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="详情操作" width="320">
          <template #default="{ row }">
            <el-space wrap>
              <el-button
                size="small"
                type="primary"
                :icon="Histogram"
                @click="openSpectrumDialog(row)"
                :disabled="!row.spectrum_url"
              >
                频谱
              </el-button>
              <el-button
                size="small"
                type="success"
                :icon="VideoPlay"
                @click="toggleAudio(row)"
                :disabled="!row.audio_url"
              >
                声音
              </el-button>
              <el-button
                size="small"
                type="info"
                :icon="PictureFilled"
                @click="openNoiseDialog(row)"
                :disabled="!row.noise_analysis_url"
              >
                噪声分析
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="table.count"
          :page-size="table.pageSize"
          :current-page="table.page"
          :page-sizes="[10, 20, 30, 50]"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="spectrumDialog.visible"
      width="60%"
      :title="spectrumDialog.title || '频谱数据'"
      destroy-on-close
    >
      <div v-loading="spectrumDialog.loading" class="spectrum-dialog-body">
        <div v-if="spectrumDialog.data" ref="spectrumChartRef" class="echarts-container" />
        <el-empty v-else-if="!spectrumDialog.loading" description="暂无频谱数据" />
      </div>
      <template #footer>
        <el-button @click="spectrumDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="noiseDialog.visible"
      width="40%"
      :title="noiseDialog.title || '噪声分析'"
      destroy-on-close
    >
      <div class="noise-image-wrapper">
        <el-image
          v-if="noiseDialog.src"
          :src="noiseDialog.src"
          fit="contain"
          style="width: 100%; max-height: 60vh"
          :preview-src-list="[noiseDialog.src]"
        />
        <el-empty v-else description="暂无噪声分析图片" />
      </div>
      <template #footer>
        <el-button @click="noiseDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Histogram, VideoPlay, PictureFilled } from '@element-plus/icons-vue'
import { useDynamicNoiseAnalysisStore } from '@/store/dynamicNoiseAnalysis'
import { dynamicNoiseApi } from '@/api/dynamicNoise'

const store = useDynamicNoiseAnalysisStore()
const {
  filters,
  vehicleModels,
  workConditionOptions,
  measurePointOptions,
  soundPressureSeries,
  speechClaritySeries,
  axisTypes,
  table,
  isLoading,
  error
} = storeToRefs(store)

const soundChartRef = ref(null)
const speechChartRef = ref(null)
const spectrumChartRef = ref(null)
const tableRef = ref(null)
let soundChart = null
let speechChart = null
let spectrumChart = null

const axisTypeLabel = {
  speed: '车速',
  rpm: '转速'
}

const axisTypeOptions = computed(() => {
  if (!axisTypes.value?.length) return []
  return axisTypes.value.map((type) => ({
    label: axisTypeLabel[type] || type,
    value: type
  }))
})

const activeSoundAxisType = ref('')
const activeClarityAxisType = ref('')
watch(
  axisTypes,
  (types) => {
    if (!types?.length) {
      activeSoundAxisType.value = ''
      activeClarityAxisType.value = ''
      return
    }
    if (!types.includes(activeSoundAxisType.value)) {
      activeSoundAxisType.value = types[0]
    }
    if (!types.includes(activeClarityAxisType.value)) {
      activeClarityAxisType.value = types[0]
    }
  },
  { immediate: true }
)

const soundSeries = computed(() =>
  (soundPressureSeries.value || []).filter((series) =>
    activeSoundAxisType.value ? series.x_axis_type === activeSoundAxisType.value : true
  )
)

const speechSeries = computed(() =>
  (speechClaritySeries.value || []).filter((series) =>
    activeClarityAxisType.value ? series.x_axis_type === activeClarityAxisType.value : true
  )
)

const xAxisTitle = (type) => (type === 'rpm' ? '转速 (rpm)' : '车速 (km/h)')

const tableRows = computed(() => table.value?.results || [])
const expandedRowKeys = ref([])

watch(tableRows, () => {
  expandedRowKeys.value = []
})

const handleVehicleChange = async () => {
  await store.fetchWorkConditions()
}

const handleWorkConditionChange = async () => {
  await store.fetchMeasurePoints()
}

const handleQuery = async () => {
  store.setFilters({ page: 1 })
  await store.query()
}

const handleReset = () => {
  store.resetFilters()
}

const handlePageChange = async (page) => {
  store.setFilters({ page })
  await store.query()
}

const handlePageSizeChange = async (size) => {
  store.setFilters({ pageSize: size, page: 1 })
  await store.query()
}

const initSoundChart = () => {
  if (!soundChartRef.value) return
  soundChart = soundChart || echarts.init(soundChartRef.value)
}

const initSpeechChart = () => {
  if (!speechChartRef.value) return
  speechChart = speechChart || echarts.init(speechChartRef.value)
}

const renderLineChart = (instance, series, axisType, unitLabel) => {
  if (!instance) return
  if (!series?.length) {
    instance.clear()
    return
  }
  instance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll', top: 0 },
    grid: { left: 48, right: 24, top: 70, bottom: 60 },
    xAxis: {
      type: 'value',
      name: xAxisTitle(axisType),
      nameLocation: 'middle',
      nameGap: 25
    },
    yAxis: {
      type: 'value',
      name: unitLabel
    },
    series: series.map((item) => ({
      name: item.name,
      type: 'line',
      smooth: false,
      symbol: 'circle',
      showSymbol: false,
      lineStyle: { width: 2 },
      data: item.data || []
    }))
  })
}

watch(soundSeries, async () => {
  await nextTick()
  initSoundChart()
  renderLineChart(soundChart, soundSeries.value, activeSoundAxisType.value, 'dB(A)')
})

watch(speechSeries, async () => {
  await nextTick()
  initSpeechChart()
  renderLineChart(speechChart, speechSeries.value, activeClarityAxisType.value, '%AI')
})

const resizeCharts = () => {
  soundChart?.resize()
  speechChart?.resize()
  spectrumChart?.resize()
}

onMounted(async () => {
  await store.initialize()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  soundChart?.dispose()
  speechChart?.dispose()
  spectrumChart?.dispose()
  soundChart = null
  speechChart = null
  spectrumChart = null
})

const spectrumCache = reactive(new Map())
const spectrumDialog = reactive({
  visible: false,
  loading: false,
  data: null,
  title: ''
})

const noiseDialog = reactive({
  visible: false,
  src: '',
  title: ''
})

const openSpectrumDialog = async (row) => {
  if (!row.spectrum_url) {
    ElMessage.warning('当前数据暂无频谱文件')
    return
  }
  spectrumDialog.visible = true
  spectrumDialog.loading = true
  spectrumDialog.data = null
  spectrumDialog.title = `${row.vehicle_model_name || ''} ${row.work_condition || ''} ${row.measure_point || ''}`
  if (spectrumCache.has(row.id)) {
    spectrumDialog.data = spectrumCache.get(row.id)
    spectrumDialog.loading = false
    await nextTick()
    renderSpectrumChart()
    return
  }
  try {
    const res = await dynamicNoiseApi.getSpectrum(row.id)
    spectrumDialog.data = res?.data || null
    if (spectrumDialog.data) {
      spectrumCache.set(row.id, spectrumDialog.data)
    }
    await nextTick()
    renderSpectrumChart()
  } catch (err) {
    ElMessage.error(err?.message || '频谱数据加载失败')
  } finally {
    spectrumDialog.loading = false
  }
}

const openNoiseDialog = (row) => {
  if (!row.noise_analysis_url) {
    ElMessage.warning('当前数据暂无噪声分析图片')
    return
  }
  noiseDialog.visible = true
  noiseDialog.src = row.noise_analysis_url
  noiseDialog.title = `${row.vehicle_model_name || ''} ${row.work_condition || ''} ${row.measure_point || ''}`
}

const renderSpectrumChart = () => {
  if (!spectrumDialog.visible || !spectrumDialog.data) return
  spectrumChart = spectrumChart || (spectrumChartRef.value ? echarts.init(spectrumChartRef.value) : null)
  if (!spectrumChart) return
  const { values = [], x_axis: xAxis = [], y_axis: yAxis = [], x_axis_type: axisType } = spectrumDialog.data
  if (!values.length) {
    spectrumChart.clear()
    return
  }
  spectrumChart.setOption({
    tooltip: {
      position: 'top'
    },
    grid: { height: '70%', top: '10%' },
    xAxis: {
      type: 'value',
      name: xAxisTitle(axisType),
      min: xAxis.length ? Math.min(...xAxis) : null,
      max: xAxis.length ? Math.max(...xAxis) : null
    },
    yAxis: {
      type: 'value',
      name: '频率 (Hz)',
      min: yAxis.length ? Math.min(...yAxis) : null,
      max: yAxis.length ? Math.max(...yAxis) : null
    },
    visualMap: {
      min: Math.min(...values.map((item) => item[2])),
      max: Math.max(...values.map((item) => item[2])),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0
    },
    series: [
      {
        type: 'heatmap',
        data: values,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.4)'
          }
        }
      }
    ]
  })
  spectrumChart.resize()
}

watch(
  () => spectrumDialog.visible,
  async (visible) => {
    if (visible && spectrumDialog.data) {
      await nextTick()
      renderSpectrumChart()
    }
  }
)

const toggleAudio = (row) => {
  if (!row.audio_url) {
    ElMessage.warning('当前数据暂无音频文件')
    return
  }
  const isExpanded = expandedRowKeys.value.includes(row.id)
  expandedRowKeys.value = isExpanded ? [] : [row.id]
  if (tableRef.value) {
    tableRef.value.toggleRowExpansion(row, !isExpanded)
  }
}
</script>

<style scoped>
.dynamic-noise-analysis {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
.chart-body {
  width: 100%;
}
.echarts-container {
  width: 100%;
  height: 420px;
}
.table-card .dynamic-table {
  margin-top: 12px;
}
.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
.audio-player-panel {
  padding: 12px 24px 24px;
}
:deep(.el-table__expand-icon) {
  display: none;
}
.spectrum-dialog-body {
  min-height: 360px;
}
.noise-image-wrapper {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.error-alert {
  margin-top: 12px;
}
</style>
