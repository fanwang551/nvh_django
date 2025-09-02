<template>
  <div class="sound-absorption-query">
    <!-- 查询表单 -->
    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>吸声系数查询</span>
        </div>
      </template>
      
      <el-form :model="searchForm" label-width="120px" class="search-form">
        <el-row :gutter="20">
          <!-- 零件名称选择 -->
          <el-col :span="8">
            <el-form-item label="零件名称">
              <el-select
                v-model="searchForm.partName"
                placeholder="请选择零件名称"
                clearable
                filterable
                :loading="partNamesLoading"
                style="width: 100%"
                @change="onPartNameChange"
              >
                <el-option
                  v-for="option in partNameOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 材料组成选择 -->
          <el-col :span="8">
            <el-form-item label="材料组成">
              <el-select
                v-model="searchForm.materialComposition"
                placeholder="请选择材料组成"
                clearable
                filterable
                :loading="materialCompositionsLoading"
                :disabled="!searchForm.partName"
                style="width: 100%"
                @change="onMaterialCompositionChange"
              >
                <el-option
                  v-for="option in materialCompositionOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 克重选择 -->
          <el-col :span="8">
            <el-form-item label="克重(g/m²)">
              <el-select
                v-model="searchForm.weight"
                placeholder="请选择克重"
                clearable
                filterable
                :loading="weightsLoading"
                :disabled="!searchForm.materialComposition"
                style="width: 100%"
                @change="onWeightChange"
              >
                <el-option
                  v-for="option in weightOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-row class="button-row">
          <el-col :span="24">
            <el-button
              type="primary"
              :loading="queryLoading"
              :disabled="!canQuery"
              @click="handleQuery"
            >
              查询
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 查询结果 -->
    <div v-if="hasResults" class="results-section">
      <!-- 基本信息卡片 -->
      <div v-for="(item, index) in queryResult" :key="item.id" class="result-item">
        <el-card class="result-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>查询结果 {{ index + 1 }}</span>
              <el-button
                v-if="item.test_image_path"
                type="primary"
                size="small"
                @click="showImageDialog(item)"
              >
                查看测试图
              </el-button>
            </div>
          </template>

          <!-- 基本信息 -->
          <div class="basic-info">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="零件名称">
                {{ item.part_name }}
              </el-descriptions-item>
              <el-descriptions-item label="材料组成">
                {{ item.material_composition }}
              </el-descriptions-item>
              <el-descriptions-item label="材料厂家">
                {{ item.manufacturer || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="测试机构">
                {{ item.test_institution || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="厚度(mm)">
                {{ item.thickness }}
              </el-descriptions-item>
              <el-descriptions-item label="克重(g/m²)">
                {{ item.weight }}
              </el-descriptions-item>
              <el-descriptions-item label="备注" :span="3">
                {{ item.remarks || '无' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 频率数据表格 -->
          <div class="frequency-table">
            <h4>频率数据</h4>
            <el-table :data="getTableData(item)" stripe border>
              <el-table-column prop="type" label="数据类型" width="100" align="center" fixed="left" />
              <el-table-column
                v-for="freq in frequencies"
                :key="freq"
                :prop="`freq_${freq}`"
                :label="`${freq}Hz`"
                width="80"
                align="center"
              >
                <template #default="scope">
                  {{ scope.row[`freq_${freq}`] || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center" fixed="right">
                <template #default="scope">
                  <el-button
                    v-if="scope.row.type === '测试值' && item.test_image_path"
                    type="primary"
                    size="small"
                    @click="showImageDialog(item)"
                  >
                    查看测试图
                  </el-button>
                  <span v-else-if="scope.row.type === '测试值' && !item.test_image_path" class="no-image-text">
                    无测试图
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>

      <!-- 图表展示 -->
      <el-card class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>吸声系数对比曲线</span>
          </div>
        </template>
        
        <div id="absorptionChart" style="width: 100%; height: 500px;"></div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="!queryLoading && queryResult.length === 0"
      description="暂无查询结果"
      style="margin-top: 40px;"
    />

    <!-- 图片查看弹窗 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="测试图片"
      width="80%"
      center
    >
      <div v-if="currentImageData" class="image-dialog-content">
        <div class="image-info">
          <p><strong>零件名称：</strong>{{ currentImageData.part_name }}</p>
          <p><strong>材料组成：</strong>{{ currentImageData.material_composition }}</p>
          <p><strong>克重：</strong>{{ currentImageData.weight }}g/m²</p>
          <p v-if="currentImageData.test_date"><strong>测试日期：</strong>{{ currentImageData.test_date }}</p>
          <p v-if="currentImageData.test_location"><strong>测试地点：</strong>{{ currentImageData.test_location }}</p>
          <p v-if="currentImageData.test_engineer"><strong>测试工程师：</strong>{{ currentImageData.test_engineer }}</p>
        </div>
        
        <div class="image-container">
          <el-empty 
            v-if="!currentImageData.test_image_path"
            description="暂无测试图片"
            :image-size="80"
          />
          <img
            v-else
            :src="currentImageData.test_image_path"
            :alt="`${currentImageData.part_name}测试图片`"
            style="width: 100%; max-height: 500px; object-fit: contain;"
            @error="handleImageError"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useSoundAbsorptionQueryStore } from '@/store/soundAbsorptionQuery'
import * as echarts from 'echarts'

export default {
  name: 'SoundAbsorptionQuery',
  setup() {
    const store = useSoundAbsorptionQueryStore()
    let chartInstance = null

    // 频率列表
    const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

    // 计算属性
    const searchForm = computed(() => store.searchForm)
    const partNameOptions = computed(() => store.partNameOptions)
    const materialCompositionOptions = computed(() => store.materialCompositionOptions)
    const weightOptions = computed(() => store.weightOptions)
    const queryResult = computed(() => store.queryResult)
    const chartData = computed(() => store.chartData)
    
    const partNamesLoading = computed(() => store.partNamesLoading)
    const materialCompositionsLoading = computed(() => store.materialCompositionsLoading)
    const weightsLoading = computed(() => store.weightsLoading)
    const queryLoading = computed(() => store.queryLoading)
    
    const canQuery = computed(() => store.canQuery)
    const hasResults = computed(() => store.hasResults)
    
    const imageDialogVisible = computed({
      get: () => store.imageDialogVisible,
      set: (value) => {
        if (!value) {
          store.closeImageDialog()
        }
      }
    })
    const currentImageData = computed(() => store.currentImageData)

    // 方法
    const onPartNameChange = async (partName) => {
      try {
        await store.onPartNameChange(partName)
      } catch (error) {
        ElMessage.error('加载材料组成选项失败')
      }
    }

    const onMaterialCompositionChange = async (materialComposition) => {
      try {
        await store.onMaterialCompositionChange(materialComposition)
      } catch (error) {
        ElMessage.error('加载克重选项失败')
      }
    }

    const onWeightChange = (weight) => {
      store.onWeightChange(weight)
    }

    const handleQuery = async () => {
      try {
        await store.queryData()
        
        if (store.hasResults) {
          ElMessage.success(`查询成功，共找到 ${store.queryResult.length} 条数据`)
          
          // 等待DOM更新后再初始化图表
          await nextTick()
          initChart()
        } else {
          ElMessage.info('未找到匹配的数据')
        }
      } catch (error) {
        ElMessage.error(error.message || '查询失败')
      }
    }

    const handleReset = () => {
      store.resetState()
      destroyChart()
      ElMessage.info('已重置查询条件')
    }

    const showImageDialog = (data) => {
      store.showImageDialog(data)
    }

    const handleImageError = (event) => {
      event.target.src = '/placeholder-image.png' // 设置占位图片
      ElMessage.warning('图片加载失败')
    }

    // 获取表格数据
    const getTableData = (item) => {
      const testRow = { type: '测试值' }
      const targetRow = { type: '目标值' }
      
      frequencies.forEach(freq => {
        const testValue = item.test_frequency_data[`test_value_${freq}`]
        const targetValue = item.target_frequency_data[`target_value_${freq}`]
        
        testRow[`freq_${freq}`] = testValue !== null && testValue !== undefined ? testValue : '-'
        targetRow[`freq_${freq}`] = targetValue !== null && targetValue !== undefined ? targetValue : '-'
      })
      
      return [testRow, targetRow]
    }

    // 初始化图表
    const initChart = () => {
      destroyChart()
      
      const chartDom = document.getElementById('absorptionChart')
      if (!chartDom) return
      
      chartInstance = echarts.init(chartDom)
      
      const option = store.getChartOption()
      chartInstance.setOption(option)
      
      // 绑定点击事件
      chartInstance.on('click', (params) => {
        if (params.data && params.data.itemData) {
          showImageDialog(params.data.itemData)
        }
      })
      
      // 响应式处理
      window.addEventListener('resize', chartInstance.resize)
    }

    // 销毁图表
    const destroyChart = () => {
      if (chartInstance) {
        window.removeEventListener('resize', chartInstance.resize)
        chartInstance.dispose()
        chartInstance = null
      }
    }

    // 生命周期
    onMounted(async () => {
      try {
        await store.initializePageData()
      } catch (error) {
        ElMessage.error('初始化页面数据失败')
      }
    })

    onUnmounted(() => {
      destroyChart()
    })

    return {
      // 状态
      searchForm,
      partNameOptions,
      materialCompositionOptions,
      weightOptions,
      queryResult,
      chartData,
      partNamesLoading,
      materialCompositionsLoading,
      weightsLoading,
      queryLoading,
      canQuery,
      hasResults,
      imageDialogVisible,
      currentImageData,
      frequencies,
      
      // 方法
      onPartNameChange,
      onMaterialCompositionChange,
      onWeightChange,
      handleQuery,
      handleReset,
      showImageDialog,
      handleImageError,
      getTableData
    }
  }
}
</script>

<style scoped>
.sound-absorption-query {
  padding: 20px;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.search-form {
  .button-row {
    margin-top: 20px;
    text-align: center;
  }
}

.results-section {
  margin-top: 20px;
}

.result-item {
  margin-bottom: 20px;
}

.result-card {
  .basic-info {
    margin-bottom: 20px;
  }
  
  .frequency-table {
    h4 {
      margin-bottom: 10px;
      color: #303133;
      font-weight: 600;
    }
  }
}

.chart-card {
  margin-top: 20px;
}

.image-dialog-content {
  .image-info {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    p {
      margin: 8px 0;
      color: #606266;
    }
  }
  
  .image-container {
    text-align: center;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 10px;
    background-color: #fff;
  }
}

.no-image-text {
  color: #909399;
  font-size: 12px;
}

/* 响应式处理 */
@media (max-width: 768px) {
  .search-form {
    :deep(.el-col) {
      margin-bottom: 15px;
    }
  }
  
  .basic-info {
    :deep(.el-descriptions) {
      font-size: 12px;
    }
  }
  
  .frequency-table {
    overflow-x: auto;
  }
}
</style>