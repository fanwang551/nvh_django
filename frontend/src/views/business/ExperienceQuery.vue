<template>
  <div class="experience">
    <div class="header">
      <div class="title">经验数据库</div>
      <div class="actions">
        <el-button type="primary" @click="handleCreate" plain>新增经验</el-button>
        <el-button disabled title="未开通导出">导出</el-button>
        <el-button @click="handleSettings">设置</el-button>
      </div>
    </div>

    <div class="search-bar">
      <el-input
        v-model="filters.q"
        placeholder="🔍 输入关键字搜索..."
        clearable
        @keyup.enter.native="handleSearch"
      />
      <el-select
        v-model="filters.category"
        placeholder="分类筛选"
        clearable
        filterable
        allow-create
        default-first-option
      >
        <el-option
          v-for="c in categoryOptions"
          :key="c"
          :label="c"
          :value="c"
        />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <div class="meta">共找到 {{ total }} 条记录</div>

    <el-table :data="items" border stripe class="table">
      <el-table-column prop="id" label="ID" width="90" />
      <el-table-column prop="category" label="问题分类" width="160" />
      <el-table-column prop="problem_name" label="问题名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="keywords" label="问题关键字" min-width="220" show-overflow-tooltip />
      <el-table-column prop="description" label="问题描述" min-width="260" show-overflow-tooltip />
      <el-table-column prop="creator" label="创建人" width="120" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" link @click="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, jumper, sizes, total"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        :current-page="page"
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" width="900px" :close-on-click-modal="false">
      <template #title>
        <div class="dialog-title">经验详情</div>
      </template>

      <div v-if="detail" class="detail">
        <!-- 基本信息 -->
        <div class="card">
          <div class="card-title">📋 基本信息</div>
          <div class="grid">
            <div>ID: {{ detail.id }}</div>
            <div>问题分类: {{ detail.category }}</div>
            <div class="span">问题名称: {{ detail.problem_name }}</div>
            <div class="span">问题关键字: {{ detail.keywords }}</div>
            <div>创建人: {{ detail.creator || '-' }}</div>
            <div>创建时间: {{ formatTime(detail.create_time) }}</div>
          </div>
        </div>

        <!-- 问题描述 -->
        <div class="card">
          <div class="card-title">📝 问题描述</div>
          <div class="content">{{ detail.description || '（无）' }}</div>
        </div>

        <!-- 问题分析 -->
        <div class="card">
          <div class="card-title">🔍 问题分析</div>
          <div class="content">{{ detail.analysis_content || '（无）' }}</div>
        </div>

        <!-- 解决方案 -->
        <div class="card">
          <div class="card-title">💡 解决方案</div>
          <div class="content">{{ detail.solution_content || '（无）' }}</div>
        </div>

        <!-- 相关附件 -->
        <div class="card">
          <div class="card-title">📎 相关附件</div>

          <div class="attach-section">
            <div class="attach-title">【问题描述】</div>
            <div class="thumbs">
              <el-image
                v-for="(src, i) in (detail.problem_media?.images || [])"
                :key="`pm-img-${i}`"
                :src="src"
                :preview-src-list="detail.problem_media?.images || []"
                :initial-index="i"
                fit="cover"
                hide-on-click-modal
                lazy
                class="thumb"
              />
              <div
                v-for="(src, i) in (detail.problem_media?.videos || [])"
                :key="`pm-vid-${i}`"
                class="video-thumb"
                @click="openVideo(src)"
              >
                <div class="video-badge">▶️</div>
                <div class="video-name">视频{{ i + 1 }}</div>
              </div>
            </div>
          </div>

          <div class="attach-section">
            <div class="attach-title">【问题分析】</div>
            <div class="thumbs">
              <el-image
                v-for="(src, i) in (detail.analysis_media?.images || [])"
                :key="`an-img-${i}`"
                :src="src"
                :preview-src-list="detail.analysis_media?.images || []"
                :initial-index="i"
                fit="cover"
                hide-on-click-modal
                lazy
                class="thumb"
              />
              <div
                v-for="(src, i) in (detail.analysis_media?.videos || [])"
                :key="`an-vid-${i}`"
                class="video-thumb"
                @click="openVideo(src)"
              >
                <div class="video-badge">▶️</div>
                <div class="video-name">视频{{ i + 1 }}</div>
              </div>
            </div>
          </div>

          <div class="attach-section">
            <div class="attach-title">【解决方案】</div>
            <div class="thumbs">
              <el-image
                v-for="(src, i) in (detail.solution_media?.images || [])"
                :key="`so-img-${i}`"
                :src="src"
                :preview-src-list="detail.solution_media?.images || []"
                :initial-index="i"
                fit="cover"
                hide-on-click-modal
                lazy
                class="thumb"
              />
              <div
                v-for="(src, i) in (detail.solution_media?.videos || [])"
                :key="`so-vid-${i}`"
                class="video-thumb"
                @click="openVideo(src)"
              >
                <div class="video-badge">▶️</div>
                <div class="video-name">视频{{ i + 1 }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 视频播放器 -->
    <el-dialog v-model="videoVisible" width="800px" :close-on-click-modal="false">
      <template #title>
        <div class="dialog-title">视频播放器</div>
      </template>
      <div class="video-box">
        <video v-if="videoUrl" :src="videoUrl" controls style="width: 100%; max-height: 70vh" />
      </div>
      <template #footer>
        <el-button @click="videoVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
  
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { experienceApi } from '@/api/experience'
import {
  filters,
  page,
  pageSize,
  total,
  items,
  categoryOptions,
  loadList,
  resetFilters
} from '@/store/experienceQuery'

const detailVisible = ref(false)
const detail = ref(null)

const videoVisible = ref(false)
const videoUrl = ref('')

const onPageChange = (p) => {
  page.value = p
  loadList()
}

const onSizeChange = (s) => {
  pageSize.value = s
  page.value = 1
  loadList()
}

const handleSearch = () => {
  page.value = 1
  loadList()
}

const handleReset = () => {
  resetFilters()
  loadList()
}

const openDetail = async (row) => {
  try {
    const res = await experienceApi.detail(row.id)
    detail.value = res?.data || null
    detailVisible.value = true
  } catch (e) {
    ElMessage.error('获取详情失败')
  }
}

const openVideo = (src) => {
  videoUrl.value = src
  videoVisible.value = true
}

const formatTime = (t) => {
  if (!t) return '-'
  try {
    const d = new Date(t)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch {
    return t
  }
}

const handleCreate = () => {
  ElMessage.info('新增功能将后续提供')
}

const handleSettings = () => {
  ElMessage.info('设置功能将后续提供')
}

onMounted(loadList)
</script>

<style scoped>
.experience {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.title { font-size: 18px; font-weight: 600; }
.actions { display: flex; gap: 8px; }

.search-bar {
  display: grid;
  grid-template-columns: 1fr 220px auto auto;
  gap: 8px;
  margin: 16px 0;
}
.meta { margin: 6px 0 10px; color: #606266; }
.table { width: 100%; }
.pager { display: flex; justify-content: center; margin: 16px 0; }

.dialog-title { font-weight: 600; }
.detail .card { border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.card-title { font-weight: 600; margin-bottom: 8px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.grid .span { grid-column: 1 / -1; }
.content { white-space: pre-wrap; line-height: 1.6; color: #303133; }

.attach-section { margin-top: 8px; }
.attach-title { font-weight: 600; margin-bottom: 8px; }
.thumbs { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }
.thumb { width: 100%; height: 90px; object-fit: cover; border-radius: 6px; }
.video-thumb { position: relative; height: 90px; border-radius: 6px; background: #f5f7fa; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 1px solid #ebeef5; }
.video-badge { position: absolute; top: 6px; left: 6px; font-size: 16px; }
.video-name { color: #606266; font-size: 12px; }

.video-box { display: flex; align-items: center; justify-content: center; }
</style>
