import { defineStore } from 'pinia'
import { dashboardApi } from '@/api/dashboard'

export const useHomeDashboardStore = defineStore('homeDashboard', {
  state: () => ({
    dashboardData: null,
    loading: false,
    loadedAt: null,
    error: null
  }),

  getters: {
    hasLoaded: (state) => !!state.loadedAt
  },

  actions: {
    /**
     * 加载首页仪表盘数据
     * @param {boolean} force 是否强制重新加载
     */
    async load(force = false) {
      if (this.loading) return
      if (!force && this.dashboardData) return

      try {
        this.loading = true
        this.error = null
        const res = await dashboardApi.getHomeDashboard()
        this.dashboardData = res?.data || {}
        this.loadedAt = Date.now()
      } catch (error) {
        console.error('加载首页仪表盘数据失败:', error)
        this.error = error
        throw error
      } finally {
        this.loading = false
      }
    },

    reset() {
      this.dashboardData = null
      this.loadedAt = null
      this.error = null
    }
  }
})

