可能相关代码"D:\pythonProject\zlbbses\nvh_django\frontend\src\views\vehicle-data\VocOdorData.vue"
"D:\pythonProject\zlbbses\nvh_django\frontend\src\store\vocQuery.js";"D:\pythonProject\zlbbses\nvh_django\backend\apps\voc\views.py"
"D:\pythonProject\zlbbses\nvh_django\backend\apps\voc\serializers.py"等；
---

**需求说明：**

**一、筛选框优化**
- 将"项目名称"筛选条件由单选改为多选

**二、柱状图功能重构（适用于VOC柱状图和气味数据柱状图）**

**2.1 按钮位置调整**
- 删除表格操作列中的"图表"按钮
- 在"列选择"按钮旁边新增"图表"按钮

**2.2 图表生成逻辑**
- 点击"图表"按钮后，基于当前筛选结果生成柱状图
- **数据校验**：筛选结果中的零部件分类必须统一（仅整车或仅零件），不可混合

**2.3 柱状图命名规则**
- 基础格式：`车型-样品编号-检测状态-开发阶段`
- **智能简化规则**（当筛选结果中某字段值完全相同时，隐藏该字段）：
  - 车型相同 → 不显示车型
  - 样品编号相同 → 不显示样品编号
  - 检测状态相同 → 不显示检测状态
  - 开发阶段相同 → 不显示开发阶段

**2.4 图表显示优化**
- 删除图表上方的"项目"标题

---

**关键变更总结：**
1. 项目名称：单选 → 多选
2. 图表按钮：操作列 → 列选择旁边
3. 图表数据：单条记录 → 当前筛选结果（需校验零部件分类一致性）
4. 命名规则：动态简化重复字段
5. 界面优化：移除"项目"标题