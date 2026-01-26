/**
 * NVH 试验任务管理 Store
 * 管理：列表查询、分页、筛选、抽屉状态、三表单数据、闭环提示条
 */
import { defineStore } from 'pinia'
import { nvhTaskApi } from '@/api/nvhTask'
import { userApi } from '@/api/user'
import { useUserStore } from '@/store/index'

export const useTaskStore = defineStore('nvhTask', {
  state: () => ({
    // ==================== 列表相关 ====================
    list: {
      items: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false
    },

    // 筛选条件
    filters: {
      model: '',
      vin_or_part_no: '',
      test_name: '',
      warning_system_status: '',
      requester_name: '',
      tester_name: '',
      is_closed: '',
      schedule_start_from: '',
      schedule_start_to: '',
      entry_exit_dispose_type: '',
      has_contract_no: '',
      report_required: '',
      week_closure_filter: '' // 本周闭环筛选：'closed' | 'unclosed' | ''
    },

    // ==================== 统计数据 ====================
    statistics: {
      total_tasks: 0,
      month_tasks: 0,
      week_tasks: 0,
      week_closed: 0,
      week_unclosed: 0,
      loading: false
    },

    // ==================== 抽屉相关 ====================
    drawer: {
      visible: false,
      currentMainId: null,
      currentMain: null,
      activeTab: 'entryExit',
      loading: false
    },

    // ==================== 三表单数据 ====================
    entryExit: {
      data: null,
      loading: false,
      dirty: false
    },

    testInfo: {
      data: null,
      loading: false,
      dirty: false
    },

    docApproval: {
      data: null,
      loading: false,
      dirty: false
    },

    // ==================== 进出登记选择 ====================
    entryExitList: {
      items: [],
      loading: false
    },

    // ==================== 进出登记记录管理 ====================
    entryExitRecords: {
      items: [],
      total: 0,
      page: 1,
      pageSize: 10,
      loading: false
    },

    // ==================== 过程记录表名选项 ====================
    processOptions: [],

    // ==================== 用户信息 ====================
    currentUsername: '',
    currentFullname: '',
    currentGroupNames: [],
    hasSchedulerWhitelist: false,
    schedulerPermissionLoading: false
  }),

  getters: {
    // 是否为安排人员（可编辑）
    isScheduler: (state) => {
      return !!state.hasSchedulerWhitelist
    },

    // 闭环提示条数据
    closureStatus: (state) => {
      const main = state.drawer.currentMain
      const entryExit = state.entryExit.data
      const testInfo = state.testInfo.data
      const docApproval = state.docApproval.data

      const status = {
        entryExit: { exists: false, submitted: false },
        testInfo: { exists: false, submitted: false, teardownOk: true, processOk: true },
        docApproval: { exists: false, submitted: false, fileOk: true },
        missingItems: []
      }

      // EntryExit 状态
      if (main?.entry_exit || entryExit) {
        status.entryExit.exists = true
        status.entryExit.submitted = (entryExit?.status || main?.entry_exit_status) === 'SUBMITTED'
      }
      if (!status.entryExit.exists) {
        status.missingItems.push({ tab: 'entryExit', field: 'bind', message: '未绑定进出登记' })
      } else if (!status.entryExit.submitted) {
        status.missingItems.push({ tab: 'entryExit', field: 'submit', message: '进出登记未提交' })
      }

      // TestInfo 状态
      if (testInfo) {
        status.testInfo.exists = true
        status.testInfo.submitted = testInfo.status === 'SUBMITTED'

        if (testInfo.include_teardown_record === '是' && !testInfo.teardown_attachment_url) {
          status.testInfo.teardownOk = false
          status.missingItems.push({ tab: 'testInfo', field: 'teardown_attachment_url', message: '缺少拆装记录表图片' })
        }
        if (testInfo.include_process_record === '是' && (testInfo.process_attachment_count || 0) < 1) {
          status.testInfo.processOk = false
          status.missingItems.push({ tab: 'testInfo', field: 'process_attachments', message: '缺少试验过程记录表图片（至少1张）' })
        }
        if (!status.testInfo.submitted && status.testInfo.teardownOk && status.testInfo.processOk) {
          status.missingItems.push({ tab: 'testInfo', field: 'submit', message: '试验信息未提交' })
        }
      } else {
        status.missingItems.push({ tab: 'testInfo', field: 'create', message: '未填写试验信息' })
      }

      // DocApproval 状态
      if (docApproval) {
        status.docApproval.exists = true
        status.docApproval.submitted = docApproval.status === 'SUBMITTED'

        if (!docApproval.file_url) {
          status.docApproval.fileOk = false
          status.missingItems.push({ tab: 'docApproval', field: 'file_url', message: '缺少技术资料发放批准单文件' })
        }
        if (!status.docApproval.submitted && status.docApproval.fileOk) {
          status.missingItems.push({ tab: 'docApproval', field: 'submit', message: '技术资料发放批准单未提交' })
        }
      } else {
        status.missingItems.push({ tab: 'docApproval', field: 'create', message: '未填写技术资料发放批准单' })
      }

      return status
    },

    // 是否已闭环
    isClosed: (state) => {
      return state.drawer.currentMain?.is_closed || false
    }
  },

  actions: {
    // ==================== 初始化 ====================

    initUserInfo() {
      const userStore = useUserStore()
      this.currentUsername = userStore.username || ''
      this.currentFullname = userStore.fullName || ''
      this.loadSchedulerPermission()
    },

    async loadSchedulerPermission() {
      if (this.schedulerPermissionLoading) return
      this.schedulerPermissionLoading = true
      try {
        const res = await userApi.getUserGroups()
        const groupNames = res?.group_names || []
        const hasFlag = res?.permissions?.has_scheduler_whitelist
        this.currentGroupNames = groupNames
        this.hasSchedulerWhitelist = typeof hasFlag === 'boolean' ? hasFlag : groupNames.includes('NVH组组长')
      } catch (e) {
        this.currentGroupNames = []
        this.hasSchedulerWhitelist = false
      } finally {
        this.schedulerPermissionLoading = false
      }
    },

    // ==================== 列表操作 ====================

    async loadList() {
      this.list.loading = true
      try {
        const params = {
          page: this.list.page,
          page_size: this.list.pageSize,
          ...this.getActiveFilters()
        }
        const res = await nvhTaskApi.listMainRecords(params)
        const data = res?.data || {}
        this.list.items = data.items || []
        this.list.total = data.total || 0
        this.list.page = data.page || 1
        this.list.pageSize = data.page_size || 20
        
        // 加载列表后刷新统计数据
        this.loadStatistics()
      } finally {
        this.list.loading = false
      }
    },

    getActiveFilters() {
      const result = {}
      Object.entries(this.filters).forEach(([key, value]) => {
        // 排除 week_closure_filter，这是前端内部使用的标识
        if (key === 'week_closure_filter') return
        
        if (value !== '' && value !== null && value !== undefined) {
          result[key] = value
        }
      })
      return result
    },

    setFilter(key, value) {
      if (key in this.filters) {
        this.filters[key] = value
      }
    },

    resetFilters() {
      Object.keys(this.filters).forEach(key => {
        this.filters[key] = ''
      })
      this.list.page = 1
    },

    setPage(page) {
      this.list.page = page
    },

    setPageSize(size) {
      this.list.pageSize = size
      this.list.page = 1
    },

    // ==================== 主记录 CRUD ====================

    async createMainRecord(data) {
      const payload = {
        ...data,
        task_scenario: data.task_scenario || 'NORMAL',
        doc_requirement: data.doc_requirement !== undefined ? data.doc_requirement : false
      }
      const res = await nvhTaskApi.createMainRecord(payload)
      await this.loadList()
      return res
    },

    async updateMainRecord(id, data) {
      const res = await nvhTaskApi.updateMainRecord(id, data)
      await this.loadList()
      // 如果更新了当前抽屉中的主记录，刷新抽屉数据
      if (this.drawer.currentMainId === id) {
        await this.refreshMainRecord()
      }
      return res
    },

    async deleteMainRecord(id) {
      const res = await nvhTaskApi.deleteMainRecord(id)
      await this.loadList()
      return res
    },

    // ==================== 抽屉操作 ====================

    async openDrawer(mainId) {
      this.drawer.visible = true
      this.drawer.currentMainId = mainId
      this.drawer.loading = true

      // 重置表单数据
      this.entryExit.data = null
      this.entryExit.dirty = false
      this.testInfo.data = null
      this.testInfo.dirty = false
      this.docApproval.data = null
      this.docApproval.dirty = false

      try {
        // 加载主记录详情
        const res = await nvhTaskApi.getMainRecord(mainId)
        this.drawer.currentMain = res?.data || null

        // 根据闭环状态决定默认 Tab
        const closureStatus = this.closureStatus
        if (closureStatus.missingItems.length > 0) {
          this.drawer.activeTab = closureStatus.missingItems[0].tab
        } else {
          this.drawer.activeTab = 'testInfo'
        }
      } finally {
        this.drawer.loading = false
      }
    },

    closeDrawer() {
      this.drawer.visible = false
      this.drawer.currentMainId = null
      this.drawer.currentMain = null
    },

    setActiveTab(tab) {
      this.drawer.activeTab = tab
    },

    // ==================== EntryExit 操作 ====================

    async loadEntryExit() {
      const mainId = this.drawer.currentMainId
      const main = this.drawer.currentMain
      if (!main?.entry_exit) {
        this.entryExit.data = null
        return
      }

      this.entryExit.loading = true
      try {
        const res = await nvhTaskApi.getEntryExit(main.entry_exit.id)
        this.entryExit.data = res?.data || null
      } finally {
        this.entryExit.loading = false
      }
    },

    async loadEntryExitList() {
      this.entryExitList.loading = true
      try {
        const res = await nvhTaskApi.listEntryExits({ page_size: 100, dispose_type: '使用中' })
        this.entryExitList.items = res?.data?.items || []
      } finally {
        this.entryExitList.loading = false
      }
    },

    async createEntryExit(data) {
      const res = await nvhTaskApi.createEntryExit(data)
      return res?.data
    },

    async updateEntryExit(id, data) {
      const res = await nvhTaskApi.updateEntryExit(id, data)
      this.entryExit.data = res?.data || null
      this.entryExit.dirty = false
      return res
    },

    async bindEntryExit(entryExitId) {
      const mainId = this.drawer.currentMainId
      await nvhTaskApi.updateMainRecord(mainId, { entry_exit_id: entryExitId })
      // 重新加载主记录和进出登记
      const res = await nvhTaskApi.getMainRecord(mainId)
      this.drawer.currentMain = res?.data || null
      await this.loadEntryExit()
      await this.loadList()
    },

    async unbindEntryExit() {
      const mainId = this.drawer.currentMainId
      await nvhTaskApi.updateMainRecord(mainId, { entry_exit_id: null })
      const res = await nvhTaskApi.getMainRecord(mainId)
      this.drawer.currentMain = res?.data || null
      this.entryExit.data = null
      await this.loadList()
    },

    async submitEntryExit() {
      const id = this.entryExit.data?.id
      if (!id) return
      const res = await nvhTaskApi.submitEntryExit(id)
      this.entryExit.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    async unsubmitEntryExit() {
      const id = this.entryExit.data?.id
      if (!id) return
      const res = await nvhTaskApi.unsubmitEntryExit(id)
      this.entryExit.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    // ==================== 进出登记记录管理 ====================

    async loadEntryExitRecords(page = 1) {
      this.entryExitRecords.loading = true
      this.entryExitRecords.page = page
      try {
        const res = await nvhTaskApi.listAllEntryExits({
          page: this.entryExitRecords.page,
          page_size: this.entryExitRecords.pageSize
        })
        const data = res?.data || {}
        this.entryExitRecords.items = data.items || []
        this.entryExitRecords.total = data.total || 0
      } finally {
        this.entryExitRecords.loading = false
      }
    },

    async deleteEntryExitRecord(id) {
      await nvhTaskApi.deleteEntryExit(id)
      // 刷新记录列表
      await this.loadEntryExitRecords(this.entryExitRecords.page)
      // 如果当前抽屉中的进出登记被删除，刷新抽屉数据
      if (this.entryExit.data?.id === id) {
        await this.refreshMainRecord()
        await this.loadEntryExit()
      }
      // 刷新主列表
      await this.loadList()
    },

    // ==================== TestInfo 操作 ====================

    async loadTestInfo() {
      const mainId = this.drawer.currentMainId
      if (!mainId) return

      this.testInfo.loading = true
      try {
        const res = await nvhTaskApi.getTestInfo(mainId)
        this.testInfo.data = res?.data || null
      } finally {
        this.testInfo.loading = false
      }
    },

    async updateTestInfo(data) {
      const mainId = this.drawer.currentMainId
      if (!mainId) return
      const res = await nvhTaskApi.updateTestInfo(mainId, data)
      this.testInfo.data = res?.data || null
      this.testInfo.dirty = false
      return res
    },

    async submitTestInfo() {
      const id = this.testInfo.data?.id
      if (!id) return
      const res = await nvhTaskApi.submitTestInfo(id)
      this.testInfo.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    async unsubmitTestInfo() {
      const id = this.testInfo.data?.id
      if (!id) return
      const res = await nvhTaskApi.unsubmitTestInfo(id)
      this.testInfo.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    // ==================== DocApproval 操作 ====================

    async loadDocApproval() {
      const mainId = this.drawer.currentMainId
      if (!mainId) return

      this.docApproval.loading = true
      try {
        const res = await nvhTaskApi.getDocApproval(mainId)
        this.docApproval.data = res?.data || null
      } finally {
        this.docApproval.loading = false
      }
    },

    async updateDocApproval(data) {
      const mainId = this.drawer.currentMainId
      if (!mainId) return
      const res = await nvhTaskApi.updateDocApproval(mainId, data)
      this.docApproval.data = res?.data || null
      this.docApproval.dirty = false
      return res
    },

    async submitDocApproval() {
      const id = this.docApproval.data?.id
      if (!id) return
      const res = await nvhTaskApi.submitDocApproval(id)
      this.docApproval.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    async unsubmitDocApproval() {
      const id = this.docApproval.data?.id
      if (!id) return
      const res = await nvhTaskApi.unsubmitDocApproval(id)
      this.docApproval.data = res?.data || null
      await this.refreshMainRecord()
      await this.loadList()
      return res
    },

    // ==================== 过程记录附件操作 ====================

    async loadProcessAttachments() {
      const testInfoId = this.testInfo.data?.id
      if (!testInfoId) return []
      const res = await nvhTaskApi.listProcessAttachments(testInfoId)
      return res?.data || []
    },

    async createProcessAttachment(data) {
      const res = await nvhTaskApi.createProcessAttachment(data)
      const created = res?.data || null
      if (created && this.testInfo.data && created.test_info === this.testInfo.data.id) {
        this.testInfo.data.process_attachment_count = (this.testInfo.data.process_attachment_count || 0) + 1
      }
      return created
    },

    async updateProcessAttachment(id, data) {
      const res = await nvhTaskApi.updateProcessAttachment(id, data)
      return res?.data
    },

    async deleteProcessAttachment(id) {
      await nvhTaskApi.deleteProcessAttachment(id)
      if (this.testInfo.data) {
        const current = this.testInfo.data.process_attachment_count || 0
        this.testInfo.data.process_attachment_count = Math.max(0, current - 1)
      }
    },

    // ==================== 过程记录表名选项 ====================

    async loadProcessOptions() {
      const res = await nvhTaskApi.listProcessOptions()
      this.processOptions = res?.data || []
    },

    async createProcessOption(name) {
      const res = await nvhTaskApi.createProcessOption({ test_process_name: name })
      await this.loadProcessOptions()
      return res?.data
    },

    // ==================== 辅助方法 ====================

    async refreshMainRecord() {
      const mainId = this.drawer.currentMainId
      if (!mainId) return
      const res = await nvhTaskApi.getMainRecord(mainId)
      this.drawer.currentMain = res?.data || null
    },

    // 定位到缺项
    locateMissingItem(item) {
      if (item?.tab) {
        this.drawer.activeTab = item.tab
      }
      // 返回 field 供组件滚动定位
      return item?.field
    },

    // ==================== 导出 Excel ====================

    async exportToExcel() {
      const params = this.getActiveFilters()
      const res = await nvhTaskApi.exportMainRecords(params)
      return res
    },

    // ==================== 获取上次填写数据 ====================

    async getLastMainRecord() {
      const res = await nvhTaskApi.getLastMainRecord()
      return res?.data || null
    },

    // ==================== 统计数据 ====================

    async loadStatistics() {
      this.statistics.loading = true
      try {
        const res = await nvhTaskApi.getTaskStatistics()
        const data = res?.data || {}
        this.statistics.total_tasks = data.total_tasks || 0
        this.statistics.month_tasks = data.month_tasks || 0
        this.statistics.week_tasks = data.week_tasks || 0
        this.statistics.week_closed = data.week_closed || 0
        this.statistics.week_unclosed = data.week_unclosed || 0
      } catch (e) {
        console.error('加载统计数据失败:', e)
      } finally {
        this.statistics.loading = false
      }
    }
  }
})

export default useTaskStore
