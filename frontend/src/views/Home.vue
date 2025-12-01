<template>
  <div class="screen">
    <!-- Row 1: 顶部欢迎 + KPI -->
    <section class="row row-top">
      <div class="hero">
        <div class="hero-main">
          <h1 class="title">NVH 试验智能分析平台</h1>
          <p class="subtitle">
            你好，
            <span class="subtitle-user">
              {{ userStore.fullName || userStore.username || '用户' }}
            </span>
            <span class="subtitle-dot">·</span>
            <span class="subtitle-datetime">
              <span class="subtitle-date">{{ currentDateDisplay }}</span>
              <span class="subtitle-time">{{ currentTimeDisplay }}</span>
            </span>
          </p>
          <div class="hero-actions">
            <el-button
              class="hero-primary-btn"
              type="primary"
              size="large"
              round
              @click="goToBusinessCenter"
            >
              进入业务中心
            </el-button>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card" v-for="card in kpiCards" :key="card.key">
          <div class="kpi-icon" :style="{ background: card.bg }">
            <el-icon :size="22">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="kpi-meta">
            <div class="kpi-label">{{ card.label }}</div>
            <div class="kpi-value">{{ formatNumber(card.value) }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Row 2: 趋势与分布 -->
    <section class="row grid-2 trend-row">
      <div class="chart-card">
        <div class="chart-title">总试验数据月度趋势（最近36个月）</div>
        <div ref="trendRef" class="chart-box"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">各类试验数据量分布</div>
        <div ref="distributionRef" class="chart-box"></div>
      </div>
    </section>

    <!-- Row 3: 最新车型性能看板（滚动表格） -->
    <section class="row">
      <div class="table-card">
        <div class="card-header">
          <div>
            <div class="card-title-main">最新车型性能看板</div>
            <div class="card-subtitle-main">数据来源：气密性 / 整车隔声试验</div>
          </div>
          <div class="card-extra">鼠标悬停停止滚动</div>
        </div>
        <div
          class="table-body"
          @mouseenter="pauseTableScroll"
          @mouseleave="resumeTableScroll"
        >
          <el-table
            :data="visibleVehicleRows"
            border
            stripe
            size="small"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column prop="vehicle_model_name" label="车型名称" min-width="120" />
            <el-table-column prop="production_year" label="生产年份" width="90" />
            <el-table-column label="驱动 / 悬挂" min-width="150">
              <template #default="{ row }">
                {{ formatDriveSuspension(row) }}
              </template>
            </el-table-column>
            <el-table-column label="配置" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.configuration || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="uncontrolled_leakage" label="气密性 (SCFM)" min-width="120">
              <template #default="{ row }">
                {{ formatDecimal(row.uncontrolled_leakage) }}
              </template>
            </el-table-column>
            <el-table-column prop="sound_insulation_performance" label="隔声性能 (dB)" min-width="120">
              <template #default="{ row }">
                {{ formatDecimal(row.sound_insulation_performance) }}
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!vehiclePerformance.length" class="empty-tip">暂无车型性能数据</div>
        </div>
      </div>
    </section>

    <!-- Row 4: 专项分析（雷达图 + 气味柱状图） -->
    <section class="row grid-2 row-bottom">
      <div class="chart-card">
        <div class="chart-title">整车噪声工况分析（RMS）</div>
        <div class="chart-subtitle">轮播展示最近 3 个车型</div>
        <div ref="radarRef" class="chart-box"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">整车气味评测（最近5个样品）</div>
        <div class="chart-subtitle">静态/动态前后排及均值</div>
        <div ref="odorRef" class="chart-box"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  UserFilled,
  OfficeBuilding,
  Setting,
  Refresh,
  TrendCharts,
  PieChart,
  Histogram,
  Tickets
} from '@element-plus/icons-vue'
import { useUserStore, useHomeDashboardStore } from '@/store'
import { userApi } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const homeDashboardStore = useHomeDashboardStore()

// 时间显示
const currentDateTime = ref('')
const weekdayMap = ['日', '一', '二', '三', '四', '五', '六']
let timeTimer = null

const currentDateDisplay = computed(() => {
  if (!currentDateTime.value) return ''
  const parts = currentDateTime.value.split(' ')
  if (parts.length >= 2) {
    return `${parts[0]} ${parts[1]}`
  }
  return parts[0]
})

const currentTimeDisplay = computed(() => {
  if (!currentDateTime.value) return ''
  const parts = currentDateTime.value.split(' ')
  return parts[2] || ''
})

function formatDateTime(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const w = weekdayMap[date.getDay()]
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  const ss = String(date.getSeconds()).padStart(2, '0')
  return `${y}年${m}月${d}日 星期${w} ${hh}:${mm}:${ss}`
}

function updateCurrentTime() {
  currentDateTime.value = formatDateTime(new Date())
}

function goToBusinessCenter() {
  router.push({ name: 'BusinessCenter' })
}

// KPI 数据
const kpiCards = ref([
  {
    key: 'total_tests',
    label: '总试验数',
    value: 0,
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#2563eb,#3b82f6)'
  },
  {
    key: 'year_tests',
    label: '本年度试验数',
    value: 0,
    icon: Histogram,
    bg: 'linear-gradient(135deg,#22c55e,#16a34a)'
  },
  {
    key: 'vehicle_models',
    label: '车型库总数',
    value: 0,
    icon: Tickets,
    bg: 'linear-gradient(135deg,#f97316,#ea580c)'
  },
  {
    key: 'samples',
    label: '样品总数',
    value: 0,
    icon: PieChart,
    bg: 'linear-gradient(135deg,#ec4899,#db2777)'
  }
])

// 图表 refs
const trendRef = ref(null)
const distributionRef = ref(null)
const radarRef = ref(null)
const odorRef = ref(null)

let trendChart = null
let distributionChart = null
let radarChart = null
let odorChart = null

// 车型性能滚动表
const vehiclePerformance = ref([])
const tableScrollOffset = ref(0)
const tableScrollPaused = ref(false)
const visibleRowsCount = 8
let tableScrollTimer = null

const repeatedVehicleRows = computed(() => {
  if (!vehiclePerformance.value.length) return []
  return [...vehiclePerformance.value, ...vehiclePerformance.value]
})

const visibleVehicleRows = computed(() => {
  const start = tableScrollOffset.value
  const end = start + visibleRowsCount
  return repeatedVehicleRows.value.slice(start, end)
})

// 路由
const goToBusiness = () => router.push('/business')
const goToPermission = () => router.push('/permission')
const goToIAQCenter = () => router.push('/vehicle-data/iaq')

// 刷新用户信息
const refreshUserInfo = async () => {
  try {
    const info = await userApi.getUserInfo()
    userStore.setUserInfo(info)
  } catch (e) {
    console.error(e)
  }
}

// 加载并渲染数据（使用 Pinia 缓存）
const reloadAll = async () => {
  try {
    await homeDashboardStore.load()
    const data = homeDashboardStore.dashboardData || {}

    // KPI
    const kpis = data.kpis || {}
    kpiCards.value = kpiCards.value.map(card => ({
      ...card,
      value: kpis[card.key] ?? 0
    }))

    // 车型性能表
    vehiclePerformance.value = data.vehicle_performance || []
    resetTableScroll()

    await nextTick()

    renderTrendChart(data.trend_36_months || {})
    renderDistributionChart(data.test_type_distribution || [])
    renderRadarChart(data.noise_radar || {})
    renderOdorChart(data.odor_bars || [])
  } catch (err) {
    console.error(err)
    ElMessage.error('加载首页数据失败')
  }
}

// 格式化
const formatNumber = (val) => {
  if (val == null || isNaN(val)) return 0
  if (val >= 10000) {
    return (val / 10000).toFixed(1) + '万'
  }
  return val
}

const formatDecimal = (value) => {
  if (value == null || isNaN(value)) return '-'
  return Number(value).toFixed(1)
}

// 图表：月度趋势
function renderTrendChart(trend) {
  if (!trendRef.value) return
  if (!trendChart) trendChart = echarts.init(trendRef.value)
  const months = trend.months || []
  const counts = trend.counts || []

  const total = months.length
  let dataZoom = []
  if (total > 0) {
    const visibleCount = Math.min(10, total)
    const startIndex = total - visibleCount
    const endIndex = total - 1
    dataZoom = [
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        startValue: startIndex,
        endValue: endIndex,
        height: 22,
        bottom: 10
      }
    ]
  }

  trendChart.setOption({
    grid: { left: 50, right: 20, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { color: '#6b7280', rotate: 40 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    tooltip: { trigger: 'axis' },
    dataZoom,
    series: [
      {
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#2563eb' },
        itemStyle: { color: '#2563eb' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37,99,235,0.35)' },
            { offset: 1, color: 'rgba(37,99,235,0.02)' }
          ])
        }
      }
    ]
  })
}

// 图表：试验类型分布
function renderDistributionChart(list) {
  if (!distributionRef.value) return
  if (!distributionChart) distributionChart = echarts.init(distributionRef.value)
  const names = list.map(item => item.label)
  const values = list.map(item => item.count || 0)
  distributionChart.setOption({
    grid: { left: 120, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#4b5563' }
    },
    tooltip: { trigger: 'axis' },
    series: [
      {
        type: 'bar',
        data: values,
        barWidth: 18,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#0ea5e9' },
            { offset: 1, color: '#22c55e' }
          ])
        }
      }
    ]
  })
}

// 图表：噪声雷达图
function renderRadarChart(noiseRadar) {
  if (!radarRef.value) return
  if (!radarChart) radarChart = echarts.init(radarRef.value)
  const conditions = noiseRadar.conditions || []
  const series = noiseRadar.series || []
  const indicators = conditions.map(item => ({
    name: item.label || item.work_condition || `工况${item.id}`,
    max: 100
  }))

  const seriesData = series.map(item => ({
    name: item.vehicle_model_name,
    value: (item.values || []).map(v => (v == null ? 0 : Number(v)))
  }))

  radarChart.setOption({
    tooltip: {},
    legend: {
      data: series.map(s => s.vehicle_model_name),
      bottom: 4,
      textStyle: { color: '#111827', fontSize: 12 }
    },
    radar: {
      indicator: indicators,
      radius: '60%',
      center: ['50%', '40%'],
      axisName: {
        color: '#111827',
        fontSize: 13,
        fontWeight: '600',
        padding: [2, 4]
      },
      splitLine: { lineStyle: { color: ['#e5e7eb'] } },
      splitArea: { areaStyle: { color: ['#f9fafb', '#eff6ff'] } },
      axisLine: { lineStyle: { color: '#cbd5f5' } }
    },
    series: [
      {
        type: 'radar',
        data: seriesData,
        areaStyle: { opacity: 0.15 }
      }
    ]
  })
}

// 图表：整车气味柱状图
function renderOdorChart(odorBars) {
  if (!odorRef.value) return
  if (!odorChart) odorChart = echarts.init(odorRef.value)
  const xLabels = ['静态前排', '动态前排', '静态后排', '动态后排', '均值']
  const series = odorBars.map(sample => ({
    name:
      [sample.project_name, sample.development_stage, sample.status]
        .filter(Boolean)
        .join('-') ||
      sample.project_name ||
      sample.part_name ||
      `样品${sample.id}`,
    type: 'bar',
    data: [
      Number(sample.odor_static_front || 0),
      Number(sample.odor_dynamic_front || 0),
      Number(sample.odor_static_rear || 0),
      Number(sample.odor_dynamic_rear || 0),
      Number(sample.odor_mean || 0)
    ]
  }))

  odorChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: series.map(s => s.name),
      top: 0,
      textStyle: { color: '#4b5563' }
    },
    grid: { left: 60, right: 20, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: xLabels,
      axisLabel: { color: '#4b5563' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 10,
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series
  })
}

// 车型性能辅助
const formatDriveSuspension = (row) => {
  const drive = row.drive_type || '—'
  const suspension = row.suspension_type || '—'
  return `${drive} / ${suspension}`
}

// 表格滚动控制
function resetTableScroll() {
  clearTableScrollTimer()
  tableScrollOffset.value = 0
  if (vehiclePerformance.value.length > visibleRowsCount) {
    startTableScroll()
  }
}

function startTableScroll() {
  if (tableScrollTimer || tableScrollPaused.value) return
  tableScrollTimer = setInterval(() => {
    const total = vehiclePerformance.value.length
    if (total <= visibleRowsCount) return
    const maxOffset = total
    tableScrollOffset.value = (tableScrollOffset.value + 1) % maxOffset
  }, 2500)
}

function clearTableScrollTimer() {
  if (tableScrollTimer) {
    clearInterval(tableScrollTimer)
    tableScrollTimer = null
  }
}

function pauseTableScroll() {
  tableScrollPaused.value = true
  clearTableScrollTimer()
}

function resumeTableScroll() {
  tableScrollPaused.value = false
  startTableScroll()
}

// 自适应
function handleResize() {
  trendChart && trendChart.resize()
  distributionChart && distributionChart.resize()
  radarChart && radarChart.resize()
  odorChart && odorChart.resize()
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  updateCurrentTime()
  timeTimer = setInterval(updateCurrentTime, 1000)
  await refreshUserInfo()
  await reloadAll()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart && trendChart.dispose()
  distributionChart && distributionChart.dispose()
  radarChart && radarChart.dispose()
  odorChart && odorChart.dispose()
  clearTableScrollTimer()
  if (timeTimer) {
    clearInterval(timeTimer)
  }
})
</script>

<style scoped>
.screen {
  padding: 16px;
  min-height: calc(100vh - 32px);
  background: radial-gradient(1200px 600px at 10% -10%, #e6f0ff 0%, transparent 70%),
              radial-gradient(1000px 600px at 110% 10%, #fff0f0 0%, transparent 60%),
              linear-gradient(180deg, #f9fbff 0%, #f6f7fb 100%);
}

.row {
  margin-top: 16px;
}

.row:first-of-type {
  margin-top: 0;
}

.row-top {
  display: grid;
  grid-template-columns: minmax(420px, 440px) 1fr;
  gap: 12px;
  align-items: stretch;
}

.row.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.trend-row .chart-card {
  height: 100%;
}

.row-bottom .chart-card {
  height: 100%;
  min-height: 360px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 18px;
  border-radius: 14px;
  background: rgba(255,255,255,0.86);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(226,232,240,0.9);
}

.hero-main {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  flex: 1;
}

.title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subtitle {
  margin: 0;
  margin-top: 6px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 15px;
  font-weight: 500;
  color: #4b5563;
  letter-spacing: 0.01em;
}

.subtitle-user {
  font-weight: 600;
  color: #1d4ed8;
}

.subtitle-dot {
  color: #9ca3af;
}

.subtitle-datetime {
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(59,130,246,0.06), rgba(59,130,246,0.02));
  box-shadow: 0 8px 18px rgba(37,99,235,0.12);
  color: #0f172a;
  font-size: 14px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

.subtitle-date,
.subtitle-time {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.04em;
}

.subtitle-date {
  font-weight: 500;
}

.subtitle-time {
  font-size: 15px;
  font-weight: 600;
}

.hero-actions {
  margin-top: 18px;
}

.hero-primary-btn {
  padding: 0 22px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.06em;
  box-shadow: 0 14px 30px rgba(37,99,235,0.32);
}

.hero-description {
  margin: 0;
  margin-top: 2px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-entry-links {
  letter-spacing: 0.02em;
}

.hero-entry {
  transition: color 0.2s ease;
}

.hero-entry:hover {
  color: #2563eb;
}

.hero-entry-separator {
  color: #9ca3af;
}

.hero-side {
  display: none;
}

.hero-time-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.hero-time-value {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #111827;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0,1fr));
  gap: 12px;
}
.kpi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #eef0f5;
  transition: transform .2s ease, box-shadow .2s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
.kpi-icon {
  width: 44px; height: 44px; border-radius: 10px;
  color: #fff; display: flex; align-items: center; justify-content: center;
}
.kpi-meta { flex: 1; }
.kpi-label { color: #8a93a6; font-size: 12px; }
.kpi-value { color: #1f2d3d; font-size: 20px; font-weight: 700; }

.chart-card {
  background: #ffffff;
  border: 1px solid #eef0f5;
  border-radius: 12px;
  padding: 12px;
  min-height: 280px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
.chart-card:hover { border-color: #d7e3ff; box-shadow: 0 8px 20px rgba(59,118,246,0.08); }
.chart-title { color: #2b3a55; font-weight: 600; margin-bottom: 4px; }
.chart-subtitle { color: #9ca3af; font-size: 12px; margin-bottom: 4px; }
.chart-box { width: 100%; height: 260px; }
.row-bottom .chart-box { height: 360px; }

.table-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eef0f5;
  padding: 16px 16px 12px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-title-main {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.card-subtitle-main {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

.card-extra {
  font-size: 12px;
  color: #9ca3af;
}

.table-body {
  position: relative;
  margin-top: 6px;
}

.table-body :deep(.el-table) {
  font-size: 13px;
}

.table-body :deep(.el-table__header-wrapper th) {
  font-size: 13px;
  font-weight: 600;
}

.empty-tip {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #9ca3af;
}

@media (max-width: 992px) {
  .row-top {
    grid-template-columns: 1fr;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0,1fr));
  }
  .row.grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
