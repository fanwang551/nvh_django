/**
 * 动刚度查询相关API
 */
import request from '@/utils/request'

const dynamicStiffnessApi = {
  /**
   * 获取零件名称列表
   * @param {number} vehicleModelId - 车型ID
   * @returns {Promise}
   */
  getPartNames(vehicleModelId) {
    return request.get('/dynamic-stiffness/part-names/', {
      vehicle_model_id: vehicleModelId
    })
  },

  /**
   * 获取子系统列表
   * @param {number} vehicleModelId - 车型ID
   * @param {string} partName - 零件名称
   * @returns {Promise}
   */
  getSubsystems(vehicleModelId, partName) {
    return request.get('/dynamic-stiffness/subsystems/', {
      vehicle_model_id: vehicleModelId,
      part_name: partName
    })
  },

  /**
   * 获取测点列表
   * @param {number} vehicleModelId - 车型ID
   * @param {string} partName - 零件名称
   * @param {string} subsystem - 子系统
   * @returns {Promise}
   */
  getTestPoints(vehicleModelId, partName, subsystem) {
    return request.get('/dynamic-stiffness/test-points/', {
      vehicle_model_id: vehicleModelId,
      part_name: partName,
      subsystem: subsystem
    })
  },

  /**
   * 查询动刚度数据
   * @param {Object} params - 查询参数
   * @param {number} params.vehicleModelId - 车型ID
   * @param {string} params.partName - 零件名称
   * @param {string} params.subsystem - 子系统
   * @param {Array} params.testPoints - 测点列表
   * @returns {Promise}
   */
  queryData(params) {
    const requestParams = {
      vehicle_model_id: params.vehicleModelId
    }

    if (params.partName) {
      requestParams.part_name = params.partName
    }

    if (params.subsystem) {
      requestParams.subsystem = params.subsystem
    }

    if (params.testPoints && params.testPoints.length > 0) {
      requestParams.test_points = params.testPoints.join(',')
    }

    return request.get('/dynamic-stiffness/data/', requestParams)
  }
}

export default dynamicStiffnessApi
