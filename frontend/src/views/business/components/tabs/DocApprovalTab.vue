<template>
  <div class="doc-approval-tab" v-loading="store.docApproval.loading">
    <div class="section-title">技术资料发放批准单</div>

    <el-form :model="formData" label-width="120px" :disabled="isSubmitted && !store.isScheduler">
      <el-form-item label="名称">
        <el-input v-model="formData.doc_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="编号">
        <el-input v-model="formData.doc_no" @change="markDirty" />
      </el-form-item>
      <el-form-item label="数量">
        <el-input-number v-model="formData.quantity" :min="0" style="width: 100%" @change="markDirty" />
      </el-form-item>
      <el-form-item label="接收人">
        <el-input v-model="formData.receiver_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="发放人">
        <el-input v-model="formData.issuer_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="批准人">
        <el-input v-model="formData.approver_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="发放日期">
        <el-date-picker v-model="formData.issue_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" @change="markDirty" />
      </el-form-item>
      <el-form-item label="文件(图片)">
        <div class="upload-area">
          <el-image
            v-if="formData.file_url"
            :src="getImageUrl(formData.file_url)"
            fit="cover"
            style="width: 120px; height: 90px; border-radius: 6px"
            :preview-src-list="[getImageUrl(formData.file_url)]"
          />
          <el-upload
            action="/api/nvh-task/upload/"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="uploadFile"
          >
            <el-button size="small">{{ formData.file_url ? '更换文件' : '上传文件' }}</el-button>
          </el-upload>
          <span v-if="!formData.file_url" class="upload-hint">* 提交前必须上传文件</span>
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
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useTaskStore } from '@/store/NVHtask'
import { nvhTaskApi } from '@/api/nvhTask'

const store = useTaskStore()

const formData = ref({
  doc_name: '',
  doc_no: '',
  quantity: null,
  receiver_name: '',
  issuer_name: '',
  approver_name: 'admin',
  issue_date: null,
  file_url: ''
})

const uploading = ref(false)

const currentMain = computed(() => store.drawer.currentMain)
const docApprovalData = computed(() => store.docApproval.data)
const isSubmitted = computed(() => docApprovalData.value?.status === 'SUBMITTED')

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/media/')) return url
  if (url.startsWith('nvh_task/')) return `/media/${url}`
  return `/media/${url}`
}

const markDirty = () => {
  store.docApproval.dirty = true
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

/**
 * 上传技术资料文件
 */
const uploadFile = async ({ file }) => {
  uploading.value = true
  try {
    const res = await nvhTaskApi.uploadImage(file, 'nvh_task_approval')
    if (res?.data?.relative_path) {
      formData.value.file_url = res.data.relative_path
      markDirty()
      ElMessage.success('文件上传成功')
      // 自动保存到后端
      await store.updateDocApproval({ file_url: res.data.relative_path })
    }
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 监听数据变化
watch(docApprovalData, (val) => {
  if (val) {
    formData.value = { ...val }
  }
}, { immediate: true })

// 初始化默认值
watch(currentMain, (main) => {
  if (main && !docApprovalData.value?.doc_no) {
    formData.value.doc_no = main.contract_no || ''
    formData.value.receiver_name = main.requester_name || ''
    formData.value.issuer_name = store.currentFullname || ''
  }
}, { immediate: true })

// 保存
const handleSave = async () => {
  try {
    await store.updateDocApproval(formData.value)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

// 提交
const handleSubmit = async () => {
  try {
    await store.submitDocApproval()
    ElMessage.success('提交成功')
  } catch (e) {
    ElMessage.error(e?.message || '提交失败')
  }
}

// 撤回
const handleUnsubmit = async () => {
  try {
    await store.unsubmitDocApproval()
    ElMessage.success('撤回成功')
  } catch (e) {
    ElMessage.error('撤回失败')
  }
}

onMounted(async () => {
  await store.loadDocApproval()

  // 设置默认发放日期为今天
  if (!formData.value.issue_date) {
    formData.value.issue_date = new Date().toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.doc-approval-tab {
  padding: 16px 8px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-hint {
  font-size: 12px;
  color: #e6a23c;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
