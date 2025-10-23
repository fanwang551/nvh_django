一、模块概述
在 apps 目录下新建 VOC模块，用于VOC（挥发性有机化合物）检测数据的展示、筛选和可视化分析。

二、功能需求
2.1 数据展示功能
触发方式： 点击"数据中心"下的"VOC数据"菜单

展示内容：

默认加载所有VOC检测数据
使用分页展示
支持根据筛选条件动态刷新数据
2.2 数据筛选功能
筛选条件：

项目名称
零件名称
检测状态（对应 sample_info.status）
委托单号
交互逻辑：

支持多条件组合筛选
选择筛选条件后实时更新数据展示
2.3 检测结果表格
表头结构：

列名	说明	格式要求
项目名称	关联项目信息vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')	-
委托单号	test_order_no	-
零部件名称	part_name	-
苯 (Benzene)	benzene	保留3位小数<br>单位：mg/m³
甲苯 (Toluene)	toluene	同上
乙苯 (Ethylbenzene)	ethylbenzene	同上
二甲苯 (Xylene)	xylene	同上
苯乙烯 (Styrene)	styrene	同上
甲醛 (Formaldehyde)	formaldehyde	同上
乙醛 (Acetaldehyde)	acetaldehyde	同上
丙烯醛 (Acrolein)	acrolein	同上
TVOC	tvoc	同上
显示要求：

数值保留3位小数
单位"mg/m³"换行显示在物质名称下方
支持自定义选择展示哪些VOC物质列
2.4 数据可视化功能
触发方式： 需要你帮忙设计

3.1 动态分组选择器
[分组维度选择]
  主分组： [下拉选择：零件名称 ▼]
  副分组： [下拉选择：检测状态 ▼]
  
[VOC物质选择]
  ☑ 苯  ☑ 甲苯  ☑ 乙苯  ☑ 二甲苯  ☑ 苯乙烯
  ☑ 甲醛  ☑ 乙醛  ☑ 丙烯醛  ☑ TVOC
  
[生成图表]
3.2 图表呈现
分组柱状图（Grouped Bar Chart）

示例：主分组=零件，副分组=状态

零件A          零件B          零件C
┌─┬─┬─┐      ┌─┬─┬─┐      ┌─┬─┬─┐
│█│█│█│      │█│█│█│      │█│█│█│
│█│█│█│      │█│█│█│      │█│█│█│
└─┴─┴─┘      └─┴─┴─┘      └─┴─┴─┘
标准停车行车   标准停车行车   标准停车行车

图例：█ 苯  █ 甲苯  █ 乙苯 ... 
三、数据库设计
3.1 样品信息表 (sample_info)
CREATE TABLE sample_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_model INT COMMENT 'vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')', 
    part_name VARCHAR(100) COMMENT '零件名称，整车填"整车"',
    development_stage VARCHAR(50) COMMENT '开发阶段', 
    status VARCHAR(50) COMMENT '状态',
    test_order_no VARCHAR(50) COMMENT '检测委托单号',
    sample_no VARCHAR(50) COMMENT '样品编号',
    sample_image_url VARCHAR(255) COMMENT '样品图URL',
    created_at DATETIME COMMENT '创建时间',
    INDEX idx_project_id (project_id),
    INDEX idx_sample_no (sample_no)
);
3.2 VOC检测结果表 (voc_result)
CREATE TABLE voc_result (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sample_id INT COMMENT '样品ID，关联sample_info表',
    benzene DECIMAL(10,4) COMMENT '苯 (mg/m³)',
    toluene DECIMAL(10,4) COMMENT '甲苯 (mg/m³)',
    ethylbenzene DECIMAL(10,4) COMMENT '乙苯 (mg/m³)',
    xylene DECIMAL(10,4) COMMENT '二甲苯 (mg/m³)',
    styrene DECIMAL(10,4) COMMENT '苯乙烯 (mg/m³)',
    formaldehyde DECIMAL(10,4) COMMENT '甲醛 (mg/m³)',
    acetaldehyde DECIMAL(10,4) COMMENT '乙醛 (mg/m³)',
    acrolein DECIMAL(10,4) COMMENT '丙烯醛 (mg/m³)',
    tvoc DECIMAL(10,4) COMMENT 'TVOC (mg/m³)',
    test_date DATETIME COMMENT '检测时间',
    INDEX idx_sample_id (sample_id),
    FOREIGN KEY (sample_id) REFERENCES sample_info(id)
);“前后端代码规范和当前项目保持一致，前端依旧使用pinia+vue;你需要先告诉我你的设计方案，确认方案之后再修改代码