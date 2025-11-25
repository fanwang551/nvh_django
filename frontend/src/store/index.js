import { createPinia, defineStore } from 'pinia'

// Create pinia instance
export const pinia = createPinia()

// User store
export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    userProfile: null,
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    username: (state) => state.userInfo?.user?.username || '',
    email: (state) => state.userInfo?.user?.email || '',
    fullName: (state) => {
      const info = state.userInfo
      const user = info?.user
//      // 优先使用 OIDC 返回的规范 name 字段；若包含中文字符，则移除其中的空格
//      if (info?.oidc_info?.name) {
//        const name = info.oidc_info.name || ''
//        const hasCJK = /[\u4E00-\u9FFF]/.test(name)
//        return hasCJK ? name.replace(/\s+/g, '') : name
//      }
      // 中文姓名按“姓”+“名”显示（last_name 在前, first_name 在后, 不加空格）
      if (user?.last_name || user?.first_name) {
        return `${user?.last_name || ''}${user?.first_name || ''}`.trim()
      }
      return user?.username || ''
    }
  },

  actions: {
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      this.isAuthenticated = true
    },

    setUserProfile(userProfile) {
      this.userProfile = userProfile
    },

    setLoading(loading) {
      this.loading = loading
    },

    clearUser() {
      this.userInfo = null
      this.userProfile = null
      this.isAuthenticated = false
    }
  }
})

// Export all business stores
export { useSoundInsulationCompareStore } from './soundInsulationCompare'
export { useVehicleSoundInsulationQueryStore } from './vehicleSoundInsulationQuery'
export { useVehicleReverberationQueryStore } from './vehicleReverberationQuery'
export { useSoundAbsorptionQueryStore } from './soundAbsorptionQuery'
export { useModalDataQueryStore } from './modalDataQuery'
export { useModalDataCompareStore } from './modalDataCompare'
export { useAirtightLeakCompareStore } from './airtightLeakCompare'
export { useAirtightnessImageQueryStore } from './airtightnessImageQuery'
export { useMaterialPorosityQueryStore } from './materialPorosityQuery'
export { useDynamicStiffnessQueryStore } from './dynamicStiffnessQuery'
export { useWheelPerformanceQueryStore } from './wheelPerformanceQuery'
export { useNTFQueryStore } from './NTFQuery'
export { useVocQueryStore } from './vocQuery'
export { useDynamicNoiseAnalysisStore } from './dynamicNoiseAnalysis'
