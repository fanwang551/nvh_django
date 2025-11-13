<template>
  <div class="iaq-page">
    <!-- Row 1：原头部 + KPI 保持不变（合并为一行容器） -->
    <section class="row row-top">
      <div class="header-panel">
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
      </div>

      <div class="kpi-grid">
        <div class="kpi-card" v-for="item in kpiItems" :key="item.key">
          <div class="kpi-label">{{ item.label }}</div>
          <div class="kpi-value">
            <span
                v-for="(digit, idx) in splitDigits(item.value)"
                :key="item.key + '-digit-' + idx"
                class="flip-digit"
            >{{ digit }}</span>
          </div>
          <div class="kpi-desc">{{ item.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Row 2: VOC + 气味 柱状图 -->
    <section class="row grid-2">
      <div class="monitor-block">
        <div class="block-header">
          <h3>VOC完成量监控</h3>
          <span>整车 vs 零部件</span>
        </div>
        <div class="chart" ref="vocBarRef"></div>
      </div>
      <div class="monitor-block">
        <div class="block-header">
          <h3>气味完成量监控</h3>
          <span>整车 vs 零部件</span>
        </div>
        <div class="chart" ref="odorBarRef"></div>
      </div>
    </section>

    <!-- Row 3: 最新检测数据滚动列表（全宽） -->
    <section class="row">
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
                :key="row.id + '-row-' + idx"
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
          <div v-if="!latestList.length" class="empty-state">暂无数据</div>
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

    <!-- Row 4: 各项目试验次数对比 + 词云图（并排） -->
    <section class="row grid-2 row-flat">
      <div class="monitor-block">
        <div class="block-header">
          <h3>各项目试验次数对比</h3>
          <span>整车 vs 零部件（三维柱状图）</span>
        </div>
        <div class="chart large" ref="projectBar3dRef"></div>
      </div>
      <div class="monitor-block">
        <div class="block-header">
          <h3>VOC/气味高频关键词词云</h3>
          <span>前端静态数据 | 支持 maskImage</span>
        </div>
        <div class="chart large wordcloud" ref="wordCloudRef"></div>
      </div>
    </section>

    <!-- Row 5: 月度测试完成量趋势（全宽） -->
    <section class="row">
      <div class="trend-block monitor-block">
        <div class="block-header">
          <h3>月度测试完成量趋势</h3>
          <span>{{ currentYear }} 年</span>
        </div>
        <div class="chart large" ref="monthlyTrendRef"></div>
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
import 'echarts-wordcloud'

import vocApi from '@/api/voc'

const router = useRouter()

const loading = ref(false)
const dashboardData = ref(null)
const currentTime = ref('')
const currentYear = new Date().getFullYear()

const vocBarRef = ref(null)
const odorBarRef = ref(null)
const projectBar3dRef = ref(null)
const monthlyTrendRef = ref(null)
const wordCloudRef = ref(null)

const chartRefs = {
  projectBar3d: projectBar3dRef,
  monthlyTrend: monthlyTrendRef,
  vocBar: vocBarRef,
  odorBar: odorBarRef,
  wordCloud: wordCloudRef
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

// 词云静态数据与 mask 占位（可在此粘贴 base64）
const wordCloudItems = ref([
  { name: '甲苯', value: 95 },
  { name: '乙苯', value: 88 },
  { name: '二甲苯', value: 92 },
  { name: '苯乙烯', value: 85 },
  { name: '甲醛', value: 98 },
  { name: '乙醛', value: 82 },
  { name: '丙烯醛', value: 78 },
  { name: '苯', value: 90 },
  { name: 'TVOC', value: 100 },
  { name: '丙醛', value: 76 },
  { name: '丁醛', value: 74 },
  { name: '己醛', value: 71 },
  { name: '苯甲醛', value: 79 },
  { name: '丙烯酸', value: 73 },
  { name: '正己烷', value: 68 },
  { name: '环己烷', value: 66 },
  { name: '三氯乙烯', value: 81 },
  { name: '四氯乙烯', value: 77 },
  { name: 'F710C', value: 75 },
  { name: 'A520B', value: 72 },
  { name: 'B830X', value: 78 },
  { name: 'C940Z', value: 69 },
  { name: 'D215M', value: 74 },
  { name: 'E680N', value: 71 },
  { name: 'G450P', value: 76 },
  { name: 'H920K', value: 68 },
  { name: 'J330R', value: 73 },
  { name: 'K770S', value: 70 },
  { name: 'L560T', value: 67 },
  { name: '座椅', value: 70 },
  { name: '仪表板', value: 72 },
  { name: '门板', value: 65 },
  { name: '顶棚', value: 68 },
  { name: '地毯', value: 66 },
  { name: '方向盘', value: 62 },
  { name: '中控台', value: 69 },
  { name: '遮阳板', value: 58 },
  { name: '扶手箱', value: 64 },
  { name: '手套箱', value: 61 },
  { name: '后备箱', value: 67 },
  { name: '安全带', value: 59 },
  { name: '头枕', value: 63 },
  { name: '脚垫', value: 65 },
  { name: '隔音棉', value: 68 },
  { name: '密封条', value: 60 },
  { name: '空调出风口', value: 62 },
  { name: '车窗升降器', value: 57 },
  { name: '后视镜', value: 56 },
  { name: '换挡杆', value: 61 },
  { name: '踏板', value: 58 },
  { name: '立柱', value: 64 },
  { name: '天窗', value: 66 },
  { name: '总碳', value: 55 },
  { name: '雾度', value: 52 },
  { name: '气味等级', value: 60 },
  { name: '甲醇', value: 50 },
  { name: '丙酮', value: 48 },
  { name: 'C114', value: 48 },
  { name: 'C215', value: 51 },
  { name: 'C316', value: 49 },
  { name: 'C417', value: 53 },
  { name: 'C518', value: 47 },
  { name: 'H220', value: 54 },
  { name: 'H321', value: 50 },
  { name: 'N105', value: 52 },
  { name: 'N206', value: 49 },
  { name: 'O308', value: 51 },
  { name: 'P410', value: 48 },
  { name: 'S512', value: 53 },
  { name: 'T614', value: 50 },
  { name: 'V716', value: 47 },
  { name: 'W818', value: 52 },
  { name: 'X920', value: 49 },
  { name: 'Y122', value: 51 },
  { name: 'Z224', value: 48 },
  { name: '光泽度', value: 54 },
  { name: '透光率', value: 50 },
  { name: '色差值', value: 52 },
  { name: '硬度', value: 49 },
  { name: '耐磨性', value: 51 }
])

// 将你的 base64 图片粘贴到下方变量中（例如：'data:image/png;base64,xxxx'）
const wordCloudMaskBase64 = ref('data:image/png;base64,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')

const kpiItems = computed(() => {
  const kpis = dashboardData.value?.kpis || {}
  return [
    { key: 'project_total', label: '项目总数', value: kpis.project_total ?? 0, desc: 'SampleInfo项目去重' },
    { key: 'sample_total', label: '样品总数', value: kpis.sample_total ?? 0, desc: 'SampleInfo记录数' },
    { key: 'substance_total', label: '物质库总量', value: kpis.substance_total ?? 0, desc: 'Substance记录数' },
    { key: 'annual_test_total', label: '年度测试总次数', value: kpis.annual_test_total ?? 0, desc: `${currentYear} 年` }
  ]
})

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

// 移除未使用的仪表盘构建与渲染函数

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


// 压缩词云权重，拉平数值区间，避免少数大词占满空间导致后续词无法排布
const compressWordCloudValues = (list = []) => {
  const arr = Array.isArray(list) ? [...list] : []
  // 按原始 value 从大到小排序，使用排名映射到紧凑的新权重（100..20）
  arr.sort((a, b) => (Number(b?.value || 0) - Number(a?.value || 0)))
  const n = arr.length || 1
  return arr.map((item, idx) => {
    const rankRatio = idx / Math.max(1, n - 1) // 0..1
    const newVal = 100 - Math.floor(rankRatio * 80) // 100..20，区间较窄，保证能放下更多词
    return { name: item.name, value: newVal }
  })
}

const renderWordCloud = async () => {
  const chart = ensureChartInstance('wordCloud')
  if (!chart) return
  // 加载 mask 图片（可选）
  const loadMask = () => new Promise((resolve) => {
    const src = wordCloudMaskBase64.value
    if (!src) { resolve(null); return }
    const img = new Image()
    img.src = src
    img.onload = () => resolve(img)
    img.onerror = () => resolve(null)
  })
  const mask = await loadMask()
  const colorPool = ['#4fd2dd', '#5b8ff9', '#57d9a3', '#f7ba1e', '#ff7c7c', '#8e71ff', '#00d6c9', '#c7a6ff']
  const normalized = compressWordCloudValues(wordCloudItems.value)
  chart.setOption({
    tooltip: { show: true },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        // 如提供了 mask 则使用，版式更紧凑时也能尽量铺满形状
        maskImage: mask || undefined,
        // 调小网格与字号范围，提升可排布的单词数量
        gridSize: 0.1,
        sizeRange: [6, 15],
        // 全部水平排布更容易放下更多词
        rotationRange: [-45, 45],
        rotationStep: 45,
        // 为保证图案完整，不允许越界绘制
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'HarmonyOS Sans, Microsoft YaHei, sans-serif',
          color: () => colorPool[Math.floor(Math.random() * colorPool.length)]
        },
        emphasis: {
          textStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.25)' }
        },
        data: normalized
      }
    ]
  }, true)
}
const renderAllCharts = () => {
  const data = dashboardData.value || {}
  renderCompletionBar('vocBar', data.voc_gauge)
  renderCompletionBar('odorBar', data.odor_gauge)
    renderProjectBar3d(data.project_comparison || [])
  renderMonthlyTrend(data.monthly_trend || [])
  renderWordCloud()
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
  zoom: 0.8; /* 默认按 80% 缩放展示，匹配用户期望的界面比例 */
  transform-origin: top center;
}

@supports not (zoom: 0.8) {
  .iaq-page {
    transform: scale(0.8);
    transform-origin: top center;
  }
  :global(body) {
    overflow-x: hidden;
  }
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

/* 移除未使用的仪表盘样式（gauge-grid / gauge-item） */

/* 移除未使用的 .gauge-title 样式 */

.chart {
  flex: 1;
  min-height: 200px;
}

.chart.large {
  min-height: 280px;
}

/* 词云较多（~80）时单独提升绘图区高度，确保容纳更多单词 */
.chart.wordcloud {
  min-height: 420px;
}

/* 移除未使用的 .gauge-meta 样式 */

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

/* New layout rows */
.row { margin-top: 18px; }
.row:first-of-type { margin-top: 0; }
.row.row-top {
  display: grid;
  grid-template-columns: minmax(420px, 460px) 1fr;
  gap: 18px;
  align-items: stretch;
}
.row.row-top .header-panel {
  margin-bottom: 0;
  background: #fff;
  border-radius: 16px;
  padding: 18px;
  border: 1px solid #eef0f5;
}
.row.row-top .kpi-grid {
  margin-bottom: 0;
  align-self: stretch;
}
.row.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
.row.grid-2 .monitor-block {
  height: 100%;
}
.row.row-flat .monitor-block {
  padding-top: 12px;
  padding-bottom: 12px;
}
.row.row-flat .chart.large {
  min-height: 240px;
}
.row.row-flat .chart.wordcloud {
  min-height: 320px;
}
@media (max-width: 1600px) {
  .row.row-top { grid-template-columns: 1fr; }
  .row.row-top .header-panel { margin-bottom: 16px; }
}
</style>






