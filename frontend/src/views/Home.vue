<template>
  <div class="screen">
    <!-- 顶部欢迎与时间 -->
    <section class="hero">
      <div class="hero-left">
        <h1 class="title">NVH 数字化大屏</h1>
        <p class="subtitle">
          欢迎回来，{{ userStore.fullName || userStore.username || '用户' }} · {{ currentDateTime }}
        </p>
        <div class="cta-group">
          <el-button type="primary" :icon="OfficeBuilding" @click="goToBusiness">进入业务中心</el-button>
          <el-button type="info" :icon="Setting" @click="goToPermission">权限管理</el-button>
          <el-button type="success" :icon="Refresh" @click="reloadAll">刷新数据</el-button>
        </div>
      </div>
      <div class="hero-right">
        <el-avatar :size="72" class="avatar" :icon="UserFilled" />
      </div>
    </section>

    <!-- 关键指标 -->
    <section class="kpi">
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

    <!-- 图表区 -->
    <section class="charts">
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-title">NTF 测试次数（月度）</div>
          <div ref="ntfMonthlyRef" class="chart-box"></div>
        </div>
        <div class="chart-card">
          <div class="chart-title">车型能源类型分布</div>
          <div ref="energyPieRef" class="chart-box"></div>
        </div>
        <div class="chart-card span-2">
          <div class="chart-title">轮胎品牌分布（Top 8）</div>
          <div ref="wheelBrandRef" class="chart-box"></div>
        </div>
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
  ShoppingBag
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { userApi } from '@/api/user'
import { modalApi } from '@/api/modal'
import { NtfApi } from '@/api/NTF'
import wheelPerformanceApi from '@/api/wheelPerformance'

const router = useRouter()
const userStore = useUserStore()

// 时间显示
const currentDateTime = computed(() => {
  const d = new Date()
  const opts = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }
  return d.toLocaleString('zh-CN', opts)
})

// KPI 数据
const kpiCards = ref([
  { key: 'vehicles', label: '车型总数', value: 0, icon: ShoppingBag, bg: 'linear-gradient(135deg,#5b8ff9,#3b76f6)' },
  { key: 'ntf', label: 'NTF测试次数', value: 0, icon: TrendCharts, bg: 'linear-gradient(135deg,#34d399,#10b981)' },
  { key: 'wheels', label: '车轮性能条目', value: 0, icon: TrendCharts, bg: 'linear-gradient(135deg,#fbbf24,#f59e0b)' },
  { key: 'airtight', label: '气密性图片', value: 0, icon: PieChart, bg: 'linear-gradient(135deg,#f87171,#ef4444)' }
])

// 图表 refs
const ntfMonthlyRef = ref(null)
const energyPieRef = ref(null)
const wheelBrandRef = ref(null)
let ntfMonthlyChart = null
let energyPieChart = null
let wheelBrandChart = null

// 路由
const goToBusiness = () => router.push('/business')
const goToPermission = () => router.push('/permission')

// 刷新用户信息
const refreshUserInfo = async () => {
  try {
    const info = await userApi.getUserInfo()
    userStore.setUserInfo(info)
  } catch (e) {
    console.error(e)
  }
}

// 加载并渲染数据
const reloadAll = async () => {
  try {
    const [vehiclesRes, ntfRes, wheelRes, airImgRes] = await Promise.all([
      modalApi.getVehicleModels(),
      NtfApi.getInfos(),
      wheelPerformanceApi.getWheelPerformanceList(),
      modalApi.getAirtightnessImages()
    ])

    const vehicles = vehiclesRes?.data || []
    const ntfInfos = ntfRes?.data || []
    const wheels = wheelRes?.data || []
    const airtightImgs = airImgRes?.data || []

    // KPI 更新
    setKpi('vehicles', vehicles.length)
    setKpi('ntf', ntfInfos.length)
    setKpi('wheels', wheels.length)
    setKpi('airtight', airtightImgs.length)

    await nextTick()
    // 渲染图表
    renderNtfMonthly(ntfInfos)
    renderEnergyPie(vehicles)
    renderWheelBrandBar(wheels)

  } catch (error) {
    console.error('加载数据失败', error)
    ElMessage.error('加载数据失败，请稍后重试')
  }
}

function setKpi(key, value) {
  const item = kpiCards.value.find(i => i.key === key)
  if (item) item.value = value || 0
}

function formatNumber(n) {
  if (n == null) return 0
  if (n > 10000) return (n / 10000).toFixed(1) + '万'
  return n
}

// 图表：NTF 月度次数
function renderNtfMonthly(list) {
  if (!ntfMonthlyChart) ntfMonthlyChart = echarts.init(ntfMonthlyRef.value)
  const map = new Map()
  list.forEach(it => {
    const t = it.test_time || it.testTime
    if (!t) return
    const d = new Date(t)
    if (isNaN(d)) return
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
    map.set(key, (map.get(key) || 0) + 1)
  })
  const months = Array.from(map.keys()).sort()
  const values = months.map(m => map.get(m))
  ntfMonthlyChart.setOption({
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: months, axisLabel: { color: '#a6b1c2' } },
    yAxis: { type: 'value', axisLabel: { color: '#a6b1c2' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    tooltip: { trigger: 'axis' },
    series: [{
      type: 'bar',
      data: values,
      barWidth: 18,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#5b8ff9'},{offset:1,color:'#3b76f6'}])
      }
    }]
  })
}

// 图表：能源类型
function renderEnergyPie(list) {
  if (!energyPieChart) energyPieChart = echarts.init(energyPieRef.value)
  const count = {}
  list.forEach(v => {
    const k = v.energy_type || v.energyType || '未知'
    count[k] = (count[k] || 0) + 1
  })
  const data = Object.entries(count).map(([name, value]) => ({ name, value }))
  energyPieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: '5%', textStyle: { color: '#a6b1c2' } },
    series: [{
      name: '能源类型',
      type: 'pie',
      radius: ['35%', '60%'],
      center: ['50%','55%'],
      roseType: false,
      label: { color: '#c7d0dd' },
      data
    }]
  })
}

// 图表：轮胎品牌 Top8
function renderWheelBrandBar(list) {
  if (!wheelBrandChart) wheelBrandChart = echarts.init(wheelBrandRef.value)
  const m = new Map()
  list.forEach(w => {
    const k = (w.tire_brand || '').trim() || '未知'
    m.set(k, (m.get(k) || 0) + 1)
  })
  const arr = Array.from(m.entries()).sort((a,b) => b[1]-a[1]).slice(0,8)
  const names = arr.map(a => a[0])
  const vals = arr.map(a => a[1])
  wheelBrandChart.setOption({
    grid: { left: 80, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#a6b1c2' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    yAxis: { type: 'category', data: names, axisLabel: { color: '#a6b1c2' } },
    tooltip: { trigger: 'axis' },
    series: [{
      type: 'bar',
      data: vals,
      barWidth: 14,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#f59e0b'},{offset:1,color:'#fbbf24'}])
      }
    }]
  })
}

// 自适应
function handleResize() {
  ntfMonthlyChart && ntfMonthlyChart.resize()
  energyPieChart && energyPieChart.resize()
  wheelBrandChart && wheelBrandChart.resize()
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await refreshUserInfo()
  await reloadAll()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  ntfMonthlyChart && ntfMonthlyChart.dispose()
  energyPieChart && energyPieChart.dispose()
  wheelBrandChart && wheelBrandChart.dispose()
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

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 16px;
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.6);
}
.title { margin: 0; font-size: 28px; color: #1f2d3d; }
.subtitle { margin: 6px 0 0 0; color: #606266; }
.cta-group { margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
.avatar { box-shadow: 0 6px 20px rgba(0,0,0,0.08); }

.kpi { margin-top: 16px; }
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

.charts { margin-top: 16px; }
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 12px;
}
.chart-card {
  background: #ffffff;
  border: 1px solid #eef0f5;
  border-radius: 12px;
  padding: 12px;
  min-height: 280px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
.chart-card:hover { border-color: #d7e3ff; box-shadow: 0 8px 20px rgba(59,118,246,0.08); }
.chart-card.span-2 { grid-column: span 2; }
.chart-title { color: #2b3a55; font-weight: 600; margin-bottom: 8px; }
.chart-box { width: 100%; height: 260px; }

@media (max-width: 992px) {
  .kpi-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
  .chart-grid { grid-template-columns: 1fr; }
  .chart-card.span-2 { grid-column: auto; }
}
</style>
