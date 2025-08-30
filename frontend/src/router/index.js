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
import AirtightTestChart from '@/views/business/AirtightTestChart.vue'
import AirtightnessImageQuery from '@/views/business/AirtightnessImageQuery.vue'
import SoundInsulationCompare from '@/views/business/SoundInsulationCompare.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
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
    path: '/business/airtight-test-chart',
    name: 'AirtightTestChart',
    component: AirtightTestChart,
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
})

export default router
