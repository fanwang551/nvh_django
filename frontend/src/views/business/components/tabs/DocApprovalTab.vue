<template>
  <div class="doc-approval-tab" v-loading="store.docApproval.loading">
    <div class="section-title">技术资料发放批准单</div>

    <!-- 是否需要填写技术资料 - 顶部单选 -->
    <div class="doc-requirement-radio">
      <span class="radio-label">是否需要填写技术资料：</span>
      <el-radio-group v-model="docRequirementLocal" @change="handleDocRequirementChange">
        <el-radio :value="true">是</el-radio>
        <el-radio :value="false">否</el-radio>
      </el-radio-group>
    </div>

    <!-- 不需要技术资料时的提示 -->
    <div v-if="!docRequirement" class="no-requirement-hint">
      <el-icon><InfoFilled /></el-icon>
      <span>当前不需要技术资料</span>
    </div>

    <!-- 表单区域：仅在需要技术资料时显示 -->
    <template v-if="docRequirement">
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
          <el-select
            v-model="formData.issuer_name"
            filterable
            allow-create
            default-first-option
            :loading="issuerOptionsLoading"
            :no-data-text="issuerOptionsLoading ? '加载中...' : '暂无可选人员'"
            placeholder="请选择发放人"
            style="width: 100%"
            @change="markDirty"
          >
            <el-option v-for="u in issuerOptions" :key="u.id" :label="u.display_name" :value="u.full_name" />
          </el-select>
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
            <span v-if="!formData.file_url" class="upload-hint">* 提交前必须上传文件</span>
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
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { useTaskStore } from '@/store/NVHtask'
import { nvhTaskApi } from '@/api/nvhTask'
import { userApi } from '@/api/user'

const store = useTaskStore()

// 发放人下拉选项（复用 NVH组组员 数据）
const issuerOptions = ref([])
const issuerOptionsLoading = ref(false)

const loadIssuerOptions = async () => {
  if (issuerOptionsLoading.value) return
  issuerOptionsLoading.value = true
  try {
    const res = await userApi.listUsersByGroup('NVH组组员')
    const items = res?.items || []
    issuerOptions.value = items.map(u => ({
      id: u.id,
      username: u.username,
      full_name: u.full_name,
      display_name: u.full_name || u.username
    }))
  } catch (e) {
    issuerOptions.value = []
  } finally {
    issuerOptionsLoading.value = false
  }
}

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

// doc_requirement 本地状态（用于单选控件绑定）
const docRequirementLocal = ref(false)

const currentMain = computed(() => store.drawer.currentMain)
const docApprovalData = computed(() => store.docApproval.data)
const isSubmitted = computed(() => docApprovalData.value?.status === 'SUBMITTED')

// 实际的 doc_requirement 值（从 main 读取）
const docRequirement = computed(() => currentMain.value?.doc_requirement || false)

// 监听 currentMain 变化，同步 doc_requirement
watch(currentMain, (main) => {
  if (main) {
    docRequirementLocal.value = main.doc_requirement || false
    formData.value.receiver_name = main.requester_name || ''
    formData.value.issuer_name = store.currentFullname || ''
  }
}, { immediate: true })

// 处理 doc_requirement 变化
const handleDocRequirementChange = async (value) => {
  const mainId = store.drawer.currentMainId
  if (!mainId) return
  
  // 从"是"切换到"否"时，弹出确认弹窗
  if (!value) {
    try {
      await ElMessageBox.confirm(
        '本任务不需要技术资料，确认后无需提交',
        '确认',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      // 用户点击确认：仅更新 main.doc_requirement=false
      await store.updateMainRecord(mainId, { doc_requirement: false })
      ElMessage.success('已设置为不需要技术资料')
    } catch {
      // 用户点击取消：恢复选择为"是"
      docRequirementLocal.value = true
    }
  } else {
    // 从"否"切换到"是"：直接更新 main.doc_requirement=true
    try {
      await store.updateMainRecord(mainId, { doc_requirement: true })
      ElMessage.success('已设置为需要技术资料')
      // 加载 doc_approval 数据（如果没有会自动创建）
      await store.loadDocApproval()
    } catch (e) {
      ElMessage.error('设置失败')
      docRequirementLocal.value = false
    }
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
  // 加载发放人下拉选项
  loadIssuerOptions()

  // 仅在需要技术资料时加载 doc_approval 数据
  if (docRequirement.value) {
    await store.loadDocApproval()
  }

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

.doc-requirement-radio {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.radio-label {
  font-size: 14px;
  color: #606266;
  margin-right: 16px;
}

.no-requirement-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 24px;
  background: #f4f4f5;
  border-radius: 6px;
  color: #909399;
  font-size: 14px;
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
