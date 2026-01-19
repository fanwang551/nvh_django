<template>
  <!-- 使用 Grid 布局容器，统一 loading 状态 -->
  <div class="statistics-grid" v-loading="store.statistics.loading">

    <!-- 卡片1：总任务 (静态) -->
    <div class="stat-card card-blue">
      <div class="card-content">
        <el-icon class="card-icon" :size="32"><Document /></el-icon>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.total_tasks }}</div>
          <div class="card-label">总任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片2：本月任务 (静态) -->
    <div class="stat-card card-purple">
      <div class="card-content">
        <el-icon class="card-icon" :size="32"><Calendar /></el-icon>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.month_tasks }}</div>
          <div class="card-label">本月任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片3：本周任务 (静态) -->
    <div class="stat-card card-cyan">
      <div class="card-content">
        <el-icon class="card-icon" :size="32"><pDataAnalysis /></el-icon>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.week_tasks }}</div>
          <div class="card-label">本周任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片4：本周已闭环 (可点击筛选) -->
    <div
      class="stat-card card-green is-clickable"
      :class="{ 'is-active': weekClosureFilter === 'closed' }"
      @click="handleWeekClosureFilter('closed')"
    >
      <div class="card-content">
        <!-- 选中时显示选中标记，未选中显示普通图标 -->
        <el-icon class="card-icon" :size="32"><CircleCheckFilled /></el-icon>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.week_closed }}</div>
          <div class="card-label">本周已闭环 <span class="action-hint">(点击筛选)</span></div>
        </div>
        <!-- 选中状态指示器 -->
        <div class="active-indicator" v-if="weekClosureFilter === 'closed'">
          <el-icon><Select /></el-icon>
        </div>
      </div>
    </div>

    <!-- 卡片5：本周未闭环 (可点击筛选) -->
    <div
      class="stat-card card-orange is-clickable"
      :class="{ 'is-active': weekClosureFilter === 'unclosed' }"
      @click="handleWeekClosureFilter('unclosed')"
    >
      <div class="card-content">
        <el-icon class="card-icon" :size="32"><WarningFilled /></el-icon>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.week_unclosed }}</div>
          <div class="card-label">本周未闭环 <span class="action-hint">(点击筛选)</span></div>
        </div>
        <!-- 选中状态指示器 -->
        <div class="active-indicator" v-if="weekClosureFilter === 'unclosed'">
          <el-icon><Select /></el-icon>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
// 引入更多图标以丰富视觉
import {
  Document, Calendar, DataAnalysis as pDataAnalysis,
  CircleCheckFilled, WarningFilled, Select
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/store/NVHtask'

const store = useTaskStore()

// 当前本周闭环筛选状态
const weekClosureFilter = computed(() => store.filters.week_closure_filter)

// 处理本周闭环筛选按钮点击
const handleWeekClosureFilter = (type) => {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1)) // 本周一
  weekStart.setHours(0, 0, 0, 0)

  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6) // 本周日
  weekEnd.setHours(23, 59, 59, 999)

  // 如果点击的是当前已选中的卡片，则取消筛选
  if (store.filters.week_closure_filter === type) {
    store.setFilter('week_closure_filter', '')
    store.setFilter('schedule_start_from', '')
    store.setFilter('schedule_start_to', '')
    store.setFilter('is_closed', '')
  } else {
    // 应用筛选
    store.setFilter('week_closure_filter', type)
    store.setFilter('schedule_start_from', formatDate(weekStart))
    store.setFilter('schedule_start_to', formatDate(weekEnd))
    store.setFilter('is_closed', type === 'closed' ? 'true' : 'false')
  }

  store.setPage(1)
  store.loadList()
}

const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
/* Grid 布局：5列等宽，占满整行 */
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  width: 100%;
}

/* 基础卡片样式 */
.stat-card {
  height: 90px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  border: 1px solid transparent; /* 预留边框位置避免抖动 */
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 100%;
  gap: 16px;
}

/* 图标基础样式 */
.card-icon {
  padding: 10px;
  border-radius: 12px;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.stat-card:hover .card-icon {
  transform: scale(1.1);
}

.card-data {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  min-width: 0; /* 防止文本溢出 */
}

.card-value {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.card-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 可点击卡片的额外样式 */
.stat-card.is-clickable {
  cursor: pointer;
  user-select: none;
}

.action-hint {
  font-size: 11px;
  opacity: 0.6;
  font-weight: normal;
}

/* ---------------- 配色方案 ---------------- */

/* 1. 总任务: 蓝色 (原有) */
.card-blue {
  background: linear-gradient(135deg, #f0f7ff 0%, #e1effe 100%);
}
.card-blue .card-icon {
  background: #dbebff;
  color: #409eff;
}
.card-blue .card-value { color: #2c3e50; }

/* 2. 本月: 紫色 (区分颜色) */
.card-purple {
  background: linear-gradient(135deg, #f9f5ff 0%, #f0e6ff 100%);
}
.card-purple .card-icon {
  background: #ede4ff;
  color: #722ed1;
}
.card-purple .card-value { color: #2c3e50; }

/* 3. 本周: 青色 (区分颜色) */
.card-cyan {
  background: linear-gradient(135deg, #f0fcff 0%, #e1fafd 100%);
}
.card-cyan .card-icon {
  background: #cef6ff;
  color: #13c2c2;
}
.card-cyan .card-value { color: #2c3e50; }

/* 4. 已闭环: 绿色 (强调) */
.card-green {
  background: linear-gradient(135deg, #f6ffed 0%, #eaffd6 100%);
}
.card-green .card-icon {
  background: #d9f7be;
  color: #52c41a;
}
.card-green .card-value { color: #52c41a; } /* 数字跟随主题色 */

/* 5. 未闭环: 橙色 (警告) */
.card-orange {
  background: linear-gradient(135deg, #fff7e6 0%, #ffeed0 100%);
}
.card-orange .card-icon {
  background: #ffe7ba;
  color: #fa8c16;
}
.card-orange .card-value { color: #fa8c16; } /* 数字跟随主题色 */


/* ---------------- 选中(Active)状态样式 ---------------- */

.stat-card.is-active {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 绿色卡片选中态 */
.card-green.is-active {
  border: 1.5px solid #52c41a;
  background: #f6ffed;
}

/* 橙色卡片选中态 */
.card-orange.is-active {
  border: 1.5px solid #fa8c16;
  background: #fff7e6;
}

/* 右上角选中勾选标记 */
.active-indicator {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 32px 32px 0;
  z-index: 1;
}

.active-indicator .el-icon {
  position: absolute;
  top: 4px; /* 调整图标位置 */
  right: -30px;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}

/* 绿色卡片角标颜色 */
.card-green .active-indicator {
  border-color: transparent #52c41a transparent transparent;
}

/* 橙色卡片角标颜色 */
.card-orange .active-indicator {
  border-color: transparent #fa8c16 transparent transparent;
}


/* ---------------- 响应式调整 ---------------- */
@media (max-width: 1400px) {
  .statistics-grid {
    grid-template-columns: repeat(3, 1fr); /* 中屏变3列 */
  }
}

@media (max-width: 768px) {
  .statistics-grid {
    grid-template-columns: 1fr; /* 手机屏变单列或双列 */
  }
}
</style>
