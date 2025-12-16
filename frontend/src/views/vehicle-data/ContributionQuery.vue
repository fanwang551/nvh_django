<template>
  <div class="page">
    <!-- 搜索框模块 -->
    <el-card shadow="never" class="search-card">
      <template #header>
        <div class="card-header">
          <span class="title">搜索框</span>
        </div>
      </template>
      <el-form :inline="true" class="query-form">
        <!-- 车型名称 -->
        <el-form-item label="车型名称">
          <el-select
            v-model="selectedProjectName"
            placeholder="请选择车型名称"
            clearable
            filterable
            :loading="vmLoading"
            style="width: 260px"
            @change="onProjectChange"
          >
            <el-option
              v-for="opt in projectOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <!-- 测试状态 -->
        <el-form-item label="测试状态">
          <el-select
            v-model="selectedStatus"
            :placeholder="statusPlaceholder"
            clearable
            :disabled="!selectedProjectName || !hasHierarchy"
            style="width: 200px"
            @change="onStatusChange"
          >
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <!-- 委托单号 -->
        <el-form-item label="委托单号">
          <el-select
            v-model="selectedOrderNo"
            :placeholder="orderPlaceholder"
            clearable
            :disabled="!selectedProjectName || !hasHierarchy || selectedStatus === null"
            style="width: 220px"
            @change="onOrderChange"
          >
            <el-option
              v-for="opt in orderOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <!-- 重置按钮 -->
        <el-form-item>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>

        <!-- 查询按钮 -->
        <el-form-item>
          <el-button type="primary" :disabled="!canQuery" @click="handleQuery">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 整车溯源结果模块 -->
    <el-card shadow="never" class="result-card" v-if="!insufficient && rows.length > 0">
      <template #header>
        <div class="card-header">
          <span class="title">整车溯源结果</span>
          <span class="subtitle">按项目(车型)输出GOi/GVi TOP25</span>
        </div>
      </template>
      <el-table
        :data="rows"
        border
        style="width: 100%"
        :header-cell-style="{ backgroundColor: '#409EFF', color: '#fff', fontWeight: 600 }"
      >
        <el-table-column label="气味污染物可能来源" align="center">
          <el-table-column prop="goi_rank" label="TOP25" width="80" align="center" />
          <el-table-column prop="goi_part_name" label="零部件" align="center" />
          <el-table-column prop="goi_value" label="贡献度Goi" width="140" align="center">
            <template #default="scope">
              {{ formatNumber(scope.row.goi_value) }}
            </template>
          </el-table-column>
        </el-table-column>

        <el-table-column label="挥发性有机污染物可能来源" align="center">
          <el-table-column prop="gvi_rank" label="TOP25" width="80" align="center" />
          <el-table-column prop="gvi_part_name" label="零部件" align="center" />
          <el-table-column prop="gvi_value" label="贡献度Gvi" width="140" align="center">
            <template #default="scope">
              {{ formatNumber(scope.row.gvi_value) }}
            </template>
          </el-table-column>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 溯源贡献度可视化模块：单独卡片，位于溯源结果表下方 -->
    <el-card
      v-if="!insufficient && (goiTop25.length > 0 || gviTop25.length > 0)"
      shadow="never"
      class="viz-card"
    >
      <template #header>
        <div class="card-header">
          <span class="title">溯源贡献度可视化</span>
          <span class="subtitle">TOP10 + 其他（GOi / GVi）</span>
        </div>
      </template>
      <div class="viz-grid">
        <div>
          <div ref="goiPieRef" class="pie-box"></div>
        </div>
        <div>
          <div ref="gviPieRef" class="pie-box"></div>
        </div>
      </div>
    </el-card>
    <!-- 数据不足弹窗 -->
    <el-dialog v-model="insufficientDialog" title="数据不足" width="600px">
      <div class="insufficient-msg">
        零部件数需≥25，当前项目仅有 {{ partsCount }} 个零部件，数据不足。
      </div>
      <el-divider content-position="left">已有零部件 ({{ partsCount }})</el-divider>
      <el-scrollbar height="260px">
        <div class="part-list">
          <el-tag
            v-for="(name, idx) in partNames"
            :key="idx"
            style="margin: 4px"
          >{{ name }}</el-tag>
        </div>
      </el-scrollbar>
      <template #footer>
        <el-button @click="insufficientDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
  
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import vocApi from '@/api/voc'
import { substancesApi } from '@/api/substances'

import * as echarts from 'echarts'

const vmLoading = ref(false)

// 车型层级数据源
const vehicleSamples = ref([])      // 含 project_name / status / test_order_no / sample_no 的整车样品
const fallbackProjects = ref([])    // 兜底：仅有项目名称的选项

// 三级联动选中值
const selectedProjectName = ref(null)
const selectedStatus = ref(null)    // 状态值（包含占位符 '__EMPTY__'）
const selectedOrderNo = ref(null)

const insufficient = ref(false)
const partsCount = ref(0)
const partNames = ref([])
const insufficientDialog = ref(false)

const goiTop25 = ref([])
const gviTop25 = ref([])

const rows = computed(() => {
  const maxLen = Math.max(goiTop25.value.length, gviTop25.value.length)
  const list = []
  for (let i = 0; i < maxLen; i++) {
    const goiItem = goiTop25.value[i]
    const gviItem = gviTop25.value[i]
    list.push({
      goi_rank: goiItem ? goiItem.rank : null,
      goi_part_name: goiItem ? goiItem.part_name : null,
      goi_value: goiItem ? goiItem.goi : null,
      gvi_rank: gviItem ? gviItem.rank : null,
      gvi_part_name: gviItem ? gviItem.part_name : null,
      gvi_value: gviItem ? gviItem.gvi : null
    })
  }
  return list
})

// 是否具备完整的三级联动数据源（存在整车样品列表）
const hasHierarchy = computed(() => vehicleSamples.value.length > 0)

// 车型名称选项：优先使用整车样品数据，其次使用兜底项目列表
const projectOptions = computed(() => {
  const result = []
  const seen = new Set()
  const source = hasHierarchy.value ? vehicleSamples.value : fallbackProjects.value

  source.forEach(item => {
    const name = item.project_name
    if (!name || seen.has(name)) {
      return
    }
    seen.add(name)
    result.push({
      value: name,
      label: name
    })
  })

  return result
})

// 测试状态选项（依赖车型，仅在有整车样品数据时可用）
const statusOptions = computed(() => {
  const result = []
  const seen = new Set()

  if (!hasHierarchy.value || !selectedProjectName.value) {
    return result
  }

  vehicleSamples.value.forEach(item => {
    if (item.project_name !== selectedProjectName.value) {
      return
    }
    const rawStatus = (item.status || '').trim()
    const value = rawStatus || '__EMPTY__'
    if (seen.has(value)) {
      return
    }
    seen.add(value)
    result.push({
      value,
      label: rawStatus || '未设置状态'
    })
  })

  return result
})

// 有效的状态过滤值（仅在有真实状态值时参与过滤）
const effectiveStatus = computed(() => {
  if (!hasHierarchy.value || selectedStatus.value === null) {
    return ''
  }
  return selectedStatus.value === '__EMPTY__' ? '' : selectedStatus.value
})

// 委托单号选项（依赖车型 + 状态，仅在有整车样品数据时可用）
const orderOptions = computed(() => {
  const result = []
  const seen = new Set()

  if (!hasHierarchy.value || !selectedProjectName.value || selectedStatus.value === null) {
    return result
  }

  vehicleSamples.value.forEach(item => {
    if (item.project_name !== selectedProjectName.value) {
      return
    }
    const rawStatus = (item.status || '').trim()
    const statusKey = rawStatus || '__EMPTY__'
    if (statusKey !== selectedStatus.value) {
      return
    }
    const orderNo = (item.test_order_no || '').trim()
    if (!orderNo || seen.has(orderNo)) {
      return
    }
    seen.add(orderNo)
    result.push({
      value: orderNo,
      label: orderNo
    })
  })

  return result
})

// 下拉占位提示
const statusPlaceholder = computed(() => {
  return selectedProjectName.value ? '请选择测试状态' : '请先选择车型'
})

const orderPlaceholder = computed(() => {
  if (!selectedProjectName.value) {
    return '请先选择车型'
  }
  if (selectedStatus.value === null) {
    return '请先选择测试状态'
  }
  return '请选择委托单号'
})

// 是否可以执行查询
const canQuery = computed(() => {
  if (!selectedProjectName.value) {
    return false
  }
  if (!hasHierarchy.value) {
    // 兜底模式：仅按车型查询
    return true
  }
  if (selectedStatus.value === null) {
    return false
  }
  if (!orderOptions.value.length) {
    return false
  }
  return !!selectedOrderNo.value
})

const formatNumber = (val) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  return isNaN(num) ? '-' : num.toFixed(3)
}

const loadVehicleModels = async () => {
  vmLoading.value = true
  try {
    // 直接基于 SampleInfo 的“整车”样品生成下拉项：同一项目名的多条样品全部展示
    const testsResp = await substancesApi.getTestList({ part_name: '整车', page_size: 10000 })
    const tests = (testsResp?.data?.results || [])
      .map(r => r?.sample_info || {})
      .filter(s => s.project_name)

    if (tests.length > 0) {
      // 构造整车样品列表，供三级联动使用
      vehicleSamples.value = tests.map(s => ({
        project_name: s.project_name,
        status: s.status,
        test_order_no: s.test_order_no,
        sample_no: s.sample_no
      }))
      fallbackProjects.value = []
    } else {
      // 兜底：若没有整车样品，则退回到仅以项目名展示
      const resp = await vocApi.getVehicleModelOptions()
      const options = resp.data || []
      fallbackProjects.value = options
        .filter(item => item && item.value)
        .map(item => ({
          project_name: item.value
        }))
      vehicleSamples.value = []
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('获取车型数据失败')
  } finally {
    vmLoading.value = false
  }
}

const handleQuery = async () => {
  if (!selectedProjectName.value) return
  try {
    const params = {
      project_name: selectedProjectName.value
    }
    // 在具备三级联动数据源时，附加状态与委托单号过滤
    if (hasHierarchy.value) {
      const statusFilter = effectiveStatus.value
      if (statusFilter) {
        params.status = statusFilter
      }
      if (selectedOrderNo.value) {
        params.test_order_no = selectedOrderNo.value
      }
    }

    const resp = await vocApi.getContributionTop25(params)
    insufficient.value = !!resp.data?.insufficient
    partsCount.value = resp.data?.parts_count || 0
    partNames.value = resp.data?.part_names || []

    if (insufficient.value) {
      goiTop25.value = []
      gviTop25.value = []
      insufficientDialog.value = true
    } else {
      goiTop25.value = resp.data?.goi_top25 || []
      gviTop25.value = resp.data?.gvi_top25 || []
      insufficientDialog.value = false
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('查询失败')
  }
}

const handleReset = () => {
  selectedProjectName.value = null
  selectedStatus.value = null
  selectedOrderNo.value = null

  insufficient.value = false
  partsCount.value = 0
  partNames.value = []
  insufficientDialog.value = false

  goiTop25.value = []
  gviTop25.value = []
}

// 级联选择联动处理
const resetDownstreamSelection = () => {
  selectedStatus.value = null
  selectedOrderNo.value = null
}

const onProjectChange = () => {
  resetDownstreamSelection()
}

const onStatusChange = () => {
  selectedOrderNo.value = null
}

const onOrderChange = () => {
  // 仅更新选中值，不自动触发查询
}

onMounted(async () => {
  await loadVehicleModels()
})


// ================= 可视化：GOi/GVi 饼图（TOP10 + 其他） =================
const goiPieRef = ref(null)
const gviPieRef = ref(null)
let goiPieChart = null
let gviPieChart = null

const formatFixed3 = (n) => {
  const num = Number(n)
  return isNaN(num) ? '-' : num.toFixed(3)
}

// 将TOP25数据处理为 TOP10 + 其他
const buildPieSeriesData = (list, valueKey) => {
  if (!Array.isArray(list) || list.length === 0) return []
  const sorted = [...list].sort((a, b) => Number(b[valueKey] || 0) - Number(a[valueKey] || 0))
  const top10 = sorted.slice(0, 10)
  const others = sorted.slice(10)
  const otherSum = others.reduce((acc, cur) => acc + Number(cur[valueKey] || 0), 0)

  const seriesData = top10.map(item => ({
    name: '[' + item.rank + '] ' + item.part_name,
    value: Number(item[valueKey] || 0),
    __raw: item
  }))
  if (otherSum > 0) {
    seriesData.push({ name: '其他', value: otherSum, __raw: null })
  }
  return seriesData
}

const renderGoiPie = () => {
  if (!goiPieRef.value) return
  if (!goiPieChart) goiPieChart = echarts.init(goiPieRef.value)
  const data = buildPieSeriesData(goiTop25.value, 'goi')
  const option = {
    title: { text: 'GOi 贡献度分布（TOP10+其他）', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: function(p) {
        const val = formatFixed3(p.value)
        return p.name + '<br/>值：' + val + '<br/>占比：' + p.percent + '%'
      }
    },
    legend: { type: 'scroll', bottom: 0 },
    series: [
      {
        name: 'GOi',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        label: {
          show: true,
          formatter: function(params) { return params.name + '  ' + params.percent + '%' },
        },
        data: data
      }
    ]
  }
  goiPieChart.setOption(option)
}

const renderGviPie = () => {
  if (!gviPieRef.value) return
  if (!gviPieChart) gviPieChart = echarts.init(gviPieRef.value)
  const data = buildPieSeriesData(gviTop25.value, 'gvi')
  const option = {
    title: { text: 'GVi 贡献度分布（TOP10+其他）', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: function(p) {
        const val = formatFixed3(p.value)
        return p.name + '<br/>值：' + val + '<br/>占比：' + p.percent + '%'
      }
    },
    legend: { type: 'scroll', bottom: 0 },
    series: [
      {
        name: 'GVi',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        label: {
          show: true,
          formatter: function(params) { return params.name + '  ' + params.percent + '%' },
        },
        data: data
      }
    ]
  }
  gviPieChart.setOption(option)
}

const disposeCharts = () => {
  if (goiPieChart) { goiPieChart.dispose(); goiPieChart = null }
  if (gviPieChart) { gviPieChart.dispose(); gviPieChart = null }
}

const resizeHandler = () => {
  if (goiPieChart) goiPieChart.resize()
  if (gviPieChart) gviPieChart.resize()
}

watch([goiTop25, gviTop25, insufficient], async () => {
  if (insufficient.value) {
    disposeCharts()
    return
  }
  await nextTick()
  if (goiTop25.value && goiTop25.value.length) {
    renderGoiPie()
  } else if (goiPieChart) {
    goiPieChart.clear()
  }
  if (gviTop25.value && gviTop25.value.length) {
    renderGviPie()
  } else if (gviPieChart) {
    gviPieChart.clear()
  }
})

onMounted(() => {
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  disposeCharts()
})</script>

<style scoped>
.page { padding: 12px; }
.card-header { display: flex; align-items: baseline; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.subtitle { color: #909399; font-size: 13px; }
.search-card { margin-bottom: 16px; }
.result-card { margin-top: 16px; }
.query-form { margin: 0; }
.insufficient-msg { color: #e6a23c; margin-bottom: 12px; }
.part-list { display: flex; flex-wrap: wrap; }

/* 可视化模块样式 */
.viz-card { margin-top: 16px; }
.viz-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.pie-box { height: 360px; }

@media (max-width: 1024px) {
  .viz-grid { grid-template-columns: 1fr; }
}
</style>

