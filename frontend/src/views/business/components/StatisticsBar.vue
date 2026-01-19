<template>
  <!-- 使用 Grid 布局容器，统一 loading 状态 -->
  <div class="statistics-grid" v-loading="store.statistics.loading">

    <!-- 卡片1：总任务 (静态 - 统一使用 info 样式) -->
    <div class="stat-card is-static">
      <div class="card-content">
        <div class="icon-wrapper color-primary">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.total_tasks }}</div>
          <div class="card-label">总任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片2：本月任务 (静态 - 统一使用 info 样式) -->
    <div class="stat-card is-static">
      <div class="card-content">
        <div class="icon-wrapper color-primary">
          <el-icon :size="24"><Calendar /></el-icon>
        </div>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.month_tasks }}</div>
          <div class="card-label">本月任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片3：本周任务 (静态 - 统一使用 info 样式) -->
    <div class="stat-card is-static">
      <div class="card-content">
        <div class="icon-wrapper color-primary">
          <el-icon :size="24"><pDataAnalysis /></el-icon>
        </div>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.week_tasks }}</div>
          <div class="card-label">本周任务</div>
        </div>
      </div>
    </div>

    <!-- 卡片4：本周已闭环 (筛选 - 绿色文字) -->
    <div
      class="stat-card is-clickable color-success"
      :class="{ 'is-active': weekClosureFilter === 'closed' }"
      @click="handleWeekClosureFilter('closed')"
    >
      <div class="card-content">
        <div class="icon-wrapper">
          <el-icon :size="24"><CircleCheckFilled /></el-icon>
        </div>
        <div class="card-data">
          <!-- 文字颜色由 CSS 控制 -->
          <div class="card-value">{{ store.statistics.week_closed }}</div>
          <div class="card-label">本周已闭环 <span class="action-hint" v-if="weekClosureFilter !== 'closed'">/ 筛选</span></div>
        </div>
        <!-- 选中角标 -->
        <div class="active-indicator" v-if="weekClosureFilter === 'closed'">
          <el-icon><Select /></el-icon>
        </div>
      </div>
    </div>

    <!-- 卡片5：本周未闭环 (筛选 - 橙色文字) -->
    <div
      class="stat-card is-clickable color-warning"
      :class="{ 'is-active': weekClosureFilter === 'unclosed' }"
      @click="handleWeekClosureFilter('unclosed')"
    >
      <div class="card-content">
        <div class="icon-wrapper">
          <el-icon :size="24"><WarningFilled /></el-icon>
        </div>
        <div class="card-data">
          <div class="card-value">{{ store.statistics.week_unclosed }}</div>
          <div class="card-label">本周未闭环 <span class="action-hint" v-if="weekClosureFilter !== 'unclosed'">/ 筛选</span></div>
        </div>
        <!-- 选中角标 -->
        <div class="active-indicator" v-if="weekClosureFilter === 'unclosed'">
          <el-icon><Select /></el-icon>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Document, Calendar, DataAnalysis as pDataAnalysis,
  CircleCheckFilled, WarningFilled, Select
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/store/NVHtask'

const store = useTaskStore()

const weekClosureFilter = computed(() => store.filters.week_closure_filter)

const handleWeekClosureFilter = (type) => {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1))
  weekStart.setHours(0, 0, 0, 0)

  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)
  weekEnd.setHours(23, 59, 59, 999)

  if (store.filters.week_closure_filter === type) {
    store.setFilter('week_closure_filter', '')
    store.setFilter('schedule_start_from', '')
    store.setFilter('schedule_start_to', '')
    store.setFilter('is_closed', '')
  } else {
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
/* --------------------------------------
   布局结构
-------------------------------------- */
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  width: 100%;
}

/* --------------------------------------
   卡片统一基础样式 ( 白色)
-------------------------------------- */
.stat-card {
  height: 90px;
  background-color: #fff; /* 所有卡片默认为白色 */
  border: 1px solid #e4e7ed; /* 浅灰边框 */
  border-radius: 6px;
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

/* 悬停效果：轻微上浮，边框加深 */
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #c0c4cc;
}

.card-content {
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 100%;
  gap: 16px;
}

/* --------------------------------------
   内容元素样式
-------------------------------------- */
.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 8px; /* 方形圆角 */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa; /* 统一的淡灰背景 */
  color: #606266; /* 默认图标色 */
  transition: all 0.3s;
}

.card-data {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.card-value {
  font-size: 28px;
  font-weight: 600; /* 去掉过粗的字体 */
  line-height: 1.2;
  margin-bottom: 4px;
  color: #303133; /* 默认深黑字 */
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif;
}

.card-label {
  font-size: 13px;
  color: #909399;
}

/* --------------------------------------
   色彩主题 (仅改变图标色和文字色)
-------------------------------------- */

/* 1. 主题蓝 (用于前三个静态卡片) */
.color-primary {
  color: #409eff; /* Element 蓝 */
  background-color: #ecf5ff; /* 极淡蓝背景 */
}
/* 静态卡片不需要文字变色 */


/* 2. 成功绿 (用于已闭环) */
.stat-card.color-success .icon-wrapper {
  color: #67c23a;
  background-color: #f0f9eb;
}
.stat-card.color-success .card-value {
  color: #67c23a; /* 数字变绿 */
}

/* 3. 警告橙 (用于未闭环) */
.stat-card.color-warning .icon-wrapper {
  color: #e6a23c;
  background-color: #fdf6ec;
}
.stat-card.color-warning .card-value {
  color: #e6a23c; /* 数字变橙 */
}

/* --------------------------------------
   交互样式
-------------------------------------- */
.stat-card.is-clickable {
  cursor: pointer;
}

.action-hint {
  font-size: 12px;
  opacity: 0.5;
  transform: scale(0.9);
  display: inline-block;
}

/* --------------------------------------
   选中状态 (背景色 2: 淡蓝色)
-------------------------------------- */
.stat-card.is-active {
  background-color: #ecf5ff; /* 这是允许的第二种背景色 */
  border-color: currentColor; /* 边框跟随文字颜色 */
  box-shadow: none; /* 选中时扁平化 */
}

/* 选中时的特殊处理 */
.stat-card.color-success.is-active {
  border: 1px solid #67c23a;
}
.stat-card.color-warning.is-active {
  border: 1px solid #e6a23c;
}

/* 角标样式 */
.active-indicator {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  z-index: 1;
}

.active-indicator .el-icon {
  position: absolute;
  top: 6px;
  right: -36px;
  color: #fff;
  font-size: 14px;
}

/* 角标颜色适配 */
.stat-card.color-success .active-indicator {
  border-color: transparent #67c23a transparent transparent;
}
.stat-card.color-warning .active-indicator {
  border-color: transparent #e6a23c transparent transparent;
}

/* --------------------------------------
   响应式
-------------------------------------- */
@media (max-width: 1400px) {
  .statistics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
