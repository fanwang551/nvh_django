<template>
  <div class="business-center">
    <div class="page-header">
      <h2>业务中心</h2>
      <p class="page-description">选择业务功能模块</p>
    </div>

    <el-collapse v-model="activeGroups" class="business-groups">
      <!-- 模态和气密性模块-->
      <el-collapse-item name="modal" class="group-item">
        <template #title>
          <h3 class="group-title">模态和气密性模块</h3>
        </template>
        <div class="group-divider"></div>
        <div class="modules-grid">
          <div
            v-for="module in modalAirtightnessModules"
            :key="module.name"
            class="module-card"
            role="button"
            tabindex="0"
            @click="openModule(module)"
            @keydown.enter.prevent="openModule(module)"
          >
            <div class="module-media">
              <el-icon :size="20" class="media-icon">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title" :title="module.title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 吸隔声模块-->
      <el-collapse-item name="sound" class="group-item">
        <template #title>
          <h3 class="group-title">吸隔声模块</h3>
        </template>
        <div class="group-divider"></div>
        <div class="modules-grid">
          <div
            v-for="module in soundModules"
            :key="module.name"
            class="module-card"
            role="button"
            tabindex="0"
            @click="openModule(module)"
            @keydown.enter.prevent="openModule(module)"
          >
            <div class="module-media">
              <el-icon :size="20" class="media-icon">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title" :title="module.title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 动刚度模块-->
      <el-collapse-item name="dynamic" class="group-item">
        <template #title>
          <h3 class="group-title">动刚度模块</h3>
        </template>
        <div class="group-divider"></div>
        <div class="modules-grid">
          <div
            v-for="module in dynamicStiffnessModules"
            :key="module.name"
            class="module-card"
            role="button"
            tabindex="0"
            @click="openModule(module)"
            @keydown.enter.prevent="openModule(module)"
          >
            <div class="module-media">
              <el-icon :size="20" class="media-icon">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title" :title="module.title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 车轮性能模块 -->
      <el-collapse-item name="wheel" class="group-item">
        <template #title>
          <h3 class="group-title">车轮性能模块</h3>
        </template>
        <div class="group-divider"></div>
        <div class="modules-grid">
          <div
            v-for="module in wheelPerformanceModules"
            :key="module.name"
            class="module-card"
            role="button"
            tabindex="0"
            @click="openModule(module)"
            @keydown.enter.prevent="openModule(module)"
          >
            <div class="module-media">
              <el-icon :size="20" class="media-icon">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title" :title="module.title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
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
  Picture,
  MagicStick,
  Setting,
  Odometer
} from '@element-plus/icons-vue'

const router = useRouter()

// 控制折叠面板展开状态
const activeGroups = ref(['modal', 'sound', 'dynamic', 'wheel'])

// 模态和气密性模块
const modalAirtightnessModules = ref([
  {
    name: 'modal-data-query',
    title: '模态数据查询',
    desc: '按车型/零件检索模态数据',
    icon: DataAnalysis,
    bg: 'linear-gradient(135deg,#5b8ff9,#3b76f6)'
  },
  {
    name: 'modal-data-compare',
    title: '模态数据对比',
    desc: '多车型/状态可视化对比',
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#34d399,#10b981)'
  },
  {
    name: 'airtight-leak-compare',
    title: '气密性泄漏量对比',
    desc: '整车及分系统泄漏量对照',
    icon: Connection,
    bg: 'linear-gradient(135deg,#f59e0b,#fbbf24)'
  },
  {
    name: 'airtightness-image-query',
    title: '气密性测试图片查询',
    desc: '三大区域测试图像速览',
    icon: Picture,
    bg: 'linear-gradient(135deg,#f87171,#ef4444)'
  }
])

// 吸隔声模块
const soundModules = ref([
  {
    name: 'sound-insulation-compare',
    title: '区域隔声量（ATF）对比',
    desc: '按区域对比不同车型隔声量',
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#a78bfa,#7c3aed)'
  },
  {
    name: 'acoustic-analysis',
    title: '声学测试数据分析',
    desc: '车型/工况/测点曲线与指标',
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#60a5fa,#3b82f6)'
  },
  {
    name: 'vehicle-sound-insulation-query',
    title: '车型隔声量查询',
    desc: '检索特定车型隔声量数据',
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#60a5fa,#3b82f6)'
  },
  {
    name: 'vehicle-reverberation-query',
    title: '车辆混响时间查询',
    desc: '车型混响时间曲线与对比',
    icon: Monitor,
    bg: 'linear-gradient(135deg,#22d3ee,#06b6d4)'
  },
  {
    name: 'sound-absorption-query',
    title: '吸声系数查询',
    desc: '材料吸声性能快速检索',
    icon: MagicStick,
    bg: 'linear-gradient(135deg,#fb7185,#ec4899)'
  },
  {
    name: 'sound-insulation-coefficient-query',
    title: '隔声量查询',
    desc: '标准隔声量测试数据查询',
    icon: MagicStick,
    bg: 'linear-gradient(135deg,#f59e0b,#fbbf24)'
  },
  {
    name: 'material-porosity-flow-resistance-query',
    title: '材料孔隙率和流阻查询',
    desc: '多维度材料特性数据汇总',
    icon: MagicStick,
    bg: 'linear-gradient(135deg,#4ade80,#22c55e)'
  }
])

// 动刚度模块
const dynamicStiffnessModules = ref([
  {
    name: 'dynamic-stiffness-query',
    title: '动刚度查询',
    desc: '曲线/峰值/参数一体化呈现',
    icon: MagicStick,
    bg: 'linear-gradient(135deg,#fdba74,#fb923c)'
  },
  {
    name: 'vehicle-mount-isolation-query',
    title: '整车悬置隔振率查询',
    desc: '悬置隔振率频段对比',
    icon: Setting,
    bg: 'linear-gradient(135deg,#93c5fd,#60a5fa)'
  },
  {
    name: 'suspension-isolation-query',
    title: '整车悬架隔振率查询',
    desc: '悬架隔振特性趋势分析',
    icon: Setting,
    bg: 'linear-gradient(135deg,#86efac,#22c55e)'
  }
])

// 车轮性能模块
const wheelPerformanceModules = ref([
  {
    name: 'wheel-performance-query',
    title: '车轮性能查询',
    desc: '轮辋/传递函数等关键指标',
    icon: Odometer,
    bg: 'linear-gradient(135deg,#38bdf8,#0ea5e9)'
  },
  {
    name: 'ntf-query',
    title: 'NTF 查询',
    desc: 'NTF曲线/热力图一目了然',
    icon: TrendCharts,
    bg: 'linear-gradient(135deg,#c084fc,#a855f7)'
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

.business-groups {
  max-width: 1200px;
  margin: 0 auto;
}

.group-item {
  margin-bottom: 20px;
}

.group-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.group-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 16px 0 20px 0;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  max-width: 100%;
}

/* 响应式：最多6列 */
@media (min-width: 1080px) {
  .modules-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (min-width: 900px) and (max-width: 1079px) {
  .modules-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (min-width: 720px) and (max-width: 899px) {
  .modules-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 540px) and (max-width: 719px) {
  .modules-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 360px) and (max-width: 539px) {
  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 359px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }
}

.module-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: color .2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
}
.module-card:hover { /* 仅保留文字变蓝，不做阴影和位移 */ }
.module-card:focus-visible { outline: 3px solid rgba(59,130,246,0.25); outline-offset: 2px; }

/* 移除箭头提示 */
.module-card::after { content: none; }

.module-media {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f6ff;
  color: #3b82f6;
}

.module-content { overflow: hidden; }
.module-title { font-size: 14px; font-weight: 600; color: #1f2d3d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.module-card:hover .module-title, .module-card:focus-visible .module-title { color: #2563eb; }
/* 描述已移除，保留占位选择器以兼容但不使用 */
.module-desc { display: none; }

/* 深度选择器，覆盖 Element Plus 折叠面板样式 */
:deep(.el-collapse-item__header) {
  background-color: #fafafa;
  border: none;
  padding: 12px 16px;
  border-radius: 8px;
}

:deep(.el-collapse-item__content) {
  padding: 0 16px 16px 16px;
  border: none;
}

:deep(.el-collapse-item) {
  border: none;
}
</style>


