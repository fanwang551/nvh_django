import request from '@/utils/request'

/**
 * NVH 试验任务管理 API
 */
export const nvhTaskApi = {
  // ==================== MainRecord ====================

  /**
   * 获取主记录列表
   * @param {Object} params 筛选参数
   */
  listMainRecords(params = {}) {
    return request.get('/nvh-task/main-records/', params)
  },

  /**
   * 获取主记录详情
   * @param {number} id
   */
  getMainRecord(id) {
    return request.get(`/nvh-task/main-records/${id}/`)
  },

  /**
   * 创建主记录
   * @param {Object} data
   */
  createMainRecord(data) {
    return request.post('/nvh-task/main-records/', data)
  },

  /**
   * 更新主记录
   * @param {number} id
   * @param {Object} data
   */
  updateMainRecord(id, data) {
    return request.patch(`/nvh-task/main-records/${id}/`, data)
  },

  /**
   * 删除主记录（软删除）
   * @param {number} id
   */
  deleteMainRecord(id) {
    return request.delete(`/nvh-task/main-records/${id}/`)
  },

  // ==================== EntryExit ====================

  /**
   * 获取进出登记列表
   * @param {Object} params
   */
  listEntryExits(params = {}) {
    return request.get('/nvh-task/entry-exits/', params)
  },

  /**
   * 获取进出登记详情
   * @param {number} id
   */
  getEntryExit(id) {
    return request.get(`/nvh-task/entry-exits/${id}/`)
  },

  /**
   * 创建进出登记
   * @param {Object} data
   */
  createEntryExit(data) {
    return request.post('/nvh-task/entry-exits/', data)
  },

  /**
   * 更新进出登记
   * @param {number} id
   * @param {Object} data
   */
  updateEntryExit(id, data) {
    return request.patch(`/nvh-task/entry-exits/${id}/`, data)
  },

  /**
   * 删除进出登记（软删除）
   * @param {number} id
   */
  deleteEntryExit(id) {
    return request.delete(`/nvh-task/entry-exits/${id}/`)
  },

  /**
   * 提交进出登记
   * @param {number} id
   */
  submitEntryExit(id) {
    return request.post(`/nvh-task/entry-exits/${id}/submit/`)
  },

  /**
   * 撤回进出登记
   * @param {number} id
   */
  unsubmitEntryExit(id) {
    return request.post(`/nvh-task/entry-exits/${id}/unsubmit/`)
  },

  // ==================== TestInfo ====================

  /**
   * 获取或创建试验信息（get_or_create）
   * @param {number} mainId 主记录ID
   */
  getTestInfo(mainId) {
    return request.get(`/nvh-task/main-records/${mainId}/test-info/`)
  },

  /**
   * 更新试验信息
   * @param {number} mainId 主记录ID
   * @param {Object} data
   */
  updateTestInfo(mainId, data) {
    return request.patch(`/nvh-task/main-records/${mainId}/test-info/`, data)
  },

  /**
   * 提交试验信息
   * @param {number} id TestInfo ID
   */
  submitTestInfo(id) {
    return request.post(`/nvh-task/test-infos/${id}/submit/`)
  },

  /**
   * 撤回试验信息
   * @param {number} id TestInfo ID
   */
  unsubmitTestInfo(id) {
    return request.post(`/nvh-task/test-infos/${id}/unsubmit/`)
  },

  // ==================== DocApproval ====================

  /**
   * 获取或创建技术资料发放批准单（get_or_create）
   * @param {number} mainId 主记录ID
   */
  getDocApproval(mainId) {
    return request.get(`/nvh-task/main-records/${mainId}/doc-approval/`)
  },

  /**
   * 更新技术资料发放批准单
   * @param {number} mainId 主记录ID
   * @param {Object} data
   */
  updateDocApproval(mainId, data) {
    return request.patch(`/nvh-task/main-records/${mainId}/doc-approval/`, data)
  },

  /**
   * 提交技术资料发放批准单
   * @param {number} id DocApproval ID
   */
  submitDocApproval(id) {
    return request.post(`/nvh-task/doc-approvals/${id}/submit/`)
  },

  /**
   * 撤回技术资料发放批准单
   * @param {number} id DocApproval ID
   */
  unsubmitDocApproval(id) {
    return request.post(`/nvh-task/doc-approvals/${id}/unsubmit/`)
  },

  // ==================== TestProcessAttachment ====================

  /**
   * 获取过程记录附件列表
   * @param {number} testInfoId
   */
  listProcessAttachments(testInfoId) {
    return request.get('/nvh-task/process-attachments/', { test_info_id: testInfoId })
  },

  /**
   * 创建过程记录附件
   * @param {Object} data
   */
  createProcessAttachment(data) {
    return request.post('/nvh-task/process-attachments/', data)
  },

  /**
   * 更新过程记录附件
   * @param {number} id
   * @param {Object} data
   */
  updateProcessAttachment(id, data) {
    return request.patch(`/nvh-task/process-attachments/${id}/`, data)
  },

  /**
   * 删除过程记录附件（软删除）
   * @param {number} id
   */
  deleteProcessAttachment(id) {
    return request.delete(`/nvh-task/process-attachments/${id}/`)
  },

  // ==================== TestProcessList ====================

  /**
   * 获取过程记录表名选项列表
   */
  listProcessOptions() {
    return request.get('/nvh-task/process-list-options/')
  },

  /**
   * 创建过程记录表名（输入即新增）
   * @param {Object} data
   */
  createProcessOption(data) {
    return request.post('/nvh-task/process-list-options/', data)
  }
}

export default nvhTaskApi
