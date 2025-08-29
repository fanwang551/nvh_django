<template>
  <div class="permission-management">
    <div class="page-header">
      <h2>权限管理</h2>
      <p class="page-description">管理用户权限和角色分配</p>
    </div>
    
    <el-row :gutter="20">
      <!-- 权限统计 -->
      <el-col :span="8" v-for="stat in permissionStats" :key="stat.title">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="20">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 用户权限列表 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户权限</span>
              <div class="header-actions">
                <el-button type="primary" size="small" :icon="Plus">
                  添加用户
                </el-button>
                <el-button type="success" size="small" :icon="Refresh" @click="refreshUserList">
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table :data="userList" v-loading="loading" stripe>
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="scope">
                <el-tag :type="getRoleTagType(scope.row.role)">
                  {{ scope.row.role }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === '活跃' ? 'success' : 'info'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastLogin" label="最后登录" width="150" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" @click="editUser(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteUser(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <!-- 角色管理 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>角色管理</span>
              <el-button type="primary" size="small" :icon="Plus">
                新建角色
              </el-button>
            </div>
          </template>
          
          <div class="role-list">
            <div 
              v-for="role in roleList" 
              :key="role.name"
              class="role-item"
              @click="selectRole(role)"
              :class="{ active: selectedRole?.name === role.name }"
            >
              <div class="role-info">
                <div class="role-name">{{ role.name }}</div>
                <div class="role-description">{{ role.description }}</div>
                <div class="role-users">{{ role.userCount }} 个用户</div>
              </div>
              <div class="role-actions">
                <el-button type="text" size="small" :icon="Edit" />
                <el-button type="text" size="small" :icon="Delete" />
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 权限详情 -->
        <el-card style="margin-top: 20px;" v-if="selectedRole">
          <template #header>
            <span>{{ selectedRole.name }} 权限详情</span>
          </template>
          
          <div class="permission-list">
            <div v-for="permission in selectedRole.permissions" :key="permission" class="permission-item">
              <el-icon class="permission-icon"><Check /></el-icon>
              <span>{{ permission }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  UserFilled, 
  Key,
  Plus,
  Refresh,
  Edit,
  Delete,
  Check
} from '@element-plus/icons-vue'

// 权限统计数据
const permissionStats = ref([
  {
    title: '总用户数',
    value: '45',
    icon: User,
    color: '#409eff'
  },
  {
    title: '活跃用户',
    value: '38',
    icon: UserFilled,
    color: '#67c23a'
  },
  {
    title: '角色数量',
    value: '6',
    icon: Key,
    color: '#e6a23c'
  }
])

// 用户列表
const userList = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: '管理员',
    status: '活跃',
    lastLogin: '2024-01-15 14:30'
  },
  {
    id: 2,
    username: 'user1',
    email: 'user1@example.com',
    role: '普通用户',
    status: '活跃',
    lastLogin: '2024-01-15 10:15'
  },
  {
    id: 3,
    username: 'user2',
    email: 'user2@example.com',
    role: '业务员',
    status: '离线',
    lastLogin: '2024-01-14 16:20'
  }
])

// 角色列表
const roleList = ref([
  {
    name: '管理员',
    description: '系统管理员，拥有所有权限',
    userCount: 2,
    permissions: ['用户管理', '系统配置', '数据管理', '权限管理', '日志查看']
  },
  {
    name: '业务员',
    description: '业务操作人员',
    userCount: 15,
    permissions: ['数据查看', '业务操作', '报告生成']
  },
  {
    name: '普通用户',
    description: '基础用户权限',
    userCount: 28,
    permissions: ['数据查看', '个人资料管理']
  }
])

const loading = ref(false)
const selectedRole = ref(null)

// 获取角色标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    '管理员': 'danger',
    '业务员': 'warning',
    '普通用户': 'info'
  }
  return typeMap[role] || 'info'
}

// 刷新用户列表
const refreshUserList = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('用户列表已刷新')
  }, 1000)
}

// 编辑用户
const editUser = (user) => {
  ElMessage.info(`编辑用户: ${user.username}`)
}

// 删除用户
const deleteUser = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${user.username} 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 选择角色
const selectRole = (role) => {
  selectedRole.value = role
}

onMounted(() => {
  // 默认选择第一个角色
  if (roleList.value.length > 0) {
    selectedRole.value = roleList.value[0]
  }
})
</script>

<style scoped>
.permission-management {
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

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stat-title {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.role-list {
  max-height: 300px;
  overflow-y: auto;
}

.role-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.role-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.role-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.role-info {
  flex: 1;
}

.role-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.role-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.role-users {
  font-size: 12px;
  color: #409eff;
}

.role-actions {
  display: flex;
  gap: 4px;
}

.permission-list {
  max-height: 200px;
  overflow-y: auto;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.permission-item:last-child {
  border-bottom: none;
}

.permission-icon {
  color: #67c23a;
  font-size: 14px;
}
</style>
