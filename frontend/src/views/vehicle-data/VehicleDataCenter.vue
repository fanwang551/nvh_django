<template>
  <div class="page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">车身数据中心</span>
          <span class="subtitle">选择下方模块进入对应中心</span>
        </div>
      </template>

      <div class="grid">
        <el-card class="grid-item" @click="go('/vehicle-data/iaq')" shadow="hover">
          <div class="item-title">车内空气质量中心</div>
          <div class="item-desc">VOC/气味等车内空气质量相关数据</div>
        </el-card>
        <el-card class="grid-item" @click="go('/vehicle-data/data')" shadow="hover">
          <div class="item-title">数据中心</div>
          <div class="item-desc">VOC数据、气味数据、全谱数据</div>
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
.page-card { }
.card-header { display: flex; align-items: baseline; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.subtitle { color: #909399; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-item { cursor: pointer; user-select: none; }
.item-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.item-desc { color: #909399; font-size: 13px; }
@media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
</style>

