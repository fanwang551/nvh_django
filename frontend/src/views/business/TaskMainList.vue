<template>
  <div class="task-main-list page-container">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-left">
        <div class="title">试验任务管理</div>
        <div class="subtitle">共 {{ store.list.total }} 条记录</div>
      </div>
      <div class="header-actions">
        <el-button v-if="store.isScheduler" type="primary" icon="Plus" class="add-btn" @click="handleCreate">
          新增主记录
        </el-button>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <div class="filter-card">
      <div class="filter-grid">
        <el-input v-model="store.filters.model" placeholder="车型" clearable class="filter-item" />
        <el-input v-model="store.filters.vin_or_part_no" placeholder="VIN/零件编号" clearable class="filter-item" />
        <el-input v-model="store.filters.test_name" placeholder="试验名称" clearable class="filter-item" />
        <el-input v-model="store.filters.tester_name" placeholder="测试人员" clearable class="filter-item" />

        <el-select v-model="store.filters.warning_system_status" placeholder="预警状态" clearable class="filter-item">
          <el-option label="是" value="是" />
          <el-option label="无需" value="无需" />
          <el-option label="已申请" value="已申请" />
          <el-option label="未申请" value="未申请" />
          <el-option label="待申请" value="待申请" />
        </el-select>

        <el-select v-model="store.filters.is_closed" placeholder="闭环状态" clearable class="filter-item">
          <el-option label="已闭环" value="true" />
          <el-option label="未闭环" value="false" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="排期开始"
          end-placeholder="排期结束"
          value-format="YYYY-MM-DD"
          class="filter-item date-item"
          @change="handleDateChange"
        />

        <el-input v-model="store.filters.requester_name" placeholder="任务提出人" clearable class="filter-item" />
        <el-input v-model="store.filters.contract_no" placeholder="合同编号" clearable class="filter-item" />

        <div class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <el-table
        v-loading="store.list.loading"
        :data="store.list.items"
        stripe
        class="modern-table"
        header-row-class-name="table-header-row"
        row-class-name="table-body-row"
        @row-dblclick="handleRowDblClick"
      >
        <el-table-column label="闭环" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.is_closed ? 'success' : 'warning'"
              effect="plain"
              round
              size="small"
              class="status-tag"
            >
              {{ row.is_closed ? '已闭环' : '未闭环' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="样品状态" width="110" align="center">
          <template #default="{ row }">
            {{ row.entry_exit_dispose_type || row.entry_exit?.dispose_type || '--' }}
          </template>
        </el-table-column>

        <el-table-column prop="warning_system_status" label="预警" width="90" align="center" />
        <el-table-column prop="model" label="车型" width="110" show-overflow-tooltip align="center" />

        <el-table-column prop="vin_or_part_no" label="VIN/零件编号" width="180" show-overflow-tooltip align="center">
          <template #default="{ row }">
            <div class="copy-wrapper" @click="copyText(row.vin_or_part_no)">
              <span class="copy-text">{{ row.vin_or_part_no }}</span>
              <el-icon class="copy-icon"><DocumentCopy /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="test_name" label="试验名称" min-width="200" show-overflow-tooltip align="center" />
        <el-table-column prop="tester_name" label="测试人员" width="110" align="center" />
        <el-table-column prop="requester_name" label="提出人" width="110" align="center" />

        <el-table-column label="排期时间" width="220" align="center">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.schedule_start) }}</span>
            <span class="date-separator">~</span>
            <span class="date-text">{{ formatDate(row.schedule_end) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="排期备注" width="200" align="center">
          <template #default="{ row }">
            <div class="schedule-remark-cell">{{ row.schedule_remark || '--' }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="test_location" label="地点" width="120" show-overflow-tooltip align="center" />

        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-group">
              <el-button type="primary" link class="action-btn" @click="openDrawer(row)">查看</el-button>
              <template v-if="store.isScheduler">
                <el-divider direction="vertical" />
                <el-button type="primary" link class="action-btn" @click="handleEdit(row)">修改</el-button>
                <el-divider direction="vertical" />
                <el-button type="danger" link class="action-btn" @click="handleDelete(row)">删除</el-button>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区 -->
      <div class="pager-section">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :page-size="store.list.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="store.list.total"
          :current-page="store.list.page"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 详情抽屉 -->
    <TaskDetailDrawer />

    <!-- 新增主记录对话框 -->
    <el-dialog v-model="createDialogVisible" :title="isEdit ? '修改主记录' : '新增主记录'" width="600px" class="custom-dialog">
      <el-form :model="createForm" label-width="120px" class="custom-form">
        <el-form-item label="车型" required>
          <el-input v-model="createForm.model" />
        </el-form-item>
        <el-form-item label="VIN/零件编号" required>
          <el-input v-model="createForm.vin_or_part_no" />
        </el-form-item>
        <el-form-item label="试验名称" required>
          <el-input v-model="createForm.test_name" />
        </el-form-item>
        <el-form-item label="预警系统状态" required>
          <el-select v-model="createForm.warning_system_status" style="width: 100%">
            <el-option label="是" value="是" />
            <el-option label="无需" value="无需" />
            <el-option label="已申请" value="已申请" />
            <el-option label="未申请" value="未申请" />
            <el-option label="待申请" value="待申请" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务提出人" required>
          <el-input v-model="createForm.requester_name" />
        </el-form-item>
        <el-form-item label="测试人员" required>
          <el-input v-model="createForm.tester_name" />
        </el-form-item>
        <el-form-item label="排期开始" required>
          <el-date-picker v-model="createForm.schedule_start" type="datetime" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排期结束">
          <el-date-picker v-model="createForm.schedule_end" type="datetime" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排期备注">
          <el-input v-model="createForm.schedule_remark" />
        </el-form-item>
        <el-form-item label="试验地点">
          <el-input v-model="createForm.test_location" />
        </el-form-item>
        <el-form-item label="合同编号">
          <el-input v-model="createForm.contract_no" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMainRecord">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, Plus } from '@element-plus/icons-vue' // 引入图标
import { useTaskStore } from '@/store/NVHtask'
import TaskDetailDrawer from './components/TaskDetailDrawer.vue'

const store = useTaskStore()

// 日期范围
const dateRange = ref([])

// 新增对话框
const createDialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const createForm = ref({
  model: '',
  vin_or_part_no: '',
  test_name: '',
  warning_system_status: '',
  requester_name: '',
  tester_name: '',
  schedule_start: null,
  schedule_end: null,
  schedule_remark: '',
  test_location: '',
  contract_no: '',
  remark: ''
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    return dateStr.split('T')[0]
  } catch {
    return dateStr
  }
}

// 复制文本
const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 日期范围变化
const handleDateChange = (val) => {
  if (val && val.length === 2) {
    store.setFilter('schedule_start_from', val[0])
    store.setFilter('schedule_start_to', val[1])
  } else {
    store.setFilter('schedule_start_from', '')
    store.setFilter('schedule_start_to', '')
  }
}

// 搜索
const handleSearch = () => {
  store.setPage(1)
  store.loadList()
}

// 重置
const handleReset = () => {
  dateRange.value = []
  store.resetFilters()
  store.loadList()
}

// 分页
const handlePageChange = (page) => {
  store.setPage(page)
  store.loadList()
}

const handleSizeChange = (size) => {
  store.setPageSize(size)
  store.loadList()
}

// 打开抽屉
const openDrawer = (row) => {
  store.openDrawer(row.id)
}

// 双击行打开抽屉
const handleRowDblClick = (row) => {
  store.openDrawer(row.id)
}

// 新增
const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  createForm.value = {
    model: '',
    vin_or_part_no: '',
    test_name: '',
    warning_system_status: '',
    requester_name: '',
    tester_name: '',
    schedule_start: null,
    schedule_end: null,
    schedule_remark: '',
    test_location: '',
    contract_no: '',
    remark: ''
  }
  createDialogVisible.value = true
}

// 修改
const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  createForm.value = {
    model: row.model || '',
    vin_or_part_no: row.vin_or_part_no || '',
    test_name: row.test_name || '',
    warning_system_status: row.warning_system_status || '',
    requester_name: row.requester_name || '',
    tester_name: row.tester_name || '',
    schedule_start: row.schedule_start ? new Date(row.schedule_start) : null,
    schedule_end: row.schedule_end ? new Date(row.schedule_end) : null,
    schedule_remark: row.schedule_remark || '',
    test_location: row.test_location || '',
    contract_no: row.contract_no || '',
    remark: row.remark || ''
  }
  createDialogVisible.value = true
}

const submitMainRecord = async () => {
  try {
    if (isEdit.value) {
      await store.updateMainRecord(editingId.value, createForm.value)
      ElMessage.success('更新成功')
    } else {
      await store.createMainRecord(createForm.value)
      ElMessage.success('创建成功')
    }
    createDialogVisible.value = false
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该任务吗？', '提示', { type: 'warning' })
    await store.deleteMainRecord(row.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  store.initUserInfo()
  store.loadList()
})
</script>

<style scoped>
/* 变量定义 */
.page-container {
  --primary-color: #409eff;
  --header-bg: #409eff; /* 企业蓝 */
  --header-text: #ffffff;
  --row-hover-bg: #f0f7ff; /* 极浅的蓝色 */
  --stripe-bg: #fafafa; /* 干净的浅灰 */
  --border-color: #ebeef5;
  --text-main: #303133;
  --text-secondary: #606266;

  padding: 20px;
  max-width: 100%;
  min-height: 100vh;
  background-color: #f5f7fa; /* 页面整体底色 */
  box-sizing: border-box;
}

/* 1. 头部区域 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-left .title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.2;
}

.header-left .subtitle {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.add-btn {
  padding: 8px 20px;
  font-weight: 500;
}

/* 2. 筛选卡片 */
.filter-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.04);
  border: 1px solid var(--border-color);
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-item {
  width: 140px; /* 默认宽度 */
}

.date-item {
  width: 240px !important;
}

.filter-actions {
  margin-left: auto; /* 按钮靠右或紧随其后 */
  display: flex;
  gap: 12px;
}

/* 3. 表格卡片 */
.table-card {
  background: #fff;
  border-radius: 12px;
  padding: 0; /* 表格贴边，分页有padding */
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.04);
  border: 1px solid var(--border-color);
  overflow: hidden; /* 保证圆角 */
  display: flex;
  flex-direction: column;
}

/* 表格样式深度定制 */
.modern-table {
  width: 100%;
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: var(--header-bg);
  --el-table-header-text-color: var(--header-text);
}

/* 表头样式 */
:deep(.el-table__header-wrapper th) {
  background-color: var(--header-bg) !important;
  color: var(--header-text) !important;
  font-weight: 600;
  height: 48px;
  font-size: 14px;
  border-bottom: none; /* 去除表头下边框，用颜色区分 */
  border-right: 1px solid rgba(255, 255, 255, 0.2) !important; /* 表头间轻微分割 */
}

:deep(.el-table__header-wrapper th:last-child) {
  border-right: none !important;
}

/* 去除单元格竖线，保留横线 */
:deep(.el-table td.el-table__cell) {
  border-right: none !important;
  border-bottom: 1px solid var(--border-color);
  padding: 12px 0;
  color: var(--text-main);
}

/* 斑马纹背景 */
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: var(--stripe-bg);
}

/* Hover 效果 */
:deep(.el-table__body tr:hover > td) {
  background-color: var(--row-hover-bg) !important;
}

/* 修复固定列背景色问题 (确保斑马纹和hover在固定列也生效) */
:deep(.el-table__fixed-right) {
  height: 100% !important;
}

/* 4. 单元格内部细节 */
.status-tag {
  border: none;
  font-weight: 500;
}

.copy-wrapper {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-main);
  transition: color 0.2s;
  max-width: 100%;
}

.copy-text {
  font-family: 'Roboto Mono', monospace; /* 等宽字体适合编号 */
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-icon {
  margin-left: 4px;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
  color: var(--primary-color);
}

.copy-wrapper:hover {
  color: var(--primary-color);
}

.copy-wrapper:hover .copy-icon {
  opacity: 1;
}

.date-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.date-separator {
  margin: 0 4px;
  color: #c0c4cc;
}

.schedule-remark-cell {
  white-space: normal;
  word-break: break-all;
  line-height: 1.4;
  padding: 0 8px;
}

.action-group {
  display: flex;
  justify-content: center;
  align-items: center;
}

.action-btn {
  font-size: 13px;
  padding: 4px 8px;
}

/* 5. 分页区 */
.pager-section {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end; /* 靠右或居中 */
  background: #fff;
}

/* 响应式调整 */
@media (max-width: 1400px) {
  .filter-item {
    width: 120px;
  }
  .date-item {
    width: 220px !important;
  }
}
</style>
