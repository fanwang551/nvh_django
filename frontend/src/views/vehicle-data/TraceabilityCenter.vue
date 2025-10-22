<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">溯源中心</span>
          <span class="subtitle">Traceability Center</span>
        </div>
      </template>
      <div class="content">此页面用于数据溯源、流程追踪与审计。</div>
    </el-card>
  </div>
</template>

<script setup>
// 预留：接入溯源业务逻辑
</script>

<style scoped>
.page { padding: 12px; }
.card-header { display: flex; align-items: baseline; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.subtitle { color: #909399; font-size: 13px; }
.content { color: #606266; font-size: 14px; }
</style>

