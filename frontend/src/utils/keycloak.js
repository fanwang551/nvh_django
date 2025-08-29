import Keycloak from 'keycloak-js'

// Keycloak configuration
const initOptions = {
  url: 'https://account-test.sgmw.com.cn/auth/',
  realm: 'demo',
  clientId: 'front',
  onLoad: 'login-required'
}

// Create Keycloak instance
const keycloak = new Keycloak(initOptions)

// Initialize Keycloak
export const initKeycloak = () => {
  return new Promise((resolve, reject) => {
    console.log('正在初始化Keycloak认证...')
    
    keycloak.init({
      onLoad: initOptions.onLoad,
      checkLoginIframe: false,
      enableLogging: true,
      flow: 'standard',
      responseMode: 'query',
      pkceMethod: 'S256'
    }).then((authenticated) => {
      if (!authenticated) {
        console.log('用户未认证，跳转到登录页面')
        keycloak.login({
          redirectUri: window.location.origin
        })
      } else {
        console.log('用户认证成功')
        console.log('Token:', keycloak.token)
        console.log('用户信息:', keycloak.tokenParsed)
        
        // 设置token刷新
        setupTokenRefresh()
        resolve(keycloak)
      }
    }).catch(error => {
      console.error('Keycloak初始化失败:', error)
      reject(error)
    })
  })
}

// 设置token自动刷新
const setupTokenRefresh = () => {
  setInterval(() => {
    keycloak.updateToken(70).then((refreshed) => {
      if (refreshed) {
        console.log('Token已刷新')
      } else {
        console.log('Token仍然有效，剩余时间:', 
          Math.round(keycloak.tokenParsed.exp + keycloak.timeSkew - new Date().getTime() / 1000) + '秒')
      }
    }).catch(error => {
      console.error('Token刷新失败:', error)
      // Token刷新失败，重新登录
      keycloak.login()
    })
  }, 60000) // 每分钟检查一次
}

// 登出功能
export const logout = () => {
  console.log('用户登出')
  keycloak.logout({
    redirectUri: 'https://account-test.sgmw.com.cn/auth/realms/demo/account/'
  })
}

export default keycloak
