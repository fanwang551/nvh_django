<template>
  <div class="side-menu">
    <!-- 收起按钮 -->
    <div class="menu-header">
      <el-button
        type="text"
        :icon="isCollapsed ? Expand : Fold"
        @click="toggleCollapse"
        class="collapse-btn"
      />
    </div>

    <el-menu
      :default-active="activeMenu"
      class="menu-container"
      @select="handleMenuSelect"
      :collapse="isCollapsed"
      :unique-opened="true"
    >
      <!-- 首页 -->
      <el-menu-item index="home">
        <el-icon><House /></el-icon>
        <template #title>首页</template>
      </el-menu-item>

      <!-- 业务中心 -->
      <el-menu-item index="business">
        <el-icon><OfficeBuilding /></el-icon>
        <template #title>NVH数据中心</template>
      </el-menu-item>

      <!-- 权限管理 -->
      <el-menu-item index="permission">
        <el-icon><Key /></el-icon>
        <template #title>权限管理</template>
      </el-menu-item>

      <!-- 车身数据中心（含子菜单） -->
      <el-sub-menu index="vehicle-data">
        <template #title>
          <el-icon><Collection /></el-icon>
          <span>车身数据中心</span>
        </template>
        <el-menu-item index="/vehicle-data/iaq">车内空气质量中心</el-menu-item>
        <el-sub-menu index="vehicle-data-data">
          <template #title>数据中心</template>
          <el-menu-item index="/vehicle-data/data/voc">VOC及气味数据库</el-menu-item>
          <el-menu-item index="/vehicle-data/data/SubstancesData">全谱数据库</el-menu-item>
        </el-sub-menu>
        <!-- 溯源中心（二级子菜单） -->
        <el-sub-menu index="traceability">
          <template #title>
            <el-icon><Search /></el-icon>
            <span>溯源中心</span>
          </template>
          <el-menu-item index="/traceability/contribution">整车溯源</el-menu-item>
          <el-menu-item index="/traceability/substance-item">污染物分项溯源</el-menu-item>
        </el-sub-menu>
      </el-sub-menu>

      <!-- 其他 -->
      <el-menu-item index="others">
        <el-icon><More /></el-icon>
        <template #title>其他</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { House, OfficeBuilding, Key, More, Fold, Expand, Collection, Search } from '@element-plus/icons-vue'

const route = useRoute()
const emit = defineEmits(['menu-select', 'collapse-change'])

// 当前激活的菜单项
const activeMenu = ref('home')

// 菜单收起状态
const isCollapsed = ref(false)

// 根据路由设置激活菜单
const setActiveMenuByRoute = () => {
  const routeMenuMap = {
    '/': 'home',
    '/business': 'business',
    '/permission': 'permission',
    '/others': 'others'
  }

  // 溯源中心相关路由（现在是车身数据中心的子菜单）
  if (route.path.startsWith('/traceability')) {
    // 使用完整路径作为activeMenu，确保子菜单项正确高亮
    activeMenu.value = route.path
    return
  }
  
  if (route.path.startsWith('/vehicle-data')) {
    // 使用完整路径作为activeMenu，确保子菜单项正确高亮
    activeMenu.value = route.path
    return
  }
  
  activeMenu.value = routeMenuMap[route.path] || 'home'
}

// 监听路由变化
watch(() => route.path, () => {
  setActiveMenuByRoute()
}, { immediate: true })

// 菜单选择处理
const handleMenuSelect = (index) => {
  activeMenu.value = index
  emit('menu-select', index)
}

// 切换收起状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('collapse-change', isCollapsed.value)
}
</script>

<style scoped>
.side-menu {
  height: 100%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.menu-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 16px;
  border-bottom: 1px solid #e4e7ed;
}

.collapse-btn {
  color: #606266;
  font-size: 16px;
  padding: 8px;
}

.collapse-btn:hover {
  color: #409eff;
  background-color: #ecf5ff;
}

.menu-container {
  border-right: none;
  flex: 1;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover) {
  background-color: #ecf5ff;
  color: #409eff;
}

:deep(.el-menu-item.is-active) {
  background-color: #409eff;
  color: white;
}

:deep(.el-menu-item.is-active:hover) {
  background-color: #337ecc;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
}

:deep(.el-menu-item span) {
  font-size: 14px;
  font-weight: 500;
}

/* 菜单项激活状态的图标颜色 */
:deep(.el-menu-item.is-active .el-icon) {
  color: white;
}

/* 菜单项悬停状态的图标颜色 */
:deep(.el-menu-item:hover .el-icon) {
  color: #409eff;
}

:deep(.el-menu-item.is-active:hover .el-icon) {
  color: white;
}
</style>
