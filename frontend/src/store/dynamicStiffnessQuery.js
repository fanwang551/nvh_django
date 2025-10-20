import { defineStore } from 'pinia'
import modalApi from '@/api/modal'
import dynamicStiffnessApi from '@/api/dynamicStiffness'

export const useDynamicStiffnessQueryStore = defineStore('dynamicStiffnessQuery', {
  state: () => ({
    // 业务数据状态 - 查询表单状态
    searchForm: {
      vehicleModelId: null,
      partName: null,
      subsystem: [],
      testPoints: []
    },

    // 业务数据状态 - 选项数据
    vehicleModelOptions: [],
    partNameOptions: [],
    subsystemOptions: [],
    testPointOptions: [],

    // 业务状态 - 加载状态
    vehicleModelsLoading: false,
    partNamesLoading: false,
    subsystemsLoading: false,
    testPointsLoading: false,
    loading: false, // 查询时的加载状态

    // 业务数据状态 - 查询结果
    queryResult: {
      count: 0,
      results: []
    }
  }),

  getters: {
    // 是否可以查询
    canQuery: (state) => {
      return state.searchForm.vehicleModelId !== null
    },

    // 是否有查询结果
    hasResults: (state) => {
      return state.queryResult.results.length > 0
    },

    // 基础信息（从第一条数据中提取）
    basicInfo: (state) => {
      if (state.queryResult.results.length === 0) return null
      
      const firstResult = state.queryResult.results[0]
      // 解析测试图片字段：支持数组或JSON字符串
      let testPhotoList = []
      const rawPhoto = firstResult.test_photo_path
      if (Array.isArray(rawPhoto)) {
        testPhotoList = rawPhoto
      } else if (typeof rawPhoto === 'string') {
        try {
          const parsed = JSON.parse(rawPhoto)
          if (Array.isArray(parsed)) {
            testPhotoList = parsed
          } else if (parsed) {
            testPhotoList = [parsed]
          }
        } catch (e) {
          // 非JSON字符串，按单个路径处理
          if (rawPhoto.trim()) testPhotoList = [rawPhoto]
        }
      }
      // 过滤空值
      testPhotoList = (testPhotoList || []).filter(Boolean)

      return {
        vehicleModelName: firstResult.vehicle_model_name,
        suspensionType: firstResult.suspension_type,
        partName: firstResult.part_name,
        testDate: firstResult.test_date,
        testLocation: firstResult.test_location,
        testEngineer: firstResult.test_engineer,
        analysisEngineer: firstResult.analysis_engineer,
        testPhotoList
      }
    }
  },

  actions: {
    /**
     * 初始化页面数据
     */
    async initializePageData() {
      await this.loadVehicleModels()
    },

    /**
     * 加载车型列表
     */
    async loadVehicleModels() {
      this.vehicleModelsLoading = true
      try {
        const response = await modalApi.getVehicleModels()
        if (response.success) {
          this.vehicleModelOptions = response.data || []
        } else {
          throw new Error(response.message || '获取车型列表失败')
        }
      } catch (error) {
        console.error('加载车型列表失败:', error)
        throw error
      } finally {
        this.vehicleModelsLoading = false
      }
    },

    /**
     * 处理车型变化
     */
    async handleVehicleModelChange(vehicleModelId) {
      this.searchForm.vehicleModelId = vehicleModelId
      
      // 重置下级选项
      this.searchForm.partName = null
      this.searchForm.subsystem = []
      this.searchForm.testPoints = []
      this.partNameOptions = []
      this.subsystemOptions = []
      this.testPointOptions = []
      
      // 清空查询结果
      this.queryResult = { count: 0, results: [] }
      
      if (vehicleModelId) {
        await this.loadPartNames(vehicleModelId)
      }
    },

    /**
     * 加载零件名称列表
     */
    async loadPartNames(vehicleModelId) {
      this.partNamesLoading = true
      try {
        const response = await dynamicStiffnessApi.getPartNames(vehicleModelId)
        if (response.success) {
          this.partNameOptions = response.data || []
        } else {
          throw new Error(response.message || '获取零件名称列表失败')
        }
      } catch (error) {
        console.error('加载零件名称列表失败:', error)
        throw error
      } finally {
        this.partNamesLoading = false
      }
    },

    /**
     * 处理零件名称变化
     */
    async handlePartNameChange(partName) {
      this.searchForm.partName = partName
      
      // 重置下级选项
      this.searchForm.subsystem = []
      this.searchForm.testPoints = []
      this.subsystemOptions = []
      this.testPointOptions = []
      
      if (partName && this.searchForm.vehicleModelId) {
        await this.loadSubsystems(this.searchForm.vehicleModelId, partName)
      }
    },

    /**
     * 加载子系统列表
     */
    async loadSubsystems(vehicleModelId, partName) {
      this.subsystemsLoading = true
      try {
        const response = await dynamicStiffnessApi.getSubsystems(vehicleModelId, partName)
        if (response.success) {
          this.subsystemOptions = response.data || []
        } else {
          throw new Error(response.message || '获取子系统列表失败')
        }
      } catch (error) {
        console.error('加载子系统列表失败:', error)
        throw error
      } finally {
        this.subsystemsLoading = false
      }
    },

    /**
     * 处理子系统变化
     */
    async handleSubsystemChange(subsystem) {
      this.searchForm.subsystem = Array.isArray(subsystem) ? subsystem : (subsystem ? [subsystem] : [])
      
      // 重置下级选项
      this.searchForm.testPoints = []
      this.testPointOptions = []
      
      if (this.searchForm.vehicleModelId && this.searchForm.partName) {
        // 如果选择了多个子系统，则忽略子系统过滤，加载车型+零件下的所有测点
        let subsystemParam
        if (Array.isArray(this.searchForm.subsystem) && this.searchForm.subsystem.length === 1) {
          subsystemParam = this.searchForm.subsystem[0]
        }
        await this.loadTestPoints(this.searchForm.vehicleModelId, this.searchForm.partName, subsystemParam)
      }
    },

    /**
     * 加载测点列表
     */
    async loadTestPoints(vehicleModelId, partName, subsystem) {
      this.testPointsLoading = true
      try {
        const response = await dynamicStiffnessApi.getTestPoints(vehicleModelId, partName, subsystem)
        if (response.success) {
          this.testPointOptions = response.data || []
          // 默认选择所有测点
          this.searchForm.testPoints = this.testPointOptions.map(option => option.value)
        } else {
          throw new Error(response.message || '获取测点列表失败')
        }
      } catch (error) {
        console.error('加载测点列表失败:', error)
        throw error
      } finally {
        this.testPointsLoading = false
      }
    },

    /**
     * 查询动刚度数据
     */
    async queryData() {
      if (!this.canQuery) {
        throw new Error('请先选择车型')
      }

      this.loading = true
      try {
        const response = await dynamicStiffnessApi.queryData({
          vehicleModelId: this.searchForm.vehicleModelId,
          partName: this.searchForm.partName,
          subsystem: this.searchForm.subsystem,
          testPoints: this.searchForm.testPoints
        })

        if (response.success) {
          this.queryResult = response.data || { count: 0, results: [] }
        } else {
          throw new Error(response.message || '查询动刚度数据失败')
        }
      } catch (error) {
        console.error('查询动刚度数据失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 重置查询条件
     */
    resetSearchForm() {
      this.searchForm = {
        vehicleModelId: null,
        partName: null,
        subsystem: [],
        testPoints: []
      }
      
      this.partNameOptions = []
      this.subsystemOptions = []
      this.testPointOptions = []
      this.queryResult = { count: 0, results: [] }
    }
  }
})
