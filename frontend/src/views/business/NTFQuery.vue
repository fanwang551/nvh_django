<template>
  <div class="ntf-query">
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form label-width="80px" class="filter-form">
        <el-form-item label="车型">
          <el-select
            v-model="localVehicleIds"
            placeholder="请选择车型（可多选）"
            multiple
            filterable
            clearable
            :loading="isLoading && !localVehicleIds.length"
            @change="handleVehicleChange"
          >
            <el-option
              v-for="item in vehicleOptions"
              :key="item.id"
              :label="item.vehicle_model_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测点">
          <el-select
            v-model="localPoints"
            placeholder="请选择测点（可多选）"
            multiple
            filterable
            clearable
            :loading="isLoading && !localPoints.length"
            @change="handlePointsChange"
          >
            <el-option v-for="p in measurementPointOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-alert v-if="error" type="error" :title="error" show-icon />

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试结果</span>
          <div v-if="tableRows.length && levelStats.total > 0" class="level-stats">
            <span class="level-item ntf-cell ntf-cell--low">
              <strong>&lt;60</strong>：{{ levelStats.low.percent }}%
            </span>
            <span class="level-item ntf-cell ntf-cell--medium">
              <strong>60-65</strong>：{{ levelStats.medium.percent }}%
            </span>
            <span class="level-item ntf-cell ntf-cell--high">
              <strong>&gt;65</strong>：{{ levelStats.high.percent }}%
            </span>
          </div>
        </div>
      </template>
      <el-table
        v-if="tableRows.length"
        :data="tableRows"
        border
        stripe
        class="result-table"
        :span-method="tableSpanMethod"
      >
        <el-table-column prop="vehicle_model_name" label="车型" min-width="160" />
        <el-table-column prop="measurement_point" label="测点" min-width="140" />
        <el-table-column label="方向" min-width="100">
          <template #default="{ row }">
            {{ getDirectionLabel(row) }}
          </template>
        </el-table-column>
        <el-table-column label="目标" min-width="120">
          <template #default="{ row }">
            <span :class="getValueClass(row.target)">{{ formatValue(row.target) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-for="column in seatColumns"
          :key="column.key"
          :label="column.label"
          min-width="120"
        >
          <template #default="{ row }">
            <span :class="getValueClass(row[column.key])">{{ formatValue(row[column.key]) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无测试结果数据" />
    </el-card>

    <el-card class="heatmap-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">NTF Function Map 热力图</span>
        </div>
      </template>
      <div v-if="heatmap.points.length && heatmap.frequency.length">
        <div ref="heatmapRef" class="heatmap" :style="{ height: heatmapHeight + 'px' }"></div>
      </div>
      <el-empty v-else description="暂无热力图数据" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useNTFQueryStore } from '@/store'

defineOptions({ name: 'NTFQuery' })

const VALUE_LEVEL = { HIGH: 'high', MEDIUM: 'medium', LOW: 'low' }

echarts.use([HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent, TitleComponent, CanvasRenderer])

const store = useNTFQueryStore()
const { vehicleOptions, measurementPointOptions, seatColumns, tableRows, heatmap, isLoading, error } = storeToRefs(store)

const localVehicleIds = ref([])
const localPoints = ref([])
const heatmapRef = ref(null)
let chartInstance = null

// 动态计算热力图容器高度：确保每个测点有足够行高，超出容器时外层可滚动
const heatmapHeight = computed(() => {
  const rows = Array.isArray(heatmap.value?.points) ? heatmap.value.points.length : 0
  const BASE_OFFSET = 110 // 顶/底部 grid 留白等
  const ROW_HEIGHT = 20   // 每个测点期望行高
  return Math.max(420, BASE_OFFSET + rows * ROW_HEIGHT)
})

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  return numeric.toFixed(2)
}

function classifyValue(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return null
  if (numeric > 65) return VALUE_LEVEL.HIGH
  if (numeric >= 60) return VALUE_LEVEL.MEDIUM
  return VALUE_LEVEL.LOW
}

function getValueClass(value) {
  const level = classifyValue(value)
  return level ? `ntf-cell ntf-cell--${level}` : 'ntf-cell'
}

function tableSpanMethod({ column, rowIndex }) {
  const rows = Array.isArray(tableRows.value) ? tableRows.value : []
  if (!column || !rows.length) return { rowspan: 1, colspan: 1 }
  const groupKey = (r) => `${r.vehicle_model_name}__${r.measurement_point}`
  const currentKey = groupKey(rows[rowIndex])
  if (column.property === 'vehicle_model_name' || column.property === 'measurement_point') {
    const isStart = rowIndex === 0 || groupKey(rows[rowIndex - 1]) !== currentKey
    if (!isStart) return { rowspan: 0, colspan: 0 }
    let count = 1
    let i = rowIndex + 1
    while (i < rows.length && groupKey(rows[i]) === currentKey) {
      count += 1
      i += 1
    }
    return { rowspan: count, colspan: 1 }
  }
  return { rowspan: 1, colspan: 1 }
}

function getDirectionLabel(row) {
  if (!row) return '-'
  const raw = (row.direction ?? row.direction_label ?? '').toString()
  if (!raw) return '-'
  const m = raw.toUpperCase().match(/[XYZ]/)
  return m ? m[0] : raw
}

const levelStats = computed(() => {
  const stats = { total: 0, low: { count: 0, percent: 0 }, medium: { count: 0, percent: 0 }, high: { count: 0, percent: 0 } }
  const seatKeys = Array.isArray(seatColumns.value) ? seatColumns.value.map((c) => c.key) : []
  if (!Array.isArray(tableRows.value) || !seatKeys.length) return stats
  for (const row of tableRows.value) {
    for (const key of seatKeys) {
      const v = Number(row?.[key])
      if (!Number.isFinite(v)) continue
      stats.total += 1
      if (v > 65) stats.high.count += 1
      else if (v >= 60) stats.medium.count += 1
      else stats.low.count += 1
    }
  }
  if (stats.total > 0) {
    stats.low.percent = Math.round((stats.low.count / stats.total) * 100)
    stats.medium.percent = Math.round((stats.medium.count / stats.total) * 100)
    stats.high.percent = Math.round((stats.high.count / stats.total) * 100)
  }
  return stats
})

function buildHeatmapSeriesData() {
  if (!heatmap.value?.matrix?.length) return []
  const data = []
  const matrix = heatmap.value.matrix
  matrix.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      const numeric = Number(value)
      data.push([colIndex, rowIndex, Number.isFinite(numeric) ? numeric : null])
    })
  })
  return data
}

function renderHeatmap() {
  if (!heatmapRef.value) return
  if (!chartInstance) chartInstance = echarts.init(heatmapRef.value)
  const data = buildHeatmapSeriesData()
  const valueRange = computeHeatmapRange()
  const option = {
    title: { left: 'center', text: 'Frequency vs Measurement Point' },
    tooltip: {
      trigger: 'item',
      formatter(params) {
        const point = heatmap.value.points[params.value[1]]
        const frequency = heatmap.value.frequency[params.value[0]]
        const value = params.value[2]
        const displayValue = Number.isFinite(value) ? value.toFixed(2) : '-'
        return `测点：${point}<br/>频率：${frequency} Hz<br/>NTF：${displayValue}`
      }
    },
    grid: { top: 60, left: 80, right: 20, bottom: 50 },
    xAxis: { type: 'category', data: heatmap.value.frequency, name: '频率 (Hz)', nameGap: 18, axisLabel: { fontSize: 10, rotate: 45 } },
    yAxis: { type: 'category', data: heatmap.value.points, name: '测点', nameGap: 16, axisLabel: { fontSize: 12 } },
    visualMap: {
      min: valueRange.min,
      max: valueRange.max,
      orient: 'vertical',
      right: 10,
      top: 'center',
      align: 'auto',
      calculable: true,
      inRange: {
        color: ['#1a237e', '#3949ab', '#42a5f5', '#66bb6a', '#fdd835', '#fb8c00', '#e53935', '#b71c1c']
      }
    },
    series: [{ name: 'NTF Heatmap', type: 'heatmap', data, label: { show: false } }]
  }
  chartInstance.setOption(option)
  // 高度变化后触发布局刷新
  chartInstance.resize()
}

function computeHeatmapRange() {
  const values = []
  const m = heatmap.value?.matrix || []
  for (const row of m) {
    for (const v of row || []) {
      const n = Number(v)
      if (Number.isFinite(n)) values.push(n)
    }
  }
  if (!values.length) return { min: 49, max: 69 }
  return { min: Math.min(...values), max: Math.max(...values) }
}

function handleResize() { if (chartInstance) chartInstance.resize() }

watch(
  () => heatmap.value,
  async (newValue) => {
    if (!newValue) return
    await nextTick()
    if (newValue.points.length && newValue.frequency.length) renderHeatmap()
    else if (chartInstance) chartInstance.clear()
  },
  { deep: true }
)

async function handleVehicleChange(ids) {
  store.selectedVehicleIds = Array.isArray(ids) ? ids : []
  await store.fetchMeasurementPoints()
  await store.multiQuery()
}

async function handlePointsChange(points) {
  store.selectedPoints = Array.isArray(points) ? points : []
  await store.multiQuery()
}

onMounted(async () => {
  await store.fetchVehicleOptions()
  await store.fetchMeasurementPoints()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) { chartInstance.dispose(); chartInstance = null }
})
</script>

<style scoped>
.ntf-query { display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.filter-form { max-width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: center; }
.heatmap { width: 100%; height: 420px; }
.result-table { --el-table-border-color: #ebeef5; }
.ntf-cell { font-weight: 600; }
.ntf-cell--high { color: #f56c6c; }
.ntf-cell--medium { color: #e6a23c; }
.ntf-cell--low { color: #67c23a; }
.level-stats { display: flex; gap: 12px; align-items: center; }
.level-item strong { margin-right: 4px; }
</style>
