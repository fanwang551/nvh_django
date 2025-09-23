<template>
  <div class="ntf-query">
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">查询条件</span>
        </div>
      </template>
      <el-form label-width="80px" class="filter-form">
        <el-form-item label="车型">
          <el-select
            v-model="localVehicleId"
            placeholder="请选择车型"
            filterable
            clearable
            :loading="isLoading && !localVehicleId"
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
      </el-form>
    </el-card>

    <el-alert v-if="error" type="error" :title="error" show-icon />

    <el-card v-loading="isLoading" class="info-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试信息</span>
          <el-tag v-if="detail?.development_stage" effect="plain">{{ detail.development_stage }}</el-tag>
        </div>
      </template>
      <el-empty v-if="!detail" description="请选择车型查看测试信息" />
      <div v-else class="info-content">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="测试人员">{{ detail.tester || '-' }}</el-descriptions-item>
          <el-descriptions-item label="测试时间">{{ formatDateTime(detail.test_time) }}</el-descriptions-item>
          <el-descriptions-item label="测试地点">{{ detail.location || '-' }}</el-descriptions-item>
          <el-descriptions-item label="车型码">
            <span>{{ detail.vehicle?.code || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="VIN码">
            <span>{{ detail.vehicle?.vin || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="驱动方式">
            <span>{{ detail.vehicle?.drive_type || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="悬挂形式">{{ detail.suspension_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="天窗形式">{{ detail.sunroof_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="座位数">{{ detail.seat_count || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="image-gallery">
          <div v-for="slot in imageSlots" :key="slot.key" class="image-item">
            <div class="image-title">{{ slot.label }}</div>
            <el-image
              v-if="detail.images?.[slot.key]"
              :src="detail.images?.[slot.key]"
              fit="cover"
              :preview-src-list="[detail.images?.[slot.key]]"
            >
              <template #error>
                <div class="image-placeholder">加载失败</div>
              </template>
            </el-image>
            <div v-else class="image-placeholder">暂无图片</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试结果</span>
        </div>
      </template>
      <el-table
        v-if="tableRows.length"
        :data="tableRows"
        border
        stripe
        class="result-table"
      >
        <el-table-column prop="measurement_point" label="测点" min-width="140" />
        <el-table-column prop="direction_label" label="方向" min-width="100" />
        <el-table-column label="目标" min-width="120">
          <template #default="{ row }">
            <span :class="getValueClass(row.target)">{{ formatValue(row.target) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-for="column in seatColumns"
          :key="column.key"
          :label="column.label"
          min-width="120"
        >
          <template #default="{ row }">
            <span :class="getValueClass(row[column.key])">{{ formatValue(row[column.key]) }}</span>
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
      <div v-if="heatmap.points.length && heatmap.frequency.length" ref="heatmapRef" class="heatmap"></div>
      <el-empty v-else description="暂无热力图数据" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useNTFQueryStore } from '@/store'

const VALUE_LEVEL = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
}

echarts.use([HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent, TitleComponent, CanvasRenderer])

const store = useNTFQueryStore()
const { vehicleOptions, detail, seatColumns, tableRows, heatmap, isLoading, error, selectedVehicleId } = storeToRefs(store)

const localVehicleId = ref(selectedVehicleId.value)
const heatmapRef = ref(null)
let chartInstance = null

const imageSlots = computed(() => [
  { key: 'front', label: '前排测试图片' },
  { key: 'middle', label: '中排测试图片' },
  { key: 'rear', label: '后排测试图片' }
])

function formatDateTime(value) {
  if (!value) {
    return '-'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  const numeric = Number(value)
  if (Number.isNaN(numeric)) {
    return value
  }
  return numeric.toFixed(2)
}

function classifyValue(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return null
  }
  if (numeric > 65) {
    return VALUE_LEVEL.HIGH
  }
  if (numeric >= 60) {
    return VALUE_LEVEL.MEDIUM
  }
  return VALUE_LEVEL.LOW
}

function getValueClass(value) {
  const level = classifyValue(value)
  if (!level) {
    return 'ntf-cell'
  }
  return `ntf-cell ntf-cell--${level}`
}

function buildHeatmapSeriesData() {
  if (!heatmap.value?.matrix?.length) {
    return []
  }
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

function computeHeatmapRange() {
  const values = []
  heatmap.value.matrix.forEach((row) => {
    row.forEach((value) => {
      const numeric = Number(value)
      if (Number.isFinite(numeric)) {
        values.push(numeric)
      }
    })
  })
  if (!values.length) {
    return { min: 0, max: 0 }
  }
  return {
    min: Math.min(...values),
    max: Math.max(...values)
  }
}

function renderHeatmap() {
  if (!heatmapRef.value) {
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(heatmapRef.value)
  }

  const data = buildHeatmapSeriesData()
  const valueRange = computeHeatmapRange()

  const option = {
    title: {
      left: 'center',
      text: 'Frequency vs Measurement Point'
    },
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
    grid: {
      top: 60,
      left: 80,
      right: 20,
      bottom: 50
    },
    xAxis: {
      type: 'category',
      data: heatmap.value.frequency,
      name: '频率 (Hz)',
      nameGap: 18,
      axisLabel: {
        fontSize: 10,
        rotate: 45
      }
    },
    yAxis: {
      type: 'category',
      data: heatmap.value.points,
      name: '测点',
      nameGap: 16,
      axisLabel: {
        fontSize: 12
      }
    },
    visualMap: {
      min: valueRange.min,
      max: valueRange.max,
      orient: 'vertical',
      right: 10,
      top: 'center',
      calculable: true,
      inRange: {
        color: ['#33cc33', '#ffeb3b', '#f44336']
      }
    },
    series: [
      {
        name: 'NTF Heatmap',
        type: 'heatmap',
        data,
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.4)'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)
  chartInstance.resize()
}

const handleVehicleChange = async (value) => {
  if (!value) {
    store.resetData()
    return
  }
  await store.loadByVehicle(value)
  await nextTick()
  if (heatmap.value.points.length && heatmap.value.frequency.length) {
    renderHeatmap()
  } else if (chartInstance) {
    chartInstance.clear()
  }
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(
    selectedVehicleId,
    (value) => {
      if (localVehicleId.value !== value) {
        localVehicleId.value = value
      }
    }
)

watch(
    () => heatmap.value,
    async (newValue) => {
      if (!newValue) {
        return
      }
      await nextTick()
      if (newValue.points.length && newValue.frequency.length) {
        renderHeatmap()
      } else if (chartInstance) {
        chartInstance.clear()
      }
    },
    { deep: true }
)


onMounted(async () => {
  await store.fetchVehicleOptions()
  if (localVehicleId.value) {
    await handleVehicleChange(localVehicleId.value)
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.ntf-query {
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

.filter-form {
  max-width: 420px;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.image-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-title {
  font-weight: 500;
  color: #606266;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  background-color: #f5f7fa;
  border-radius: 8px;
  color: #909399;
}

.heatmap {
  width: 100%;
  height: 420px;
}

.result-table {
  --el-table-border-color: #ebeef5;
}

.ntf-cell {
  font-weight: 600;
}

.ntf-cell--high {
  color: #f56c6c;
}

.ntf-cell--medium {
  color: #e6a23c;
}

.ntf-cell--low {
  color: #67c23a;
}
</style>



