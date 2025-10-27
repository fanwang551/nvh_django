import pandas as pd
import json
import math
from pathlib import Path


def calculate_max_in_range(frequency_list, value_list, min_freq, max_freq):
    """计算指定频率范围内的最大值"""
    max_val = None
    for freq, val in zip(frequency_list, value_list):
        if min_freq <= freq <= max_freq and not (isinstance(val, float) and math.isnan(val)):
            if max_val is None or val > max_val:
                max_val = val
    return round(max_val, 2) if max_val is not None else None


def parse_column_name(col_name):
    """解析列名，返回 (id, position, direction)"""
    parts = col_name.split('_')
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return None, None, None


def process_excel_to_sql(excel_path, output_dir='./'):
    """处理Excel文件并生成SQL文件"""

    # 读取Excel文件
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names[1:]  # 跳过第一个sheet

    # 存储所有记录的数据
    records = {}  # {id: {position: {direction: values}}}

    print(f"开始处理 {len(sheet_names)} 个sheets...")

    # 遍历所有sheet
    for sheet_name in sheet_names:
        print(f"处理 sheet: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        # 获取频率列
        frequency_col = df.iloc[:, 0].tolist()

        # 处理每一列数据
        for col in df.columns[1:]:
            record_id, position, direction = parse_column_name(col)

            if not record_id or not position or not direction:
                continue

            # 初始化数据结构
            if record_id not in records:
                records[record_id] = {}
            if position not in records[record_id]:
                records[record_id][position] = {
                    'frequency': frequency_col,
                    'x_values': [],
                    'y_values': [],
                    'z_values': []
                }

            # 存储数据
            values = df[col].tolist()
            direction_lower = direction.lower()
            records[record_id][position][f'{direction_lower}_values'] = values

    print(f"共处理 {len(records)} 条记录")

    # 生成SQL语句
    sql_statements = []

    for record_id, positions in records.items():
        ntf_curve = {}

        for position, data in positions.items():
            position_lower = position.lower()

            # 计算统计数据
            stats = {}
            for direction in ['x', 'y', 'z']:
                values_key = f'{direction}_values'
                if values_key in data and data[values_key]:
                    max_20_200 = calculate_max_in_range(
                        data['frequency'], data[values_key], 20, 200
                    )
                    max_200_500 = calculate_max_in_range(
                        data['frequency'], data[values_key], 200, 500
                    )
                    stats[direction] = {
                        'max_20_200': max_20_200,
                        'max_200_500': max_200_500
                    }

            # 构建位置数据
            ntf_curve[position_lower] = {
                'frequency': data['frequency'],
                'x_values': data.get('x_values', []),
                'y_values': data.get('y_values', []),
                'z_values': data.get('z_values', []),
                'stats': stats
            }

        # 生成SQL更新语句
        json_str = json.dumps(ntf_curve, ensure_ascii=False)
        # 转义单引号
        json_str = json_str.replace("'", "\\'")

        sql = f"UPDATE `ntf_test_result` SET `ntf_curve` = '{json_str}' WHERE `id` = {record_id};\n"
        sql_statements.append(sql)

    # 分成三个文件
    total = len(sql_statements)
    chunk_size = math.ceil(total / 3)

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for i in range(3):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total)

        file_path = output_path / f'update_ntf_curve_part_{i + 1}.sql'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('-- NTF Curve Update Script\n')
            f.write(f'-- Part {i + 1} of 3\n')
            f.write(f'-- Records: {start_idx + 1} to {end_idx}\n\n')

            for sql in sql_statements[start_idx:end_idx]:
                f.write(sql)

        print(f"生成文件: {file_path} (包含 {end_idx - start_idx} 条记录)")

    print("\n处理完成！")


if __name__ == '__main__':
    excel_path = r"C:\Users\wangfan\Desktop\整车ATF&NTF数据.xlsx"
    output_dir = r"C:\Users\wangfan\Desktop\sql_output"

    process_excel_to_sql(excel_path, output_dir)
