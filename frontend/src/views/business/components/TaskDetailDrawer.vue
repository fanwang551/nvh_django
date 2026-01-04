<template>
  <el-drawer
    v-model="store.drawer.visible"
    :title="drawerTitle"
    size="65%"
    direction="rtl"
    :before-close="handleClose"
  >
    <template #header>
      <div class="drawer-header">
        <div class="drawer-title">
          <span>{{ drawerTitle }}</span>
          <el-tag :type="store.isClosed ? 'success' : 'warning'" size="small" style="margin-left: 12px">
            {{ store.isClosed ? '已闭环' : '未闭环' }}
          </el-tag>
        </div>
        <div class="drawer-subtitle" v-if="currentMain">
          排期：{{ formatDate(currentMain.schedule_start) }} ~ {{ formatDate(currentMain.schedule_end) }}
          | 测试人员：{{ currentMain.tester_name }}
        </div>
      </div>
    </template>

    <div v-loading="store.drawer.loading" class="drawer-content">
      <!-- 闭环提示条 -->
      <ClosureBar />

      <!-- Tabs -->
      <el-tabs v-model="store.drawer.activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="进出登记" name="entryExit">
          <template #label>
            <span>进出登记</span>
            <el-tag v-if="closureStatus.entryExit.exists" :type="closureStatus.entryExit.submitted ? 'success' : 'info'" size="small" style="margin-left: 6px">
              {{ closureStatus.entryExit.submitted ? '已提交' : '未提交' }}
            </el-tag>
          </template>
          <EntryExitTab v-if="store.drawer.activeTab === 'entryExit'" />
        </el-tab-pane>

        <el-tab-pane label="试验信息" name="testInfo">
          <template #label>
            <span>试验信息</span>
            <el-tag v-if="closureStatus.testInfo.exists" :type="closureStatus.testInfo.submitted ? 'success' : 'info'" size="small" style="margin-left: 6px">
              {{ closureStatus.testInfo.submitted ? '已提交' : '未提交' }}
            </el-tag>
          </template>
          <TestInfoTab v-if="store.drawer.activeTab === 'testInfo'" />
        </el-tab-pane>

        <el-tab-pane label="技术资料" name="docApproval">
          <template #label>
            <span>技术资料</span>
            <el-tag v-if="closureStatus.docApproval.exists" :type="closureStatus.docApproval.submitted ? 'success' : 'info'" size="small" style="margin-left: 6px">
              {{ closureStatus.docApproval.submitted ? '已提交' : '未提交' }}
            </el-tag>
          </template>
          <DocApprovalTab v-if="store.drawer.activeTab === 'docApproval'" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useTaskStore } from '@/store/NVHtask'
import ClosureBar from './ClosureBar.vue'
import EntryExitTab from './tabs/EntryExitTab.vue'
import TestInfoTab from './tabs/TestInfoTab.vue'
import DocApprovalTab from './tabs/DocApprovalTab.vue'

const store = useTaskStore()

const currentMain = computed(() => store.drawer.currentMain)
const closureStatus = computed(() => store.closureStatus)

const drawerTitle = computed(() => {
  const main = currentMain.value
  if (!main) return '任务详情'
  return `${main.model} / ${main.vin_or_part_no} / ${main.test_name}`
})

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    return dateStr.split('T')[0]
  } catch {
    return dateStr
  }
}

const handleTabChange = (tab) => {
  // Tab 切换时的处理（lazy load 已在各 Tab 组件内实现）
}

const handleClose = async (done) => {
  // 检查是否有未保存的数据
  const hasDirty = store.entryExit.dirty || store.testInfo.dirty || store.docApproval.dirty
  if (hasDirty) {
    try {
      await ElMessageBox.confirm('有未保存的修改，确定关闭吗？', '提示', { type: 'warning' })
      store.closeDrawer()
      done()
    } catch {
      // 取消关闭
    }
  } else {
    store.closeDrawer()
    done()
  }
}
</script>

<style scoped>
.drawer-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.drawer-subtitle {
  font-size: 13px;
  color: #909399;
}

.drawer-content {
  padding: 0 8px;
}
</style>
