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
            clearable
            :loading="isLoading && !localVehicleIds.length"
            @change="handleVehicleChange"
            style="min-width: 200px;"
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
              v-for="item in filteredVehicleOptions"
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
            <el-option label="全选" value="__SELECT_ALL__" />
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
      <div ref="heatmapRef" v-show="heatmap.points.length && heatmap.frequency.length" class="heatmap" :style="{ height: heatmapHeight + 'px' }"></div>
      <el-empty v-show="!heatmap.points.length || !heatmap.frequency.length" description="暂无热力图数据" />
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
  import { HeatmapChart, CustomChart } from 'echarts/charts'
  import { GridComponent, TooltipComponent, VisualMapComponent, TitleComponent } from 'echarts/components'
  import { CanvasRenderer } from 'echarts/renderers'
  import { Search } from '@element-plus/icons-vue'
  import { useNTFQueryStore } from '@/store'

defineOptions({ name: 'NTFQuery' })

const VALUE_LEVEL = { HIGH: 'high', MEDIUM: 'medium', LOW: 'low' }

  echarts.use([HeatmapChart, CustomChart, GridComponent, TooltipComponent, VisualMapComponent, TitleComponent, CanvasRenderer])
  
  const store = useNTFQueryStore()
  const { vehicleOptions, measurementPointOptions, seatColumns, tableRows, heatmap, isLoading, error, vehicleCards } = storeToRefs(store)
  
  const localVehicleIds = ref([])
  const localPoints = ref([])
  const localPositions = ref([])
  const localDirections = ref([])
  const vehicleModelSearch = ref('')

  const filteredVehicleOptions = computed(() => {
    const keyword = vehicleModelSearch.value.trim().toLowerCase()
    const list = vehicleOptions.value || []
    if (!keyword) return list
    return list.filter((item) => {
      const name = (item?.vehicle_model_name ?? '').toString().toLowerCase()
      return name.includes(keyword)
    })
  })
// 静态的 位置 与 方向 选项（不级联）
const positionStaticOptions = ['front', 'middle', 'rear']
const directionStaticOptions = ['x', 'y', 'z']
const heatmapRef = ref(null)
let chartInstance = null

// 动态计算热力图容器高度：确保每个测点有足够行高，包括像素级间隔线
const heatmapHeight = computed(() => {
  const rows = Array.isArray(heatmap.value?.points) ? heatmap.value.points.length : 0
  if (rows === 0) return 400
  const BASE_OFFSET = 100 // 顶/底部 grid 留白
  const ROW_HEIGHT = 18   // 减小每个数据行期望行高
  const GAP_HEIGHT = 2    // 间隔行高度
  const totalDataRows = rows
  const totalGapRows = Math.max(0, rows - 1)
  // 设置最大高度限制，避免过高
  const calculatedHeight = BASE_OFFSET + totalDataRows * ROW_HEIGHT + totalGapRows * GAP_HEIGHT
  return Math.min(Math.max(400, calculatedHeight), 600) // 限制在400-600px之间
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

function buildHeatmapSeriesData(matrix) {
  if (!matrix?.length) return []
  const data = []
  matrix.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      const numeric = Number(value)
      if (!Number.isFinite(numeric)) {
        data.push([colIndex, rowIndex, null, null])
        return
      }
      // 固定颜色映射范围：49-69
      // 规则：≤49 映射到49（深蓝/紫色）；49-69 按梯度；≥69 映射到69（红色）
      const mapped = numeric <= 49 ? 49 : (numeric >= 69 ? 69 : numeric)
      // 第四个维度保留真实值供 tooltip 展示
      data.push([colIndex, rowIndex, mapped, numeric])
    })
  })
  return data
}

function renderHeatmap() {
  if (!heatmapRef.value) return
  
  // 检查 chartInstance 是否还有效，如果 DOM 被重建则需要重新初始化
  if (chartInstance) {
    try {
      const dom = chartInstance.getDom()
      if (dom !== heatmapRef.value) {
        chartInstance.dispose()
        chartInstance = null
      }
    } catch (e) {
      chartInstance = null
    }
  }

  if (!chartInstance) chartInstance = echarts.init(heatmapRef.value)

  const originalPoints = heatmap.value.points || []
  const originalMatrix = heatmap.value.matrix || []
  const originalFrequency = heatmap.value.frequency || []

  const data = buildHeatmapSeriesData(originalMatrix)
  const valueRange = computeHeatmapRange()
  const total = originalFrequency.length
  const step = Math.max(1, Math.floor(total / 10))

  const gapIndices = []
  for (let i = 0; i < originalPoints.length - 1; i += 1) gapIndices.push(i)

  const GAP_PX = 5
  const renderGapItem = (params, api) => {
    const i = api.value(0)
    const yTop = api.coord([0, i + 1])[1]
    const yBottom = api.coord([0, i])[1]
    const yMiddle = (yTop + yBottom) / 2
    const left = api.coord([-0.5, 0])[0]
    const right = api.coord([originalFrequency.length - 0.5, 0])[0]
    const width = right - left
    return {
      type: 'rect',
      silent: true,
      shape: { x: left, y: Math.round(yMiddle - GAP_PX / 2), width, height: GAP_PX },
      style: api.style({ fill: '#ffffff' })
    }
  }

  const option = {
    title: { left: 'center', text: 'Frequency vs Measurement Point', top: 10 },
    tooltip: {
      trigger: 'item',
      formatter(params) {
        const rowIndex = params.value[1]
        const point = originalPoints[rowIndex]
        const frequency = originalFrequency[params.value[0]]
        const raw = params.value?.[3]
        const value = Number.isFinite(raw) ? raw : params.value?.[2]
        const displayValue = Number.isFinite(value) ? Number(value).toFixed(2) : '-'
        return `测点：${point}<br/>频率：${frequency} Hz<br/>NTF：${displayValue}`
      }
    },
    // 调整 grid 边距：增加左侧和右侧空间
    grid: {
      top: 50,
      left: 180,    // 增加左侧边距以显示完整测点名称
      right: 75,   // 增加右侧边距避免与 visualMap 重叠
      bottom: 40
    },
    xAxis: {
      type: 'category',
      data: originalFrequency,
      name: '频率 (Hz)',
      nameGap: 18,
      nameLocation: 'middle',
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
    yAxis: {
      type: 'category',
      data: originalPoints,
      name: '测点',
      nameGap: 20,
      nameLocation: 'middle',
      axisLabel: {
        fontSize: 11,
        // 确保标签不被截断
        overflow: 'none',
        width: 130,  // 设置标签最大宽度
        ellipsis: '...'  // 超长显示省略号
      }
    },
    visualMap: {
      min: valueRange.min,
      max: valueRange.max,
      orient: 'vertical',
      right: 15,      // 调整右侧位置
      top: 'center',
      align: 'right',  // 对齐方式
      calculable: true,
      itemWidth: 20,   // 减小宽度
      itemHeight: 120, // 调整高度
      textStyle: {
        fontSize: 11
      },
      inRange: {
        color: ['#1a237e', '#3949ab', '#42a5f5', '#66bb6a', '#fdd835', '#fb8c00', '#e53935', '#b71c1c']
      }
    },
    series: [
      {
        name: 'NTF Heatmap',
        type: 'heatmap',
        data,
        label: { show: false },
        itemStyle: { borderWidth: 0 }
      },
      {
        name: 'Row Gaps',
        type: 'custom',
        renderItem: renderGapItem,
        data: gapIndices.map((i) => [i]),
        z: 5,
        silent: true
      }
    ]
  }
  chartInstance.setOption(option, true) // 使用 notMerge 确保完全更新
  chartInstance.resize()
}

function computeHeatmapRange() {
  // 固定颜色映射范围：49-69
  return { min: 49, max: 69 }
}

function handleResize() { if (chartInstance) chartInstance.resize() }

watch(
  () => heatmap.value,
  async (newValue) => {
    if (!newValue) return
    await nextTick()
    await nextTick() // 额外等待确保 DOM 完全更新
    if (newValue.points.length && newValue.frequency.length) {
      renderHeatmap()
    } else if (chartInstance) {
      chartInstance.clear()
    }
  },
  { deep: true }
)

async function handleVehicleChange(ids) {
  store.selectedVehicleIds = Array.isArray(ids) ? ids : []
  // 选择车型后加载对应的测点选项，但不立即查询数据
  await store.fetchFilters()
  // 只有同时选择了车型和测点才查询数据
  if (store.selectedVehicleIds.length > 0 && store.selectedPoints.length > 0) {
    await store.multiQuery()
  } else {
    // 清空数据
    store.resetData()
  }
}

async function handlePointsChange(points) {
  let actualPoints = Array.isArray(points) ? points : []
  
  // 处理全选逻辑
  if (actualPoints.includes('__SELECT_ALL__')) {
    // 获取当前实际选中的测点（排除全选标记）
    const currentSelected = localPoints.value.filter(p => p !== '__SELECT_ALL__')
    const allOptions = measurementPointOptions.value || []
    
    // 判断当前是否已全选（实际选中数等于总数）
    if (currentSelected.length === allOptions.length && allOptions.length > 0) {
      // 已全选，点击全选 → 取消所有
      actualPoints = []
    } else {
      // 未全选，点击全选 → 选择所有
      actualPoints = [...allOptions]
    }
  } else {
    // 移除全选标记
    actualPoints = actualPoints.filter(p => p !== '__SELECT_ALL__')
  }
  
  localPoints.value = actualPoints
  store.selectedPoints = actualPoints
  await store.fetchFilters()
  
  // 只有同时选择了车型和测点才查询数据
  if (store.selectedVehicleIds.length > 0 && store.selectedPoints.length > 0) {
    await store.multiQuery()
  } else {
    // 清空数据
    store.resetData()
  }
}

async function handlePositionsChange(positions) {
  store.selectedPositions = Array.isArray(positions) ? positions : []
  // 只有同时选择了车型和测点才查询数据
  if (store.selectedVehicleIds.length > 0 && store.selectedPoints.length > 0) {
    await store.multiQuery()
  }
}

async function handleDirectionsChange(directions) {
  store.selectedDirections = Array.isArray(directions) ? directions : []
  // 只有同时选择了车型和测点才查询数据
  if (store.selectedVehicleIds.length > 0 && store.selectedPoints.length > 0) {
    await store.multiQuery()
  }
}

onMounted(async () => {
  // 只加载车型选项，不加载其他数据
  await store.fetchVehicleOptions()
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

/* 优化热力图容器样式 */
.heatmap {
  width: 100%;
  min-height: 400px;
  max-height: 600px; /* 限制最大高度 */
}

/* 热力图卡片添加最大高度限制 */
.heatmap-card {
  max-height: 700px; /* 限制卡片最大高度 */
}

.heatmap-card :deep(.el-card__body) {
  overflow: auto; /* 内容过多时可滚动 */
}

.result-table { --el-table-border-color: #ebeef5; }
.ntf-cell { font-weight: 600; }
.ntf-cell--high { color: #f56c6c; }
.ntf-cell--medium { color: #e6a23c; }
.ntf-cell--low { color: #67c23a; }
.level-stats { display: flex; gap: 12px; align-items: center; }
.level-item strong { margin-right: 4px; }

.vehicle-model-search-option { padding: 0; cursor: default; }
.vehicle-model-search-input { width: 100%; }
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
.vehicle-model-empty { display: block; padding: 4px 12px; font-size: 12px; color: #909399; }

/* 车辆信息卡片样式 */
.vehicle-info-card { }
.vehicle-card-list { display: grid; grid-template-columns: repeat(2, minmax(360px, 1fr)); gap: 12px; }
.vehicle-card { font-size: 13px; }
.vehicle-card :deep(.el-card__body) { padding: 10px 12px; }
.vehicle-card-title { font-weight: 600; margin-bottom: 6px; line-height: 1.4; }
.vehicle-card-rows { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); column-gap: 16px; row-gap: 6px; }
.vehicle-card-row { display: grid; grid-template-columns: 80px 1fr; align-items: center; line-height: 1.4; }
.vehicle-card-row .label { color: #606266; }
.vehicle-card-row .value { color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

@media (max-width: 992px) {
  .vehicle-card-list { grid-template-columns: 1fr; }
  .vehicle-card-rows { grid-template-columns: 1fr; }
  .vehicle-card-row { grid-template-columns: 90px 1fr; }
}
</style>
