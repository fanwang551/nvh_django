<template>
  <div class="test-info-tab" v-loading="store.testInfo.loading">
    <!-- 来源字段（只读） -->
    <div class="readonly-section">
      <div class="section-title">来源信息（只读）</div>
      <div class="info-grid">
        <div class="info-item"><span class="label">委托日期：</span>{{ formatDate(currentMain?.schedule_start) }}</div>
        <div class="info-item"><span class="label">任务单编号：</span>{{ currentMain?.contract_no || '--' }}</div>
        <div class="info-item"><span class="label">委托联系人：</span>{{ currentMain?.requester_name || '--' }}</div>
        <div class="info-item"><span class="label">样品编号：</span>{{ currentMain?.vin_or_part_no || '--' }}</div>
        <div class="info-item"><span class="label">项目平台：</span>{{ currentMain?.model || '--' }}</div>
        <div class="info-item"><span class="label">试验项目：</span>{{ currentMain?.test_name || '--' }}</div>
        <div class="info-item"><span class="label">送件人：</span>{{ currentMain?.requester_name || '--' }}</div>
        <div class="info-item"><span class="label">接收人：</span>{{ currentMain?.tester_name || '--' }}</div>
        <div class="info-item"><span class="label">入库时间：</span>{{ formatDateTime(currentMain?.entry_exit?.enter_time) || '--' }}</div>
        <div class="info-item"><span class="label">出库时间：</span>{{ formatDateTime(currentMain?.entry_exit?.dispose_time) || '--' }}</div>
      </div>
    </div>

    <!-- 编辑区域 -->
    <div class="edit-section">
      <div class="section-title">试验信息</div>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="160px" :disabled="isSubmitted && !store.isScheduler">
        <el-form-item label="联系方式" prop="contact_phone">
          <el-input v-model="formData.contact_phone" @change="markDirty" />
        </el-form-item>
        <el-form-item label="样品名称" prop="sample_type">
          <el-select v-model="formData.sample_type" placeholder="选择样品类型" clearable style="width: 100%" @change="markDirty">
            <el-option label="零件" value="零件" />
            <el-option label="整车" value="整车" />
          </el-select>
        </el-form-item>
        <el-form-item label="研发阶段" prop="rd_stage">
          <el-select v-model="formData.rd_stage" placeholder="选择研发阶段" clearable style="width: 100%" @change="markDirty">
            <el-option label="MULE" value="MULE" />
            <el-option label="PRO" value="PRO" />
            <el-option label="OTS" value="OTS" />
            <el-option label="NS" value="NS" />
            <el-option label="S" value="S" />
            <el-option label="不涉及" value="不涉及" />
          </el-select>
        </el-form-item>
        <el-form-item label="送件部门" prop="delivery_dept">
          <el-input v-model="formData.delivery_dept" @change="markDirty" />
        </el-form-item>

        <!-- 拆装记录 -->
        <el-form-item label="是否包含拆装记录表" prop="include_teardown_record">
          <el-select v-model="formData.include_teardown_record" style="width: 100%" @change="handleTeardownRecordChange">
            <el-option label="是" value="是" />
            <el-option label="否" value="否" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.include_teardown_record === '是'" label="拆装记录表图片">
          <div class="upload-area">
            <el-image
              v-if="formData.teardown_attachment_url"
              :src="getImageUrl(formData.teardown_attachment_url)"
              fit="cover"
              style="width: 120px; height: 90px; border-radius: 6px"
              :preview-src-list="[getImageUrl(formData.teardown_attachment_url)]"
            />
            <el-upload
              action="/api/nvh-task/upload/"
              :show-file-list="false"
              :before-upload="beforeUpload"
              :http-request="uploadTeardownImage"
            >
              <el-button size="small">{{ formData.teardown_attachment_url ? '更换图片' : '上传图片' }}</el-button>
            </el-upload>
            <el-button v-if="formData.teardown_attachment_url" size="small" type="danger" plain @click="removeTeardownImage">移除</el-button>
            <span v-if="isTeardownTemp" class="upload-hint pending">图片已上传，请点击保存草稿</span>
          </div>
        </el-form-item>

        <!-- 过程记录 -->
        <el-form-item label="是否包含过程记录表" prop="include_process_record">
          <el-select v-model="formData.include_process_record" style="width: 100%" @change="markDirty">
            <el-option label="是" value="是" />
            <el-option label="否" value="否" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.include_process_record === '是'" label="过程记录表">
          <div class="process-list">
            <div class="process-hint">至少上传1张过程记录表图片</div>
            <div v-for="(att, index) in processAttachments" :key="att.id" class="process-item">
              <el-image
                :src="getImageUrl(att.file_url)"
                fit="cover"
                style="width: 80px; height: 60px; border-radius: 4px"
                :preview-src-list="processAttachments.map(a => getImageUrl(a.file_url))"
                :initial-index="index"
              />
              <span class="process-name">{{ att.record_name }}</span>
              <el-button type="danger" link size="small" @click="deleteAttachment(att.id)">删除</el-button>
            </div>
            <div v-for="pending in pendingProcessUploads" :key="pending.client_id" class="process-item pending-item">
              <el-image
                :src="getImageUrl(pending.file_url)"
                fit="cover"
                style="width: 80px; height: 60px; border-radius: 4px"
                :preview-src-list="pendingProcessUploads.map(a => getImageUrl(a.file_url))"
              />
              <span class="process-name">{{ pending.record_name }}</span>
              <span class="pending-text">待保存</span>
              <el-button type="danger" link size="small" @click="removePendingProcess(pending.client_id)">移除</el-button>
            </div>
            <div class="add-process">
              <el-select v-model="newAttachment.record_name" placeholder="选择或输入表名" filterable allow-create style="width: 200px">
                <el-option v-for="opt in store.processOptions" :key="opt.id" :label="opt.test_process_name" :value="opt.test_process_name" />
              </el-select>
              <el-upload
                action="/api/nvh-task/upload/"
                :show-file-list="false"
                :before-upload="beforeUpload"
                :http-request="uploadProcessImage"
              >
                <el-button size="small" :disabled="!newAttachment.record_name" :loading="uploading">上传图片</el-button>
              </el-upload>
              <span v-if="pendingProcessUploads.length > 0" class="process-hint pending">已选择 {{ pendingProcessUploads.length }} 张图片，点击保存草稿后生效</span>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="handleSave" :disabled="isSubmitted && !store.isScheduler">保存草稿</el-button>
        <el-button v-if="!isSubmitted" type="primary" @click="handleSubmit">提交</el-button>
        <el-button v-else type="warning" @click="handleUnsubmit">撤回提交</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useTaskStore } from '@/store/NVHtask'
import { nvhTaskApi } from '@/api/nvhTask'

const store = useTaskStore()

const formRef = ref(null)
const formData = ref({
  contact_phone: '',
  sample_type: '',
  rd_stage: '',
  delivery_dept: '',
  include_teardown_record: '否',
  include_process_record: '否',
  teardown_attachment_url: ''
})

// 表单校验规则 - 所有字段必填
const formRules = {
  contact_phone: [{ required: true, message: '请输入联系方式', trigger: 'blur' }],
  sample_type: [{ required: true, message: '请选择样品名称', trigger: 'change' }],
  rd_stage: [{ required: true, message: '请选择研发阶段', trigger: 'change' }],
  delivery_dept: [{ required: true, message: '请输入送件部门', trigger: 'blur' }],
  include_teardown_record: [{ required: true, message: '请选择是否包含拆装记录表', trigger: 'change' }],
  include_process_record: [{ required: true, message: '请选择是否包含过程记录表', trigger: 'change' }]
}

const processAttachments = ref([])
const newAttachment = ref({ record_name: '' })
const uploading = ref(false)
const saving = ref(false)
const pendingProcessUploads = ref([])

const currentMain = computed(() => store.drawer.currentMain)
const testInfoData = computed(() => store.testInfo.data)
const isSubmitted = computed(() => testInfoData.value?.status === 'SUBMITTED')

const TEMP_PREFIX = 'nvh_task/_temp/'
const isTeardownTemp = computed(() => (formData.value.teardown_attachment_url || '').startsWith(TEMP_PREFIX))

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    return dateStr.split('T')[0]
  } catch {
    return dateStr
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return null
  try {
    return dateStr.replace('T', ' ').substring(0, 16)
  } catch {
    return dateStr
  }
}

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/media/')) return url
  if (url.startsWith('nvh_task/')) return `/media/${url}`
  return `/media/${url}`
}

const markDirty = () => {
  store.testInfo.dirty = true
}

const handleTeardownRecordChange = (val) => {
  markDirty()
  if (val === '否') {
    formData.value.teardown_attachment_url = ''
  }
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件（jpg/png/webp/gif）')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

const uploadTeardownImage = async ({ file }) => {
  uploading.value = true
  try {
    const res = await nvhTaskApi.uploadImage(file, 'teardown_record')
    if (res?.data?.relative_path) {
      formData.value.teardown_attachment_url = res.data.relative_path
      formData.value.include_teardown_record = '是'
      markDirty()
      ElMessage.success('拆装记录图片已上传，请点击保存草稿')
    }
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const removeTeardownImage = () => {
  formData.value.teardown_attachment_url = ''
  markDirty()
}

const uploadProcessImage = async ({ file }) => {
  if (!newAttachment.value.record_name) {
    ElMessage.warning('请先选择或输入过程记录表名')
    return
  }

  uploading.value = true
  try {
    const uploadRes = await nvhTaskApi.uploadImage(file, 'nvh_test_process')
    if (!uploadRes?.data?.relative_path) {
      throw new Error('上传失败，未获取到文件路径')
    }

    pendingProcessUploads.value.push({
      client_id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
      record_name: newAttachment.value.record_name,
      file_url: uploadRes.data.relative_path
    })
    formData.value.include_process_record = '是'
    markDirty()
    newAttachment.value.record_name = ''
    ElMessage.success('过程记录图片已上传，请点击保存草稿')
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const removePendingProcess = (clientId) => {
  pendingProcessUploads.value = pendingProcessUploads.value.filter(p => p.client_id !== clientId)
}

const deleteAttachment = async (id) => {
  try {
    await store.deleteProcessAttachment(id)
    await loadAttachments()
    ElMessage.success('删除成功')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const loadAttachments = async () => {
  if (testInfoData.value?.id) {
    processAttachments.value = await store.loadProcessAttachments()
  }
}

watch(testInfoData, (val) => {
  if (val) {
    formData.value = {
      ...formData.value,
      contact_phone: val.contact_phone ?? '',
      sample_type: val.sample_type ?? '',
      rd_stage: val.rd_stage ?? '',
      delivery_dept: val.delivery_dept ?? '',
      include_teardown_record: val.include_teardown_record ?? '否',
      include_process_record: val.include_process_record ?? '否',
      teardown_attachment_url: val.teardown_attachment_url || ''
    }

    if (formData.value.teardown_attachment_url) {
      formData.value.include_teardown_record = '是'
    }
    if ((val.process_attachment_count || 0) > 0) {
      formData.value.include_process_record = '是'
    }
    loadAttachments()
  }
}, { immediate: true })

watch([processAttachments, pendingProcessUploads], () => {
  if ((processAttachments.value?.length || 0) + (pendingProcessUploads.value?.length || 0) > 0) {
    formData.value.include_process_record = '是'
  }
}, { immediate: true })

watch(() => formData.value.teardown_attachment_url, (url) => {
  if (url) formData.value.include_teardown_record = '是'
}, { immediate: true })

const persistAll = async () => {
  await store.updateTestInfo(formData.value)

  const testInfoId = store.testInfo.data?.id || testInfoData.value?.id
  if (!testInfoId) {
    throw new Error('试验信息未初始化，无法保存过程记录附件')
  }

  if (pendingProcessUploads.value.length > 0) {
    await loadAttachments()
    const baseSortNo = processAttachments.value.length
    const pending = [...pendingProcessUploads.value]

    for (let i = 0; i < pending.length; i += 1) {
      await store.createProcessAttachment({
        test_info: testInfoId,
        record_name: pending[i].record_name,
        file_url: pending[i].file_url,
        sort_no: baseSortNo + i
      })
    }

    pendingProcessUploads.value = []
    await loadAttachments()
    await store.loadTestInfo()
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await persistAll()
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  if (formRef.value) {
    try {
      await formRef.value.validate()
    } catch {
      ElMessage.warning('请填写完整信息')
      return
    }
  }

  if (formData.value.include_teardown_record === '是' && !formData.value.teardown_attachment_url) {
    ElMessage.warning('请上传拆装记录表图片')
    return
  }

  if (formData.value.include_process_record === '是' && 
      (processAttachments.value?.length || 0) + (pendingProcessUploads.value?.length || 0) === 0) {
    ElMessage.warning('请上传至少一张过程记录表图片')
    return
  }

  saving.value = true
  try {
    await persistAll()
  } catch (e) {
    ElMessage.error('保存失败，无法提交')
    saving.value = false
    return
  }
  saving.value = false

  try {
    await store.submitTestInfo()
    ElMessage.success('提交成功')
  } catch (e) {
    ElMessage.error(e?.message || '提交失败')
  }
}

const handleUnsubmit = async () => {
  try {
    await store.unsubmitTestInfo()
    ElMessage.success('撤回成功')
  } catch (e) {
    ElMessage.error('撤回失败')
  }
}

onMounted(async () => {
  await store.loadTestInfo()
  await store.loadProcessOptions()
})
</script>

<style scoped>
.test-info-tab {
  padding: 16px 0;
}

.readonly-section {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 16px;
}

.info-item {
  font-size: 13px;
  color: #606266;
}

.info-item .label {
  color: #909399;
}

.edit-section {
  padding: 0 8px;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-hint.pending {
  font-size: 12px;
  color: #409eff;
}

.process-list {
  width: 100%;
}

.process-hint {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.process-hint.pending {
  color: #409eff;
  margin-bottom: 0;
}

.process-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.process-item.pending-item {
  opacity: 0.9;
}

.process-name {
  flex: 1;
  font-size: 13px;
}

.pending-text {
  font-size: 12px;
  color: #409eff;
}

.add-process {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
