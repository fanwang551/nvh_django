<template>
  <div class="top-navbar">
    <div class="navbar-left">
      <!-- Logo区域 -->
      <div class="logo">
        <el-icon class="logo-icon" :size="24">
          <DataAnalysis />
        </el-icon>
        <span class="system-title">NVH数据管理系统</span>
      </div>
    </div>
    
    <div class="navbar-right">
      <!-- 用户信息区域 -->
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-icon class="user-icon">
              <User />
            </el-icon>
            <span class="username">{{ userStore.fullName || userStore.username || '用户' }}</span>
            <el-icon class="dropdown-icon">
              <ArrowDown />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  DataAnalysis, 
  User, 
  ArrowDown, 
  Setting, 
  SwitchButton 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { logout as keycloakLogout } from '@/utils/keycloak'

const router = useRouter()
const userStore = useUserStore()

// 下拉菜单命令处理
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录处理
const handleLogout = () => {
  ElMessage.success('正在退出登录...')
  keycloakLogout()
}
</script>

<style scoped>
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  background-color: #409eff;
  color: white;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  color: white;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-icon {
  font-size: 18px;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.dropdown-icon {
  font-size: 12px;
  transition: transform 0.3s;
}

.user-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
}

/* 下拉菜单样式调整 */
:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-dropdown-menu__item) {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f5f7fa;
  color: #409eff;
}
</style>
