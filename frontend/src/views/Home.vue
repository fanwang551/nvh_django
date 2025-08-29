<template>
  <div class="home">
    <div class="page-header">
      <h2>欢迎使用NVH数据管理系统</h2>
      <p class="page-description">系统概览和快速操作</p>
    </div>

    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-info">
              <h3>欢迎回来，{{ userStore.fullName || userStore.username || '用户' }}！</h3>
              <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
            </div>
            <div class="welcome-avatar">
              <el-avatar :size="60" :icon="UserFilled" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 系统状态 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-button @click="refreshUserInfo" type="primary" size="small" :icon="Refresh">
                刷新
              </el-button>
            </div>
          </template>
          <div v-if="loading">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统状态">
                <el-tag type="success">正常运行</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前用户">
                {{ userStore.username || '未知' }}
              </el-descriptions-item>
              <el-descriptions-item label="邮箱">
                {{ userStore.email || '未知' }}
              </el-descriptions-item>
              <el-descriptions-item label="认证状态">
                <el-tag type="success">已认证</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <!-- 快速操作 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button
              @click="$router.push('/profile')"
              type="primary"
              :icon="User"
              class="action-button"
            >
              查看个人信息
            </el-button>
            <el-button
              @click="testAuth"
              type="success"
              :icon="Key"
              class="action-button"
            >
              测试认证
            </el-button>
            <el-button
              @click="goToBusiness"
              type="warning"
              :icon="OfficeBuilding"
              class="action-button"
            >
              业务中心
            </el-button>
            <el-button
              @click="goToPermission"
              type="info"
              :icon="Setting"
              class="action-button"
            >
              权限管理
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 系统信息 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6" v-for="info in systemInfo" :key="info.label">
              <div class="system-info-item">
                <div class="info-icon" :style="{ backgroundColor: info.color }">
                  <el-icon :size="20">
                    <component :is="info.icon" />
                  </el-icon>
                </div>
                <div class="info-content">
                  <div class="info-label">{{ info.label }}</div>
                  <div class="info-value">{{ info.value }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UserFilled,
  User,
  Key,
  OfficeBuilding,
  Setting,
  Refresh,
  Monitor,
  DataAnalysis,
  Connection,
  Document
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { userApi } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 系统信息
const systemInfo = ref([
  {
    label: '前端框架',
    value: 'Vue 3 + Vite',
    icon: Monitor,
    color: '#409eff'
  },
  {
    label: '后端框架',
    value: 'Django + DRF',
    icon: DataAnalysis,
    color: '#67c23a'
  },
  {
    label: '认证系统',
    value: 'Keycloak',
    icon: Connection,
    color: '#e6a23c'
  },
  {
    label: 'UI组件',
    value: 'Element Plus',
    icon: Document,
    color: '#f56c6c'
  }
])

// 刷新用户信息
const refreshUserInfo = async () => {
  try {
    loading.value = true
    const userInfo = await userApi.getUserInfo()
    userStore.setUserInfo(userInfo)
    ElMessage.success('用户信息刷新成功')
  } catch (error) {
    console.error('Failed to refresh user info:', error)
    ElMessage.error('刷新用户信息失败')
  } finally {
    loading.value = false
  }
}

// 认证测试
const testAuth = async () => {
  try {
    const result = await userApi.authTest()
    ElMessage.success('认证测试成功')
    console.log('Auth test result:', result)
  } catch (error) {
    console.error('Auth test failed:', error)
    ElMessage.error('认证测试失败')
  }
}

// 跳转到业务中心
const goToBusiness = () => {
  router.push('/business')
}

// 跳转到权限管理
const goToPermission = () => {
  router.push('/permission')
}

onMounted(() => {
  refreshUserInfo()
})
</script>

<style scoped>
.home {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.welcome-card {
  background-color: #409eff;
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.welcome-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.welcome-info p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.welcome-avatar {
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-button {
  width: 100%;
  height: 40px;
}

.system-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.system-info-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.el-header {
  padding: 10px;
  background-color: transparent;
}

/* 欢迎卡片内的Element Plus组件样式覆盖 */
:deep(.welcome-card .el-card__body) {
  padding: 0;
}
</style>