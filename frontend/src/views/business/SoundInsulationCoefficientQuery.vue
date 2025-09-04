<template>
  <div class="sound-insulation-coefficient-query">
    <!-- 查询表单 -->
    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>隔声量查询</span>
        </div>
      </template>
      
      <el-form :model="store.searchCriteria" label-width="90px" class="search-form">
        <el-row :gutter="4">
          <!-- 测试类型选择 -->
          <el-col :span="5">
            <el-form-item label="测试类型">
              <el-select
                v-model="store.searchCriteria.testType"
                placeholder="请选择测试类型"
                clearable
                filterable
                :loading="store.testTypesLoading"
                style="width: 100%"
                @change="onTestTypeChange"
              >
                <el-option
                  v-for="option in store.testTypes"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 零件名称选择 -->
          <el-col :span="5">
            <el-form-item label="零件名称">
              <el-select
                v-model="store.searchCriteria.partName"
                placeholder="请选择零件名称"
                clearable
                filterable
                :loading="store.partNamesLoading"
                style="width: 100%"
                @change="onPartNameChange"
              >
                <el-option
                  v-for="option in store.partNames"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 材料组成选择 -->
          <el-col :span="5">
            <el-form-item label="材料组成">
              <el-select
                v-model="store.searchCriteria.materialComposition"
                placeholder="请选择材料组成"
                clearable
                filterable
                :loading="store.materialCompositionsLoading"
                style="width: 100%"
                @change="onMaterialCompositionChange"
              >
                <el-option
                  v-for="option in store.materialCompositions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 克重选择 -->
          <el-col :span="5">
            <el-form-item label="克重">
              <el-select
                v-model="store.searchCriteria.weight"
                placeholder="请选择克重"
                clearable
                filterable
                :loading="store.weightsLoading"
                style="width: 100%"
                @change="onWeightChange"
              >
                <el-option
                  v-for="option in store.weights"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 操作按钮 -->
          <el-col :span="4">
            <el-form-item label=" ">
              <div class="button-group">
                <el-button
                  type="primary"
                  :loading="store.queryLoading"
                  :disabled="!store.isValidQuery"
                  @click="handleQuery"
                >
                  查询
                </el-button>
                <el-button @click="handleReset">重置</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 查询结果 -->
    <div v-if="store.hasResults" class="results-section">
      <!-- 基本信息卡片 -->
      <div v-for="(item, index) in store.queryResults" :key="item.id" class="result-item">
        <el-card class="result-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>隔声量系数</span>
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
              <el-descriptions-item label="零件名称">{{ item.part_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="材料组成">{{ item.material_composition || '-' }}</el-descriptions-item>
              <el-descriptions-item label="测试类型">{{ item.test_type_display || '-' }}</el-descriptions-item>
              <el-descriptions-item label="厚度">{{ item.thickness ? `${item.thickness}mm` : '-' }}</el-descriptions-item>
              <el-descriptions-item label="克重">{{ item.weight ? `${item.weight}g/m²` : '-' }}</el-descriptions-item>
              <el-descriptions-item label="材料厂家">{{ item.manufacturer || '-' }}</el-descriptions-item>
              <el-descriptions-item label="测试机构">{{ item.test_institution || '-' }}</el-descriptions-item>
              <el-descriptions-item label="测试日期">{{ item.test_date || '-' }}</el-descriptions-item>
              <el-descriptions-item label="测试地点">{{ item.test_location || '-' }}</el-descriptions-item>
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
            <span>隔声量对比曲线</span>
          </div>
        </template>
        
        <div id="insulationChart" style="width: 100%; height: 500px;"></div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="!store.queryLoading && store.queryResults.length === 0"
      description="暂无查询结果"
      style="margin-top: 40px;"
    />

    <!-- 加载状态 -->
    <div v-if="store.queryLoading" class="loading-container">
      <el-loading-spinner />
      <p>正在查询数据...</p>
    </div>

    <!-- 测试图片弹窗 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="测试图片详情"
      width="600px"
      :before-close="closeImageDialog"
    >
      <div v-if="currentImageData" class="image-dialog-content">
        <!-- 基本信息 -->
        <div class="image-basic-info">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="零件名称">{{ currentImageData.part_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="材料组成">{{ currentImageData.material_composition || '-' }}</el-descriptions-item>
            <el-descriptions-item label="测试类型">{{ currentImageData.test_type_display || '-' }}</el-descriptions-item>
            <el-descriptions-item label="克重">{{ currentImageData.weight ? `${currentImageData.weight}g/m²` : '-' }}</el-descriptions-item>
            <el-descriptions-item label="测试工程师">{{ currentImageData.test_engineer || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ currentImageData.remarks || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 测试图片 -->
        <div v-if="currentImageData.test_image_path" class="image-section">
          <h4>测试图片</h4>
          <div class="image-container">
            <img
              :src="getImageUrl(currentImageData.test_image_path)"
              :alt="`${currentImageData.part_name}测试图片`"
              class="test-image"
              @error="handleImageError"
            />
          </div>
        </div>
        <div v-else class="no-image">
          <el-empty description="暂无测试图片" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onActivated, onDeactivated, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useSoundInsulationCoefficientQueryStore } from '@/store/soundInsulationCoefficientQuery'
import { getImageUrl, handleImageError } from '@/utils/imageService'
import * as echarts from 'echarts'

export default {
  name: 'SoundInsulationCoefficientQuery',
  setup() {
    const store = useSoundInsulationCoefficientQueryStore()
    let chartInstance = null

    // UI状态管理（组件职责）
    const imageDialogVisible = ref(false)
    const currentImageData = ref(null)

    // 频率列表
    const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

    // UI交互处理：测试类型变化
    const onTestTypeChange = async (testType) => {
      try {
        await store.handleTestTypeChange(testType)
      } catch (error) {
        ElMessage.error('加载零件名称选项失败')
      }
    }

    // UI交互处理：零件名称变化
    const onPartNameChange = async (partName) => {
      try {
        await store.handlePartNameChange(partName)
      } catch (error) {
        ElMessage.error('加载材料组成选项失败')
      }
    }

    // UI交互处理：材料组成变化
    const onMaterialCompositionChange = async (materialComposition) => {
      try {
        await store.handleMaterialCompositionChange(materialComposition)
      } catch (error) {
        ElMessage.error('加载克重选项失败')
      }
    }

    // UI交互处理：克重变化
    const onWeightChange = (weight) => {
      store.handleWeightChange(weight)
    }

    // UI状态管理：显示图片弹窗
    const showImageDialog = (data) => {
      if (data && data.test_image_path) {
        currentImageData.value = data
        imageDialogVisible.value = true
      }
    }

    // UI状态管理：关闭图片弹窗
    const closeImageDialog = () => {
      imageDialogVisible.value = false
      currentImageData.value = null
    }

    const handleQuery = async () => {
      try {
        await store.queryData()

        if (store.hasResults) {
          ElMessage.success(`查询成功，共找到 ${store.queryResults.length} 条数据`)

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
      closeImageDialog()
      ElMessage.info('已重置查询条件')
    }

    // 获取表格数据
    const getTableData = (item) => {
      if (!item) return []

      const testRow = { type: '测试值' }
      const targetRow = { type: '目标值' }

      frequencies.forEach(freq => {
        const testValue = item.test_frequency_data?.[`test_value_${freq}`]
        const targetValue = item.target_frequency_data?.[`target_value_${freq}`]

        testRow[`freq_${freq}`] = testValue !== null && testValue !== undefined ? testValue : '-'
        targetRow[`freq_${freq}`] = targetValue !== null && targetValue !== undefined ? targetValue : '-'
      })

      return [testRow, targetRow]
    }

    // 图表管理：获取图表配置（组件职责）
    const getChartOption = () => {
      // 定义固定的颜色方案，确保测试值和目标值有明显区分
      const testValueColor = '#409EFF'  // 蓝色 - 测试值
      const targetValueColor = '#67C23A' // 绿色 - 目标值

      const series = []
      if (store.formattedChartData && Array.isArray(store.formattedChartData)) {
        store.formattedChartData.forEach((item, index) => {
          if (!item || !item.testData || !Array.isArray(item.testData)) return

          // 测试值曲线（蓝色实线）
          series.push({
            name: `测试值`,
            type: 'line',
            data: item.testData.map((value, freqIndex) => ({
              value: value,
              freq: frequencies[freqIndex],
              freqLabel: `${frequencies[freqIndex]}Hz`,
              itemData: item.itemData
            })),
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3,
              color: testValueColor,
              type: 'solid'
            },
            itemStyle: {
              color: testValueColor
            },
            emphasis: {
              focus: 'series',
              symbolSize: 12
            },
            connectNulls: false
          })

          // 目标值曲线（绿色虚线）
          if (item.targetData && Array.isArray(item.targetData)) {
            series.push({
              name: `目标值`,
              type: 'line',
              data: item.targetData.map((value, freqIndex) => ({
                value: value,
                freq: frequencies[freqIndex],
                freqLabel: `${frequencies[freqIndex]}Hz`,
                itemData: item.itemData
              })),
              symbol: 'diamond',
              symbolSize: 8,
              lineStyle: {
                width: 3,
                color: targetValueColor,
                type: 'dashed'
              },
              itemStyle: {
                color: targetValueColor
              },
              emphasis: {
                focus: 'series',
                symbolSize: 12
              },
              connectNulls: false
            })
          }
        })
      }

      return {
        title: {
          text: '隔声量对比曲线',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const data = params.data
            if (!data || !data.itemData) return ''

            const item = data.itemData
            return `
              <div style="text-align: left;">
                <strong>${item.part_name || '未知零件'}</strong><br/>
                <strong>材料组成:</strong> ${item.material_composition || '-'}<br/>
                <strong>测试类型:</strong> ${item.test_type_display || '-'}<br/>
                <strong>频率:</strong> ${data.freqLabel}<br/>
                <strong>隔声量:</strong> ${data.value !== null ? data.value + ' dB' : '-'}<br/>
                <strong>克重:</strong> ${item.weight ? item.weight + 'g/m²' : '-'}
              </div>
            `
          }
        },
        legend: {
          data: ['测试值', '目标值'],
          top: 30,
          itemGap: 20
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: frequencies.map(f => `${f}Hz`),
          name: '频率 (Hz)',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: '隔声量 (dB)',
          nameLocation: 'middle',
          nameGap: 50,
          axisLabel: {
            formatter: '{value} dB'
          }
        },
        series: series,
        dataZoom: [
          {
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            start: 0,
            end: 100
          }
        ]
      }
    }

    // 图表管理：初始化图表（组件职责）
    const initChart = () => {
      destroyChart()

      const chartDom = document.getElementById('insulationChart')
      if (!chartDom || !store.formattedChartData || !Array.isArray(store.formattedChartData) || !store.formattedChartData.length) return

      chartInstance = echarts.init(chartDom)

      // 使用组件内的图表配置
      const option = getChartOption()
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

    // 生命周期管理
    onMounted(async () => {
      try {
        await store.initializeData()
      } catch (error) {
        ElMessage.error('初始化数据失败')
      }
    })

    onActivated(async () => {
      // 组件被激活时重新初始化图表
      if (store.hasResults) {
        await nextTick()
        initChart()
      }
    })

    onDeactivated(() => {
      // 组件被停用时销毁图表
      destroyChart()
    })

    onUnmounted(() => {
      // 组件卸载时清理资源
      destroyChart()
    })

    return {
      // Store
      store,

      // UI状态
      imageDialogVisible,
      currentImageData,
      frequencies,

      // 方法
      onTestTypeChange,
      onPartNameChange,
      onMaterialCompositionChange,
      onWeightChange,
      handleQuery,
      handleReset,
      showImageDialog,
      closeImageDialog,
      handleImageError,
      getImageUrl,
      getTableData
    }
  }
}
</script>

<style scoped>
.sound-insulation-coefficient-query {
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
  .button-group {
    display: flex;
    gap: 4px;
    align-items: center;
    justify-content: flex-start;
  }

  .button-group .el-button {
    margin-left: 0;
    margin-right: 0;
    font-size: 13px;
    padding: 8px 12px;
  }
}

.results-section {
  margin-top: 20px;
}

.result-item {
  margin-bottom: 20px;
}

.result-card {
  border: 1px solid #e4e7ed;
}

.basic-info {
  margin-bottom: 20px;
}

.frequency-table {
  margin-top: 20px;
}

.frequency-table h4 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.chart-card {
  margin-top: 20px;
  border: 1px solid #e4e7ed;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.loading-container p {
  margin-top: 10px;
  font-size: 14px;
}

.image-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.image-basic-info {
  margin-bottom: 20px;
}

.image-basic-info h4 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.image-section {
  margin-top: 20px;
}

.image-section h4 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.image-container {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.test-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-image {
  padding: 40px;
  text-align: center;
}

.no-image-text {
  color: #909399;
  font-size: 12px;
}

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 12px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 8px 0;
}

/* 描述列表样式优化 */
:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-descriptions__content) {
  color: #303133;
}
</style>
