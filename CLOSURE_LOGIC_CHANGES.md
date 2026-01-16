# 闭环逻辑改造完成说明

## 改造概述
任务闭环判断逻辑已从固定三表（EntryExit/TestInfo/DocApproval）全部提交，改为按任务场景和技术资料要求动态判断。

## 后端改造

### 1. 模型变更 (backend/apps/nvh_task/models.py)
在 `MainRecord` 模型新增两个字段：
- `task_scenario`: CharField，默认 "NORMAL"，允许值：
  - NORMAL（正常任务）
  - CANCEL_WITH_SAMPLE（取消且有样品）
  - CANCEL_NO_SAMPLE（取消且无样品）
- `doc_requirement`: BooleanField，默认 False，表示是否要求技术资料

**注意：未执行迁移，需手动执行**

### 2. 闭环逻辑变更 (backend/apps/nvh_task/services.py)
`refresh_main_closed()` 函数按新规则实现：

#### 场景闭环规则
1. **NORMAL（正常任务）**
   - doc_requirement=0: 需要 EntryExit + TestInfo
   - doc_requirement=1: 需要 EntryExit + TestInfo + DocApproval

2. **CANCEL_WITH_SAMPLE（取消且有样品）**
   - 仅需 EntryExit
   - doc_requirement 不生效

3. **CANCEL_NO_SAMPLE（取消且无样品）**
   - 直接闭环（无需任何表单）
   - doc_requirement 不生效

#### 表单 OK 口径
- 记录存在
- is_deleted = false
- status = SUBMITTED

### 3. API 变更 (backend/apps/nvh_task/serializers.py & views.py)
- 序列化器支持读写 `task_scenario` 和 `doc_requirement`
- 列表/详情接口返回这两个字段
- MainRecord 更新时，若 `task_scenario` 或 `doc_requirement` 变化，触发闭环刷新

## 前端改造

### 1. Store 变更 (frontend/src/store/NVHtask.js)
- `createMainRecord`: 自动添加默认值 task_scenario="NORMAL", doc_requirement=false
- `updateMainRecord`: 更新后刷新当前抽屉数据

### 2. 主记录创建/编辑 (frontend/src/views/business/TaskMainList.vue)
在"添加主记录"弹窗中，在"是否出报告"字段后新增：
- **任务状态** 下拉选择：
  - 正常 → NORMAL
  - 取消有样品 → CANCEL_WITH_SAMPLE
  - 取消无样品 → CANCEL_NO_SAMPLE
- 默认值：NORMAL
- 必填校验

### 3. 技术资料页签 (frontend/src/views/business/components/tabs/DocApprovalTab.vue)
在表单顶部新增：
- **是否需要填写技术资料** 开关
  - 开启（是）→ doc_requirement=1，显示"必填（影响闭环）"
  - 关闭（否）→ doc_requirement=0，显示"可选（不影响闭环）"
- 仅安排人员可修改
- 修改后立即调用 updateMainRecord 保存到后端并触发闭环刷新

## 验收点

✅ 1. 模型字段已添加（未执行迁移）
✅ 2. MainRecord API 返回 task_scenario 和 doc_requirement
✅ 3. 创建主记录时可选择任务状态
✅ 4. DocApprovalTab 可切换 doc_requirement
✅ 5. 闭环逻辑符合规则表：
   - NORMAL + doc_requirement=0: EntryExit + TestInfo
   - NORMAL + doc_requirement=1: EntryExit + TestInfo + DocApproval
   - CANCEL_WITH_SAMPLE: 仅 EntryExit
   - CANCEL_NO_SAMPLE: 无需任何表单
✅ 6. doc_requirement 在取消场景不影响闭环

## 下一步操作

**重要：需要手动执行数据库迁移**

```bash
cd backend
python manage.py makemigrations nvh_task
python manage.py migrate nvh_task
```

迁移后，已有记录的默认值：
- task_scenario: "NORMAL"
- doc_requirement: False (0)

## 测试建议

1. 创建新任务，选择不同任务状态
2. 在 DocApprovalTab 切换技术资料要求
3. 提交不同表单组合，验证闭环状态
4. 修改任务状态，验证闭环状态自动更新
