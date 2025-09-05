<template>
  <div class="main-layout">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="main-header">
        <TopNavbar />
      </el-header>
      
      <el-container>
        <!-- 侧边菜单栏 -->
        <el-aside class="main-aside" :width="sideMenuWidth">
          <SideMenu
            @menu-select="handleMenuSelect"
            @collapse-change="handleCollapseChange"
          />
        </el-aside>
        
        <!-- 主内容区域 -->
        <el-main class="main-content">
          <!-- 标签页导航 -->
          <div class="tab-navigation">
            <TabNavigation 
              :active-tab="activeTab"
              :tabs="openTabs"
              @tab-click="handleTabClick"
              @tab-remove="handleTabRemove"
            />
          </div>
          
          <!-- 内容区域 -->
          <div class="content-area">
            <keep-alive :include="cachedComponents">
              <router-view />
            </keep-alive>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TopNavbar from './TopNavbar.vue'
import SideMenu from './SideMenu.vue'
import TabNavigation from './TabNavigation.vue'

const router = useRouter()
const route = useRoute()

// 当前激活的标签页
const activeTab = ref('home')

// 已打开的标签页列表
const openTabs = reactive([
  { name: 'home', title: '首页', closable: false }
])

// 侧边菜单宽度
const sideMenuWidth = ref('200px')

// 需要缓存的组件列表
const cachedComponents = ref([
  'ModalDataQuery',
  'ModalDataCompare',
  'AirtightLeakCompare',
  'AirtightnessImageQuery',
  'SoundInsulationCompare',
  'VehicleSoundInsulationQuery',
  'VehicleReverberationQuery',
  'SoundAbsorptionQuery',
  'SoundInsulationCoefficientQuery',
  'MaterialPorosityFlowResistanceQuery',
  'DynamicStiffnessQuery',
  'VehicleMountIsolationQuery'
])

// 菜单选择处理
const handleMenuSelect = (menuKey) => {
  const menuConfig = {
    'home': { name: 'home', title: '首页', route: '/' },
    'business': { name: 'business', title: '业务中心', route: '/business' },
    'permission': { name: 'permission', title: '权限管理', route: '/permission' },
    'others': { name: 'others', title: '其他', route: '/others' }
  }

  const menu = menuConfig[menuKey]
  if (menu) {
    // 检查标签页是否已存在
    const existingTab = openTabs.find(tab => tab.name === menu.name)
    if (!existingTab) {
      openTabs.push({
        name: menu.name,
        title: menu.title,
        closable: menu.name !== 'home' // 首页不可关闭
      })
    }

    // 切换到对应标签页
    activeTab.value = menu.name
    router.push(menu.route)
  }
}

// 添加业务子页面标签页
const addBusinessTab = (routePath) => {
  const businessTabConfig = {
    '/business/modal-data-query': { name: 'modal-data-query', title: '模态数据查询' },
    '/business/modal-data-compare': { name: 'modal-data-compare', title: '模态数据对比' },
    '/business/airtight-leak-compare': { name: 'airtight-leak-compare', title: '气密性泄漏量对比' },
    '/business/airtightness-image-query': { name: 'airtightness-image-query', title: '气密性测试图片查询' },
    '/business/sound-insulation-compare': { name: 'sound-insulation-compare', title: '区域隔声量（ATF）对比' },
    '/business/vehicle-sound-insulation-query': { name: 'vehicle-sound-insulation-query', title: '车型隔声量查询' },
    '/business/vehicle-reverberation-query': { name: 'vehicle-reverberation-query', title: '车辆混响时间查询' },
    '/business/sound-absorption-query': { name: 'sound-absorption-query', title: '吸声系数查询' },
    '/business/sound-insulation-coefficient-query': { name: 'sound-insulation-coefficient-query', title: '隔声量查询' },
    '/business/material-porosity-flow-resistance-query': { name: 'material-porosity-flow-resistance-query', title: '材料孔隙率流阻查询' },
    '/business/dynamic-stiffness-query': { name: 'dynamic-stiffness-query', title: '动刚度查询' },
    '/business/vehicle-mount-isolation-query': { name: 'vehicle-mount-isolation-query', title: '整车悬置隔振率查询' }
  }

  const tabConfig = businessTabConfig[routePath]
  if (tabConfig) {
    // 检查标签页是否已存在
    const existingTab = openTabs.find(tab => tab.name === tabConfig.name)
    if (!existingTab) {
      openTabs.push({
        name: tabConfig.name,
        title: tabConfig.title,
        closable: true
      })
    }

    // 切换到对应标签页
    activeTab.value = tabConfig.name
  }
}

// 标签页点击处理
const handleTabClick = (tabName) => {
  activeTab.value = tabName
  const allRoutes = {
    'home': '/',
    'business': '/business',
    'permission': '/permission',
    'others': '/others',
    'modal-data-query': '/business/modal-data-query',
    'modal-data-compare': '/business/modal-data-compare',
    'airtight-leak-compare': '/business/airtight-leak-compare',
    'airtightness-image-query': '/business/airtightness-image-query',
    'sound-insulation-compare': '/business/sound-insulation-compare',
    'vehicle-sound-insulation-query': '/business/vehicle-sound-insulation-query',
    'vehicle-reverberation-query': '/business/vehicle-reverberation-query',
    'sound-absorption-query': '/business/sound-absorption-query',
    'sound-insulation-coefficient-query': '/business/sound-insulation-coefficient-query',
    'material-porosity-flow-resistance-query': '/business/material-porosity-flow-resistance-query',
    'dynamic-stiffness-query': '/business/dynamic-stiffness-query',
    'vehicle-mount-isolation-query': '/business/vehicle-mount-isolation-query'
  }

  if (allRoutes[tabName]) {
    router.push(allRoutes[tabName])
  }
}

// 标签页关闭处理
const handleTabRemove = (tabName) => {
  const index = openTabs.findIndex(tab => tab.name === tabName)
  if (index > -1 && openTabs[index].closable) {
    openTabs.splice(index, 1)

    // 如果关闭的是当前激活标签页，切换到前一个标签页
    if (activeTab.value === tabName) {
      const newActiveTab = openTabs[Math.max(0, index - 1)]
      if (newActiveTab) {
        handleTabClick(newActiveTab.name)
      }
    }
  }
}

// 侧边菜单收起状态变化处理
const handleCollapseChange = (collapsed) => {
  sideMenuWidth.value = collapsed ? '64px' : '200px'
}

// 监听路由变化，自动处理业务子页面标签页
watch(() => route.path, (newPath) => {
  if (newPath.startsWith('/business/')) {
    addBusinessTab(newPath)
  }
}, { immediate: true })
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background-color: #f5f7fa;
}

.main-header {
  padding: 0;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.main-aside {
  background-color: #fff;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  z-index: 999;
}

.main-content {
  padding: 0;
  background-color: #f5f7fa;
}

.tab-navigation {
  background-color: #fff;
  padding: 0 16px;
  border-bottom: 1px solid #e4e7ed;
}

.content-area {
  padding: 20px;
  height: calc(100vh - 60px - 41px); /* 减去header和tab的高度 */
  overflow-y: auto;
}

/* 滚动条样式 */
.content-area::-webkit-scrollbar {
  width: 6px;
}

.content-area::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.content-area::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
