<template>
  <div class="profile">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>个人资料</h1>
          <el-button @click="$router.push('/')" type="primary" size="small">返回首页</el-button>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card v-loading="loading">
              <template #header>
                <div class="card-header">
                  <span>用户信息</span>
                  <el-button @click="loadUserInfo" type="primary" size="small">刷新</el-button>
                </div>
              </template>
              
              <el-descriptions :column="2" border>
                <el-descriptions-item label="用户名">
                  {{ userStore.username || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="邮箱">
                  {{ userStore.email || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="姓名">
                  {{ userStore.fullName || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="认证状态">
                  <el-tag type="success">已认证</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="用户ID">
                  {{ userStore.userInfo?.oidc_info?.sub || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="邮箱验证">
                  <el-tag :type="userStore.userInfo?.oidc_info?.email_verified ? 'success' : 'warning'">
                    {{ userStore.userInfo?.oidc_info?.email_verified ? '已验证' : '未验证' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import { userApi } from '@/api/user'

const userStore = useUserStore()
const loading = ref(false)

const loadUserInfo = async () => {
  try {
    loading.value = true
    const userInfo = await userApi.getUserInfo()
    userStore.setUserInfo(userInfo)
    ElMessage.success('用户信息加载成功')
  } catch (error) {
    console.error('Failed to load user info:', error)
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile {
  min-height: 100vh;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-main {
  padding: 20px;
}

.el-header {
  padding: 10px;
  background-color: transparent;
}
</style>
