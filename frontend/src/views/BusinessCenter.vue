<template>
  <div class="business-center">
    <div class="cards-grid">
      <div
        v-for="module in modules"
        :key="module.name"
        class="module-card"
        role="button"
        tabindex="0"
        @click="openModule(module)"
        @keydown.enter.prevent="openModule(module)"
      >
        <span class="category-tag" :class="`tag-${module.category}`">{{ categoryLabel[module.category] }}</span>
        <div class="module-media" :class="`media-${module.category}`">
          <el-icon :size="28" class="media-icon">
            <component :is="module.icon" />
          </el-icon>
        </div>
        <div class="module-title" :title="module.title">{{ module.title }}</div>
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
  Picture,
  MagicStick,
  Setting,
  Odometer
} from '@element-plus/icons-vue'

const router = useRouter()

// 分类标签显示
const categoryLabel = {
  modal: '模态/气密',
  sound: '吸隔声',
  dynamic: '动刚度',
  other: '其他'
}

// 扁平化业务模块（取消折叠分组，统一卡片网格）
const modules = ref([
  // 模态与气密性（蓝色系）
  { name: 'modal-data-query', title: '模态查询', icon: DataAnalysis, category: 'modal' },
  { name: 'modal-data-compare', title: '模态对比', icon: TrendCharts, category: 'modal' },
  { name: 'airtight-leak-compare', title: '气密性泄漏量', icon: Connection, category: 'modal' },
  { name: 'airtightness-image-query', title: '气密性测试图', icon: Picture, category: 'modal' },

  // 吸隔声（绿色系）
  { name: 'vehicle-sound-insulation-query', title: '整车隔声量', icon: TrendCharts, category: 'sound' },
  { name: 'vehicle-reverberation-query', title: '整车混响时间', icon: Monitor, category: 'sound' },
  { name: 'sound-insulation-compare', title: '区域隔声量', icon: TrendCharts, category: 'sound' },
  { name: 'ntf-query', title: '传递函数', icon: TrendCharts, category: 'sound' },
  { name: 'sound-absorption-query', title: '材料吸声', icon: MagicStick, category: 'sound' },
  { name: 'sound-insulation-coefficient-query', title: '材料隔声量', icon: MagicStick, category: 'sound' },
  { name: 'material-porosity-flow-resistance-query', title: '孔隙率流阻', icon: MagicStick, category: 'sound' },

  // 动刚度（橙色系）
  { name: 'dynamic-stiffness-query', title: '动刚度', icon: MagicStick, category: 'dynamic' },
  { name: 'vehicle-mount-isolation-query', title: '悬置隔振率', icon: Setting, category: 'dynamic' },
  { name: 'suspension-isolation-query', title: '悬架隔振率', icon: Setting, category: 'dynamic' },

  // 其他功能（紫色系）
  { name: 'acoustic-analysis', title: '原始数据分析', icon: TrendCharts, category: 'other' },
  { name: 'wheel-performance-query', title: '车轮性能', icon: Odometer, category: 'other' },
  { name: 'experience-query', title: '经验库', icon: DataAnalysis, category: 'other' }
])

const openModule = (module) => {
  router.push(`/business/${module.name}`)
}
</script>

<style scoped>
.business-center {
  padding: 0 8px;
}

.cards-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .cards-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .cards-grid { grid-template-columns: 1fr; }
}

.module-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 12px 18px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  transition: box-shadow .2s ease, transform .08s ease;
}
.module-card:hover { box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
.module-card:active { transform: scale(0.98); }
.module-card:focus-visible { outline: 3px solid rgba(59,130,246,0.25); outline-offset: 2px; }

.category-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  line-height: 18px;
  color: #1f2937;
  background: #f3f4f6;
}
.tag-modal { color: #1d4ed8; background: #e0e7ff; }
.tag-sound { color: #065f46; background: #d1fae5; }
.tag-dynamic { color: #9a3412; background: #ffedd5; }
.tag-other { color: #5b21b6; background: #ede9fe; }

.module-media {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}
.media-modal { background: #eef2ff; color: #3b82f6; }
.media-sound { background: #ecfdf5; color: #10b981; }
.media-dynamic { background: #fff7ed; color: #f59e0b; }
.media-other { background: #f5f3ff; color: #8b5cf6; }

.module-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f2d3d;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}
</style>

