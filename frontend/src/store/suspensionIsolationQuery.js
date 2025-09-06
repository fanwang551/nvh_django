import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import modalApi from '@/api/modal'
import { getSuspensionMeasuringPoints, querySuspensionIsolationData } from '@/api/suspensionIsolation'

/**
 * 悬架隔振率查询状态管理
 * 遵循项目Pinia规范：只保存数据状态，不保存DOM相关对象
 */
export const useSuspensionIsolationQueryStore = defineStore('suspensionIsolationQuery', () => {
  // ==================== 状态数据 ====================
  
  // 查询表单状态
  const searchForm = ref({
    vehicleModelId: null,
    measuringPoints: [] // 测点多选
  })

  // 车型选项
  const vehicleModelOptions = ref([])
  const vehicleModelsLoading = ref(false)

  // 测点选项
  const measuringPointOptions = ref([])
  const measuringPointsLoading = ref(false)

  // 查询结果
  const queryResult = ref({
    count: 0,
    results: []
  })
  
  // 基本信息
  const basicInfo = ref(null)

  // 加载状态
  const loading = ref(false)

  // ==================== 计算属性 ====================
  
  // 是否可以查询：车型必选
  const canQuery = computed(() => {
    return searchForm.value.vehicleModelId !== null
  })

  // 是否有查询结果
  const hasResults = computed(() => {
    return queryResult.value.results.length > 0
  })

  // ==================== 方法 ====================
  
  /**
   * 初始化：加载车型列表
   */
  async function initialize() {
    await loadVehicleModels()
  }

  /**
   * 加载车型列表
   */
  async function loadVehicleModels() {
    vehicleModelsLoading.value = true
    try {
      const response = await modalApi.getVehicleModels()
      if (response.success) {
        vehicleModelOptions.value = response.data
      }
    } finally {
      vehicleModelsLoading.value = false
    }
  }

  /**
   * 加载测点列表
   * @param {number} vehicleModelId - 车型ID
   */
  async function loadMeasuringPoints(vehicleModelId) {
    console.log('开始加载测点列表，车型ID:', vehicleModelId)
    measuringPointsLoading.value = true
    try {
      const response = await getSuspensionMeasuringPoints({ vehicle_model_id: vehicleModelId })
      console.log('测点列表API响应:', response)
      if (response.success) {
        measuringPointOptions.value = response.data
        console.log('测点列表加载成功，数量:', response.data.length)
      } else {
        throw new Error(response.message || '获取测点列表失败')
      }
    } catch (error) {
      console.error('加载测点列表失败:', error)
      measuringPointOptions.value = []
      throw error
    } finally {
      measuringPointsLoading.value = false
      console.log('测点列表加载完成，最终状态:', {
        loading: measuringPointsLoading.value,
        optionsCount: measuringPointOptions.value.length
      })
    }
  }

  /**
   * 执行查询
   */
  async function queryData() {
    if (!canQuery.value) {
      throw new Error('查询条件不完整')
    }

    loading.value = true
    try {
      const params = {
        vehicle_model_id: searchForm.value.vehicleModelId
      }

      // 添加测点筛选条件
      if (searchForm.value.measuringPoints.length > 0) {
        params.measuring_points = searchForm.value.measuringPoints.join(',')
      }

      const response = await querySuspensionIsolationData(params)
      if (response.success) {
        queryResult.value = {
          count: response.data.count,
          results: response.data.results
        }

        // 提取基本信息（从第一条记录中获取）
        if (response.data.results.length > 0) {
          const firstResult = response.data.results[0]
          basicInfo.value = {
            vehicleModelName: firstResult.vehicle_model_name,
            testDate: firstResult.test_date,
            testLocation: firstResult.test_location,
            testEngineer: firstResult.test_engineer,
            suspensionType: firstResult.suspension_type,
            tirePressure: firstResult.tire_pressure,
            testCondition: firstResult.test_condition
          }
        } else {
          basicInfo.value = null
        }
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置车型ID
   * @param {number} value - 车型ID
   */
  function setVehicleModelId(value) {
    searchForm.value.vehicleModelId = value
    // 清空之前的测点选择
    searchForm.value.measuringPoints = []
    // 清空查询结果
    clearResults()
  }

  /**
   * 设置测点
   * @param {Array} points - 测点数组
   */
  function setMeasuringPoints(points) {
    searchForm.value.measuringPoints = points
  }

  /**
   * 重置搜索表单
   */
  function resetSearchForm() {
    searchForm.value = {
      vehicleModelId: null,
      measuringPoints: []
    }
    measuringPointOptions.value = []
    clearResults()
  }

  /**
   * 清空查询结果
   */
  function clearResults() {
    queryResult.value = {
      count: 0,
      results: []
    }
    basicInfo.value = null
  }

  // ==================== 返回状态和方法 ====================
  
  return {
    // 状态
    searchForm,
    vehicleModelOptions,
    vehicleModelsLoading,
    measuringPointOptions,
    measuringPointsLoading,
    queryResult,
    basicInfo,
    loading,
    
    // 计算属性
    canQuery,
    hasResults,
    
    // 方法
    initialize,
    loadVehicleModels,
    loadMeasuringPoints,
    queryData,
    setVehicleModelId,
    setMeasuringPoints,
    resetSearchForm,
    clearResults
  }
})