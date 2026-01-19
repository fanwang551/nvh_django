<template>
  <div class="statistics-bar" v-loading="store.statistics.loading">
    <!-- 左侧：统计卡片 -->
    <div class="stat-cards">
      <!-- 卡片1：总任务 -->
      <div class="stat-card card-blue">
        <div class="card-content">
          <el-icon class="card-icon" :size="32"><Document /></el-icon>
          <div class="card-data">
            <div class="card-value">{{ store.statistics.total_tasks }}</div>
            <div class="card-label">总任务</div>
          </div>
        </div>
      </div>

      <!-- 卡片2：本月任务 -->
      <div class="stat-card card-green">
        <div class="card-content">
          <el-icon class="card-icon" :size="32"><Calendar /></el-icon>
          <div class="card-data">
            <div class="card-value">{{ store.statistics.month_tasks }}</div>
            <div class="card-label">本月任务</div>
          </div>
        </div>
      </div>

      <!-- 卡片3：本周任务 -->
      <div class="stat-card card-orange">
        <div class="card-content">
          <el-icon class="card-icon" :size="32"><Clock /></el-icon>
          <div class="card-data">
            <div class="card-value">{{ store.statistics.week_tasks }}</div>
            <div class="card-label">本周任务</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：功能按钮 -->
    <div class="filter-buttons">
      <el-button
        :type="weekClosureFilter === 'closed' ? 'success' : ''"
        :plain="weekClosureFilter !== 'closed'"
        class="filter-btn"
        @click="handleWeekClosureFilter('closed')"
      >
        本周已闭环 ({{ store.statistics.week_closed }})
      </el-button>
      <el-button
        :type="weekClosureFilter === 'unclosed' ? 'warning' : ''"
        :plain="weekClosureFilter !== 'unclosed'"
        class="filter-btn"
        @click="handleWeekClosureFilter('unclosed')"
      >
        本周未闭环 ({{ store.statistics.week_unclosed }})
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document, Calendar, Clock } from '@element-plus/icons-vue'
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

  // 如果点击的是当前已选中的按钮，则取消筛选
  if (store.filters.week_closure_filter === type) {
    // 取消筛选
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

  // 重置到第一页并加载列表
  store.setPage(1)
  store.loadList()
}

// 格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
.statistics-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 20px;
  min-height: 80px;
}

/* 左侧统计卡片容器 */
.stat-cards {
  display: flex;
  gap: 16px;
  flex: 1;
}

/* 统计卡片 */
.stat-card {
  width: 180px;
  height: 80px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: default;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 16px;
  height: 100%;
  gap: 12px;
}

.card-icon {
  flex-shrink: 0;
}

.card-data {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1;
}

.card-label {
  font-size: 12px;
  color: #909399;
  line-height: 1;
}

/* 卡片主题色 */
.card-blue {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}

.card-blue .card-icon {
  color: #409eff;
}

.card-blue .card-value {
  color: #409eff;
}

.card-green {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.card-green .card-icon {
  color: #67c23a;
}

.card-green .card-value {
  color: #67c23a;
}

.card-orange {
  background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%);
}

.card-orange .card-icon {
  color: #e6a23c;
}

.card-orange .card-value {
  color: #e6a23c;
}

/* 右侧功能按钮容器 */
.filter-buttons {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.filter-btn {
  width: 160px;
  height: 40px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

/* 按钮选中状态 */
.filter-btn.el-button--success:not(.is-plain) {
  background-color: #67c23a;
  border-color: #67c23a;
  color: #ffffff;
}

.filter-btn.el-button--warning:not(.is-plain) {
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: #ffffff;
}

/* 按钮未选中状态（plain） */
.filter-btn.el-button--success.is-plain {
  color: #67c23a;
  background: transparent;
  border-color: #67c23a;
}

.filter-btn.el-button--warning.is-plain {
  color: #e6a23c;
  background: transparent;
  border-color: #e6a23c;
}

/* 按钮悬停效果 */
.filter-btn.el-button--success.is-plain:hover {
  background-color: rgba(103, 194, 58, 0.1);
}

.filter-btn.el-button--warning.is-plain:hover {
  background-color: rgba(230, 162, 60, 0.1);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .stat-card {
    width: 160px;
  }

  .filter-btn {
    width: 140px;
    font-size: 13px;
  }
}

@media (max-width: 1200px) {
  .statistics-bar {
    flex-wrap: wrap;
  }

  .stat-cards {
    width: 100%;
  }

  .filter-buttons {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
