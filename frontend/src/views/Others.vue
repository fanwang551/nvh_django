<template>
  <div class="others">
    <div class="page-header">
      <h2>其他功能</h2>
      <p class="page-description">系统工具和辅助功能</p>
    </div>
    
    <el-row :gutter="20">
      <!-- 系统工具 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统工具</span>
            </div>
          </template>
          
          <div class="tool-grid">
            <div 
              v-for="tool in systemTools" 
              :key="tool.name"
              class="tool-item"
              @click="handleToolClick(tool.name)"
            >
              <div class="tool-icon" :style="{ backgroundColor: tool.color }">
                <el-icon :size="24">
                  <component :is="tool.icon" />
                </el-icon>
              </div>
              <div class="tool-info">
                <div class="tool-title">{{ tool.title }}</div>
                <div class="tool-description">{{ tool.description }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 系统信息 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
              <el-button type="primary" size="small" :icon="Refresh" @click="refreshSystemInfo">
                刷新
              </el-button>
            </div>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item 
              v-for="info in systemInfo" 
              :key="info.label"
              :label="info.label"
            >
              <el-tag v-if="info.type === 'tag'" :type="info.tagType">
                {{ info.value }}
              </el-tag>
              <span v-else>{{ info.value }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 日志查看 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统日志</span>
              <div class="header-actions">
                <el-select v-model="logLevel" size="small" style="width: 120px;">
                  <el-option label="全部" value="all" />
                  <el-option label="错误" value="error" />
                  <el-option label="警告" value="warning" />
                  <el-option label="信息" value="info" />
                </el-select>
                <el-button type="primary" size="small" :icon="Download">
                  导出日志
                </el-button>
                <el-button type="danger" size="small" :icon="Delete">
                  清空日志
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="log-container">
            <div 
              v-for="log in filteredLogs" 
              :key="log.id"
              class="log-item"
              :class="log.level"
            >
              <div class="log-time">{{ log.timestamp }}</div>
              <div class="log-level">
                <el-tag :type="getLogTagType(log.level)" size="small">
                  {{ log.level.toUpperCase() }}
                </el-tag>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Setting, 
  Monitor, 
  DataAnalysis, 
  Document,
  Refresh,
  Download,
  Delete,
  Tools,
  Connection,
  Warning
} from '@element-plus/icons-vue'

// 系统工具
const systemTools = ref([
  {
    name: 'backup',
    title: '数据备份',
    description: '备份系统数据',
    icon: Document,
    color: '#409eff'
  },
  {
    name: 'monitor',
    title: '系统监控',
    description: '监控系统状态',
    icon: Monitor,
    color: '#67c23a'
  },
  {
    name: 'analysis',
    title: '数据分析',
    description: '分析系统数据',
    icon: DataAnalysis,
    color: '#e6a23c'
  },
  {
    name: 'maintenance',
    title: '系统维护',
    description: '系统维护工具',
    icon: Tools,
    color: '#f56c6c'
  },
  {
    name: 'connection',
    title: '连接测试',
    description: '测试外部连接',
    icon: Connection,
    color: '#909399'
  },
  {
    name: 'settings',
    title: '系统配置',
    description: '修改系统配置',
    icon: Setting,
    color: '#606266'
  }
])

// 系统信息
const systemInfo = ref([
  { label: '系统版本', value: 'v1.0.0', type: 'text' },
  { label: '运行状态', value: '正常', type: 'tag', tagType: 'success' },
  { label: '启动时间', value: '2024-01-15 08:00:00', type: 'text' },
  { label: '运行时长', value: '6小时30分钟', type: 'text' },
  { label: 'CPU使用率', value: '15%', type: 'text' },
  { label: '内存使用率', value: '45%', type: 'text' },
  { label: '磁盘使用率', value: '68%', type: 'text' },
  { label: '数据库状态', value: '连接正常', type: 'tag', tagType: 'success' }
])

// 日志级别
const logLevel = ref('all')

// 系统日志
const systemLogs = ref([
  {
    id: 1,
    timestamp: '2024-01-15 14:30:15',
    level: 'info',
    message: '用户 admin 登录系统'
  },
  {
    id: 2,
    timestamp: '2024-01-15 14:25:30',
    level: 'warning',
    message: '系统内存使用率达到80%'
  },
  {
    id: 3,
    timestamp: '2024-01-15 14:20:45',
    level: 'error',
    message: '数据库连接超时，已自动重连'
  },
  {
    id: 4,
    timestamp: '2024-01-15 14:15:20',
    level: 'info',
    message: '系统定时任务执行完成'
  },
  {
    id: 5,
    timestamp: '2024-01-15 14:10:10',
    level: 'info',
    message: '数据备份任务开始执行'
  }
])

// 过滤后的日志
const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return systemLogs.value
  }
  return systemLogs.value.filter(log => log.level === logLevel.value)
})

// 工具点击处理
const handleToolClick = (toolName) => {
  const messages = {
    backup: '数据备份功能开发中...',
    monitor: '系统监控功能开发中...',
    analysis: '数据分析功能开发中...',
    maintenance: '系统维护功能开发中...',
    connection: '连接测试功能开发中...',
    settings: '系统配置功能开发中...'
  }
  
  ElMessage.info(messages[toolName] || '功能开发中...')
}

// 刷新系统信息
const refreshSystemInfo = () => {
  ElMessage.success('系统信息已刷新')
}

// 获取日志标签类型
const getLogTagType = (level) => {
  const typeMap = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return typeMap[level] || 'info'
}
</script>

<style scoped>
.others {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.tool-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.tool-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.tool-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.tool-info {
  flex: 1;
}

.tool-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.tool-description {
  font-size: 14px;
  color: #909399;
}

.log-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Courier New', monospace;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.error {
  background-color: #fef0f0;
}

.log-item.warning {
  background-color: #fdf6ec;
}

.log-time {
  font-size: 12px;
  color: #909399;
  width: 140px;
  flex-shrink: 0;
}

.log-level {
  width: 60px;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  font-size: 13px;
  color: #606266;
}

/* 滚动条样式 */
.log-container::-webkit-scrollbar {
  width: 6px;
}

.log-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
