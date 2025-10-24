# VOC_odor 模块需求文档

## 一、需求概述

将现有 VOC 模块升级为 VOC_odor 模块，在保留原有 VOC 检测数据展示功能的基础上，新增气味（odor）检测数据的展示功能。两类数据共享筛选条件，分别以独立表格展示。

---

## 二、功能需求

### 2.1 页面布局
```
┌─────────────────────────────────────┐
│         筛选条件区（共用）            │
├─────────────────────────────────────┤
│      VOC 检测结果表（已有功能）       │
├─────────────────────────────────────┤
│      气味检测结果表（新增功能）       │
└─────────────────────────────────────┘
```

### 2.2 筛选功能
- **筛选条件**：保持现有筛选条件不变
- **作用范围**：筛选条件同时作用于 VOC 表格和气味表格
- **数据加载**：默认加载所有数据，支持分页

### 2.3 VOC 检测结果表（优化）

**表头结构**：保持现有结构不变

**列选择功能优化**：
- 现有可选列：委托单号、零部件等
- **新增可选列**：在委托单号后添加
  - 检测时间
  - 开发阶段
  - 检测状态

### 2.4 气味检测结果表（新增）

**表头结构**：

| 列名 | 说明  | 数据格式 |
|------|-----|----------|
| 项目名称 | 必选列 | 文本 |
| 检测时间 | 可选列 | 日期时间 |
| 委托单号 | 可选列 | 文本 |
| 开发阶段 | 可选列 | 文本 |
| 检测状态 | 可选列 | 文本 |
| 零部件 | 可选列 | 文本 |
| 静态-前排 | 必选列 | 数值（保留1位小数） |
| 静态-后排 | 必选列 | 数值（保留1位小数） |
| 动态-前排 | 必选列 | 数值（保留1位小数） |
| 动态-后排 | 必选列 | 数值（保留1位小数） |
| 气味均值 | 必选列 | 数值（保留1位小数） |

**列选择功能**：
- 可选列：检测时间、委托单号、零部件、开发阶段、检测状态


**数据显示要求**：
- 所有气味数值保留 1 位小数

---

## 三、数据库设计

### 3.1 样品信息表（sample_info）
保持不变

### 3.2 检测结果表重构

**原表名**：`voc_result`  
**新表名**：`voc_odor_result`

**表结构**：修改表名并添加五列数据

```sql
CREATE TABLE voc_odor_result (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    sample_id INT NOT NULL COMMENT '样品ID，关联sample_info表',
    
    -- VOC 检测数据（原有字段）
    benzene DECIMAL(10,4) COMMENT '苯 (mg/m³)',
    toluene DECIMAL(10,4) COMMENT '甲苯 (mg/m³)',
    ethylbenzene DECIMAL(10,4) COMMENT '乙苯 (mg/m³)',
    xylene DECIMAL(10,4) COMMENT '二甲苯 (mg/m³)',
    styrene DECIMAL(10,4) COMMENT '苯乙烯 (mg/m³)',
    formaldehyde DECIMAL(10,4) COMMENT '甲醛 (mg/m³)',
    acetaldehyde DECIMAL(10,4) COMMENT '乙醛 (mg/m³)',
    acrolein DECIMAL(10,4) COMMENT '丙烯醛 (mg/m³)',
    tvoc DECIMAL(10,4) COMMENT 'TVOC (mg/m³)',
    test_date DATE COMMENT '检测时间',
    
    -- 气味检测数据（新增字段）
    static_front DECIMAL(6,1) DEFAULT NULL COMMENT '静态-前排',
    static_rear DECIMAL(6,1) DEFAULT NULL COMMENT '静态-后排',
    dynamic_front DECIMAL(6,1) DEFAULT NULL COMMENT '动态-前排',
    dynamic_rear DECIMAL(6,1) DEFAULT NULL COMMENT '动态-后排',
    odor_mean DECIMAL(6,1) DEFAULT NULL COMMENT '气味均值',
    
    INDEX idx_sample_id (sample_id),
    INDEX idx_test_date (test_date),
    FOREIGN KEY (sample_id) REFERENCES sample_info(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='VOC和气味检测结果表';

```

**字段说明**：
- 气味数据字段使用 `DECIMAL(3,1)` 类型，支持保留 1 位小数

---

## 四、实现要点

### 4.1 前端改动
1. **文件重命名**：`VocData.vue` → `VocOdorData.vue`
2. **新增组件**：气味检测结果表组件
3. **共享筛选**：筛选条件同时控制两个表格的数据请求
4. **列选择器**：两个表格各自独立的列显示控制

### 4.2 后端改动
1. **表重命名**：`voc_result` → `voc_odor_result`
2. **API 调整**：
   - 修改对应的前后端代码，保证数据能正常加载即可
3. **数据迁移**：编写迁移脚本将现有数据迁移到新表
---



