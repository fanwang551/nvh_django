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
          <span class="card-title">频谱曲线</span>
        </div>
      </template>
      <div v-if="spectrumSeries.length" ref="spectrumRef" class="echarts-container"></div>
      <el-empty v-else description="暂无频谱数据" />
    </el-card>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">总声压级 (OA) 曲线</span>
        </div>
      </template>
      <div v-if="oaSeries.length" ref="oaRef" class="echarts-container"></div>
      <el-empty v-else description="暂无OA数据" />
    </el-card>

    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">数据表格</span>
          <span class="card-subtitle">共 {{ tableRows.length }} 条</span>
        </div>
      </template>
      <el-table :data="tableRows" stripe border v-loading="isLoading" empty-text="暂无数据">
        <el-table-column prop="vehicle_model_name" label="车型" min-width="150" />
        <el-table-column prop="work_condition" label="工况" min-width="120" />
        <el-table-column prop="measure_point" label="测点" min-width="140" />
        <el-table-column prop="speech_clarity" label="语音清晰度" min-width="140" />
        <el-table-column prop="rms_value" label="有效值" min-width="120" />
        <el-table-column prop="test_date" label="测试日期" min-width="140" />
      </el-table>
    </el-card>
  </div>
  
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { storeToRefs } from 'pinia'
import { useAcousticAnalysisStore } from '@/store/acousticAnalysis'

echarts.use([LineChart, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, CanvasRenderer])

const store = useAcousticAnalysisStore()
const { filters, vehicleModels, workConditionOptions, measurePointOptions, spectrumSeries, oaSeries, tableRows, isLoading } = storeToRefs(store)

const spectrumRef = ref(null)
const oaRef = ref(null)
let spectrumChart = null
let oaChart = null

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
  if (!spectrumSeries.value.length) {
    spectrumChart.clear()
    return
  }

  spectrumChart.setOption({
    tooltip: { trigger: 'axis' },
    // 将图例放到顶部，避免与图像重叠，便于点击
    legend: { type: 'scroll', top: 0 },
    // 给顶部留出更多空间以容纳图例，同时增大底部留白避免与缩放条重叠
    grid: { left: 40, right: 20, top: 70, bottom: 90 },
    // 限制频率横坐标最大到 12800 Hz，并将轴标题上移一些避免与缩放条重叠
    xAxis: { type: 'value', name: '频率 (Hz)', nameLocation: 'middle', nameGap: 18, max: 12800 },
    yAxis: { type: 'value', name: '声压级 dB(A)' },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: spectrumSeries.value.map((s) => ({
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
  if (!oaSeries.value.length) {
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
          const s = oaSeries.value.find((x) => x.name === p.seriesName)
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
    legend: { type: 'scroll' },
    grid: { left: 40, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'value', name: '时间', nameLocation: 'middle', nameGap: 25 },
    yAxis: { type: 'value', name: 'OA' },
    series: oaSeries.value.map((s) => ({
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

watch(spectrumSeries, async () => {
  await nextTick()
  initCharts()
  renderSpectrum()
}, { deep: true })

watch(oaSeries, async () => {
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
.card-title { font-size: 16px; font-weight: 600; }
.card-subtitle { font-size: 12px; color: #909399; }
.search-form { padding-top: 8px; }
.form-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 0; }
.echarts-container { width: 100%; height: 420px; }
</style>
