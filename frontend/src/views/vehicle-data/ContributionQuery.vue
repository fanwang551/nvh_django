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
        <el-form-item label="项目名称">
          <el-select
            v-model="selectedVehicleModelId"
            placeholder="请选择项目名称"
            clearable
            filterable
            :loading="vmLoading"
            style="width: 320px"
            @change="handleQuery"
          >
            <el-option
              v-for="opt in vehicleModelOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!selectedVehicleModelId" @click="handleQuery">查询</el-button>
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

    <!-- 数据不足弹窗 -->
    <el-dialog v-model="insufficientDialog" title="数据不足" width="600px">
      <div class="insufficient-msg">
        零部件数需≥35，当前项目仅有 {{ partsCount }} 个零部件，数据不足。
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import vocApi from '@/api/voc'

const selectedVehicleModelId = ref(null)
const vehicleModelOptions = ref([])
const vmLoading = ref(false)

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

const formatNumber = (val) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  return isNaN(num) ? '-' : num.toFixed(3)
}

const loadVehicleModels = async () => {
  vmLoading.value = true
  try {
    const resp = await vocApi.getVehicleModelOptions()
    vehicleModelOptions.value = resp.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('获取项目名称失败')
  } finally {
    vmLoading.value = false
  }
}

const handleQuery = async () => {
  if (!selectedVehicleModelId.value) return
  try {
    const resp = await vocApi.getContributionTop25({ vehicle_model_id: selectedVehicleModelId.value })
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

onMounted(async () => {
  await loadVehicleModels()
})
</script>

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
</style>

