import pandas as pd
import json
from collections import defaultdict

# 配置
EXCEL_FILES = [
    r"C:\Users\wangfan\Desktop\01-NVH数据库数据\37_小鹏P7_NTF.xlsx",
    r"C:\Users\wangfan\Desktop\01-NVH数据库数据\40_长安糯玉米_NTF.xlsx",
    r"C:\Users\wangfan\Desktop\01-NVH数据库数据\32_大众ID4X_NTF.xlsx",
    r"C:\Users\wangfan\Desktop\01-NVH数据库数据\38_长安深蓝SL03_NTF.xlsx",
    r"C:\Users\wangfan\Desktop\01-NVH数据库数据\39_岚图梦想家_NTF.xlsx"

]
OUTPUT_SQL = r"C:\Users\wangfan\Desktop\01-NVH数据库数据\update_ntf_curve32_37_38_39_40.sql"


def calculate_stats(frequency, values):
    """计算20-200和200-500频率段的最大值"""
    df = pd.DataFrame({'freq': frequency, 'val': values})

    max_20_200 = df[df['freq'] <= 200]['val'].max()
    max_200_500 = df[(df['freq'] > 200) & (df['freq'] <= 500)]['val'].max()

    return {
        "max_20_200": round(float(max_20_200), 2) if pd.notna(max_20_200) else None,
        "max_200_500": round(float(max_200_500), 2) if pd.notna(max_200_500) else None
    }


def parse_column_name(col_name):
    """解析列名，返回(id, position, direction)
    例如: '846_Rear_X' -> ('846', 'rear', 'x')
    """
    # 跳过频率列
    if col_name in ['Frequency', '频率', 'frequency', 'freq', 'Freq']:
        return None, None, None

    parts = str(col_name).strip().split('_')
    if len(parts) == 3:
        record_id = parts[0]
        position = parts[1].lower()  # Rear -> rear, Front -> front
        direction = parts[2].lower()  # X -> x, Y -> y, Z -> z
        return record_id, position, direction

    return None, None, None


def get_frequency_column(df):
    """智能识别频率列"""
    possible_names = ['Frequency', 'frequency', '频率', 'freq', 'Freq']

    for name in possible_names:
        if name in df.columns:
            return name

    # 如果都找不到，返回第一列
    return df.columns[0]


def process_sheet(df, expected_position):
    """处理单个sheet，返回按ID组织的数据"""
    # 清理列名
    df.columns = df.columns.str.strip()

    print(f"  列名: {df.columns.tolist()}")

    # 智能识别频率列
    freq_col = get_frequency_column(df)
    print(f"  使用频率列: {freq_col}")

    # 获取频率列
    frequency = df[freq_col].round(2).tolist()
    print(f"  频率范围: {frequency[0]} - {frequency[-1]}, 共 {len(frequency)} 个点")

    # 按ID组织数据
    data_by_id = defaultdict(lambda: {
        'frequency': frequency,
        'x_values': [],
        'y_values': [],
        'z_values': [],
        'stats': {'x': {}, 'y': {}, 'z': {}}
    })

    # 处理每一列（除了频率列）
    for col in df.columns:
        if col == freq_col:
            continue

        record_id, position, direction = parse_column_name(col)

        if record_id is None:
            print(f"  警告: 无法解析列名 '{col}'，跳过")
            continue

        # 验证position是否匹配
        if position != expected_position:
            print(f"  警告: 列 '{col}' 的位置 '{position}' 与预期 '{expected_position}' 不匹配")
            continue

        print(f"  处理: ID={record_id}, Position={position}, Direction={direction}")

        # 获取数值并保留两位小数
        values = df[col].round(2).tolist()

        # 存储数据到对应的方向
        data_by_id[record_id][f'{direction}_values'] = values

        # 计算stats
        data_by_id[record_id]['stats'][direction] = calculate_stats(frequency, values)

    return dict(data_by_id)


def process_excel_file(file_path, file_id):
    """处理单个Excel文件，返回按ID组织的数据"""
    import os
    filename = os.path.basename(file_path)
    print(f"\n{'=' * 60}")
    print(f"处理文件: {filename} (文件ID={file_id})")
    print(f"{'=' * 60}")

    all_data = defaultdict(lambda: {
        'front': None,
        'middle': None,
        'rear': None
    })

    # 读取Front sheet
    front_sheet_name = f"{file_id}_Front"
    try:
        print(f"\n读取 Sheet: {front_sheet_name}")
        df_front = pd.read_excel(file_path, sheet_name=front_sheet_name)
        front_data = process_sheet(df_front, 'front')

        # 将front数据合并到all_data
        for record_id, data in front_data.items():
            all_data[record_id]['front'] = data
            print(f"  -> ID {record_id} 的 Front 数据已添加")

    except Exception as e:
        print(f"  错误: 无法读取 {front_sheet_name}: {e}")

    # 读取Rear sheet
    rear_sheet_name = f"{file_id}_Rear"
    try:
        print(f"\n读取 Sheet: {rear_sheet_name}")
        df_rear = pd.read_excel(file_path, sheet_name=rear_sheet_name)
        rear_data = process_sheet(df_rear, 'rear')

        # 将rear数据合并到all_data
        for record_id, data in rear_data.items():
            all_data[record_id]['rear'] = data
            print(f"  -> ID {record_id} 的 Rear 数据已添加")

    except Exception as e:
        print(f"  错误: 无法读取 {rear_sheet_name}: {e}")

    return dict(all_data)


def process_all_files(file_paths):
    """处理所有Excel文件"""
    all_data = defaultdict(lambda: {
        'front': None,
        'middle': None,
        'rear': None
    })

    for file_path in file_paths:
        try:
            # 从文件名提取文件ID（例如：37_小鹏P7_NTF.xlsx -> 37）
            import os
            filename = os.path.basename(file_path)
            file_id = filename.split('_')[0]

            file_data = process_excel_file(file_path, file_id)

            # 合并数据
            for record_id, positions in file_data.items():
                if positions['front']:
                    all_data[record_id]['front'] = positions['front']
                if positions['rear']:
                    all_data[record_id]['rear'] = positions['rear']
                # middle 始终为 None

        except FileNotFoundError:
            print(f"错误: 找不到文件 '{file_path}'")
        except Exception as e:
            print(f"错误: 处理文件 '{file_path}' 时出错: {e}")
            import traceback
            traceback.print_exc()

    return dict(all_data)


def generate_sql(data_by_id, output_file):
    """生成SQL更新语句"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- NTF Curve Update SQL\n")
        f.write("-- Generated automatically\n")
        f.write("-- Updates ntf_curve column in ntf_test_result table\n")
        f.write("-- Note: middle position is always null\n\n")

        sorted_ids = sorted(data_by_id.keys(), key=lambda x: int(x))

        for record_id in sorted_ids:
            positions = data_by_id[record_id]

            # 构建JSON对象（middle始终为null）
            ntf_curve = {
                'front': positions['front'],
                'middle': None,
                'rear': positions['rear']
            }

            # 转换为JSON字符串（紧凑格式）
            json_str = json.dumps(ntf_curve, ensure_ascii=False, separators=(',', ':'))

            # 转义单引号和反斜杠（MySQL要求）
            json_str_escaped = json_str.replace('\\', '\\\\').replace("'", "\\'")

            # 生成UPDATE语句
            sql = f"UPDATE `ntf_test_result` SET `ntf_curve` = '{json_str_escaped}' WHERE `id` = {record_id};\n"
            f.write(sql)

        f.write(f"\n-- Total {len(data_by_id)} records updated\n")
        f.write(f"-- Record IDs: {', '.join(sorted_ids)}\n")


def main():
    print("=" * 60)
    print("NTF数据处理程序")
    print("=" * 60)
    print(f"输出SQL文件: {OUTPUT_SQL}")
    print(f"处理文件数量: {len(EXCEL_FILES)}")

    data_by_id = process_all_files(EXCEL_FILES)

    print(f"\n{'=' * 60}")
    print(f"处理完成统计")
    print(f"{'=' * 60}")
    print(f"总共找到 {len(data_by_id)} 条记录")
    print(f"ID列表: {sorted([int(id) for id in data_by_id.keys()])}")

    if not data_by_id:
        print("错误: 没有找到任何数据")
        return

    # 统计每个ID的数据完整性
    print(f"\n数据完整性检查:")
    for record_id in sorted(data_by_id.keys(), key=lambda x: int(x)):
        positions = data_by_id[record_id]
        has_front = positions['front'] is not None
        has_rear = positions['rear'] is not None
        status = []
        if has_front:
            status.append("Front✓")
        else:
            status.append("Front✗")
        if has_rear:
            status.append("Rear✓")
        else:
            status.append("Rear✗")
        print(f"  ID {record_id}: {' | '.join(status)}")

    print(f"\n生成SQL文件...")
    generate_sql(data_by_id, OUTPUT_SQL)

    print(f"\n完成！SQL文件已保存到: {OUTPUT_SQL}")

    # 打印第一条记录作为示例
    first_id = sorted(data_by_id.keys(), key=lambda x: int(x))[0]
    print(f"\n{'=' * 60}")
    print(f"示例数据 (ID={first_id}):")
    print(f"{'=' * 60}")
    example_data = data_by_id[first_id]

    if example_data['front']:
        print(f"Front:")
        print(f"  频率点数: {len(example_data['front']['frequency'])}")
        print(f"  X方向数据点数: {len(example_data['front']['x_values'])}")
        print(f"  Y方向数据点数: {len(example_data['front']['y_values'])}")
        print(f"  Z方向数据点数: {len(example_data['front']['z_values'])}")
        print(f"  Stats: {json.dumps(example_data['front']['stats'], indent=4, ensure_ascii=False)}")

    print(f"\nMiddle: None (始终为空)")

    if example_data['rear']:
        print(f"\nRear:")
        print(f"  频率点数: {len(example_data['rear']['frequency'])}")
        print(f"  X方向数据点数: {len(example_data['rear']['x_values'])}")
        print(f"  Y方向数据点数: {len(example_data['rear']['y_values'])}")
        print(f"  Z方向数据点数: {len(example_data['rear']['z_values'])}")
        print(f"  Stats: {json.dumps(example_data['rear']['stats'], indent=4, ensure_ascii=False)}")


if __name__ == '__main__':
    main()
