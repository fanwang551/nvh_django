import { createRouter, createWebHistory } from 'vue-router'
import keycloak from '@/utils/keycloak'

// Import views
import Home from '@/views/Home.vue'
import Profile from '@/views/Profile.vue'
import BusinessCenter from '@/views/BusinessCenter.vue'
import PermissionManagement from '@/views/PermissionManagement.vue'
import Others from '@/views/Others.vue'

// Import business views
import ModalDataQuery from '@/views/business/ModalDataQuery.vue'
import ModalDataCompare from '@/views/business/ModalDataCompare.vue'
import AirtightLeakCompare from '@/views/business/AirtightLeakCompare.vue'
import AirtightnessImageQuery from '@/views/business/AirtightnessImageQuery.vue'
import SoundInsulationCompare from '@/views/business/SoundInsulationCompare.vue'
import VehicleSoundInsulationQuery from '@/views/business/VehicleSoundInsulationQuery.vue'
import VehicleReverberationQuery from '@/views/business/VehicleReverberationQuery.vue'
import WheelPerformanceQuery from '@/views/business/WheelPerformanceQuery.vue'
import ExperienceQuery from '@/views/business/ExperienceQuery.vue'
import AcousticAnalysis from '@/views/business/AcousticAnalysis.vue'
import NTFQuery from '@/views/business/NTFQuery.vue'
import SoundAbsorptionQuery from '@/views/business/SoundAbsorptionQuery.vue'
import SoundInsulationCoefficientQuery from '@/views/business/SoundInsulationCoefficientQuery.vue'
import MaterialPorosityFlowResistanceQuery from '@/views/business/MaterialPorosityFlowResistanceQuery.vue'
import DynamicStiffnessQuery from '@/views/business/DynamicStiffnessQuery.vue'
import VehicleMountIsolationQuery from '@/views/business/VehicleMountIsolationQuery.vue'
import SuspensionIsolationQuery from '@/views/business/SuspensionIsolationQuery.vue'
//import VOCQuery from '@/views/vehicle-data/VocData.vue'
// Vehicle Data Center views
import VehicleDataCenter from '@/views/vehicle-data/VehicleDataCenter.vue'
import IAQCenter from '@/views/vehicle-data/IAQCenter.vue'
import DataCenter from '@/views/vehicle-data/DataCenter.vue'
import TraceabilityCenter from '@/views/vehicle-data/TraceabilityCenter.vue'
import VocData from '@/views/vehicle-data/VocData.vue'
import OdorData from '@/views/vehicle-data/OdorData.vue'
import FullSpectrumData from '@/views/vehicle-data/FullSpectrumData.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/vehicle-data',
    name: 'VehicleDataCenter',
    component: VehicleDataCenter,
    meta: { requiresAuth: true, title: '车身数据中心' }
  },
  {
    path: '/vehicle-data/iaq',
    name: 'IAQCenter',
    component: IAQCenter,
    meta: { requiresAuth: true, title: '车内空气质量中心' }
  },
  {
    path: '/vehicle-data/data',
    name: 'DataCenter',
    component: DataCenter,
    meta: { requiresAuth: true, title: '数据中心' }
  },
  {
    path: '/vehicle-data/data/voc',
    name: 'VocData',
    component: VocData,
    meta: { requiresAuth: true, title: 'VOC数据' }
  },
  {
    path: '/vehicle-data/data/odor',
    name: 'OdorData',
    component: OdorData,
    meta: { requiresAuth: true, title: '气味数据' }
  },
  {
    path: '/vehicle-data/data/full-spectrum',
    name: 'FullSpectrumData',
    component: FullSpectrumData,
    meta: { requiresAuth: true, title: '全谱数据' }
  },
  {
    path: '/vehicle-data/trace',
    name: 'TraceabilityCenter',
    component: TraceabilityCenter,
    meta: { requiresAuth: true, title: '溯源中心' }
  },
  {
    path: '/business/experience-query',
    name: 'ExperienceQuery',
    component: ExperienceQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/acoustic-analysis',
    name: 'AcousticAnalysis',
    component: AcousticAnalysis,
    meta: { requiresAuth: true, title: '声学测试数据分析' }
  },
  {
    path: '/business',
    name: 'BusinessCenter',
    component: BusinessCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/modal-data-query',
    name: 'ModalDataQuery',
    component: ModalDataQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/modal-data-compare',
    name: 'ModalDataCompare',
    component: ModalDataCompare,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/airtight-leak-compare',
    name: 'AirtightLeakCompare',
    component: AirtightLeakCompare,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/airtightness-image-query',
    name: 'AirtightnessImageQuery',
    component: AirtightnessImageQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/sound-insulation-compare',
    name: 'SoundInsulationCompare',
    component: SoundInsulationCompare,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/vehicle-sound-insulation-query',
    name: 'VehicleSoundInsulationQuery',
    component: VehicleSoundInsulationQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/vehicle-reverberation-query',
    name: 'VehicleReverberationQuery',
    component: VehicleReverberationQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/wheel-performance-query',
    name: 'WheelPerformanceQuery',
    component: WheelPerformanceQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/ntf-query',
    name: 'NTFQuery',
    component: NTFQuery,
    meta: { requiresAuth: true, title: 'NTF查询' }
  },
  {
    path: '/business/sound-absorption-query',
    name: 'SoundAbsorptionQuery',
    component: SoundAbsorptionQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/sound-insulation-coefficient-query',
    name: 'SoundInsulationCoefficientQuery',
    component: SoundInsulationCoefficientQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/material-porosity-flow-resistance-query',
    name: 'MaterialPorosityFlowResistanceQuery',
    component: MaterialPorosityFlowResistanceQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/dynamic-stiffness-query',
    name: 'DynamicStiffnessQuery',
    component: DynamicStiffnessQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/vehicle-mount-isolation-query',
    name: 'VehicleMountIsolationQuery',
    component: VehicleMountIsolationQuery,
    meta: { requiresAuth: true }
  },
  {
    path: '/business/suspension-isolation-query',
    name: 'SuspensionIsolationQuery',
    component: SuspensionIsolationQuery,
    meta: { requiresAuth: true }
  },
//  {
//    path: '/business/voc-query',
//    name: 'VOCQuery',
//    component: VOCQuery,
//    meta: { requiresAuth: true, title: 'VOC数据查询' }
//  },
  {
    path: '/permission',
    name: 'PermissionManagement',
    component: PermissionManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/others',
    name: 'Others',
    component: Others,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (keycloak.authenticated) {
      next()
    } else {
      keycloak.login()
    }
  } else {
    next()
  }
  // 设置页面标题用于浏览器标签/潜在的标签视图
  if (to.meta && to.meta.title) {
    document.title = to.meta.title
  }
})

export default router
