<template>
  <div class="task-main-list">
    <!-- 页面标题 -->
    <div class="header">
      <div class="title">试验任务管理</div>
      <div class="actions">
        <el-button v-if="store.isScheduler" type="primary" @click="handleCreate">
          新增主记录
        </el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-section">
      <div class="filter-row">
        <el-input v-model="store.filters.model" placeholder="车型" clearable style="width: 140px" />
        <el-input v-model="store.filters.vin_or_part_no" placeholder="VIN/零件编号" clearable style="width: 160px" />
        <el-input v-model="store.filters.test_name" placeholder="试验名称" clearable style="width: 160px" />
        <el-input v-model="store.filters.tester_name" placeholder="测试人员" clearable style="width: 120px" />
        <el-select v-model="store.filters.warning_system_status" placeholder="预警状态" clearable style="width: 120px">
          <el-option label="是" value="是" />
          <el-option label="无需" value="无需" />
          <el-option label="已申请" value="已申请" />
          <el-option label="未申请" value="未申请" />
          <el-option label="待申请" value="待申请" />
        </el-select>
        <el-select v-model="store.filters.is_closed" placeholder="闭环状态" clearable style="width: 120px">
          <el-option label="已闭环" value="true" />
          <el-option label="未闭环" value="false" />
        </el-select>
      </div>
      <div class="filter-row">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="排期开始"
          end-placeholder="排期结束"
          value-format="YYYY-MM-DD"
          style="width: 260px"
          @change="handleDateChange"
        />
        <el-input v-model="store.filters.requester_name" placeholder="任务提出人" clearable style="width: 120px" />
        <el-input v-model="store.filters.contract_no" placeholder="合同编号" clearable style="width: 140px" />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>

    <!-- 列表表格 -->
    <el-table
      v-loading="store.list.loading"
      :data="store.list.items"
      border
      stripe
      class="main-table"
      @row-dblclick="handleRowDblClick"
    >
      <el-table-column label="闭环" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_closed ? 'success' : 'warning'" size="small">
            {{ row.is_closed ? '已闭环' : '未闭环' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="warning_system_status" label="预警" width="80" />
      <el-table-column prop="model" label="车型" width="100" show-overflow-tooltip />
      <el-table-column prop="vin_or_part_no" label="VIN/零件编号" width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="copyable" @click="copyText(row.vin_or_part_no)">{{ row.vin_or_part_no }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="test_name" label="试验名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="tester_name" label="测试人员" width="100" />
      <el-table-column prop="requester_name" label="任务提出人" width="100" />
      <el-table-column label="排期" width="200">
        <template #default="{ row }">
          {{ formatDate(row.schedule_start) }} ~ {{ formatDate(row.schedule_end) }}
        </template>
      </el-table-column>
      <el-table-column prop="test_location" label="地点" width="100" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="openDrawer(row)">填写/查看表单</el-button>
          <el-button v-if="store.isScheduler" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, jumper, sizes, total"
        :page-size="store.list.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.list.total"
        :current-page="store.list.page"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 详情抽屉 -->
    <TaskDetailDrawer />

    <!-- 新增主记录对话框 -->
    <el-dialog v-model="createDialogVisible" title="新增主记录" width="600px">
      <el-form :model="createForm" label-width="120px">
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
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTaskStore } from '@/store/NVHtask'
import TaskDetailDrawer from './components/TaskDetailDrawer.vue'

const store = useTaskStore()

// 日期范围
const dateRange = ref([])

// 新增对话框
const createDialogVisible = ref(false)
const createForm = ref({
  model: '',
  vin_or_part_no: '',
  test_name: '',
  warning_system_status: '',
  requester_name: '',
  tester_name: '',
  schedule_start: null,
  schedule_end: null,
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
  createForm.value = {
    model: '',
    vin_or_part_no: '',
    test_name: '',
    warning_system_status: '',
    requester_name: '',
    tester_name: '',
    schedule_start: null,
    schedule_end: null,
    test_location: '',
    contract_no: '',
    remark: ''
  }
  createDialogVisible.value = true
}

const submitCreate = async () => {
  try {
    await store.createMainRecord(createForm.value)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
  } catch (e) {
    ElMessage.error('创建失败')
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
.task-main-list {
  padding: 16px;
  max-width: 1600px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.title {
  font-size: 18px;
  font-weight: 600;
}

.filter-section {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.main-table {
  width: 100%;
}

.copyable {
  cursor: pointer;
  color: #409eff;
}

.copyable:hover {
  text-decoration: underline;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
