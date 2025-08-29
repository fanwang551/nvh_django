import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { pinia } from './store'
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
  
  // Mount app
  app.mount('#app')
  
  console.log('Vue app initialized with Keycloak authentication')
}).catch(error => {
  console.error('Failed to initialize application:', error)
})
