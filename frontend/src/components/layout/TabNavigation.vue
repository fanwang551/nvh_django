<template>
  <div class="tab-navigation">
    <el-tabs
      v-model="currentTab"
      type="card"
      class="tab-container"
      @tab-click="handleTabClick"
      @tab-remove="handleTabRemove"
    >
      <el-tab-pane
        v-for="tab in tabs"
        :key="tab.name"
        :label="tab.title"
        :name="tab.name"
        :closable="tab.closable"
      />
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'home'
  },
  tabs: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['tab-click', 'tab-remove'])

// 当前激活的标签页
const currentTab = ref(props.activeTab)

// 监听外部传入的激活标签页变化
watch(() => props.activeTab, (newValue) => {
  currentTab.value = newValue
})

// 标签页点击处理
const handleTabClick = (tab) => {
  emit('tab-click', tab.props.name)
}

// 标签页移除处理
const handleTabRemove = (tabName) => {
  emit('tab-remove', tabName)
}
</script>

<style scoped>
.tab-navigation {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.tab-container {
  margin: 0;
}

:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__item) {
  height: 40px;
  line-height: 40px;
  padding: 0 16px;
  margin-right: 0;
  border: 1px solid #e4e7ed;
  border-bottom: none;
  border-left: none;
  background-color: #f5f7fa;
  color: #606266;
  font-size: 13px;
  transition: all 0.3s;
}

:deep(.el-tabs__item:first-child) {
  border-left: 1px solid #e4e7ed;
}

:deep(.el-tabs__item:hover) {
  background-color: #ecf5ff;
  color: #409eff;
}

:deep(.el-tabs__item.is-active) {
  background-color: #fff;
  color: #409eff;
  border-color: #409eff;
  border-bottom: 1px solid #fff;
  position: relative;
  z-index: 1;
}

:deep(.el-tabs__item.is-active::after) {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #fff;
}

/* 关闭按钮样式 */
:deep(.el-tabs__item .el-icon-close) {
  margin-left: 6px;
  font-size: 12px;
  border-radius: 50%;
  transition: all 0.3s;
}

:deep(.el-tabs__item .el-icon-close:hover) {
  background-color: #f56c6c;
  color: white;
}

/* 首页标签页特殊样式（不可关闭） */
:deep(.el-tabs__item[aria-controls="pane-home"]) {
  font-weight: 600;
}

/* 标签页内容区域隐藏 */
:deep(.el-tabs__content) {
  display: none;
}

/* 滚动条样式 */
:deep(.el-tabs__nav-scroll) {
  overflow-x: auto;
}

:deep(.el-tabs__nav-scroll::-webkit-scrollbar) {
  height: 3px;
}

:deep(.el-tabs__nav-scroll::-webkit-scrollbar-track) {
  background: #f1f1f1;
}

:deep(.el-tabs__nav-scroll::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(.el-tabs__nav-scroll::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}
</style>
