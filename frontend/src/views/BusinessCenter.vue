<template>
  <div class="business-center">
    <div class="page-header">
      <h2>业务中心</h2>
      <p class="page-description">选择业务功能模块</p>
    </div>

    <el-collapse v-model="activeGroups" class="business-groups">
      <!-- 模态和气密性模块 -->
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
            @click="openModule(module)"
          >
            <div class="module-icon">
              <el-icon :size="20">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 吸隔声模块 -->
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
            @click="openModule(module)"
          >
            <div class="module-icon">
              <el-icon :size="20">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title">{{ module.title }}</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 动刚度模块 -->
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
            @click="openModule(module)"
          >
            <div class="module-icon">
              <el-icon :size="20">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title">{{ module.title }}</div>
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
            @click="openModule(module)"
          >
            <div class="module-icon">
              <el-icon :size="20">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <div class="module-title">{{ module.title }}</div>
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
    icon: DataAnalysis
  },
  {
    name: 'modal-data-compare',
    title: '模态数据对比',
    icon: TrendCharts
  },
  {
    name: 'airtight-leak-compare',
    title: '气密性泄漏量对比',
    icon: Connection
  },
  {
    name: 'airtightness-image-query',
    title: '气密性测试图片查询',
    icon: Picture
  }
])

// 吸隔声模块
const soundModules = ref([
  {
    name: 'sound-insulation-compare',
    title: '区域隔声量（ATF）对比',
    icon: TrendCharts
  },
  {
    name: 'vehicle-sound-insulation-query',
    title: '车型隔声量查询',
    icon: TrendCharts
  },
  {
    name: 'vehicle-reverberation-query',
    title: '车辆混响时间查询',
    icon: Monitor
  },
  {
    name: 'sound-absorption-query',
    title: '吸声系数查询',
    icon: MagicStick
  },
  {
    name: 'sound-insulation-coefficient-query',
    title: '隔声量查询',
    icon: MagicStick
  },
  {
    name: 'material-porosity-flow-resistance-query',
    title: '材料孔隙率和流阻查询',
    icon: MagicStick
  }
])

// 动刚度模块
const dynamicStiffnessModules = ref([
  {
    name: 'dynamic-stiffness-query',
    title: '动刚度查询',
    icon: MagicStick
  },
  {
    name: 'vehicle-mount-isolation-query',
    title: '整车悬置隔振率查询',
    icon: Setting
  },
  {
    name: 'suspension-isolation-query',
    title: '整车悬架隔振率查询',
    icon: Setting
  }
])

// 车轮性能模块
const wheelPerformanceModules = ref([
  {
    name: 'wheel-performance-query',
    title: '车轮性能查询',
    icon: Odometer
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
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
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
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.module-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.module-icon {
  color: #409eff;
  margin-bottom: 8px;
}

.module-title {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
  line-height: 1.3;
  word-break: break-all;
}

/* 深度选择器，覆盖 Element Plus 折叠面板样式 */
:deep(.el-collapse-item__header) {
  background-color: #f8f9fa;
  border: none;
  padding: 16px 20px;
  border-radius: 6px;
}

:deep(.el-collapse-item__content) {
  padding: 0 20px 20px 20px;
  border: none;
}

:deep(.el-collapse-item) {
  border: none;
}
</style>
