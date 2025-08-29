# 认证对接方案

## 解决方案介绍
认证中心使用的IAM解决方案为Keycloak。  
- GitHub: [https://github.com/keycloak/keycloak](https://github.com/keycloak/keycloak)  
- 官方文档: [https://www.keycloak.org/documentation](https://www.keycloak.org/documentation)  
- OIDC适配器: [https://github.com/keycloak/keycloak/tree/master/adapters/oidc](https://github.com/keycloak/keycloak/tree/master/adapters/oidc)  

## 端点信息
**GET请求**  
`https://account-test.sgmw.com.cn/auth/realms/demo/.well-known/openid-configuration`  

其中：  
- `token_endpoint`：获取token的端点  
- `introspection_endpoint`：自省端点  
- `userinfo_endpoint`：查询用户信息  

具体API请查询Keycloak官方网站。  

## 账号信息
**测试账号**  
- 账号: `test`  
- 密码: `B5FDs0PcyuTipj^！`  
- Realm: `demo`  
- 登录地址: `https://account-test.sgmw.com.cn/auth/realms/demo/account/`  
  - 一般不直接使用此地址登录，而是通过跳转到认证中心，认证结束后返回应用。  



## 实践示例
### Vue 示例
使用官方JS适配器:  
[https://github.com/keycloak/keycloak/tree/master/adapters/oidc/js/src/main/resources](https://github.com/keycloak/keycloak/tree/master/adapters/oidc/js/src/main/resources)  

安装依赖:  
```bash
npm install keycloak-js


```markdown
## Client 客户端
| 一般场景 | Client ID | Client Protocol | Access Type | Secret |  
|----------|-----------|-----------------|-------------|--------|  
| 前端     | `front`   | `openid-connect` | `public`    | 无     |  
| 后端     | `backend` | `openid-connect` | `bearer-only` | `8545c061-7cf7-41e5-b92b-e6769a6a75b8` |  
```
**main.js 配置**  
```javascript
import Keycloak from 'keycloak-js'

const initOptions = {
    url: 'https://account-test.sgmw.com.cn/auth/',
    realm: 'demo',
    clientId: 'front',
    onLoad: 'login-required'
}

const keycloak = Keycloak(initOptions)

keycloak.init({ onLoad: initOptions.onLoad, checkLoginIframe: false }).then((authenticated) => {
    if (!authenticated) {
        window.location.reload();
    } else {
        Vue.prototype.$keycloak = keycloak
        console.log('Authenticated')
    }

    new Vue({
        render: h => h(App),
        router,
        store,
    }).$mount('#app')

    setInterval(() => {
        keycloak.updateToken(70).then((refreshed) => {
            if (refreshed) {
                console.log('Token refreshed');
            } else {
                console.log('Token not refreshed, valid for ' 
                + Math.round(keycloak.tokenParsed.exp + keycloak.timeSkew - new Date().getTime() / 1000) + ' seconds');
            }
        }).catch(error => {
            console.log('Failed to refresh token', error)
        })
    }, 60000)
}).catch(error => {
    console.log('Authenticated Failed', error)
})
```

**拦截器配置 (request.js)**  
```javascript
import Vue from 'vue'

service.interceptors.request.use(
    config => {
        if (Vue.prototype.$keycloak.authenticated) {
            config.headers['Authorization'] = 'Bearer ' + Vue.prototype.$keycloak.token
        }
        config.headers['Content-Type'] = 'application/json'
        return config
    }
)
```

### SpringBoot 示例
**pom.xml 配置**  
```xml
<properties>
    <keycloak.version>13.0.0</keycloak.version>
</properties>

<!-- Keycloak 依赖 -->
<dependency>
    <groupId>org.keycloak</groupId>
    <artifactId>keycloak-spring-security-adapter</artifactId>
    <version>${keycloak.version}</version>
</dependency>
<dependency>
    <groupId>org.keycloak</groupId>
    <artifactId>keycloak-spring-boot-starter</artifactId>
    <version>${keycloak.version}</version>
</dependency>
<dependency>
    <groupId>org.keycloak</groupId>
    <artifactId>keycloak-core</artifactId>
    <version>${keycloak.version}</version>
</dependency>
```

**application-dev.yaml 配置**  
```yaml
# keycloak配置
keycloak:
  realm: demo
  auth-server-url: https://account-test.sgmw.com.cn/auth/
  resource: backend
  ssl-required: external
  credentials:
    secret: 8545c061-7cf7-41e5-b92b-e6769a6a75b8
  bearer-only: true
  cors: true
  principal-attribute: preferred_username
```

## 其它官方适配器
下载链接: [https://www.keycloak.org/downloads.html](https://www.keycloak.org/downloads.html)  