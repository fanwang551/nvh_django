import random
from decimal import Decimal

# 有机物阈值和嗅阈值都不为空的26个物质
substances = [
    ('50-00-0', 0.060, 0.100),  # 甲醛
    ('71-43-2', 1.500, 11.000),  # 苯
    ('108-88-3', 0.330, 1.000),  # 甲苯
    ('1330-20-7', 0.870, 1.500),  # 二甲苯
    ('100-41-4', 0.920, 1.500),  # 乙苯
    ('100-42-5', 0.070, 0.260),  # 苯乙烯
    ('141-78-6', 0.870, 5.000),  # 乙酸乙酯
    ('123-86-4', 0.010, 5.000),  # 乙酸丁酯
    ('67-64-1', 42.000, 100.000),  # 丙酮
    ('78-93-3', 5.400, 10.000),  # 丁酮
    ('110-54-3', 65.000, 100.000),  # 正己烷
    ('67-63-0', 40.000, 100.000),  # 异丙醇
    ('71-36-3', 0.830, 10.000),  # 正丁醇
    ('79-01-6', 21.400, 0.200),  # 三氯乙烯
    ('127-18-4', 8.000, 0.250),  # 四氯乙烯
    ('108-90-7', 0.210, 1.000),  # 氯苯
    ('91-20-3', 0.084, 0.500),  # 萘
    ('95-63-6', 0.350, 5.000),  # 1,2,4-三甲苯
    ('107-02-8', 0.210, 0.050),  # 丙烯醛
    ('107-13-1', 21.400, 0.500),  # 丙烯腈
    ('108-95-2', 0.040, 5.000),  # 苯酚
    ('108-10-1', 0.470, 10.000),  # 甲基异丁基酮
    ('75-09-2', 25.000, 0.600),  # 二氯甲烷
    ('123-91-1', 24.000, 0.500),  # 1,4-二氧六环
    ('107-06-2', 6.000, 1.000),  # 1,2-二氯乙烷
    ('110-19-0', 0.017, 1.000),  # 乙酸异丁酯（假设organic_threshold为1.000）
]


def generate_concentration(sample_id, odor_threshold, organic_threshold):
    """
    根据样品类型生成浓度值
    整车(1-4): 浓度较高
    零件(5-38): 浓度较低
    """
    if sample_id <= 4:  # 整车
        # 整车浓度范围：嗅阈值的0.5-5倍
        base = min(odor_threshold, organic_threshold)
        concentration = round(random.uniform(base * 0.5, base * 5), 3)
    else:  # 零件
        # 零件浓度范围：嗅阈值的0.1-2倍
        base = min(odor_threshold, organic_threshold)
        concentration = round(random.uniform(base * 0.1, base * 2), 3)

    return Decimal(str(concentration))


def calculate_qij(concentration, odor_threshold):
    """计算气味阈稀释倍数 Qij"""
    if odor_threshold and odor_threshold > 0:
        return round(float(concentration) / odor_threshold, 3)
    return None


def calculate_wih(concentration, organic_threshold):
    """计算有机物阈稀释倍数 Wih"""
    if organic_threshold and organic_threshold > 0:
        return round(float(concentration) / organic_threshold, 3)
    return None


# 生成SQL语句
sql_statements = []
sql_statements.append(
    "INSERT INTO `substance_test_details` (`concentration`, `retention_time`, `match_degree`, `concentration_ratio`, `qij`, `wih`, `sample_id`, `cas_no`) VALUES")

values = []

for sample_id in range(1, 39):  # 1-38
    for cas_no, odor_threshold, organic_threshold in substances:
        # 生成浓度
        concentration = generate_concentration(sample_id, odor_threshold, organic_threshold)

        # 生成保留时间 (随机 1.0000 - 30.0000)
        retention_time = round(random.uniform(1.0, 30.0), 4)

        # 生成匹配度 (随机 85.00 - 99.99)
        match_degree = round(random.uniform(85.0, 99.99), 2)

        # 生成浓度占比 (随机 0.100 - 15.000)
        concentration_ratio = round(random.uniform(0.1, 15.0), 3)

        # 计算 Qij 和 Wih
        qij = calculate_qij(concentration, odor_threshold)
        wih = calculate_wih(concentration, organic_threshold)

        # 格式化值
        qij_str = f"{qij}" if qij is not None else "NULL"
        wih_str = f"{wih}" if wih is not None else "NULL"

        value = f"({concentration}, {retention_time}, {match_degree}, {concentration_ratio}, {qij_str}, {wih_str}, {sample_id}, '{cas_no}')"
        values.append(value)

# 每500条记录分割一次SQL语句（避免SQL语句过长）
batch_size = 500
for i in range(0, len(values), batch_size):
    batch = values[i:i + batch_size]
    if i == 0:
        sql = "INSERT INTO `substance_test_details` (`concentration`, `retention_time`, `match_degree`, `concentration_ratio`, `qij`, `wih`, `sample_id`, `cas_no`) VALUES\n"
    else:
        sql = "\n\nINSERT INTO `substance_test_details` (`concentration`, `retention_time`, `match_degree`, `concentration_ratio`, `qij`, `wih`, `sample_id`, `cas_no`) VALUES\n"

    sql += ",\n".join(batch) + ";"
    sql_statements.append(sql)

# 输出到文件
output_file = r"C:\Users\wangfan\Desktop\车身数据库\substance_test_details_insert.sql"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_statements))

print(f"SQL语句已生成到文件: {output_file}")
print(f"总共生成 {len(values)} 条记录 (38个样品 × 26个物质)")
print(f"样品1-4为整车，浓度较高")
print(f"样品5-38为零件，浓度较低")
