import random
import os
from datetime import date

# 物质信息 (id, name, OTV, TV)
substances = [
    (1, "甲醛", 0.500, 0.100),
    (2, "乙醛", 0.050, 0.050),
    (3, "丙醛", 0.015, 0.030),
    (4, "丁醛", 0.010, 0.020),
    (5, "戊醛", 0.012, 0.025),
    (6, "己醛", 0.008, 0.015),
    (7, "庚醛", 0.010, 0.020),
    (8, "辛醛", 0.007, 0.015),
    (9, "壬醛", 0.005, 0.010),
    (10, "苯", 4.680, 0.110),
    (11, "甲苯", 2.140, 1.100),
    (12, "乙苯", 0.920, 1.500),
    (13, "二甲苯", 1.100, 1.500),
    (14, "苯乙烯", 0.070, 0.260),
    (15, "丙酮", 42.000, 1.000),
    (16, "丁酮", 5.500, 0.500),
    (17, "环己酮", 0.150, 0.200),
    (18, "乙酸乙酯", 0.870, 0.500),
    (19, "乙酸丁酯", 0.046, 0.200),
    (20, "甲醇", 100.000, 0.500),
    (21, "乙醇", 10.000, 2.000),
    (22, "异丙醇", 5.800, 1.000),
    (23, "正丁醇", 0.830, 0.300),
    (24, "三氯乙烯", 21.400, 0.200),
    (25, "四氢呋喃", 2.000, 0.300),
]

# 样品ID范围
sample_ids = list(range(21, 56))

# 生成测试日期
test_date = date(2024, 1, 15)

# 输出文件路径
output_dir = r"C:\Users\wangfan\Desktop\nvhdata"
output_file = os.path.join(output_dir, "insert_substances_data.sql")

# 确保目录存在
os.makedirs(output_dir, exist_ok=True)

# 存储所有零部件的Oi和Vi，用于计算整车指数
all_oi = []
all_vi = []

# 存储SQL语句
substances_test_sql = []
substances_test_detail_sql = []

# 用于临时存储test记录，以便后续关联detail
test_records = []

print("开始生成数据...")

for idx, sample_id in enumerate(sample_ids, 1):
    # 为每个样品生成25种物质的测试详情
    oi_sum = 0.0
    vi_sum = 0.0

    detail_records = []

    for substance_id, substance_name, otv, tv in substances:
        # 生成随机浓度 (μg/m³)
        # 根据物质特性设置不同的浓度范围
        if substance_id in [1, 20]:  # 甲醛、甲醇 - 高浓度
            concentration = round(random.uniform(10, 200), 3)
        elif substance_id in [10, 11, 15, 21]:  # 苯、甲苯、丙酮、乙醇 - 中高浓度
            concentration = round(random.uniform(5, 100), 3)
        elif substance_id in [24]:  # 三氯乙烯 - 中等浓度
            concentration = round(random.uniform(1, 50), 3)
        else:  # 其他物质 - 低浓度
            concentration = round(random.uniform(0.1, 30), 3)

        # 计算Qij = Cij / OTVj (气味阈稀释倍数)
        qij = concentration / otv

        # 计算Wih = Cih / TVh (VOC阈稀释倍数)
        wih = concentration / tv

        # 累加到Oi和Vi
        oi_sum += qij
        vi_sum += wih

        # 生成其他字段
        retention_time = round(random.uniform(1.0, 30.0), 4)
        match_degree = round(random.uniform(85.0, 99.9), 2)
        concentration_ratio = round(random.uniform(0.1, 10.0), 3)

        detail_records.append({
            'retention_time': retention_time,
            'match_degree': match_degree,
            'concentration': concentration,
            'concentration_ratio': concentration_ratio,
            'dilution_oij': round(qij, 3),
            'dilution_wih': round(wih, 3),
            'substance_id': substance_id
        })

    # 保存Oi和Vi用于计算整车指数
    all_oi.append(oi_sum)
    all_vi.append(vi_sum)

    # 计算整车指数（所有零部件的总和）
    zoi = sum(all_oi)
    zvi = sum(all_vi)

    # 计算贡献度
    goi = (oi_sum / zoi * 100) if zoi > 0 else 0
    gvi = (vi_sum / zvi * 100) if zvi > 0 else 0

    # 保存test记录和对应的detail记录
    test_records.append({
        'oi': round(oi_sum, 3),
        'goi': round(goi, 3),
        'vi': round(vi_sum, 3),
        'gvi': round(gvi, 3),
        'sample_id': sample_id,
        'details': detail_records
    })

    print(f"已生成样品 {idx}/{len(sample_ids)} (sample_id: {sample_id})")

# 生成SQL语句
print("\n正在生成SQL语句...")

# 方案：使用LAST_INSERT_ID()来关联主表和详情表
for test_record in test_records:
    # substances_test插入语句
    substances_test_sql.append(
        f"({test_record['oi']}, {test_record['goi']}, {test_record['vi']}, "
        f"{test_record['gvi']}, '{test_date}', {test_record['sample_id']})"
    )

    # 为每个test记录生成对应的detail记录
    for detail in test_record['details']:
        substances_test_detail_sql.append({
            'sql': f"({detail['retention_time']}, {detail['match_degree']}, "
                   f"{detail['concentration']}, {detail['concentration_ratio']}, "
                   f"{detail['dilution_oij']}, {detail['dilution_wih']}, "
                   f"{detail['substance_id']}, @test_id)",
            'test_index': len(substances_test_sql) - 1
        })

# 写入SQL文件
print(f"\n正在写入SQL文件到: {output_file}")

with open(output_file, 'w', encoding='utf-8') as f:
    # 写入文件头注释
    f.write("-- ========================================\n")
    f.write("-- 物质测试数据插入脚本\n")
    f.write(f"-- 生成时间: {date.today()}\n")
    f.write(f"-- 样品数量: {len(sample_ids)}\n")
    f.write(f"-- 物质种类: {len(substances)}\n")
    f.write(f"-- 测试记录: {len(substances_test_sql)}\n")
    f.write(f"-- 详细记录: {len(substances_test_detail_sql)}\n")
    f.write("-- ========================================\n\n")

    # 逐条插入，使用LAST_INSERT_ID()关联
    f.write("-- 插入数据（使用LAST_INSERT_ID()关联主表和详情表）\n\n")

    for i, test_sql in enumerate(substances_test_sql):
        # 插入substances_test
        f.write(f"-- 样品 {sample_ids[i]} 的测试记录\n")
        f.write("INSERT INTO `substances_test` (`oi`, `goi`, `vi`, `gvi`, `test_date`, `sample_id`) VALUES\n")
        f.write(test_sql + ";\n\n")

        # 获取刚插入的ID
        f.write("SET @test_id = LAST_INSERT_ID();\n\n")

        # 插入对应的detail记录
        detail_batch = [d['sql'] for d in substances_test_detail_sql if d['test_index'] == i]
        f.write(
            "INSERT INTO `substances_test_detail` (`retention_time`, `match_degree`, `concentration`, `concentration_ratio`, `dilution_oij`, `dilution_wih`, `substance_id`, `substances_test_id`) VALUES\n")
        f.write(",\n".join(detail_batch) + ";\n\n")

    # 写入统计信息
    f.write("-- ========================================\n")
    f.write("-- 数据统计\n")
    f.write(f"-- 总计生成: {len(substances_test_sql)} 条测试记录\n")
    f.write(f"-- 总计生成: {len(substances_test_detail_sql)} 条详细记录\n")
    f.write("-- ========================================\n")

print(f"\n✅ SQL文件生成成功！")
print(f"📁 文件位置: {output_file}")
print(f"📊 统计信息:")
print(f"   - 测试记录: {len(substances_test_sql)} 条")
print(f"   - 详细记录: {len(substances_test_detail_sql)} 条")
print(f"\n💡 执行方式:")
print(f"   mysql -u username -p database_name < \"{output_file}\"")
