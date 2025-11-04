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
        <!-- 第一行：车型、测点、按钮 同行显示 -->
        <el-row :gutter="12">
          <el-col :span="8">
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
          <el-col :span="8">
            <el-form-item label=" ">
              <div class="form-actions">
                <el-button type="primary" :loading="store.loadingQuery" :disabled="!store.canQuery" @click="handleSearch">查询</el-button>
                <el-button @click="handleReset">重置</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 第二行：方向选择 -->
        <el-row :gutter="12">
          <el-col :span="24">
            <el-form-item label="方向">
              <el-checkbox-group v-model="store.selectedDirections">
                <el-checkbox label="X" />
                <el-checkbox label="Y" />
                <el-checkbox label="Z" />
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
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

    <!-- 测试布置图弹窗 -->
    <el-dialog v-model="imageDialogVisible" title="测试布置图" width="60%" @close="closeImageDialog">
      <div v-if="currentImageData && currentImageData.layout_image_path" class="image-container">
        <img :src="getImageUrl(currentImageData.layout_image_path)" alt="测试布置图" class="test-image" @error="(e) => handleImageError(e, { showMessage: true })" />
      </div>
      <div v-else class="no-image">
        <el-empty description="暂无测试图" />
      </div>
      <template #footer>
        <el-button @click="closeImageDialog">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useVehicleMountIsolationQueryStore } from '@/store/vehicleMountIsolationQuery'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, ToolboxComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getImageUrl, handleImageError } from '@/utils/imageService'

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
  if (typeof d === 'string') {
    // 仅取日期部分，统一为YYYY-MM-DD
    const s = d.trim()
    if (s.length >= 10) return s.slice(0, 10).replaceAll('/', '-')
  }
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return '-'
  return dt.toISOString().slice(0, 10)
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

// 格式化横坐标名称：将括号部分换行，解决显示不全问题
const xAxisName = computed(() => {
  const raw = store.queryResult?.x_axis_label || ''
  if (!raw) return ''
  // 处理类似 "速度 (km/h)" 或 "速度(km/h)" 的情况
  const m = raw.match(/^(.*?)[\s]*\(([^)]*)\)$/)
  if (m) return `${m[1]}\n(${m[2]})`
  return raw
})

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
        type: 'line',
        data: (group.active || []).map(v => ({ value: v, itemData: item })),
        symbol: 'circle', symbolSize: 6, lineStyle: { width: 2 }
      })
      res.push({
        name: `${item.vehicle_name}-${item.measuring_point}-${D}-被动端`,
        type: 'line',
        data: (group.passive || []).map(v => ({ value: v, itemData: item })),
        symbol: 'circle', symbolSize: 6, lineStyle: { width: 2, type: 'dashed' }
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
        type: 'line',
        data: (group.isolation || []).map(v => ({ value: v, itemData: item })),
        symbol: 'circle', symbolSize: 6, lineStyle: { width: 2 }
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
  xAxis: { type: 'category', name: xAxisName.value, nameGap: 28, nameLocation: 'end', data: xAxisData.value },
  yAxis: { type: 'value', name: '振动加速度 (m/s²)' },
  series: vibrationSeries.value
}))

const isolationOption = computed(() => ({
  title: { text: '悬置隔振率性能分析', left: 'center' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { type: 'scroll', bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  toolbox: { feature: { dataZoom: { yAxisIndex: 'none' }, saveAsImage: {}, dataView: { readOnly: true } } },
  xAxis: { type: 'category', name: xAxisName.value, nameGap: 28, nameLocation: 'end', data: xAxisData.value },
  yAxis: { type: 'value', name: '隔振率 (dB)' },
  series: isolationSeries.value
}))

const renderCharts = () => {
  // 振动
  if (vibrationRef.value) {
    if (!vibrationChart) vibrationChart = echarts.init(vibrationRef.value)
    vibrationChart.setOption(vibrationOption.value, true)
    // 绑定点击事件，弹出图片
    vibrationChart.off('click')
    vibrationChart.on('click', (params) => {
      if (params && params.data && params.data.itemData) {
        showImageDialog(params.data.itemData)
      }
    })
  }
  // 隔振率
  if (isolationRef.value) {
    if (!isolationChart) isolationChart = echarts.init(isolationRef.value)
    isolationChart.setOption(isolationOption.value, true)
    // 绑定点击事件，弹出图片
    isolationChart.off('click')
    isolationChart.on('click', (params) => {
      if (params && params.data && params.data.itemData) {
        showImageDialog(params.data.itemData)
      }
    })
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

// 弹窗状态与方法
const imageDialogVisible = ref(false)
const currentImageData = ref(null)
const showImageDialog = (data) => {
  currentImageData.value = data || null
  imageDialogVisible.value = true
}
const closeImageDialog = () => {
  imageDialogVisible.value = false
  currentImageData.value = null
}
</script>

<style scoped>
.vehicle-mount-isolation-query { display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.card-subtitle { font-size: 12px; color: #909399; }
.search-form { padding-top: 8px; }
.form-actions { display: flex; gap: 12px; justify-content: flex-start; }
.info-card-list { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 4px; }
.test-info-card { min-width: 320px; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; background: #fff; }
.vehicle-name { font-weight: 600; margin-bottom: 8px; }
.info-row { margin: 4px 0; font-size: 13px; }
.info-row .label { color: #606266; margin-right: 6px; }
.echarts-container { width: 100%; height: 480px; }

.image-container { text-align: center; padding: 12px; background-color: #f5f7fa; border-radius: 6px; }
.test-image { max-width: 100%; max-height: 60vh; border-radius: 4px; }
.no-image { padding: 24px; text-align: center; }
</style>
