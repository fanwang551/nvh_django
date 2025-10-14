<template>
  <div class="main-layout">
    <el-container>
      <!-- 椤堕儴瀵艰埅鏍?-->
      <el-header class="main-header">
        <TopNavbar />
      </el-header>
      
      <el-container>
        <!-- 渚ц竟鑿滃崟鏍?-->
        <el-aside class="main-aside" :width="sideMenuWidth">
          <SideMenu
            @menu-select="handleMenuSelect"
            @collapse-change="handleCollapseChange"
          />
        </el-aside>
        
        <!-- 涓诲唴瀹瑰尯鍩?-->
        <el-main class="main-content">
          <!-- 鏍囩椤靛鑸?-->
          <div class="tab-navigation">
            <TabNavigation 
              :active-tab="activeTab"
              :tabs="openTabs"
              @tab-click="handleTabClick"
              @tab-remove="handleTabRemove"
            />
          </div>
          
          <!-- 鍐呭鍖哄煙 -->
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

// 褰撳墠婵€娲荤殑鏍囩椤?
const activeTab = ref('home')

// 宸叉墦寮€鐨勬爣绛鹃〉鍒楄〃
const openTabs = reactive([
  { name: 'home', title: '棣栭〉', closable: false }
])

// 渚ц竟鑿滃崟瀹藉害
const sideMenuWidth = ref('200px')

// 闇€瑕佺紦瀛樼殑缁勪欢鍒楄〃
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
  'SuspensionIsolationQuery'
])

// 鑿滃崟閫夋嫨澶勭悊
const handleMenuSelect = (menuKey) => {
  const menuConfig = {
    'home': { name: 'home', title: '棣栭〉', route: '/' },
    'business': { name: 'business', title: '涓氬姟涓績', route: '/business' },
    'permission': { name: 'permission', title: '鏉冮檺绠＄悊', route: '/permission' },
    'others': { name: 'others', title: '鍏朵粬', route: '/others' }
  }

  const menu = menuConfig[menuKey]
  if (menu) {
    // 妫€鏌ユ爣绛鹃〉鏄惁宸插瓨鍦?
    const existingTab = openTabs.find(tab => tab.name === menu.name)
    if (!existingTab) {
      openTabs.push({
        name: menu.name,
        title: menu.title,
        closable: menu.name !== 'home' // 棣栭〉涓嶅彲鍏抽棴
      })
    }

    // 鍒囨崲鍒板搴旀爣绛鹃〉
    activeTab.value = menu.name
    router.push(menu.route)
  }
}

// 娣诲姞涓氬姟瀛愰〉闈㈡爣绛鹃〉
const addBusinessTab = (routePath) => {
  const businessTabConfig = {
    '/business/modal-data-query': { name: 'modal-data-query', title: '妯℃€佹暟鎹煡璇? },
    '/business/modal-data-compare': { name: 'modal-data-compare', title: '妯℃€佹暟鎹姣? },
    '/business/airtight-leak-compare': { name: 'airtight-leak-compare', title: '姘斿瘑鎬ф硠婕忛噺瀵规瘮' },
    '/business/airtightness-image-query': { name: 'airtightness-image-query', title: '姘斿瘑鎬ф祴璇曞浘鐗囨煡璇? },
    '/business/sound-insulation-compare': { name: 'sound-insulation-compare', title: '鍖哄煙闅斿０閲忥紙ATF锛夊姣? },
    '/business/acoustic-analysis': { name: 'acoustic-analysis', title: '澹板娴嬭瘯鏁版嵁鍒嗘瀽' },
    '/business/vehicle-sound-insulation-query': { name: 'vehicle-sound-insulation-query', title: '杞﹀瀷闅斿０閲忔煡璇? },
    '/business/vehicle-reverberation-query': { name: 'vehicle-reverberation-query', title: '杞﹁締娣峰搷鏃堕棿鏌ヨ' },
    '/business/wheel-performance-query': { name: 'wheel-performance-query', title: '杞﹁疆鎬ц兘鏌ヨ' },
    '/business/ntf-query': { name: 'ntf-query', title: 'NTF鏌ヨ' },
    '/business/sound-absorption-query': { name: 'sound-absorption-query', title: '鍚稿０绯绘暟鏌ヨ' },
    '/business/sound-insulation-coefficient-query': { name: 'sound-insulation-coefficient-query', title: '闅斿０閲忔煡璇? },
    '/business/material-porosity-flow-resistance-query': { name: 'material-porosity-flow-resistance-query', title: '鏉愭枡瀛旈殭鐜囨祦闃绘煡璇? },
    '/business/dynamic-stiffness-query': { name: 'dynamic-stiffness-query', title: '鍔ㄥ垰搴︽煡璇? },
    '/business/vehicle-mount-isolation-query': { name: 'vehicle-mount-isolation-query', title: '鏁磋溅鎮疆闅旀尟鐜囨煡璇? },
    '/business/suspension-isolation-query': { name: 'suspension-isolation-query', title: '鏁磋溅鎮灦闅旀尟鐜囨煡璇? }
  }

  const tabConfig = businessTabConfig[routePath]
  if (tabConfig) {
    // 纭繚涓氬姟涓績鏍囩瀛樺湪
    const businessTabExists = openTabs.find(tab => tab.name === 'business')
    if (!businessTabExists) {
      openTabs.push({
        name: 'business',
        title: '涓氬姟涓績',
        closable: true
      })
    }
    
    // 妫€鏌ュ瓙椤甸潰鏍囩鏄惁宸插瓨鍦?
    const existingTab = openTabs.find(tab => tab.name === tabConfig.name)
    if (!existingTab) {
      openTabs.push({
        name: tabConfig.name,
        title: tabConfig.title,
        closable: true
      })
    }

    // 鍒囨崲鍒板搴旀爣绛鹃〉
    activeTab.value = tabConfig.name
  }
}

// 鏍囩椤电偣鍑诲鐞?
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
    'suspension-isolation-query': '/business/suspension-isolation-query'
  }

  if (allRoutes[tabName]) {
    router.push(allRoutes[tabName])
  }
}

// 鏍囩椤靛叧闂鐞?
const handleTabRemove = (tabName) => {
  const index = openTabs.findIndex(tab => tab.name === tabName)
  if (index > -1 && openTabs[index].closable) {
    openTabs.splice(index, 1)

    // 濡傛灉鍏抽棴鐨勬槸褰撳墠婵€娲绘爣绛鹃〉锛屽垏鎹㈠埌鍓嶄竴涓爣绛鹃〉
    if (activeTab.value === tabName) {
      const newActiveTab = openTabs[Math.max(0, index - 1)]
      if (newActiveTab) {
        handleTabClick(newActiveTab.name)
      }
    }
  }
}

// 渚ц竟鑿滃崟鏀惰捣鐘舵€佸彉鍖栧鐞?
const handleCollapseChange = (collapsed) => {
  sideMenuWidth.value = collapsed ? '64px' : '200px'
}

// 鐩戝惉璺敱鍙樺寲锛岃嚜鍔ㄥ鐞嗕笟鍔″瓙椤甸潰鏍囩椤?
watch(() => route.path, (newPath) => {
  if (newPath.startsWith('/business/')) {
    addBusinessTab(newPath)
  } else if (newPath === '/business') {
    // 濡傛灉鏄笟鍔′腑蹇冧富椤甸潰锛岀‘淇濅笟鍔′腑蹇冩爣绛惧瓨鍦ㄥ苟婵€娲?
    const existingTab = openTabs.find(tab => tab.name === 'business')
    if (!existingTab) {
      openTabs.push({
        name: 'business',
        title: '涓氬姟涓績',
        closable: true
      })
    }
    activeTab.value = 'business'
  }
}, { immediate: true })

// 椤甸潰鍔犺浇鏃舵牴鎹綋鍓嶈矾鐢卞垵濮嬪寲鏍囩椤电姸鎬?
const initializeTabsFromRoute = () => {
  const currentPath = route.path
  
  if (currentPath === '/business') {
    // 涓氬姟涓績涓婚〉闈?
    const existingTab = openTabs.find(tab => tab.name === 'business')
    if (!existingTab) {
      openTabs.push({
        name: 'business',
        title: '涓氬姟涓績',
        closable: true
      })
    }
    activeTab.value = 'business'
  } else if (currentPath.startsWith('/business/')) {
    // 涓氬姟瀛愰〉闈?
    addBusinessTab(currentPath)
  } else if (currentPath === '/permission') {
    const existingTab = openTabs.find(tab => tab.name === 'permission')
    if (!existingTab) {
      openTabs.push({
        name: 'permission',
        title: '鏉冮檺绠＄悊',
        closable: true
      })
    }
    activeTab.value = 'permission'
  } else if (currentPath === '/others') {
    const existingTab = openTabs.find(tab => tab.name === 'others')
    if (!existingTab) {
      openTabs.push({
        name: 'others',
        title: '鍏朵粬',
        closable: true
      })
    }
    activeTab.value = 'others'
  } else {
    // 榛樿棣栭〉
    activeTab.value = 'home'
  }
}

// 缁勪欢鎸傝浇鏃跺垵濮嬪寲鏍囩椤?
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
  height: calc(100vh - 60px - 41px); /* 鍑忓幓header鍜宼ab鐨勯珮搴?*/
  overflow-y: auto;
}

/* 婊氬姩鏉℃牱寮?*/
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

