import { defineStore } from 'pinia'
import { materialPorosityApi } from '@/api/materialPorosity'

export const useMaterialPorosityQueryStore = defineStore('materialPorosityQuery', {
    state: () => ({
        // 查询条件
        searchCriteria: {
            partNames: []
        },

        // 业务数据
        partNameOptions: [],
        queryResults: [],

        // 业务状态
        isLoading: false,
        error: null,
        partNamesLoading: false,
        queryLoading: false,
    }),

    getters: {
        // 业务验证：是否可以查询
        canQuery: (state) => {
            return state.partNameOptions.length > 0
        },

        // 业务状态：是否有查询结果
        hasResults: (state) => {
            return state.queryResults.length > 0
        },

        // 计算属性：选中的零件数量
        selectedPartCount: (state) => {
            return state.searchCriteria.partNames.length
        },

        // 业务状态：是否正在加载
        isLoadingAny: (state) => {
            return state.isLoading || state.partNamesLoading || state.queryLoading
        }
    },

    actions: {
        // API调用：加载零件名称选项
        async fetchPartNameOptions() {
            try {
                this.partNamesLoading = true
                this.error = null

                const response = await materialPorosityApi.getPartNameOptions()
                this.partNameOptions = response.data || []

                return this.partNameOptions
            } catch (error) {
                this.error = '加载零件名称选项失败'
                console.error('加载零件名称选项失败:', error)
                throw error
            } finally {
                this.partNamesLoading = false
            }
        },

        // API调用：执行查询
        async executeQuery() {
            try {
                this.queryLoading = true
                this.error = null

                const params = {}
                if (this.searchCriteria.partNames.length > 0) {
                    params.part_names = this.searchCriteria.partNames.join(',')
                }

                const response = await materialPorosityApi.queryMaterialPorosity(params)
                this.queryResults = response.data || []

                return this.queryResults
            } catch (error) {
                this.error = '查询材料孔隙率流阻数据失败'
                console.error('查询材料孔隙率流阻数据失败:', error)
                throw error
            } finally {
                this.queryLoading = false
            }
        },

        // 业务逻辑：设置查询条件
        setSearchCriteria(criteria) {
            this.searchCriteria = { ...this.searchCriteria, ...criteria }
        },

        // 业务逻辑：设置零件名称选择
        setPartNames(partNames) {
            this.searchCriteria.partNames = partNames
        },

        // 业务逻辑：清除错误状态
        clearError() {
            this.error = null
        },

        // 业务逻辑：重置所有状态
        resetState() {
            this.searchCriteria = {
                partNames: []
            }
            this.queryResults = []
            this.error = null
        },

        // 业务逻辑：初始化数据
        async initializeData() {
            if (this.partNameOptions.length === 0) {
                await this.fetchPartNameOptions()
            }
        }
    }
})
