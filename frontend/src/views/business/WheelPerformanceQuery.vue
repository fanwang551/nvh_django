<template>
  <div class="wheel-performance-query">
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form :model="filters" label-width="100px" class="search-form">
        <el-row :gutter="24">
          <el-col :span="16" >
            <el-form-item label="车型">
              <el-select
                v-model="selectedVehicleModelIds"
                placeholder="请选择车型"
                multiple
                clearable
                collapse-tags
                collapse-tags-tooltip
                @change="handleVehicleSelectionChange"
                style="width: 100%"
              >
                <template #header>
                  <el-checkbox
                    v-model="selectAllVehicles"
                    @change="handleSelectAllVehicles"
                    class="select-all-checkbox"
                  >
                    全选
                  </el-checkbox>
                </template>
                <el-option
                  v-for="item in vehicleModels"
                  :key="item.id"
                  :label="item.vehicle_model_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8" >
          <el-button type="primary" @click="handleSearch" :loading="isLoading">
            查询
          </el-button>
          <el-button @click="handleReset" :disabled="isLoading">重置</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询结果</span>
          <span class="card-subtitle">共 {{ records.length }} 条</span>
        </div>
      </template>
      <el-table
        :data="records"
        stripe
        border
        v-loading="isLoading"
        empty-text="暂无数据"
      >
        <el-table-column prop="vehicle_model_name" label="车型" min-width="140" />
        <el-table-column prop="tire_brand" label="轮胎品牌" min-width="120" />
        <el-table-column prop="tire_model" label="轮胎型号" min-width="140" />
        <el-table-column prop="is_silent" label="是否静音胎" min-width="120">
          <template #default="{ row }">
            <span>{{ row.is_silent ? '是' : '否' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="rim_material" label="轮辋材质" min-width="120" />
        <el-table-column prop="rim_mass_mt" min-width="170">
          <template #header>
            <span>轮辋质量 M<sub>T</sub> (kg)</span>
          </template>
        </el-table-column>
        <el-table-column prop="resonance_peak_f1" min-width="160">
          <template #header>
            <span>共振峰 f<sub>1</sub> (Hz)</span>
          </template>
        </el-table-column>
        <el-table-column prop="anti_resonance_peak_f2" min-width="160">
          <template #header>
            <span>反共振峰 f<sub>2</sub> (Hz)</span>
          </template>
        </el-table-column>
        <el-table-column prop="rim_lateral_stiffness" label="轮辋侧向刚度 (kN/mm)" min-width="200">
          <template #default="{ row }">
            <div class="table-metric-cell">
              <span class="metric-value">{{ row.rim_lateral_stiffness }}</span>
              <el-button type="primary" link @click="handleOpenRimModal(row)">
                查看曲线
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="force_transfer_first_peak" label="力传递率一阶峰值（Hz）" min-width="200">
          <template #default="{ row }">
            <div class="table-metric-cell">
              <span class="metric-value">{{ row.force_transfer_first_peak }}</span>
              <el-button type="primary" link @click="handleOpenForceModal(row)">
                查看曲线
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">力传递峰值曲线</span>
        </div>
      </template>
      <div v-if="chartSeries.length" ref="chartRef" class="echarts-container"></div>
      <el-empty v-else description="暂无曲线数据" />
    </el-card>

    <el-dialog
      v-model="rimModalVisible"
      width="720px"
      destroy-on-close
      class="rim-modal"
      :close-on-click-modal="false"
    >
      <template #title>
        <div class="modal-title">轮辋刚度</div>
      </template>
      <div v-if="rimModalRecord" class="rim-modal__content">
        <div class="rim-modal__tabs">
          <button
            type="button"
            class="rim-tab"
            :class="{ 'rim-tab--active': rimModalActiveTab === 'curve' }"
            @click="handleSwitchRimTab('curve')"
          >
            刚度曲线
          </button>
          <button
            type="button"
            class="rim-tab"
            :class="{ 'rim-tab--active': rimModalActiveTab === 'image' }"
            @click="handleSwitchRimTab('image')"
          >
            刚度图片
          </button>
        </div>
        <div class="rim-modal__body">
          <template v-if="rimModalActiveTab === 'curve'">
            <img
              v-if="rimModalRecord?.rim_stiffness_curve_url"
              :src="rimModalRecord.rim_stiffness_curve_url"
              alt="轮辋刚度曲线"
              class="rim-modal__image"
            />
            <el-empty v-else description="暂无刚度曲线" />
          </template>
          <template v-else>
            <img
              v-if="rimModalRecord?.rim_stiffness_image_url"
              :src="rimModalRecord.rim_stiffness_image_url"
              alt="轮辋刚度图片"
              class="rim-modal__image"
            />
            <el-empty v-else description="暂无刚度图片" />
          </template>
        </div>
        <div class="rim-modal__caption">
          <span>{{ rimModalRecord?.vehicle_model_name }}</span>
          <span v-if="rimModalRecord?.tire_model"> - {{ rimModalRecord?.tire_model }}</span>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="forceModalVisible"
      width="720px"
      destroy-on-close
      class="force-modal"
      :close-on-click-modal="false"
    >
      <template #title>
        <div class="modal-title">力传递曲线</div>
      </template>
      <div class="force-modal__content">
        <img
          v-if="forceModalRecord?.force_transfer_curve_url"
          :src="forceModalRecord.force_transfer_curve_url"
          alt="力传递曲线"
          class="force-modal__image"
        />
        <el-empty v-else description="暂无力传递曲线" />
      </div>
      <template #footer>
        <span>{{ forceModalRecord?.vehicle_model_name }}</span>
        <span v-if="forceModalRecord?.tire_model"> - {{ forceModalRecord?.tire_model }}</span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useWheelPerformanceQueryStore } from '@/store/wheelPerformanceQuery'

echarts.use([LineChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const store = useWheelPerformanceQueryStore()
const { filters, vehicleModels, records, chartSeries, isLoading, rimModal, forceModal } = storeToRefs(store)

const selectedVehicleModelIds = computed({
  get: () => filters.value.vehicleModelIds,
  set: (value) => {
    const nextValue = Array.isArray(value) ? [...value] : []
    store.setFilters({ vehicleModelIds: nextValue })
  }
})

const selectAllVehicles = ref(false)

const syncSelectAllState = (selectedIds) => {
  const selectableIds = vehicleModels.value.map((item) => item.id)

  if (!selectableIds.length) {
    selectAllVehicles.value = false
    return
  }

  const selectedSet = new Set(Array.isArray(selectedIds) ? selectedIds : [])
  const hasAll = selectableIds.every((id) => selectedSet.has(id))
  selectAllVehicles.value = hasAll
}

const handleVehicleSelectionChange = (selectedIds) => {
  const normalized = Array.isArray(selectedIds) ? selectedIds : []
  syncSelectAllState(normalized)
}

const handleSelectAllVehicles = (checked) => {
  if (checked) {
    const allIds = vehicleModels.value.map((item) => item.id)
    store.setFilters({ vehicleModelIds: allIds })
  } else {
    store.setFilters({ vehicleModelIds: [] })
  }
}

watch(
  vehicleModels,
  () => {
    syncSelectAllState(filters.value.vehicleModelIds)
  }
)

watch(
  () => filters.value.vehicleModelIds,
  (newValue) => {
    syncSelectAllState(newValue)
  },
  { immediate: true, deep: true }
)

const rimModalVisible = computed({
  get: () => rimModal.value.visible,
  set: (visible) => {
    if (!visible) {
      store.closeRimModal()
    }
  }
})
const rimModalRecord = computed(() => rimModal.value.record)
const rimModalActiveTab = computed(() => rimModal.value.activeTab)
const forceModalVisible = computed({
  get: () => forceModal.value.visible,
  set: (visible) => {
    if (!visible) {
      store.closeForceModal()
    }
  }
})
const forceModalRecord = computed(() => forceModal.value.record)

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) {
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
}

watch(
  chartSeries,
  async (newSeries) => {
    await nextTick()
    initChart()

    if (!chartInstance) {
      return
    }

    if (!newSeries.length) {
      chartInstance.clear()
      return
    }

    chartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        type: 'scroll',
        top: 0,
        left: 'center'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: 40,
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '频率（Hz）',
        nameLocation: 'middle',
        nameGap: 30,
        min: 0,
        max: 300,
        splitNumber: 6
      },
      yAxis: {
        type: 'value',
        name: '幅值 (dB)'
      },
      series: newSeries.map((series) => ({
        ...series,
        type: 'line',
        smooth: true,
        showSymbol: false,
        symbol: 'none',
        sampling: 'lttb',
        lineStyle: { width: 2 }
      }))
    })

    // 根据当前系列数据计算合适的纵轴范围，避免纵轴过大导致曲线挤在一起
    try {
      const allY = []
      newSeries.forEach((s) => {
        const dataArr = Array.isArray(s?.data) ? s.data : []
        dataArr.forEach((pt) => {
          const y = Array.isArray(pt) ? Number(pt[1]) : Number(pt)
          if (Number.isFinite(y)) allY.push(y)
        })
      })

      if (allY.length) {
        let minVal = Math.min(...allY)
        let maxVal = Math.max(...allY)
        if (Number.isFinite(minVal) && Number.isFinite(maxVal)) {
          if (minVal === maxVal) {
            minVal -= 1
            maxVal += 1
          }
          const pad = (maxVal - minVal) * 0.1
          const yMin = minVal - pad
          const yMax = maxVal + pad
          chartInstance.setOption({
            xAxis: { min: 0, max: 300, name: '频率 (Hz)' },
            yAxis: { min: yMin, max: yMax, scale: true, name: '幅值 (dB)', axisLabel: { formatter: '{value}' } }
          })
        }
      }
    } catch (e) {}
  },
  { deep: true }
)

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const handleSearch = async () => {
  await store.fetchRecords()
}

const handleReset = async () => {
  store.resetFilters()
  await store.fetchRecords()
}

const handleOpenRimModal = (record) => {
  store.openRimModal(record)
}

const handleSwitchRimTab = (tab) => {
  store.switchRimModalTab(tab)
}

const handleOpenForceModal = (record) => {
  store.openForceModal(record)
}

onMounted(async () => {
  await store.initialize()
  window.addEventListener('resize', resizeChart)
})

watch(
  isLoading,
  () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.wheel-performance-query {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

.select-all-checkbox {
  margin-left: 12px;
}

.search-form {
  padding-top: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.table-metric-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-value {
  font-weight: 600;
  color: #303133;
}

.echarts-container {
  width: 100%;
  height: 520px;
}

.rim-modal__content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rim-modal__tabs {
  display: flex;
  gap: 16px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.rim-tab {
  border: none;
  background: none;
  font-size: 14px;
  color: #909399;
  cursor: pointer;
  padding: 0;
}

.rim-tab--active {
  color: #409eff;
  text-decoration: underline;
}

.rim-modal__body {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f6f8fb;
  border-radius: 8px;
  padding: 16px;
}

.rim-modal__image {
  width: 100%;
  height: 320px;
}

.rim-modal__caption {
  text-align: center;
  color: #606266;
}

.force-modal__content {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f6f8fb;
  border-radius: 8px;
  padding: 16px;
  min-height: 320px;
}

.force-modal__image {
  width: 100%;
  height: 320px;
}

.modal-title {
  font-weight: 600;
  font-size: 16px;
}
</style>



