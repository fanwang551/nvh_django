<template>
  <div class="business-center">
    <div class="page-header">
      <h2>业务中心</h2>
      <p class="page-description">选择业务功能模块</p>
    </div>

    <div class="business-modules">
      <div
        v-for="module in businessModules"
        :key="module.name"
        class="module-item"
        @click="openModule(module)"
      >
        <div class="module-icon">
          <el-icon :size="32">
            <component :is="module.icon" />
          </el-icon>
        </div>
        <div class="module-title">{{ module.title }}</div>
        <div class="module-description">{{ module.description }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataAnalysis,
  TrendCharts,
  Connection,
  Monitor,
  Picture
} from '@element-plus/icons-vue'

const router = useRouter()

// 业务模块
const businessModules = ref([
  {
    name: 'modal-data-query',
    title: '模态数据查询',
    description: '查询和分析模态测试数据',
    icon: DataAnalysis
  },
  {
    name: 'modal-data-compare',
    title: '模态数据对比',
    description: '对比不同模态测试结果',
    icon: TrendCharts
  },
  {
    name: 'airtight-leak-compare',
    title: '气密性泄漏量对比',
    description: '对比气密性测试泄漏量数据',
    icon: Connection
  },
  {
    name: 'airtight-test-chart',
    title: '气密性测试图查询',
    description: '查看气密性测试图表和报告',
    icon: Monitor
  },
  {
    name: 'airtightness-image-query',
    title: '气密性测试图片查询',
    description: '查看各车型的气密性测试图片',
    icon: Picture
  },
  {
    name: 'sound-insulation-compare',
    title: '区域隔声量（ATF）对比',
    description: '对比不同车型在各区域的隔声量数据',
    icon: TrendCharts
  }
])

// 打开业务模块
const openModule = (module) => {
  router.push(`/business/${module.name}`)
}
</script>

<style scoped>
.business-center {
  padding: 0;
}

.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.business-modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.module-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.module-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.module-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.module-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.module-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}
</style>
