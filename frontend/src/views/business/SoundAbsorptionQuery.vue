<template>
  <div class="sound-absorption-query">
    <!-- 查询表单 -->
    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>吸声系数查询</span>
        </div>
      </template>
      
      <el-form :model="store.searchCriteria" label-width="120px" class="search-form">
        <el-row :gutter="4">
          <!-- 零件名称选择 -->
          <el-col :span="6">
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
          <el-col :span="6">
            <el-form-item label="材料组成">
              <el-select
                v-model="store.searchCriteria.materialComposition"
                placeholder="请选择材料组成"
                clearable
                filterable
                :loading="store.materialCompositionsLoading"
                :disabled="!store.searchCriteria.partName"
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
          <el-col :span="6">
            <el-form-item label="克重(g/m²)">
              <el-select
                v-model="store.searchCriteria.weight"
                placeholder="请选择克重"
                clearable
                filterable
                :loading="store.weightsLoading"
                :disabled="!store.searchCriteria.materialComposition"
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

          <el-col :span="6" style="text-align: right; padding-right: 40px;">
            <el-button
                type="primary"
                :loading="store.queryLoading"
                :disabled="!store.canQuery"
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
    <div v-if="store.hasResults" class="results-section">
      <!-- 基本信息卡片 -->
      <div v-for="(item, index) in store.queryResults" :key="item.id" class="result-item">
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
      v-else-if="!store.queryLoading && store.queryResults.length === 0"
      description="暂无查询结果"
      style="margin-top: 40px;"
    />

    <!-- 图片查看弹窗 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="测试图片"
      width="80%"
      center
      @close="closeImageDialog"
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
            :src="getImageUrl(currentImageData.test_image_path)"
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
import { ref, computed, onMounted, onActivated, onDeactivated, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useSoundAbsorptionQueryStore } from '@/store/soundAbsorptionQuery'
import { getImageUrl, handleImageError } from '@/utils/imageService'
import * as echarts from 'echarts'

export default {
  name: 'SoundAbsorptionQuery',
  setup() {
    const store = useSoundAbsorptionQueryStore()
    let chartInstance = null

    // UI状态管理（组件职责）
    const imageDialogVisible = ref(false)
    const currentImageData = ref(null)

    // 频率列表
    const frequencies = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]

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

    // 图片错误处理已移至 @/utils/imageService，直接使用导入的 handleImageError

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
      const colors = ['#5470c6', '#ee6666', '#91cc75', '#fac858', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

      const series = []
      if (store.formattedChartData && Array.isArray(store.formattedChartData)) {
        store.formattedChartData.forEach((item, index) => {
          if (!item || !item.testData || !Array.isArray(item.testData)) return

          // 测试值曲线（实线）
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
            color: colors[index % colors.length],
            type: 'solid'
          },
          itemStyle: {
            color: colors[index % colors.length]
          },
          emphasis: {
            focus: 'series',
            symbolSize: 12
          },
          connectNulls: false
        })

          // 目标值曲线（虚线）
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
            color: colors[index % colors.length],
            type: 'dashed'
          },
          itemStyle: {
            color: colors[index % colors.length]
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
          text: '吸声系数曲线对比',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
            if (params.length === 0) return ''

            const dataIndex = params[0].dataIndex
            const freq = frequencies[dataIndex]
            let result = `频率: ${freq}Hz<br/>`

            params.forEach(param => {
              if (param.value !== null && param.value !== undefined) {
                result += `${param.seriesName}: ${param.value}<br/>`
              }
            })
            result += '<br/>点击数据点查看测试详情'
            return result
          }
        },
        legend: {
          top: 30,
          type: 'scroll'
        },
        grid: {
          left: '8%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          name: '频率 (Hz)',
          nameLocation: 'middle',
          nameGap: 30,
          data: frequencies.map(freq => freq.toString()),
          axisLabel: {
            rotate: 45,
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: '吸声系数',
          nameLocation: 'middle',
          nameGap: 50,
          min: 0,
          max: 1,
          axisLabel: {
            formatter: '{value}',
            fontSize: 12
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: '#e6e6e6',
              type: 'dashed'
            }
          }
        },
        series: series,
        dataZoom: [
          {
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            start: 0,
            end: 100,
            bottom: '5%'
          }
        ]
      }
    }

    // 图表管理：初始化图表（组件职责）
    const initChart = () => {
      destroyChart()

      const chartDom = document.getElementById('absorptionChart')
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

    // 生命周期
    onMounted(async () => {
      try {
        await store.initializeData()

        // 如果有查询结果，重新渲染图表
        if (store.hasResults) {
          await nextTick()
          initChart()
        }
      } catch (error) {
        ElMessage.error('初始化页面数据失败')
      }
    })

    onActivated(async () => {
      try {
        await store.initializeData()

        // 如果有查询结果，重新渲染图表
        if (store.hasResults) {
          await nextTick()
          initChart()
        }
      } catch (error) {
        ElMessage.error('初始化页面数据失败')
      }
    })

    onDeactivated(() => {
      destroyChart()
      // 关闭可能打开的弹窗
      if (imageDialogVisible.value) {
        closeImageDialog()
      }
    })

    onUnmounted(() => {
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