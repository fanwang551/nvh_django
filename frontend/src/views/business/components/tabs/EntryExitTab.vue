<template>
  <div class="entry-exit-tab" v-loading="store.entryExit.loading">
    <!-- 未绑定状态：选择绑定方式 -->
    <div v-if="!hasBound" class="bind-section">
      <div class="bind-title">绑定进出登记</div>
      <el-radio-group v-model="bindMode" class="bind-mode">
        <el-radio label="new">新建进出登记</el-radio>
        <el-radio label="select">选择已有进出登记</el-radio>
      </el-radio-group>

      <!-- 新建模式 -->
      <div v-if="bindMode === 'new'" class="new-form">
        <el-form :model="newForm" label-width="100px">
          <el-form-item label="接收人">
            <el-input v-model="newForm.receiver_name" />
          </el-form-item>
          <el-form-item label="进入时间">
            <el-date-picker v-model="newForm.enter_time" type="datetime" style="width: 100%" />
          </el-form-item>
          <el-form-item label="用途">
            <el-input v-model="newForm.purpose" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="newForm.remark" type="textarea" :rows="2" />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="handleCreateAndBind">创建并绑定</el-button>
      </div>

      <!-- 选择已有模式 -->
      <div v-if="bindMode === 'select'" class="select-section">
        <el-select
          v-model="selectedEntryExitId"
          placeholder="搜索选择已有进出登记"
          filterable
          remote
          :remote-method="searchEntryExits"
          :loading="store.entryExitList.loading"
          style="width: 100%; margin-bottom: 12px"
        >
          <el-option
            v-for="item in store.entryExitList.items"
            :key="item.id"
            :label="`#${item.id} ${item.receiver_name || ''} ${formatDate(item.enter_time)}`"
            :value="item.id"
          />
        </el-select>
        <el-button type="primary" :disabled="!selectedEntryExitId" @click="handleBindExisting">确认绑定</el-button>
      </div>
    </div>

    <!-- 已绑定状态：显示表单 -->
    <div v-else class="form-section">
      <!-- 共用提示 -->
      <el-alert
        v-if="entryExitData && entryExitData.active_mainrecord_count > 1"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      >
        该进出登记已被 {{ entryExitData.active_mainrecord_count }} 个任务共用，编辑会影响所有绑定任务
      </el-alert>

      <el-form :model="formData" label-width="120px" :disabled="isSubmitted && !store.isScheduler">
        <el-form-item label="接收人">
          <el-input v-model="formData.receiver_name" @change="markDirty" />
        </el-form-item>
        <el-form-item label="进入时间">
          <el-date-picker v-model="formData.enter_time" type="datetime" style="width: 100%" @change="markDirty" />
        </el-form-item>
        <el-form-item label="用途">
          <el-input v-model="formData.purpose" @change="markDirty" />
        </el-form-item>
        <el-form-item label="处置类型">
          <el-select v-model="formData.dispose_type" placeholder="选择处置类型" clearable style="width: 100%" @change="markDirty">
            <el-option label="报废" value="报废" />
            <el-option label="归还" value="归还" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置人">
          <el-input v-model="formData.disposer_name" @change="markDirty" />
        </el-form-item>
        <el-form-item label="处置时间">
          <el-date-picker v-model="formData.dispose_time" type="datetime" style="width: 100%" @change="markDirty" />
        </el-form-item>
        <el-form-item v-if="formData.dispose_type === '归还'" label="归还接受人">
          <el-input v-model="formData.return_receiver" @change="markDirty" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" @change="markDirty" />
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="handleSave" :disabled="isSubmitted && !store.isScheduler">保存草稿</el-button>
        <el-button v-if="!isSubmitted" type="primary" @click="handleSubmit">提交</el-button>
        <el-button v-else type="warning" @click="handleUnsubmit">撤回提交</el-button>
        <el-button type="danger" plain @click="handleUnbind">解绑</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTaskStore } from '@/store/NVHtask'

const store = useTaskStore()

const bindMode = ref('new')
const selectedEntryExitId = ref(null)

const newForm = ref({
  receiver_name: '',
  enter_time: null,
  purpose: '测试',
  remark: ''
})

const formData = ref({
  receiver_name: '',
  enter_time: null,
  purpose: '',
  dispose_type: '',
  disposer_name: '',
  dispose_time: null,
  return_receiver: '',
  remark: ''
})

const entryExitData = computed(() => store.entryExit.data)
const hasBound = computed(() => !!store.drawer.currentMain?.entry_exit)
const isSubmitted = computed(() => entryExitData.value?.status === 'SUBMITTED')

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    return dateStr.split('T')[0]
  } catch {
    return dateStr
  }
}

const markDirty = () => {
  store.entryExit.dirty = true
}

// 监听数据变化，同步到表单
watch(entryExitData, (val) => {
  if (val) {
    formData.value = { ...val }
  }
}, { immediate: true })

// 搜索已有进出登记
const searchEntryExits = async (query) => {
  await store.loadEntryExitList()
}

// 创建并绑定
const handleCreateAndBind = async () => {
  try {
    const created = await store.createEntryExit(newForm.value)
    if (created?.id) {
      await store.bindEntryExit(created.id)
      ElMessage.success('创建并绑定成功')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 绑定已有
const handleBindExisting = async () => {
  if (!selectedEntryExitId.value) return
  try {
    await store.bindEntryExit(selectedEntryExitId.value)
    ElMessage.success('绑定成功')
  } catch (e) {
    ElMessage.error('绑定失败')
  }
}

// 解绑
const handleUnbind = async () => {
  try {
    await ElMessageBox.confirm('确定解绑该进出登记吗？', '提示', { type: 'warning' })
    await store.unbindEntryExit()
    ElMessage.success('解绑成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('解绑失败')
    }
  }
}

// 保存
const handleSave = async () => {
  try {
    await store.updateEntryExit(entryExitData.value.id, formData.value)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

// 提交（先保存再提交，确保所有字段完整保存）
const handleSubmit = async () => {
  // 提交等价于：保存草稿 + 提交（避免只保存部分字段）
  try {
    await store.updateEntryExit(entryExitData.value.id, formData.value)
  } catch (e) {
    ElMessage.error('保存失败，无法提交')
    return
  }

  try {
    await store.submitEntryExit()
    ElMessage.success('提交成功')
  } catch (e) {
    ElMessage.error(e?.message || '提交失败')
  }
}

// 撤回
const handleUnsubmit = async () => {
  try {
    await store.unsubmitEntryExit()
    ElMessage.success('撤回成功')
  } catch (e) {
    ElMessage.error('撤回失败')
  }
}

onMounted(async () => {
  // 初始化默认值
  const main = store.drawer.currentMain
  if (main) {
    newForm.value.receiver_name = main.tester_name || ''
    newForm.value.enter_time = main.schedule_start || null
  }

  // 如果已绑定，加载进出登记数据
  if (hasBound.value) {
    await store.loadEntryExit()
  }

  // 加载已有进出登记列表
  await store.loadEntryExitList()
})
</script>

<style scoped>
.entry-exit-tab {
  padding: 16px 0;
}

.bind-section {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.bind-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.bind-mode {
  margin-bottom: 20px;
}

.new-form, .select-section {
  margin-top: 16px;
}

.form-section {
  padding: 0 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
