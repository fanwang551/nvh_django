<template>
  <div class="closure-bar" :class="{ 'is-closed': store.isClosed }">
    <div class="closure-header">
      <el-icon v-if="store.isClosed" color="#67c23a"><CircleCheckFilled /></el-icon>
      <el-icon v-else color="#e6a23c"><WarningFilled /></el-icon>
      <span class="closure-title">{{ store.isClosed ? '已完成闭环' : '闭环状态' }}</span>
    </div>

    <!-- 三模块状态 -->
    <div class="status-cards">
      <div class="status-card" :class="{ ok: closureStatus.entryExit.submitted }">
        <div class="card-label">进出登记</div>
        <div class="card-status">
          {{ closureStatus.entryExit.exists ? (closureStatus.entryExit.submitted ? '已提交' : '未提交') : '未绑定' }}
        </div>
      </div>
      <div class="status-card" :class="{ ok: closureStatus.testInfo.submitted }">
        <div class="card-label">试验信息</div>
        <div class="card-status">
          {{ closureStatus.testInfo.exists ? (closureStatus.testInfo.submitted ? '已提交' : '未提交') : '未填写' }}
        </div>
        <div v-if="closureStatus.testInfo.exists && !closureStatus.testInfo.teardownOk" class="card-warn">拆装记录缺失</div>
        <div v-if="closureStatus.testInfo.exists && !closureStatus.testInfo.processOk" class="card-warn">过程记录缺失</div>
      </div>
      <div class="status-card" :class="{ ok: closureStatus.docApproval.submitted }">
        <div class="card-label">技术资料</div>
        <div class="card-status">
          {{ closureStatus.docApproval.exists ? (closureStatus.docApproval.submitted ? '已提交' : '未提交') : '未填写' }}
        </div>
        <div v-if="closureStatus.docApproval.exists && !closureStatus.docApproval.fileOk" class="card-warn">文件缺失</div>
      </div>
    </div>

    <!-- 缺项列表 -->
    <div v-if="closureStatus.missingItems.length > 0" class="missing-list">
      <div class="missing-title">待完成项：</div>
      <div
        v-for="(item, index) in closureStatus.missingItems"
        :key="index"
        class="missing-item"
        @click="handleLocate(item)"
      >
        <el-icon><Right /></el-icon>
        <span>{{ item.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheckFilled, WarningFilled, Right } from '@element-plus/icons-vue'
import { useTaskStore } from '@/store/NVHtask'

const store = useTaskStore()
const closureStatus = computed(() => store.closureStatus)

const handleLocate = (item) => {
  store.locateMissingItem(item)
}
</script>

<style scoped>
.closure-bar {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.closure-bar.is-closed {
  background: #f0f9eb;
  border-color: #e1f3d8;
}

.closure-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.closure-title {
  font-weight: 600;
  font-size: 14px;
}

.status-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.status-card {
  flex: 1;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 12px;
  text-align: center;
}

.status-card.ok {
  border-color: #67c23a;
  background: #f0f9eb;
}

.card-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.card-status {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.status-card.ok .card-status {
  color: #67c23a;
}

.card-warn {
  font-size: 11px;
  color: #e6a23c;
  margin-top: 4px;
}

.missing-list {
  border-top: 1px dashed #dcdfe6;
  padding-top: 10px;
}

.missing-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.missing-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
  padding: 4px 0;
}

.missing-item:hover {
  text-decoration: underline;
}
</style>
