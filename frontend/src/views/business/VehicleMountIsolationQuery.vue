<template>
  <div class="vehicle-mount-isolation-query">
    <!-- 条件区 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">整车悬置隔振率查询</span>
        </div>
      </template>

      <el-form label-width="90px" class="search-form">
        <el-row :gutter="16">
          <el-col :span="10">
            <el-form-item label="车型" required>
              <el-select
                v-model="selectedVehicles"
                placeholder="请选择车型"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :loading="store.loadingVehicles"
                value-key="id"
                style="width: 100%"
                @change="onVehiclesChange"
              >
                <el-option
                  v-for="item in store.vehicleOptions"
                  :key="item.id"
                  :label="`${item.name}`"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="测点">
              <el-select
                v-model="store.selectedPoints"
                :disabled="!selectedVehicles.length"
                placeholder="请选择测点"
                multiple
                collapse-tags
                collapse-tags-tooltip
                :loading="store.loadingPoints"
                style="width: 100%"
              >
                <el-option
                  v-for="item in store.measuringPointOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="方向">
              <el-checkbox-group v-model="store.selectedDirections">
                <el-checkbox label="X" />
                <el-checkbox label="Y" />
                <el-checkbox label="Z" />
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-actions">
          <el-button type="primary" :loading="store.loadingQuery" :disabled="!store.canQuery" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 测试信息卡片区域 -->
    <el-card class="info-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试信息</span>
        </div>
      </template>

      <div class="info-card-list" v-if="store.testInfoCards.length">
        <div v-for="item in store.testInfoCards" :key="item.vehicle_id" class="test-info-card">
          <div class="vehicle-name">{{ item.vehicle_name }}</div>
          <div class="info-row"><span class="label">测试人员：</span><span class="value">{{ item.test_engineer || '-' }}</span></div>
          <div class="info-row"><span class="label">测试地点：</span><span class="value">{{ item.test_location || '-' }}</span></div>
          <div class="info-row"><span class="label">测试工况：</span><span class="value">{{ item.test_condition || '-' }}</span></div>
          <div class="info-row"><span class="label">测试时间：</span><span class="value">{{ formatDate(item.test_date) }}</span></div>
        </div>
      </div>
      <el-empty v-else description="未选择车型或暂无测试信息" />
    </el-card>

    <!-- 振动曲线 -->
    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">悬置振动加速度对比</span>
          <span class="card-subtitle">{{ store.queryResult?.x_axis_label || '' }}</span>
        </div>
      </template>
      <div v-if="vibrationSeries.length" ref="vibrationRef" class="echarts-container" />
      <el-empty v-else description="暂无振动曲线数据" />
    </el-card>

    <!-- 隔振率曲线 -->
    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">悬置隔振率性能分析</span>
          <span class="card-subtitle">{{ store.queryResult?.x_axis_label || '' }}</span>
        </div>
      </template>
      <div v-if="isolationSeries.length" ref="isolationRef" class="echarts-container" />
      <el-empty v-else description="暂无隔振率曲线数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useVehicleMountIsolationQueryStore } from '@/store/vehicleMountIsolationQuery'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, ToolboxComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, ToolboxComponent, CanvasRenderer])

defineOptions({ name: 'VehicleMountIsolationQuery' })

const store = useVehicleMountIsolationQueryStore()

// 本地选择状态（用于回滚）
const selectedVehicles = ref([])
let lastValidVehicles = []

const onVehiclesChange = async () => {
  store.setSelectedVehicles(selectedVehicles.value)
  if (!store.validateEnergyType()) {
    selectedVehicles.value = lastValidVehicles
    store.setSelectedVehicles(lastValidVehicles)
    return
  }
  lastValidVehicles = [...selectedVehicles.value]
  await store.loadMeasuringPoints()
  store.setSelectedPoints([])
}

// 工具函数
const formatDate = (d) => {
  if (!d) return '-'
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return '-'
  const pad = (n) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}/${pad(dt.getMonth() + 1)}/${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`
}

// 查询
const handleSearch = async () => {
  await store.queryData()
  await nextTick()
  renderCharts()
}

const handleReset = () => {
  store.reset()
  selectedVehicles.value = []
  disposeCharts()
}

// 构造图表数据
const vibrationRef = ref(null)
const isolationRef = ref(null)
let vibrationChart = null
let isolationChart = null

const xAxisData = computed(() => store.queryResult?.data?.[0]?.speed_or_rpm || [])

const vibrationSeries = computed(() => {
  const res = []
  if (!store.queryResult?.data) return res
  const dirs = store.selectedDirections
  const dirKey = { X: 'x', Y: 'y', Z: 'z' }
  store.queryResult.data.forEach(item => {
    dirs.forEach(D => {
      const k = dirKey[D]
      const group = item[k]
      if (!group) return
      res.push({
        name: `${item.vehicle_name}-${item.measuring_point}-${D}-主动端`,
        type: 'line', data: group.active || [], symbol: 'circle', symbolSize: 6, lineStyle: { width: 2 }
      })
      res.push({
        name: `${item.vehicle_name}-${item.measuring_point}-${D}-被动端`,
        type: 'line', data: group.passive || [], symbol: 'circle', symbolSize: 6, lineStyle: { width: 2, type: 'dashed' }
      })
    })
  })
  return res
})

const isolationSeries = computed(() => {
  const res = []
  if (!store.queryResult?.data) return res
  const dirs = store.selectedDirections
  const dirKey = { X: 'x', Y: 'y', Z: 'z' }
  store.queryResult.data.forEach(item => {
    dirs.forEach(D => {
      const k = dirKey[D]
      const group = item[k]
      if (!group) return
      res.push({
        name: `${item.vehicle_name}-${item.measuring_point}-${D}-隔振率`,
        type: 'line', data: group.isolation || [], symbol: 'circle', symbolSize: 6, lineStyle: { width: 2 }
      })
    })
  })
  return res
})

const vibrationOption = computed(() => ({
  title: { text: '悬置振动加速度对比', left: 'center' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { type: 'scroll', bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  toolbox: { feature: { dataZoom: { yAxisIndex: 'none' }, saveAsImage: {}, dataView: { readOnly: true } } },
  xAxis: { type: 'category', name: store.queryResult?.x_axis_label || '', data: xAxisData.value },
  yAxis: { type: 'value', name: '振动加速度 (m/s²)' },
  series: vibrationSeries.value
}))

const isolationOption = computed(() => ({
  title: { text: '悬置隔振率性能分析', left: 'center' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { type: 'scroll', bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  toolbox: { feature: { dataZoom: { yAxisIndex: 'none' }, saveAsImage: {}, dataView: { readOnly: true } } },
  xAxis: { type: 'category', name: store.queryResult?.x_axis_label || '', data: xAxisData.value },
  yAxis: { type: 'value', name: '隔振率 (dB)' },
  series: isolationSeries.value
}))

const renderCharts = () => {
  // 振动
  if (vibrationRef.value) {
    if (!vibrationChart) vibrationChart = echarts.init(vibrationRef.value)
    vibrationChart.setOption(vibrationOption.value, true)
  }
  // 隔振率
  if (isolationRef.value) {
    if (!isolationChart) isolationChart = echarts.init(isolationRef.value)
    isolationChart.setOption(isolationOption.value, true)
  }
}

const disposeCharts = () => {
  if (vibrationChart) { vibrationChart.dispose(); vibrationChart = null }
  if (isolationChart) { isolationChart.dispose(); isolationChart = null }
}

watch(() => [store.queryResult, store.selectedDirections], async () => {
  await nextTick()
  renderCharts()
})

onMounted(async () => {
  await store.initialize()
})

onBeforeUnmount(() => {
  disposeCharts()
})

defineExpose({})
</script>

<style scoped>
.vehicle-mount-isolation-query { display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.card-subtitle { font-size: 12px; color: #909399; }
.search-form { padding-top: 8px; }
.form-actions { display: flex; gap: 12px; margin-top: 8px; }
.info-card-list { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 4px; }
.test-info-card { min-width: 320px; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; background: #fff; }
.vehicle-name { font-weight: 600; margin-bottom: 8px; }
.info-row { margin: 4px 0; font-size: 13px; }
.info-row .label { color: #606266; margin-right: 6px; }
.echarts-container { width: 100%; height: 480px; }
</style>

