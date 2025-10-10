<template>
  <div class="ntf-query">
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form inline label-width="80px" class="filter-form">
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
        <el-form-item label="位置">
          <el-select
            v-model="localPositions"
            placeholder="请选择位置（可多选）"
            multiple
            filterable
            clearable
            @change="handlePositionsChange"
          >
            <el-option v-for="p in positionStaticOptions" :key="p" :label="posLabel(p)" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="方向">
          <el-select
            v-model="localDirections"
            placeholder="请选择方向（可多选）"
            multiple
            filterable
            clearable
            @change="handleDirectionsChange"
          >
            <el-option v-for="d in directionStaticOptions" :key="d" :label="dirLabel(d)" :value="d" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-alert v-if="error" type="error" :title="error" show-icon />

    <!-- 车辆基本信息卡片 -->
    <el-card v-if="vehicleCards.length" class="vehicle-info-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">车辆基本信息</span>
        </div>
      </template>
      <div class="vehicle-card-list">
        <el-card v-for="v in vehicleCards" :key="v.vehicle_id" class="vehicle-card" shadow="never">
          <div class="vehicle-card-title">{{ v.vehicle_model_name }}（{{ v.vehicle_model_code || '-' }}）</div>
          <div class="vehicle-card-rows">
            <div class="vehicle-card-row"><span class="label">VIN</span><span class="value">{{ v.vin || '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">生产时间</span><span class="value">{{ v.production_year || '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">能源形式</span><span class="value">{{ v.energy_type || '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">悬挂形式</span><span class="value">{{ v.suspension_type || '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">天窗形式</span><span class="value">{{ v.sunroof_type || '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">座位数</span><span class="value">{{ v.seat_count ?? '-' }}</span></div>
            <div class="vehicle-card-row"><span class="label">测试人员</span><span class="value">{{ v.tester }}</span></div>
            <div class="vehicle-card-row"><span class="label">测试地点</span><span class="value">{{ v.location }}</span></div>
            <div class="vehicle-card-row"><span class="label">测试时间</span><span class="value">{{ formatDateTime(v.test_time) }}</span></div>
          </div>
        </el-card>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试结果</span>
          <div v-if="tableRows.length && levelStats.total > 0" class="level-stats">
            <span class="level-item ntf-cell ntf-cell--low">
              <strong>&lt;55</strong>：{{ levelStats.lt55.percent }}%
            </span>
            <span class="level-item ntf-cell ntf-cell--medium">
              <strong>55-60</strong>：{{ levelStats.r55_60.percent }}%
            </span>
            <span class="level-item ntf-cell ntf-cell--medium">
              <strong>60-65</strong>：{{ levelStats.r60_65.percent }}%
            </span>
            <span class="level-item ntf-cell ntf-cell--high">
              <strong>&gt;65</strong>：{{ levelStats.gt65.percent }}%
            </span>
          </div>
        </div>
      </template>
      <el-table
        v-if="tableRows.length"
        :data="pivotedRows"
        border
        stripe
        class="result-table"
        :span-method="tableSpanMethod"
        :header-cell-style="headerCellStyleCenter"
      >
        <el-table-column prop="vehicle_model_name" label="车型" min-width="160" />
        <el-table-column prop="measurement_point" label="测点" min-width="140" />
        <el-table-column label="方向" min-width="100">
          <template #default="{ row }">
            {{ getDirectionLabel(row) }}
          </template>
        </el-table-column>
        <!-- 频段改为列分组显示，移除单列显示 -->
        <el-table-column label="目标" min-width="120">
          <template #default="{ row }">
            <span :class="getValueClass(row.target)">{{ formatValue(row.target) }}</span>
          </template>
        </el-table-column>
        <!-- 以频段为列分组，内部为各座位值 -->
        <el-table-column
          v-for="band in pivotBands"
          :key="band.key"
          :label="band.label"
        >
          <el-table-column
            v-for="column in seatColumns"
            :key="band.key + ':' + column.key"
            :label="column.label"
            min-width="120"
          >
            <template #default="{ row }">
              <span :class="getValueClass(row[`${column.key}__${band.key}`])">{{ formatValue(row[`${column.key}__${band.key}`]) }}</span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="操作" min-width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" :disabled="!row.layout_image_url" @click="openLayout(row.layout_image_url)">查看布置图</el-button>
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

  <!-- 布置图弹窗 -->
  <el-dialog v-model="layoutDialogVisible" title="测点布置图" width="60%">
    <div v-if="layoutImageUrl" style="text-align:center">
      <img :src="layoutImageUrl" alt="layout" style="max-width:100%; max-height:70vh; object-fit:contain;" />
    </div>
    <el-empty v-else description="暂无布置图" />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="layoutDialogVisible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>
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
const { vehicleOptions, measurementPointOptions, seatColumns, tableRows, heatmap, isLoading, error, vehicleCards } = storeToRefs(store)

const localVehicleIds = ref([])
const localPoints = ref([])
const localPositions = ref([])
const localDirections = ref([])
// 静态的 位置 与 方向 选项（不级联）
const positionStaticOptions = ['front', 'middle', 'rear']
const directionStaticOptions = ['x', 'y', 'z']
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

function formatDateTime(value) {
  if (!value) return '-'
  try {
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return d.toLocaleString()
  } catch (_) {
    return value
  }
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

function posLabel(key) {
  const map = { front: '前排', middle: '中排', rear: '后排' }
  return map[key] || key
}

function dirLabel(key) {
  const map = { x: 'X', y: 'Y', z: 'Z' }
  return map[key] || key
}

// 将频段标签转为字段安全的 key（如 20-200Hz -> 20_200）
function bandKeyFromLabel(label) {
  const s = String(label || '')
  const m = s.match(/(\d+)\s*-\s*(\d+)/)
  if (m) return `${m[1]}_${m[2]}`
  return s.replace(/[^0-9a-zA-Z]+/g, '_')
}

// 可用频段列
const pivotBands = computed(() => {
  const rows = Array.isArray(tableRows.value) ? tableRows.value : []
  const set = new Map()
  for (const r of rows) {
    const label = r?.band
    if (!label) continue
    const key = bandKeyFromLabel(label)
    if (!set.has(key)) set.set(key, { key, label })
  }
  // 按显示顺序：20-200 在前，200-500 在后
  const arr = Array.from(set.values())
  arr.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN', { numeric: true }))
  return arr
})

// 结果表透视：同一 车型+测点+方向 合并为一行，频段展开为列
const pivotedRows = computed(() => {
  const rows = Array.isArray(tableRows.value) ? tableRows.value : []
  if (!rows.length) return []
  const seatKeys = Array.isArray(seatColumns.value) ? seatColumns.value.map((c) => c.key) : []
  const map = new Map()
  for (const r of rows) {
    const key = `${r.vehicle_model_name}__${r.measurement_point}__${r.direction}`
    const bandKey = bandKeyFromLabel(r.band)
    let obj = map.get(key)
    if (!obj) {
      obj = {
        vehicle_model_name: r.vehicle_model_name,
        vehicle_model_code: r.vehicle_model_code,
        measurement_point: r.measurement_point,
        direction: r.direction,
        direction_label: r.direction_label,
        target: r.target,
        layout_image_url: r.layout_image_url,
      }
      map.set(key, obj)
    }
    // 每个频段下为各座位的值
    for (const p of seatKeys) {
      obj[`${p}__${bandKey}`] = r[p]
    }
  }
  const result = Array.from(map.values())
  // 排序：车型 -> 测点 -> 方向 X/Y/Z
  const dirOrder = { X: 0, Y: 1, Z: 2 }
  result.sort((a, b) =>
    a.vehicle_model_name.localeCompare(b.vehicle_model_name, 'zh-CN')
      || a.measurement_point.localeCompare(b.measurement_point, 'zh-CN')
      || (dirOrder[a.direction] ?? 9) - (dirOrder[b.direction] ?? 9)
  )
  return result
})

function tableSpanMethod({ column, rowIndex }) {
  const rows = Array.isArray(pivotedRows.value) ? pivotedRows.value : []
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

// 表头居中样式
function headerCellStyleCenter() { return { textAlign: 'center' } }

function getDirectionLabel(row) {
  if (!row) return '-'
  const raw = (row.direction ?? row.direction_label ?? '').toString()
  if (!raw) return '-'
  const m = raw.toUpperCase().match(/[XYZ]/)
  return m ? m[0] : raw
}

const levelStats = computed(() => {
  const stats = {
    total: 0,
    lt55: { count: 0, percent: 0 },
    r55_60: { count: 0, percent: 0 },
    r60_65: { count: 0, percent: 0 },
    gt65: { count: 0, percent: 0 }
  }
  const seatKeys = Array.isArray(seatColumns.value) ? seatColumns.value.map((c) => c.key) : []
  if (!Array.isArray(tableRows.value) || !seatKeys.length) return stats
  for (const row of tableRows.value) {
    for (const key of seatKeys) {
      const v = Number(row?.[key])
      if (!Number.isFinite(v)) continue
      stats.total += 1
      if (v < 55) stats.lt55.count += 1
      else if (v < 60) stats.r55_60.count += 1
      else if (v <= 65) stats.r60_65.count += 1
      else stats.gt65.count += 1
    }
  }
  if (stats.total > 0) {
    stats.lt55.percent = Math.round((stats.lt55.count / stats.total) * 100)
    stats.r55_60.percent = Math.round((stats.r55_60.count / stats.total) * 100)
    stats.r60_65.percent = Math.round((stats.r60_65.count / stats.total) * 100)
    stats.gt65.percent = Math.round((stats.gt65.count / stats.total) * 100)
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
  const total = Array.isArray(heatmap.value.frequency) ? heatmap.value.frequency.length : 0
  const step = Math.max(1, Math.floor(total / 10))
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
    xAxis: {
      type: 'category',
      data: heatmap.value.frequency,
      name: '频率 (Hz)',
      nameGap: 18,
      axisLabel: {
        fontSize: 10,
        rotate: 0,
        interval(index) { return index % step === 0 },
        formatter(value) {
          const n = Number(value)
          return Number.isFinite(n) ? Math.round(n) : value
        }
      }
    },
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
  await store.fetchFilters()
  await store.multiQuery()
}

async function handlePointsChange(points) {
  store.selectedPoints = Array.isArray(points) ? points : []
  await store.fetchFilters()
  await store.multiQuery()
}

async function handlePositionsChange(positions) {
  store.selectedPositions = Array.isArray(positions) ? positions : []
  await store.multiQuery()
}

async function handleDirectionsChange(directions) {
  store.selectedDirections = Array.isArray(directions) ? directions : []
  await store.multiQuery()
}

onMounted(async () => {
  await store.fetchVehicleOptions()
  await store.fetchFilters()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) { chartInstance.dispose(); chartInstance = null }
})

// 操作列：测点布置图弹窗
const layoutImageUrl = ref('')
const layoutDialogVisible = ref(false)
function openLayout(url) {
  layoutImageUrl.value = url || ''
  layoutDialogVisible.value = !!layoutImageUrl.value
}
</script>

<style scoped>
.ntf-query { display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.filter-form { max-width: 100%; display: flex; gap: 12px; align-items: center; flex-wrap: nowrap; }
.heatmap { width: 100%; height: 420px; }
.result-table { --el-table-border-color: #ebeef5; }
.ntf-cell { font-weight: 600; }
.ntf-cell--high { color: #f56c6c; }
.ntf-cell--medium { color: #e6a23c; }
.ntf-cell--low { color: #67c23a; }
.level-stats { display: flex; gap: 12px; align-items: center; }
.level-item strong { margin-right: 4px; }

/* 车辆信息卡片样式 */
.vehicle-info-card { }
/* 两列布局，适配常见两车型场景，更扁平 */
.vehicle-card-list { display: grid; grid-template-columns: repeat(2, minmax(360px, 1fr)); gap: 12px; }
.vehicle-card { font-size: 13px; }
.vehicle-card :deep(.el-card__body) { padding: 10px 12px; }
.vehicle-card-title { font-weight: 600; margin-bottom: 6px; line-height: 1.4; }
/* 卡片内部信息两列网格，压缩高度 */
.vehicle-card-rows { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); column-gap: 16px; row-gap: 6px; }
.vehicle-card-row { display: grid; grid-template-columns: 80px 1fr; align-items: center; line-height: 1.4; }
.vehicle-card-row .label { color: #606266; }
.vehicle-card-row .value { color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 小屏降级为单列，保证可读性 */
@media (max-width: 992px) {
  .vehicle-card-list { grid-template-columns: 1fr; }
  .vehicle-card-rows { grid-template-columns: 1fr; }
  .vehicle-card-row { grid-template-columns: 90px 1fr; }
}
</style>
