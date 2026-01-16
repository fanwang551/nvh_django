<template>
  <div class="doc-approval-tab" v-loading="store.docApproval.loading">
    <div class="section-title">技术资料发放批准单</div>

    <!-- 是否需要填写技术资料 -->
    <div class="doc-requirement-section">
      <el-form-item label="是否需要填写技术资料">
        <el-switch
          v-model="docRequirement"
          :disabled="!store.isScheduler"
          @change="handleDocRequirementChange"
        />
        <span class="requirement-hint">{{ docRequirement ? '必填（影响闭环）' : '可选（不影响闭环）' }}</span>
      </el-form-item>
    </div>

    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px" :disabled="isSubmitted && !store.isScheduler">
      <el-form-item label="名称" prop="doc_name">
        <el-input v-model="formData.doc_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="数量" prop="quantity">
        <el-input-number v-model="formData.quantity" :min="0" style="width: 100%" @change="markDirty" />
      </el-form-item>
      <el-form-item label="接收人" prop="receiver_name">
        <el-input v-model="formData.receiver_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="发放人" prop="issuer_name">
        <el-input v-model="formData.issuer_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="批准人" prop="approver_name">
        <el-input v-model="formData.approver_name" @change="markDirty" />
      </el-form-item>
      <el-form-item label="发放日期" prop="issue_date">
        <el-date-picker v-model="formData.issue_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" @change="markDirty" />
      </el-form-item>
      <el-form-item label="文件(图片)" prop="file_url">
        <div class="upload-area">
          <el-image
            v-if="previewUrl"
            :src="previewUrl"
            fit="cover"
            style="width: 120px; height: 90px; border-radius: 6px"
            :preview-src-list="[previewUrl]"
          />
          <el-upload
            action="/api/nvh-task/upload/"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="uploadFile"
            :disabled="uploading"
          >
            <el-button size="small" :loading="uploading">{{ formData.file_url ? '更换文件' : '上传文件' }}</el-button>
          </el-upload>
          <el-button v-if="formData.file_url" size="small" type="danger" plain @click="handleDeleteFile">删除</el-button>
          <span v-if="!formData.file_url && docRequirement" class="upload-hint">* 提交前必须上传文件</span>
          <span v-if="!formData.file_url && !docRequirement" class="upload-hint optional">可选（不影响闭环）</span>
          <span v-if="pendingUpload" class="upload-hint pending">文件已选择，请点击保存</span>
        </div>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="handleSave" :disabled="isSubmitted && !store.isScheduler" :loading="saving">保存草稿</el-button>
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

const formRef = ref(null)
const formData = ref({
  doc_name: '',
  quantity: null,
  receiver_name: '',
  issuer_name: '',
  approver_name: '秦军旭',
  issue_date: null,
  file_url: ''
})

// 表单校验规则 - 所有字段必填
const formRules = {
  doc_name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  receiver_name: [{ required: true, message: '请输入接收人', trigger: 'blur' }],
  issuer_name: [{ required: true, message: '请输入发放人', trigger: 'blur' }],
  approver_name: [{ required: true, message: '请输入批准人', trigger: 'blur' }],
  issue_date: [{ required: true, message: '请选择发放日期', trigger: 'change' }],
  file_url: [{ required: true, message: '请上传文件(图片)', trigger: 'change' }]
}

const uploading = ref(false)
const saving = ref(false)
const pendingUpload = ref(false)  // 标记是否有待保存的上传文件
const docRequirement = ref(false)  // 是否需要填写技术资料

const currentMain = computed(() => store.drawer.currentMain)
const docApprovalData = computed(() => store.docApproval.data)
const isSubmitted = computed(() => docApprovalData.value?.status === 'SUBMITTED')

// 监听 currentMain 变化，同步 doc_requirement
watch(currentMain, (main) => {
  if (main) {
    docRequirement.value = main.doc_requirement || false
    formData.value.receiver_name = main.requester_name || ''
    formData.value.issuer_name = store.currentFullname || ''
  }
}, { immediate: true })

// 处理 doc_requirement 变化
const handleDocRequirementChange = async (value) => {
  const mainId = store.drawer.currentMainId
  if (!mainId) return
  
  try {
    await store.updateMainRecord(mainId, { doc_requirement: value })
    ElMessage.success(value ? '已设置为必填项' : '已设置为可选项')
  } catch (e) {
    ElMessage.error('设置失败')
    // 恢复原值
    docRequirement.value = !value
  }
}

// 计算预览URL
const previewUrl = computed(() => {
  const url = formData.value.file_url
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/media/')) return url
  return `/media/${url}`
})

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
 * 上传技术资料文件（上传到临时目录，不立即保存到数据库）
 */
const uploadFile = async ({ file }) => {
  uploading.value = true
  try {
    const res = await nvhTaskApi.uploadImage(file, 'nvh_task_approval')
    if (res?.data?.relative_path) {
      formData.value.file_url = res.data.relative_path
      pendingUpload.value = true  // 标记有待保存的文件
      markDirty()
      // 触发校验清除错误提示
      formRef.value?.validateField('file_url')
      ElMessage.success('文件已上传，请点击保存草稿')
    }
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

/**
 * 删除已选文件
 */
const handleDeleteFile = () => {
  formData.value.file_url = ''
  pendingUpload.value = false
  markDirty()
  // 触发校验显示必填提示
  formRef.value?.validateField('file_url')
}

// 监听数据变化
watch(docApprovalData, (val) => {
  if (val) {
    formData.value = { ...val }
    pendingUpload.value = false  // 从服务器加载的数据，没有待保存的上传
  }
}, { immediate: true })

// 保存
const handleSave = async () => {
  saving.value = true
  try {
    await store.updateDocApproval(formData.value)
    pendingUpload.value = false  // 保存成功后清除待保存标记
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 提交
const handleSubmit = async () => {
  // 前端表单校验
  if (formRef.value) {
    try {
      await formRef.value.validate()
    } catch {
      ElMessage.warning('请填写完整信息')
      return
    }
  }

  // 提交等价于：保存草稿 + 提交（避免只保存部分字段）
  saving.value = true
  try {
    await store.updateDocApproval(formData.value)
    pendingUpload.value = false
  } catch (e) {
    ElMessage.error('保存失败，无法提交')
    saving.value = false
    return
  }
  saving.value = false

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

.doc-requirement-section {
  margin-bottom: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.requirement-hint {
  margin-left: 12px;
  font-size: 13px;
  color: #606266;
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

.upload-hint.optional {
  color: #909399;
}

.upload-hint.pending {
  color: #409eff;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
