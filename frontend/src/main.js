import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { pinia, useUserStore } from './store'
import { userApi } from './api/user'
import { initKeycloak } from './utils/keycloak'

// Initialize Keycloak first, then create Vue app
initKeycloak().then((keycloak) => {
  const app = createApp(App)
  
  // Use plugins
  app.use(ElementPlus)
  app.use(router)
  app.use(pinia)
  
  // Make keycloak available globally
  app.config.globalProperties.$keycloak = keycloak
  
  // Initialize user info in store for header display
  try {
    const userStore = useUserStore()
    if (keycloak?.authenticated && keycloak?.tokenParsed) {
      const tp = keycloak.tokenParsed || {}
      // Immediate populate from token for UI
      userStore.setUserInfo({
        user: {
          id: tp.sub || '',
          username: tp.preferred_username || '',
          email: tp.email || '',
          first_name: tp.given_name || '',
          last_name: tp.family_name || '',
          is_authenticated: true,
          is_active: true
        },
        oidc_info: {
          sub: tp.sub || '',
          preferred_username: tp.preferred_username || '',
          email: tp.email || '',
          email_verified: tp.email_verified || false,
          given_name: tp.given_name || '',
          family_name: tp.family_name || '',
          name: tp.name || ''
        }
      })
      // Then try backend for authoritative info
      userApi.getUserInfo().then((info) => {
        if (info) userStore.setUserInfo(info)
      }).catch(() => {/* ignore */})
    }
  } catch (e) {
    console.warn('User store init failed:', e)
  }
  
  // Mount app
  app.mount('#app')
  
  console.log('Vue app initialized with Keycloak authentication')
}).catch(error => {
  console.error('Failed to initialize application:', error)
})
