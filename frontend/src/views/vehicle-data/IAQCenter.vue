<template>
  <div class="iaq-page">
    <section class="header-panel">
      <div class="title-section">
        <div class="logo-chip">IAQ</div>
        <div class="title-text">
          <h1>整车空气质量（VOC & 气味）监控大屏</h1>
          <p>Indoor Air Quality Monitoring Wall</p>
        </div>
      </div>
      <div class="time-section">
        <span class="time-label">当前时间</span>
        <span class="time-value">{{ currentTime }}</span>
      </div>
    </section>

    <section class="kpi-grid">
      <div class="kpi-card" v-for="item in kpiItems" :key="item.key">
        <div class="kpi-label">{{ item.label }}</div>
        <div class="kpi-value">
          <span
            v-for="(digit, idx) in splitDigits(item.value)"
            :key="`${item.key}-${idx}`"
            class="flip-digit"
          >
            {{ digit }}
          </span>
        </div>
        <div class="kpi-desc">{{ item.desc }}</div>
      </div>
    </section>

    <section class="monitor-board">
      <div class="monitor-grid">
        <div class="monitor-block">
          <div class="block-header">
            <h3>VOC完成量监控</h3>
            <span>整车 vs 零部件</span>
          </div>
          <div class="chart" ref="vocBarRef"></div>
        </div>

        <div class="monitor-block">
          <div class="block-header">
            <h3>各项目试验次数对比</h3>
            <span>整车 vs 零部件（三维柱状图）</span>
          </div>
          <div class="chart large" ref="projectBar3dRef"></div>
        </div>

        <div class="monitor-block">
          <div class="block-header">
            <h3>气味完成量监控</h3>
            <span>整车 vs 零部件</span>
          </div>
          <div class="chart" ref="odorBarRef"></div>
        </div>
      </div>
    </section>

    <section class="bottom-board">
      <div class="trend-block monitor-block">
        <div class="block-header">
          <h3>月度测试完成量趋势</h3>
          <span>{{ currentYear }} 年</span>
        </div>
        <div class="chart large" ref="monthlyTrendRef"></div>
      </div>

      <div class="list-block monitor-block">
        <div class="block-header">
          <h3>最新检测数据滚动列表</h3>
          <span>最近 40 条 | 鼠标悬停暂停</span>
        </div>
        <div class="list-header">
          <span>测试时间</span>
          <span>项目</span>
          <span>零部件</span>
          <span>样品号</span>
          <span>TVOC</span>
          <span>气味等级</span>
        </div>
        <div
          class="list-body"
          @mouseenter="pauseScroll"
          @mouseleave="resumeScroll"
        >
          <div
            class="list-wrapper"
            :style="{ transform: `translateY(-${scrollOffset}px)` }"
          >
            <div
              v-for="(row, idx) in repeatedLatestList"
              :key="`${row.id}-${idx}`"
              class="list-row"
              @click="gotoVocPage({ project_name: row.project_name || undefined })"
            >
              <span>{{ formatDateDisplay(row.test_date) }}</span>
              <span>{{ row.project_name || '-' }}</span>
              <span>{{ row.part_name || '-' }}</span>
              <span>{{ row.sample_no || '-' }}</span>
              <span>{{ formatDecimal(row.tvoc) }}</span>
              <span>{{ formatDecimal(row.odor_mean, 1) }}</span>
            </div>
          </div>
          <div v-if="!latestList.length" class="empty-state">
            暂无数据
          </div>
        </div>
        <div class="list-footer">
          <div class="scroll-hint">↓ 自动滚动显示最近 40 条数据</div>
          <div class="scroll-controls">
            <button type="button" @click="toggleScroll">
              {{ scrollPaused ? '继续滚动' : '暂停滚动' }}
            </button>
            <button type="button" @click="fetchDashboard" :disabled="loading">
              手动刷新
            </button>
          </div>
        </div>
      </div>
    </section>

    <div v-if="loading" class="loading-mask">
      <span>数据加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import 'echarts-gl'

import vocApi from '@/api/voc'

const router = useRouter()

const loading = ref(false)
const dashboardData = ref(null)
const currentTime = ref('')
const currentYear = new Date().getFullYear()

const vocVehicleRef = ref(null)
const vocPartsRef = ref(null)
const odorVehicleRef = ref(null)
const odorPartsRef = ref(null)
const vocBarRef = ref(null)
const odorBarRef = ref(null)
const projectBar3dRef = ref(null)
const monthlyTrendRef = ref(null)

const chartRefs = {
  vocVehicle: vocVehicleRef,
  vocParts: vocPartsRef,
  odorVehicle: odorVehicleRef,
  odorParts: odorPartsRef,
  projectBar3d: projectBar3dRef,
  monthlyTrend: monthlyTrendRef,
  vocBar: vocBarRef,
  odorBar: odorBarRef
}

const chartInstances = {}
const chartHandlers = {}

const scrollOffset = ref(0)
const scrollPaused = ref(false)
const rowHeight = 48
const scrollStep = 1
const scrollInterval = 40

let timeTimer = null
let refreshTimeout = null
let scrollTimer = null

const kpiItems = computed(() => {
  const kpis = dashboardData.value?.kpis || {}
  return [
    { key: 'project_total', label: '项目总数', value: kpis.project_total ?? 0, desc: 'SampleInfo项目去重' },
    { key: 'sample_total', label: '样品总数', value: kpis.sample_total ?? 0, desc: 'SampleInfo记录数' },
    { key: 'substance_total', label: '物质库总量', value: kpis.substance_total ?? 0, desc: 'Substance记录数' },
    { key: 'annual_test_total', label: '年度测试总次数', value: kpis.annual_test_total ?? 0, desc: `${currentYear} 年` }
  ]
})

const vocGauge = computed(() => dashboardData.value?.voc_gauge || { vehicle: {}, parts: {} })
const odorGauge = computed(() => dashboardData.value?.odor_gauge || { vehicle: {}, parts: {} })
const latestList = computed(() => dashboardData.value?.latest_records || [])
const repeatedLatestList = computed(() => latestList.value.concat(latestList.value))

const splitDigits = (value) => {
  return formatNumber(value).split('')
}

const formatNumber = (value) => {
  const safeValue = Number(value ?? 0)
  return safeValue.toLocaleString('zh-CN')
}

const formatDecimal = (value, fraction = 3) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  return Number(value).toFixed(fraction)
}

const formatDateDisplay = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

const updateClock = () => {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(
    now.getHours()
  )}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

const ensureChartInstance = (key) => {
  const dom = chartRefs[key]?.value
  if (!dom) return null
  if (!chartInstances[key]) {
    chartInstances[key] = echarts.init(dom)
  }
  return chartInstances[key]
}

const buildGaugeOption = (title, payload = {}) => {
  const cumulative = Number(payload?.cumulative_total ?? 0)
  const annual = Number(payload?.annual_total ?? 0)
  const axisMax = Math.max(cumulative, annual, 1)
  const gaugeMax = Math.ceil(axisMax * 1.2)
  const ratio = gaugeMax ? cumulative / gaugeMax : 0
  const innerRatio = gaugeMax ? annual / gaugeMax : 0

  return {
    title: {
      text: title,
      left: 'center',
      top: 10,
      textStyle: { color: '#cfd7ff', fontSize: 14, fontWeight: 500 }
    },
    tooltip: {
      formatter: ({ seriesIndex, value }) => (seriesIndex === 0 ? `累计完成量：${value}` : `年度完成量：${value}`)
    },
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: gaugeMax,
        splitNumber: 4,
        axisLine: {
          lineStyle: {
            width: 14,
            color: [
              [ratio, '#43f1ff'],
              [1, 'rgba(67, 241, 255, 0.1)']
            ]
          }
        },
        pointer: { show: false },
        detail: {
          fontSize: 28,
          color: '#fff',
          valueAnimation: true,
          formatter: '{value}',
          offsetCenter: [0, '40%']
        },
        title: {
          fontSize: 13,
          color: '#90a4ff',
          offsetCenter: [0, '70%']
        },
        data: [{ value: cumulative, name: '累计' }]
      },
      {
        type: 'gauge',
        radius: '65%',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: gaugeMax,
        axisLine: {
          lineStyle: {
            width: 10,
            color: [
              [innerRatio, '#ff9e4f'],
              [1, 'rgba(255, 158, 79, 0.15)']
            ]
          }
        },
        pointer: { show: false },
        detail: {
          fontSize: 16,
          color: '#ffd28a',
          offsetCenter: [0, '-30%'],
          valueAnimation: true,
          formatter: (value) => `年度 ${value}`
        },
        title: { show: false },
        data: [{ value: annual }]
      }
    ]
  }
}

const renderGaugeChart = (key, title, payload) => {
  const chart = ensureChartInstance(key)
  if (!chart) return
  chart.setOption(buildGaugeOption(title, payload), true)
}

const buildCompletionBarOption = (gauge = {}) => {
  const veh = gauge?.vehicle || {}
  const part = gauge?.parts || {}
  const categories = ['整车', '零部件']
  const annual = [Number(veh.annual_total || 0), Number(part.annual_total || 0)]
  const cumulative = [Number(veh.cumulative_total || 0), Number(part.cumulative_total || 0)]
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 8, data: ['年度', '累计'], textStyle: { color: '#6a7485' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: categories,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#dfe3ea' } },
      axisLabel: { color: '#6a7485' }
    },
    yAxis: {
      type: 'value',
      name: '试验次数',
      nameTextStyle: { color: '#6a7485' },
      axisLine: { lineStyle: { color: '#dfe3ea' } },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
      axisLabel: { color: '#6a7485' }
    },
    series: [
      {
        name: '年度',
        type: 'bar',
        data: annual,
        barWidth: 28,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b76f6' },
            { offset: 1, color: '#5b8ff9' }
          ])
        }
      },
      {
        name: '累计',
        type: 'bar',
        data: cumulative,
        barWidth: 28,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f59e0b' },
            { offset: 1, color: '#fbbf24' }
          ])
        }
      }
    ]
  }
}

const renderCompletionBar = (key, gauge) => {
  const chart = ensureChartInstance(key)
  if (!chart) return
  chart.setOption(buildCompletionBarOption(gauge), true)
}

const renderProjectBar3d = (list = []) => {
  const chart = ensureChartInstance('projectBar3d')
  if (!chart) return

  const projects = list.map((item) => item.project_name)
  const categories = ['整车', '零部件']
  const dataSource = []
  list.forEach((item, projectIndex) => {
    dataSource.push({
      value: [projectIndex, 0, item.vehicle_tests || 0],
      projectName: item.project_name,
      category: '整车'
    })
    dataSource.push({
      value: [projectIndex, 1, item.part_tests || 0],
      projectName: item.project_name,
      category: '零部件'
    })
  })

  chart.setOption(
    {
      tooltip: {
        formatter: (params) =>
          `${params.data.projectName} - ${params.data.category}<br/>测试次数：${params.value[2]}`
      },
      xAxis3D: {
        type: 'category',
        data: projects,
        axisLabel: { color: '#8a93a6' }
      },
      yAxis3D: {
        type: 'category',
        data: categories,
        axisLabel: { color: '#8a93a6' }
      },
      zAxis3D: {
        type: 'value',
        axisLabel: { color: '#8a93a6' }
      },
      grid3D: {
        boxWidth: 160,
        boxDepth: 60,
        light: { main: { intensity: 1.2, shadow: true }, ambient: { intensity: 0.5 } }
      },
      series: [
        {
          type: 'bar3D',
          data: dataSource,
          shading: 'lambert',
          label: {
            show: true,
            formatter: ({ value }) => value[2],
            textStyle: { fontSize: 12, color: '#fff' }
          },
          itemStyle: {
            opacity: 0.95,
            color: ({ data }) => (data.category === '整车' ? '#4fd2dd' : '#ff8d6e')
          }
        }
      ]
    },
    true
  )

  if (!chartHandlers.projectBar3d) {
    chart.on('click', (params) => {
      const projectName = params?.data?.projectName
      if (projectName) {
        gotoVocPage(projectName === '其他' ? {} : { project_name: projectName })
      }
    })
    chartHandlers.projectBar3d = true
  }
}

const renderMonthlyTrend = (list = []) => {
  const chart = ensureChartInstance('monthlyTrend')
  if (!chart) return
  const labels = list.map((item) => `${item.month}月`)
  const values = list.map((item) => item.value || 0)

  chart.setOption(
    {
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 40, bottom: 30 },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#dfe3ea' } },
        axisLabel: { color: '#8a93a6' }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#dfe3ea' } },
        splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
        axisLabel: { color: '#8a93a6' }
      },
      series: [
        {
          type: 'line',
          data: values,
          smooth: true,
          symbolSize: 6,
          lineStyle: { color: '#4fd2dd', width: 3 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(79, 210, 221, 0.5)' },
              { offset: 1, color: 'rgba(79, 210, 221, 0)' }
            ])
          }
        }
      ]
    },
    true
  )
}

const renderAllCharts = () => {
  const data = dashboardData.value || {}
  renderCompletionBar('vocBar', data.voc_gauge)
  renderCompletionBar('odorBar', data.odor_gauge)
    renderProjectBar3d(data.project_comparison || [])
  renderMonthlyTrend(data.monthly_trend || [])
}

const gotoVocPage = (query = {}) => {
  router.push({ name: 'VocOdorData', query })
}

const pauseScroll = () => {
  scrollPaused.value = true
}

const resumeScroll = () => {
  scrollPaused.value = false
}

const toggleScroll = () => {
  scrollPaused.value = !scrollPaused.value
}

const resetScroll = () => {
  scrollOffset.value = 0
  if (scrollTimer) {
    clearInterval(scrollTimer)
    scrollTimer = null
  }
  if (!latestList.value.length) return
  scrollTimer = setInterval(() => {
    if (scrollPaused.value) return
    scrollOffset.value += scrollStep
    const limit = rowHeight * latestList.value.length
    if (scrollOffset.value >= limit) {
      scrollOffset.value = 0
    }
  }, scrollInterval)
}

const fetchDashboard = async () => {
  try {
    loading.value = true
    const res = await vocApi.getIaqDashboard()
    dashboardData.value = res?.data || {}
    scheduleRefresh()
  } catch (error) {
    console.error('获取IAQ数据失败', error)
    ElMessage.error('获取IAQ大屏数据失败')
  } finally {
    loading.value = false
  }
}

const scheduleRefresh = () => {
  const seconds = dashboardData.value?.kpis?.refresh_interval_seconds || 86400
  if (refreshTimeout) {
    clearTimeout(refreshTimeout)
  }
  refreshTimeout = setTimeout(fetchDashboard, seconds * 1000)
}

const handleResize = () => {
  Object.values(chartInstances).forEach((instance) => instance?.resize())
}

watch(
  () => dashboardData.value,
  async (val) => {
    if (!val) return
    await nextTick()
    renderAllCharts()
  },
  { deep: true }
)

watch(
  () => latestList.value.length,
  () => {
    resetScroll()
  }
)

onMounted(() => {
  updateClock()
  timeTimer = setInterval(updateClock, 1000)
  fetchDashboard()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (timeTimer) clearInterval(timeTimer)
  if (refreshTimeout) clearTimeout(refreshTimeout)
  if (scrollTimer) clearInterval(scrollTimer)
  window.removeEventListener('resize', handleResize)
  Object.values(chartInstances).forEach((instance) => instance?.dispose())
})
</script>

<style scoped>
:global(body) {
  font-family: 'HarmonyOS Sans', 'Microsoft YaHei', sans-serif;
}

.iaq-page {
  padding: 20px;
  color: #1f2d3d;
  background: linear-gradient(180deg, #f9fbff 0%, #f6f7fb 100%);
  min-height: calc(100vh - 40px);
  position: relative;
}

.header-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-chip {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #e8eef7, #e3e9f2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}

.title-text h1 {
  margin: 0;
  font-size: 24px;
}

.title-text p {
  margin: 4px 0 0;
  color: #606266;
  font-size: 14px;
}

.time-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.time-label {
  font-size: 14px;
  color: #606266;
}

.time-value {
  font-size: 20px;
  margin-top: 4px;
  letter-spacing: 1px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid #eef0f5;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
}

.kpi-label {
  font-size: 15px;
  color: #8a93a6;
  margin-bottom: 10px;
}

.kpi-value {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  min-height: 42px;
}

.flip-digit {
  min-width: 28px;
  padding: 6px 4px;
  background: #f3f6fb;
  border-radius: 6px;
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.04);
  animation: flip 1.2s ease-in-out;
}

@keyframes flip {
  0% {
    transform: rotateX(-90deg);
    opacity: 0;
  }
  60% {
    transform: rotateX(20deg);
    opacity: 1;
  }
  100% {
    transform: rotateX(0);
  }
}

.kpi-desc {
  margin-top: 8px;
  font-size: 13px;
  color: #6e7bb8;
}

.monitor-board {
  background: rgba(5, 11, 28, 0.6);
  border-radius: 18px;
  padding: 18px;
  border: 1px solid rgba(88, 114, 255, 0.2);
  box-shadow: inset 0 0 20px rgba(3, 9, 29, 0.8);
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.monitor-block {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.block-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2b3a55;
}

.gauge-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  flex: 1;
}

.gauge-item {
  background: rgba(9, 17, 40, 0.9);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(55, 135, 255, 0.15);
  display: flex;
  flex-direction: column;
  min-height: 260px;
}

.gauge-title {
  margin: 0 0 4px;
  color: #8a93a6;
}

.chart {
  flex: 1;
  min-height: 200px;
}

.chart.large {
  min-height: 280px;
}

.gauge-meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #8a93a6;
  margin-top: 10px;
}

.bottom-board {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-top: 18px;
}

.list-header,
.list-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr 1fr 0.8fr 0.8fr;
  gap: 6px;
  font-size: 14px;
}

.list-header {
  padding: 8px 12px;
  border-radius: 8px;
  background: #f6f9ff;
  color: #2b3a55;
}

.list-body {
  position: relative;
  height: 360px;
  overflow: hidden;
  margin-top: 10px;
}

.list-wrapper {
  transition: transform 0.1s linear;
}

.list-row {
  padding: 10px 12px;
  border-bottom: 1px dashed #eef0f5;
  cursor: pointer;
  min-height: 48px;
}

.list-row:hover {
  background: #f8fbff;
}

.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6e7bb8;
}

.list-footer {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.scroll-hint {
  color: #8a93a6;
}

.scroll-controls button {
  margin-left: 8px;
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background: #fff;
  color: #2b3a55;
  cursor: pointer;
}

.scroll-controls button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-mask {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
  border-radius: 18px;
  font-size: 18px;
}

@media (max-width: 1600px) {
  .monitor-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .bottom-board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .monitor-grid {
    grid-template-columns: 1fr;
  }
}
</style>





