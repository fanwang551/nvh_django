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
      const user = state.userInfo?.user
      if (user?.first_name || user?.last_name) {
        return `${user.first_name || ''} ${user.last_name || ''}`.trim()
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
