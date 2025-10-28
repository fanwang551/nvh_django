<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">溯源中心</span>
          <span class="subtitle">Traceability Center</span>
        </div>
      </template>
      <div class="grid">
        <el-card class="grid-item" @click="go('/vehicle-data/trace/contribution')" shadow="hover">
          <div class="item-title">贡献度查询</div>
          <div class="item-desc">按项目输出GOi/GVi TOP25</div>
        </el-card>
      </div>
    </el-card>
  </div>
  
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const go = (path) => router.push(path)
</script>

<style scoped>
.page { padding: 12px; }
.card-header { display: flex; align-items: baseline; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.subtitle { color: #909399; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-item { cursor: pointer; user-select: none; }
.item-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.item-desc { color: #909399; font-size: 13px; }
@media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
</style>
