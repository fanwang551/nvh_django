# 重构功能测试清单

## ✅ 已完成的重构

### 第一组：模态数据查询功能 (ModalDataQuery + modalDataStore)

#### modalDataStore.js 重构完成：
- ✅ 移除UI状态：`modalShapeDialogVisible`、`currentModalData`、`activeTab`
- ✅ 移除UI方法：`viewModalShape()`、`closeModalShapeDialog()`、`switchDialogTab()`
- ✅ 保留所有业务逻辑方法和状态
- ✅ 更新`resetState()`方法，移除UI状态重置

#### ModalDataQuery.vue 重构完成：
- ✅ 添加UI状态管理：`modalShapeDialogVisible`、`currentModalData`、`activeTab`
- ✅ 添加UI交互方法：`viewModalShape()`、`handleCloseDialog()`、`switchDialogTab()`
- ✅ 更新模板绑定：弹窗状态绑定到组件本地状态
- ✅ 更新tab切换事件：绑定到组件本地方法
- ✅ 更新生命周期：`onDeactivated`中清理本地UI状态

### 第二组：模态数据对比功能 (ModalDataCompare + modalCompareStore)

#### modalCompareStore.js 重构完成：
- ✅ 移除UI状态：`modalShapeDialogVisible`、`currentModalData`、`activeTab`
- ✅ 移除图表UI状态：`chartInstance`、`chartInitialized`
- ✅ 移除UI方法：`showModalShapeDialog()`、`closeModalShapeDialog()`、`switchDialogTab()`、`setChartInstance()`、`clearDialogState()`
- ✅ 保留所有业务逻辑方法和状态

#### ModalDataCompare.vue 重构完成：
- ✅ 添加UI状态管理：`modalShapeDialogVisible`、`currentModalData`、`activeTab`
- ✅ 添加图表状态管理：将`chartInstance`移到组件本地
- ✅ 添加UI交互方法：`viewModalShape()`、`handleCloseDialog()`、`switchDialogTab()`
- ✅ 重构图表管理：移除对`store.setChartInstance()`的调用
- ✅ 更新模板绑定：弹窗状态和tab切换绑定到组件本地
- ✅ 更新生命周期：`onDeactivated`中清理本地UI状态和图表监听器

## 🎯 重构成果

### 职责边界清晰化：
- **Store职责**：纯业务数据管理、API调用、业务逻辑处理
- **组件职责**：UI状态管理、用户交互处理、图表管理、生命周期管理

### 数据流标准化：
```
用户UI操作 → 组件事件处理方法 → 调用Store Action → Store更新业务数据 → 组件响应数据变化 → UI自动更新
```

### 代码质量提升：
- 单一职责原则：每个方法只负责一个明确功能
- 清晰边界：Store纯业务，组件纯UI，绝不混合
- 命名规范：方法和变量名清晰表达其职责

## 📋 待测试功能

### 模态数据查询功能测试：
- [ ] 车型选择和零件加载
- [ ] 数据查询和分页
- [ ] "查看振型"弹窗显示
- [ ] 弹窗内tab切换（振型动画/测试图片）
- [ ] 弹窗关闭
- [ ] Tab切换时状态保持

### 模态数据对比功能测试：
- [ ] 级联选择控件（零件→车型→测试状态→振型类型）
- [ ] 对比数据生成
- [ ] 散点图渲染
- [ ] 图表点击事件（显示弹窗）
- [ ] 弹窗内tab切换
- [ ] Tab切换时图表重渲染
- [ ] 组件失活时状态清理

## 🚀 重构优势

1. **维护性提升**：职责清晰，修改UI不影响业务逻辑
2. **可测试性增强**：业务逻辑和UI逻辑分离，便于单元测试
3. **复用性提高**：业务逻辑可在不同组件间复用
4. **性能优化**：减少不必要的响应式依赖
5. **代码可读性**：结构清晰，易于理解和维护
