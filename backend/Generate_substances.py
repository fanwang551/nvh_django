import random
from datetime import date
import os

# 25种物质数据
substances = [
    {'id': 1, 'name': '甲醛', 'otv': 0.500, 'tv': 0.100},
    {'id': 2, 'name': '乙醛', 'otv': 0.050, 'tv': 0.050},
    {'id': 3, 'name': '丙醛', 'otv': 0.015, 'tv': 0.030},
    {'id': 4, 'name': '丁醛', 'otv': 0.010, 'tv': 0.020},
    {'id': 5, 'name': '戊醛', 'otv': 0.012, 'tv': 0.025},
    {'id': 6, 'name': '己醛', 'otv': 0.008, 'tv': 0.015},
    {'id': 7, 'name': '庚醛', 'otv': 0.010, 'tv': 0.020},
    {'id': 8, 'name': '辛醛', 'otv': 0.007, 'tv': 0.015},
    {'id': 9, 'name': '壬醛', 'otv': 0.005, 'tv': 0.010},
    {'id': 10, 'name': '苯', 'otv': 4.680, 'tv': 0.110},
    {'id': 11, 'name': '甲苯', 'otv': 2.140, 'tv': 1.100},
    {'id': 12, 'name': '乙苯', 'otv': 0.920, 'tv': 1.500},
    {'id': 13, 'name': '二甲苯', 'otv': 1.100, 'tv': 1.500},
    {'id': 14, 'name': '苯乙烯', 'otv': 0.070, 'tv': 0.260},
    {'id': 15, 'name': '丙酮', 'otv': 42.000, 'tv': 1.000},
    {'id': 16, 'name': '丁酮', 'otv': 5.500, 'tv': 0.500},
    {'id': 17, 'name': '环己酮', 'otv': 0.150, 'tv': 0.200},
    {'id': 18, 'name': '乙酸乙酯', 'otv': 0.870, 'tv': 0.500},
    {'id': 19, 'name': '乙酸丁酯', 'otv': 0.046, 'tv': 0.200},
    {'id': 20, 'name': '甲醇', 'otv': 100.000, 'tv': 0.500},
    {'id': 21, 'name': '乙醇', 'otv': 10.000, 'tv': 2.000},
    {'id': 22, 'name': '异丙醇', 'otv': 5.800, 'tv': 1.000},
    {'id': 23, 'name': '正丁醇', 'otv': 0.830, 'tv': 0.300},
    {'id': 24, 'name': '三氯乙烯', 'otv': 21.400, 'tv': 0.200},
    {'id': 25, 'name': '四氢呋喃', 'otv': 2.000, 'tv': 0.300}
]

# 35个零部件名称
component_names = [
    '仪表板总成', '门内饰板-左前', '门内饰板-右前', '门内饰板-左后', '门内饰板-右后',
    '座椅总成-驾驶', '座椅总成-副驾', '座椅总成-后排', '顶棚总成', '地毯总成',
    '方向盘总成', '中控台总成', '手套箱总成', 'A柱护板-左', 'A柱护板-右',
    'B柱护板-左', 'B柱护板-右', 'C柱护板-左', 'C柱护板-右', '后备箱内饰',
    '遮阳板-左', '遮阳板-右', '扶手箱总成', '空调出风口总成', '音响面板',
    '换挡手柄总成', '脚垫', '密封条-门框', '隔音棉', '头枕',
    '安全带总成', '后视镜壳', '杯架总成', '储物盒', '装饰条总成'
]


def generate_concentration():
    """生成随机浓度值 (μg/m³)"""
    return round(random.uniform(0.1, 50.0), 3)


def calculate_qij(concentration, otv):
    """计算气味污染物阈稀释倍数 Qij = Cij / OTVj"""
    if otv == 0:
        return 0
    return round(concentration / otv, 3)


def calculate_wih(concentration, tv):
    """计算挥发性有机物阈稀释倍数 Wih = Cih / TVh"""
    if tv == 0:
        return 0
    return round(concentration / tv, 3)


def calculate_oi(qij_list):
    """计算气味污染物指数 Oi = Σ Qij"""
    return round(sum(qij_list), 3)


def calculate_vi(wih_list):
    """计算挥发性有机污染物指数 Vi = Σ Wih"""
    return round(sum(wih_list), 3)


def calculate_goi(oi, zoi):
    """计算零部件气味污染物贡献度 GOi = (Oi / ZOi) × 100%"""
    if zoi == 0:
        return 0
    return round((oi / zoi) * 100, 3)


def calculate_gvi(vi, zvi):
    """计算部件有机污染物贡献度 GVi = (Vi / ZVi) × 100%"""
    if zvi == 0:
        return 0
    return round((vi / zvi) * 100, 3)


def generate_test_order_no():
    """生成测试单号"""
    return f"TEST{date.today().strftime('%Y%m%d')}{random.randint(1000, 9999)}"


def generate_sample_no(index):
    """生成样品编号"""
    return f"VOC{date.today().strftime('%Y%m%d')}{str(index).zfill(3)}"


def main():
    sql_lines = []

    # SQL文件头部
    sql_lines.append("-- VOC测试数据生成脚本")
    sql_lines.append("-- 生成日期: " + str(date.today()))
    sql_lines.append("-- 样品ID范围: 56-91 (35个零部件 + 1个整车)")
    sql_lines.append("-- substances_test ID范围: 46-81")
    sql_lines.append("")
    sql_lines.append("SET NAMES utf8mb4;")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_lines.append("")

    sample_id = 56
    test_id = 46
    test_date = str(date.today())

    # 存储所有零部件的Oi和Vi
    all_oi_values = []
    all_vi_values = []
    component_test_data = []

    sql_lines.append("-- ==========================================")
    sql_lines.append("-- 第一部分：生成35个零部件数据")
    sql_lines.append("-- ==========================================")
    sql_lines.append("")

    # 生成35个零部件数据
    for idx, part_name in enumerate(component_names):
        sql_lines.append(f"-- 零部件 {idx + 1}/35: {part_name}")
        sql_lines.append("")

        test_order_no = generate_test_order_no()
        sample_no = generate_sample_no(sample_id)

        # 插入样品信息（使用正确的字段名）
        sql_lines.append(f"-- 样品信息 (ID: {sample_id})")
        sql_lines.append(
            f"INSERT INTO `sample_info` (`id`, `part_name`, `development_stage`, `status`, `test_order_no`, `sample_no`, `sample_image_url`, `vehicle_model_id`) "
            f"VALUES ({sample_id}, '{part_name}', '体验阀', NULL, '{test_order_no}', '{sample_no}', NULL, 1);"
        )
        sql_lines.append("")

        # 为该零部件生成25种物质的测试数据
        qij_list = []
        wih_list = []
        detail_records = []

        for substance in substances:
            concentration = generate_concentration()
            qij = calculate_qij(concentration, substance['otv'])
            wih = calculate_wih(concentration, substance['tv'])

            qij_list.append(qij)
            wih_list.append(wih)

            detail_records.append({
                'retention_time': round(random.uniform(1.0, 30.0), 4),
                'match_degree': round(random.uniform(80.0, 99.9), 2),
                'concentration': concentration,
                'concentration_ratio': round(random.uniform(0.1, 10.0), 3),
                'dilution_oij': qij,
                'dilution_wih': wih,
                'substance_id': substance['id']
            })

        # 计算该零部件的Oi和Vi
        oi = calculate_oi(qij_list)
        vi = calculate_vi(wih_list)

        all_oi_values.append(oi)
        all_vi_values.append(vi)

        # 插入substances_test记录（GOi和GVi先设为NULL）
        sql_lines.append(f"-- 测试记录 (ID: {test_id}, Oi={oi}, Vi={vi})")
        sql_lines.append(
            f"INSERT INTO `substances_test` (`id`, `oi`, `goi`, `vi`, `gvi`, `test_date`, `sample_id`) "
            f"VALUES ({test_id}, {oi}, NULL, {vi}, NULL, '{test_date}', {sample_id});"
        )
        sql_lines.append("")

        # 保存测试ID和指标值
        component_test_data.append({
            'test_id': test_id,
            'oi': oi,
            'vi': vi
        })

        # 插入substances_test_detail记录（不指定ID，使用自增）
        sql_lines.append(f"-- 测试详情 (25种物质，ID自增)")
        for detail in detail_records:
            sql_lines.append(
                f"INSERT INTO `substances_test_detail` (`retention_time`, `match_degree`, `concentration`, "
                f"`concentration_ratio`, `dilution_oij`, `dilution_wih`, `substance_id`, `substances_test_id`) "
                f"VALUES ({detail['retention_time']}, {detail['match_degree']}, {detail['concentration']}, "
                f"{detail['concentration_ratio']}, {detail['dilution_oij']}, {detail['dilution_wih']}, "
                f"{detail['substance_id']}, {test_id});"
            )

        sql_lines.append("")
        sql_lines.append("")

        sample_id += 1
        test_id += 1

    # 计算整车指数
    zoi = sum(all_oi_values)
    zvi = sum(all_vi_values)

    sql_lines.append("-- ==========================================")
    sql_lines.append(f"-- 整车指数计算结果: ZOi={zoi}, ZVi={zvi}")
    sql_lines.append("-- ==========================================")
    sql_lines.append("")

    # 更新所有零部件的GOi和GVi
    sql_lines.append("-- ==========================================")
    sql_lines.append("-- 第二部分：更新零部件的贡献度 (GOi, GVi)")
    sql_lines.append("-- ==========================================")
    sql_lines.append("")

    for comp in component_test_data:
        goi = calculate_goi(comp['oi'], zoi)
        gvi = calculate_gvi(comp['vi'], zvi)

        sql_lines.append(
            f"UPDATE `substances_test` SET `goi` = {goi}, `gvi` = {gvi} WHERE `id` = {comp['test_id']};"
        )

    sql_lines.append("")
    sql_lines.append("")

    # 生成整车数据
    sql_lines.append("-- ==========================================")
    sql_lines.append("-- 第三部分：生成整车数据")
    sql_lines.append("-- ==========================================")
    sql_lines.append("")

    whole_vehicle_sample_id = sample_id
    whole_vehicle_test_id = test_id
    whole_test_order_no = generate_test_order_no()
    whole_sample_no = generate_sample_no(whole_vehicle_sample_id)

    sql_lines.append(f"-- 整车样品信息 (ID: {whole_vehicle_sample_id})")
    sql_lines.append(
        f"INSERT INTO `sample_info` (`id`, `part_name`, `development_stage`, `status`, `test_order_no`, `sample_no`, `sample_image_url`, `vehicle_model_id`) "
        f"VALUES ({whole_vehicle_sample_id}, '整车', '体验阀', '标准模型', '{whole_test_order_no}', '{whole_sample_no}', NULL, 1);"
    )
    sql_lines.append("")

    # 整车测试记录：oi, goi, vi, gvi 都为 NULL
    sql_lines.append(f"-- 整车测试记录 (ID: {whole_vehicle_test_id}, 所有指标为NULL)")
    sql_lines.append(
        f"INSERT INTO `substances_test` (`id`, `oi`, `goi`, `vi`, `gvi`, `test_date`, `sample_id`) "
        f"VALUES ({whole_vehicle_test_id}, NULL, NULL, NULL, NULL, '{test_date}', {whole_vehicle_sample_id});"
    )
    sql_lines.append("")

    # 整车测试详情（25种物质，ID自增）
    sql_lines.append(f"-- 整车测试详情 (25种物质，ID自增)")
    for substance in substances:
        avg_concentration = round(random.uniform(5.0, 100.0), 3)
        qij = calculate_qij(avg_concentration, substance['otv'])
        wih = calculate_wih(avg_concentration, substance['tv'])

        sql_lines.append(
            f"INSERT INTO `substances_test_detail` (`retention_time`, `match_degree`, `concentration`, "
            f"`concentration_ratio`, `dilution_oij`, `dilution_wih`, `substance_id`, `substances_test_id`) "
            f"VALUES ({round(random.uniform(1.0, 30.0), 4)}, {round(random.uniform(85.0, 99.9), 2)}, "
            f"{avg_concentration}, {round(random.uniform(1.0, 15.0), 3)}, {qij}, {wih}, {substance['id']}, {whole_vehicle_test_id});"
        )

    sql_lines.append("")
    sql_lines.append("")

    # SQL文件尾部
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_lines.append("")
    sql_lines.append("-- ==========================================")
    sql_lines.append("-- 数据生成完成")
    sql_lines.append(f"-- 样品信息: 36条 (ID: 56-91)")
    sql_lines.append(f"-- 测试记录: 36条 (ID: 46-81)")
    sql_lines.append(f"-- 测试详情: {36 * 25}条 (ID自增)")
    sql_lines.append("-- ==========================================")

    # 确保目录存在并写入文件
    output_dir = r'C:\Users\wangfan\Desktop\nvhdata'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'voc_test_data.sql')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))

    print(f"✅ SQL文件生成成功: {output_path}")
    print(f"📊 数据统计:")
    print(f"   - 样品信息: 36条 (ID: 56-91)")
    print(f"   - 测试记录: 36条 (ID: 46-81)")
    print(f"   - 测试详情: {36 * 25}条 (ID自增)")
    print(f"   - 整车指数: ZOi={zoi}, ZVi={zvi}")


if __name__ == "__main__":
    main()
