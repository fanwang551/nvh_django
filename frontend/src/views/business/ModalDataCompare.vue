<template>
  <div class="modal-data-compare">
    <div class="page-header">
      <h2>模态数据对比</h2>
      <p class="page-description">对比不同模态测试结果</p>
    </div>
    
    <div class="content-placeholder">
      <el-empty description="功能开发中..." />
    </div>
  </div>
</template>

<script setup>
// 模态数据对比页面
</script>

<style scoped>
.modal-data-compare {
  padding: 0;
}

.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.content-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
