<template>
  <div class="page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">数据中心</span>
          <span class="subtitle">包含 VOC及气味数据、全谱数据</span>
        </div>
      </template>

      <div class="grid">
        <el-card class="grid-item" @click="go('/vehicle-data/data/voc')" shadow="hover">
          <div class="item-title">VOC及气味数据</div>
          <div class="item-desc">Volatile Organic Compounds & Odor</div>
        </el-card>
        <el-card class="grid-item" @click="go('/vehicle-data/data/full-spectrum')" shadow="hover">
          <div class="item-title">全谱数据</div>
          <div class="item-desc">Full Spectrum</div>
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

