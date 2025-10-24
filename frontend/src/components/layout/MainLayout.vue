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
  'AcousticAnalysis',
  'VehicleSoundInsulationQuery',
  'VehicleReverberationQuery',
  'WheelPerformanceQuery',
  'ExperienceQuery',
  'NTFQuery',
  'SoundAbsorptionQuery',
  'SoundInsulationCoefficientQuery',
  'MaterialPorosityFlowResistanceQuery',
  'DynamicStiffnessQuery',
  'VehicleMountIsolationQuery',
  'SuspensionIsolationQuery',
  // Vehicle Data Center
  'VehicleDataCenter',
  'IAQCenter',
  'DataCenter',
  'TraceabilityCenter',
  'VocOdorData',
  'FullSpectrumData'
])

// 菜单选择处理
const handleMenuSelect = (menuKey) => {
  const menuConfig = {
    'home': { name: 'home', title: '首页', route: '/' },
    'business': { name: 'business', title: '业务中心', route: '/business' },
    'permission': { name: 'permission', title: '权限管理', route: '/permission' },
    'others': { name: 'others', title: '其他', route: '/others' },
    'vehicle-data': { name: 'vehicle-data', title: '车身数据中心', route: '/vehicle-data' }
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
    return
  }

  // 兼容：当子菜单直接传入的是路由路径时
  if (typeof menuKey === 'string' && menuKey.startsWith('/')) {
    router.push(menuKey)
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
    '/business/acoustic-analysis': { name: 'acoustic-analysis', title: '声学测试数据分析' },
    '/business/vehicle-sound-insulation-query': { name: 'vehicle-sound-insulation-query', title: '车型隔声量查询' },
    '/business/vehicle-reverberation-query': { name: 'vehicle-reverberation-query', title: '车辆混响时间查询' },
    '/business/wheel-performance-query': { name: 'wheel-performance-query', title: '车轮性能查询' },
    '/business/ntf-query': { name: 'ntf-query', title: 'NTF查询' },
    '/business/sound-absorption-query': { name: 'sound-absorption-query', title: '吸声系数查询' },
    '/business/sound-insulation-coefficient-query': { name: 'sound-insulation-coefficient-query', title: '隔声量查询' },
    '/business/material-porosity-flow-resistance-query': { name: 'material-porosity-flow-resistance-query', title: '材料孔隙率流阻查询' },
    '/business/dynamic-stiffness-query': { name: 'dynamic-stiffness-query', title: '动刚度查询' },
    '/business/vehicle-mount-isolation-query': { name: 'vehicle-mount-isolation-query', title: '整车悬置隔振率查询' },
    '/business/suspension-isolation-query': { name: 'suspension-isolation-query', title: '整车悬架隔振率查询' }
  }

  // 经验数据库：单独处理路由映射
  let tabConfig = businessTabConfig[routePath]
  if (!tabConfig && routePath === '/business/experience-query') {
    tabConfig = { name: 'experience-query', title: '经验数据' }
  }
  if (tabConfig) {
    // 确保业务中心标签存在
    const businessTabExists = openTabs.find(tab => tab.name === 'business')
    if (!businessTabExists) {
      openTabs.push({
        name: 'business',
        title: '业务中心',
        closable: true
      })
    }
    
    // 检查子页面标签是否已存在
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

// 添加车身数据中心子页面标签页
const addVehicleDataTab = (routePath) => {
  const vehicleDataTabConfig = {
    '/vehicle-data': { name: 'vehicle-data', title: '车身数据中心' },
    '/vehicle-data/iaq': { name: 'iaq-center', title: '车内空气质量中心' },
    '/vehicle-data/data': { name: 'data-center', title: '数据中心' },
    '/vehicle-data/data/voc': { name: 'voc-data', title: 'VOC数据' },
    '/vehicle-data/data/odor': { name: 'odor-data', title: '气味数据' },
    '/vehicle-data/data/full-spectrum': { name: 'full-spectrum-data', title: '全谱数据' },
    '/vehicle-data/trace': { name: 'traceability-center', title: '溯源中心' }
  }

  const config = vehicleDataTabConfig[routePath]
  if (!config) return

  const existing = openTabs.find(tab => tab.name === config.name)
  if (!existing) {
    openTabs.push({ name: config.name, title: config.title, closable: true })
  }
  activeTab.value = config.name
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
    'acoustic-analysis': '/business/acoustic-analysis',
    'vehicle-sound-insulation-query': '/business/vehicle-sound-insulation-query',
    'vehicle-reverberation-query': '/business/vehicle-reverberation-query',
    'wheel-performance-query': '/business/wheel-performance-query',
    'ntf-query': '/business/ntf-query',
    'sound-absorption-query': '/business/sound-absorption-query',
    'sound-insulation-coefficient-query': '/business/sound-insulation-coefficient-query',
    'material-porosity-flow-resistance-query': '/business/material-porosity-flow-resistance-query',
    'dynamic-stiffness-query': '/business/dynamic-stiffness-query',
    'vehicle-mount-isolation-query': '/business/vehicle-mount-isolation-query',
    'suspension-isolation-query': '/business/suspension-isolation-query',
    // Vehicle Data Center
    'vehicle-data': '/vehicle-data',
    'iaq-center': '/vehicle-data/iaq',
    'data-center': '/vehicle-data/data',
    'voc-data': '/vehicle-data/data/voc',
    'odor-data': '/vehicle-data/data/odor',
    'full-spectrum-data': '/vehicle-data/data/full-spectrum',
    'traceability-center': '/vehicle-data/trace'
  }
  // 经验数据库：追加路由映射
  allRoutes['experience-query'] = '/business/experience-query'

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
  } else if (newPath === '/business') {
    // 如果是业务中心主页面，确保业务中心标签存在并激活
    const existingTab = openTabs.find(tab => tab.name === 'business')
    if (!existingTab) {
      openTabs.push({
        name: 'business',
        title: '业务中心',
        closable: true
      })
    }
    activeTab.value = 'business'
  } else if (newPath.startsWith('/vehicle-data')) {
    addVehicleDataTab(newPath)
  }
}, { immediate: true })

// 页面加载时根据当前路由初始化标签页状态
const initializeTabsFromRoute = () => {
  const currentPath = route.path
  
  if (currentPath === '/business') {
    // 业务中心主页面
    const existingTab = openTabs.find(tab => tab.name === 'business')
    if (!existingTab) {
      openTabs.push({
        name: 'business',
        title: '业务中心',
        closable: true
      })
    }
    activeTab.value = 'business'
  } else if (currentPath.startsWith('/business/')) {
    // 业务子页面
    addBusinessTab(currentPath)
  } else if (currentPath === '/vehicle-data') {
    const existingVD = openTabs.find(tab => tab.name === 'vehicle-data')
    if (!existingVD) {
      openTabs.push({ name: 'vehicle-data', title: '车身数据中心', closable: true })
    }
    activeTab.value = 'vehicle-data'
  } else if (currentPath.startsWith('/vehicle-data/')) {
    addVehicleDataTab(currentPath)
  } else if (currentPath === '/permission') {
    const existingTab = openTabs.find(tab => tab.name === 'permission')
    if (!existingTab) {
      openTabs.push({
        name: 'permission',
        title: '权限管理',
        closable: true
      })
    }
    activeTab.value = 'permission'
  } else if (currentPath === '/others') {
    const existingTab = openTabs.find(tab => tab.name === 'others')
    if (!existingTab) {
      openTabs.push({
        name: 'others',
        title: '其他',
        closable: true
      })
    }
    activeTab.value = 'others'
  } else {
    // 默认首页
    activeTab.value = 'home'
  }
}

// 组件挂载时初始化标签页
initializeTabsFromRoute()
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
