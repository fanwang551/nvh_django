// 非 pinia 轻量 store：经验数据检索
// 负责集中管理过滤条件、分页与列表加载逻辑，供页面直接引用

import { reactive, ref } from 'vue'
import { experienceApi } from '@/api/experience'

// 状态
export const filters = reactive({ q: '', category: '' })
export const page = ref(1)
export const pageSize = ref(20)
export const total = ref(0)
export const items = ref([])
export const categoryOptions = ref([])

// 行为
export async function loadList() {
  const params = {
    q: filters.q?.trim() || '',
    category: filters.category || '',
    page: page.value,
    page_size: pageSize.value
  }
  const res = await experienceApi.list(params)
  const { data } = res || {}
  items.value = data?.items || []
  total.value = data?.total || 0
  page.value = data?.page || 1
  pageSize.value = data?.page_size || 20

  // 从当前数据提取分类选项（临时方案）
  const cats = new Set(categoryOptions.value)
  for (const it of items.value) {
    if (it.category) cats.add(it.category)
  }
  categoryOptions.value = Array.from(cats)
}

export function setQuery(q) {
  filters.q = q || ''
}

export function setCategory(category) {
  filters.category = category || ''
}

export function resetFilters() {
  filters.q = ''
  filters.category = ''
  page.value = 1
  pageSize.value = 20
}

