import os

# 定义目录路径
directory_path = r"D:\pythonProject\zlbbses\nvh_django\backend\media\dynamic_stiffness\suspension_isolation"

# 检查目录是否存在
if os.path.exists(directory_path):
    # 获取目录下所有文件
    files = os.listdir(directory_path)

    # 定义常见图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.mp4')

    # 筛选出图片文件
    image_files = [f for f in files if f.lower().endswith(image_extensions)]

    # 打印图片文件名
    print(f"找到 {len(image_files)} 个图片文件：\n")
    for idx, image_file in enumerate(image_files, 1):
        print(f"{idx}. {image_file}")

    # 如果没有找到图片文件
    if not image_files:
        print("该目录下没有找到图片文件")
        print("\n目录下所有文件：")
        for f in files:
            print(f"  - {f}")
else:
    print(f"错误：目录不存在 - {directory_path}")



# import pandas as pd
# import json
#
# # 读取Excel文件
# excel_path = r"C:\Users\wangfan\Desktop\nvhdata\汉EV.xlsx"
# df = pd.read_excel(excel_path)
#
# # 设置vehicle_model_id
# vehicle_model_id = 5
#
# # 生成SQL插入语句
# sql_statements = []
#
# # 获取列名（从第二列开始，第一列是frequency标识）
# condition_point_ids = df.columns[1:].tolist()
#
# # 遍历每个condition_point_id（每一列）
# for col_idx, condition_point_id in enumerate(condition_point_ids, start=1):
#     # 提取频率值（第一列，跳过表头）
#     frequencies = df.iloc[:, 0].tolist()
#
#     # 提取对应的dB(A)值，并保留两位小数
#     db_values = df.iloc[:, col_idx].tolist()
#     db_values_rounded = [round(float(val), 2) for val in db_values]
#
#     # 构建JSON对象
#     spectrum_json = {
#         "frequency": frequencies,
#         "dB(A)": db_values_rounded
#     }
#
#     # 转换为JSON字符串，并转义单引号
#     json_str = json.dumps(spectrum_json, ensure_ascii=False)
#     json_str_escaped = json_str.replace("'", "\\'")
#
#     # 生成SQL插入语句
#     sql = f"""INSERT INTO `test_data_all` (`spectrum_json`, `vehicle_model_id`, `condition_point_id`)
# VALUES ('{json_str_escaped}', {vehicle_model_id}, {condition_point_id});"""
#
#     sql_statements.append(sql)
#
# # 将SQL语句写入文件
# output_file = r"C:\Users\wangfan\Desktop\nvhdata\HANEVinsert_statements.sql"
# with open(output_file, 'w', encoding='utf-8') as f:
#     f.write('\n\n'.join(sql_statements))
#
# print(f"成功生成 {len(sql_statements)} 条SQL插入语句")
# print(f"SQL文件已保存至: {output_file}")
#
# # 打印前两条SQL语句作为示例
# print("\n前两条SQL语句示例：")
# for i, sql in enumerate(sql_statements[:2], 1):
#     print(f"\n--- 语句 {i} ---")
#     print(sql)


# import pandas as pd
# import json
#
# # 读取Excel文件
# excel_file = r"C:\Users\wangfan\Desktop\01-NVH数据库数据\ntf_test_result.xlsx"
# df = pd.read_excel(excel_file)
#
# # vehicle_model_id 和 ntf_info_id 的映射关系
# mapping = {
#     1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
#     11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18,
#     19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 27,
#     27: 28, 28: 29, 29: 30, 30: 31, 31: 32, 32: 33, 33: 34, 34: 35,
#     35: 36, 36: 37, 37: 38, 38: 39, 39: 40
# }
#
# # 生成SQL文件
# output_file = r"C:\Users\wangfan\Desktop\01-NVH数据库数据\insert_ntf_test_result.sql"
#
# with open(output_file, 'w', encoding='utf-8') as f:
#     f.write("-- 插入 ntf_test_result 数据\n")
#     f.write("SET NAMES utf8mb4;\n")
#     f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
#
#     for index, row in df.iterrows():
#         # 获取字段值
#         id_val = row['id'] if pd.notna(row['id']) else 'NULL'
#         measurement_point = str(row['measurement_point']).replace("'", "\\'") if pd.notna(
#             row['measurement_point']) else ''
#         vehicle_model_id = int(row['vehicle_model_id']) if pd.notna(row['vehicle_model_id']) else None
#
#         # 根据映射关系获取 ntf_info_id
#         if vehicle_model_id and vehicle_model_id in mapping:
#             ntf_info_id = mapping[vehicle_model_id]
#         else:
#             print(f"警告: 第 {index + 2} 行的 vehicle_model_id={vehicle_model_id} 没有对应的映射关系，跳过")
#             continue
#
#         # 处理 ntf_curve (JSON字段)
#         if pd.notna(row['ntf_curve']) and str(row['ntf_curve']).strip():
#             try:
#                 # 如果已经是JSON格式，直接使用
#                 ntf_curve = json.dumps(json.loads(str(row['ntf_curve'])), ensure_ascii=False).replace("'", "\\'")
#                 ntf_curve_sql = f"'{ntf_curve}'"
#             except:
#                 # 如果不是JSON，尝试转换
#                 ntf_curve_sql = 'NULL'
#         else:
#             ntf_curve_sql = 'NULL'
#
#         # 处理 layout_image_url
#         if pd.notna(row['layout_image_url']) and str(row['layout_image_url']).strip():
#             layout_image_url = str(row['layout_image_url']).replace("'", "\\'")
#             layout_image_url_sql = f"'{layout_image_url}'"
#         else:
#             layout_image_url_sql = 'NULL'
#
#         # 生成INSERT语句
#         sql = f"INSERT INTO `ntf_test_result` (`id`, `measurement_point`, `layout_image_url`, `ntf_curve`, `ntf_info_id`) VALUES ({id_val}, '{measurement_point}', {layout_image_url_sql}, {ntf_curve_sql}, {ntf_info_id});\n"
#
#         f.write(sql)
#
#     f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")
#
# print(f"SQL文件已生成: {output_file}")
# print(f"共处理 {len(df)} 条记录")



# import pandas as pd
# import json
# from collections import defaultdict
#
# # 配置
# EXCEL_FILE = r"C:\Users\wangfan\Desktop\数据调试.xlsx"
# OUTPUT_SQL = r"C:\Users\wangfan\Desktop\01-NVH数据库数据\update_ntf_curve.sql"
#
#
# def calculate_stats(frequency, values):
#     """计算20-200和200-500频率段的最大值"""
#     df = pd.DataFrame({'freq': frequency, 'val': values})
#
#     max_20_200 = df[df['freq'] <= 200]['val'].max()
#     max_200_500 = df[(df['freq'] > 200) & (df['freq'] <= 500)]['val'].max()
#
#     return {
#         "max_20_200": round(float(max_20_200), 2) if pd.notna(max_20_200) else None,
#         "max_200_500": round(float(max_200_500), 2) if pd.notna(max_200_500) else None
#     }
#
#
# def parse_column_name(col_name):
#     """解析列名，返回(id, position, direction)
#     例如: '631_Front_X' -> ('631', 'front', 'x')
#     """
#     # 跳过频率列（可能是Frequency或频率）
#     if col_name in ['Frequency', '频率', 'frequency']:
#         return None, None, None
#
#     parts = str(col_name).split('_')
#     if len(parts) == 3:
#         record_id = parts[0]
#         position = parts[1].lower()  # Front -> front
#         direction = parts[2].lower()  # X -> x
#         return record_id, position, direction
#     return None, None, None
#
#
# def get_frequency_column(df):
#     """智能识别频率列"""
#     # 可能的频率列名
#     possible_names = ['Frequency', 'frequency', '频率', 'freq', 'Freq']
#
#     for name in possible_names:
#         if name in df.columns:
#             return name
#
#     # 如果都找不到，返回第一列
#     return df.columns[0]
#
#
# def process_excel(file_path):
#     """处理Excel文件，返回按ID组织的数据"""
#     data_by_id = defaultdict(lambda: {'front': None, 'middle': None, 'rear': None})
#
#     # 读取三个sheet
#     sheet_names = [0, 1, 2]  # Sheet1, Sheet2, Sheet3
#
#     for sheet_idx in sheet_names:
#         print(f"\n正在处理 Sheet {sheet_idx + 1}...")
#         df = pd.read_excel(file_path, sheet_name=sheet_idx)
#
#         # 清理列名（去除空格和制表符）
#         df.columns = df.columns.str.strip()
#
#         # 打印列名用于调试
#         print(f"列名: {df.columns.tolist()}")
#
#         # 智能识别频率列
#         freq_col = get_frequency_column(df)
#         print(f"使用频率列: {freq_col}")
#
#         # 获取频率列
#         frequency = df[freq_col].round(2).tolist()
#         print(f"频率范围: {frequency[0]} - {frequency[-1]}, 共 {len(frequency)} 个点")
#
#         # 处理每一列（除了频率列）
#         for col in df.columns:
#             if col == freq_col:
#                 continue
#
#             record_id, position, direction = parse_column_name(col)
#
#             if record_id is None:
#                 print(f"警告: 无法解析列名 '{col}'")
#                 continue
#
#             print(f"  处理: ID={record_id}, Position={position}, Direction={direction}")
#
#             # 初始化该ID的position数据结构
#             if data_by_id[record_id][position] is None:
#                 data_by_id[record_id][position] = {
#                     'frequency': frequency,
#                     'x_values': [],
#                     'y_values': [],
#                     'z_values': [],
#                     'stats': {'x': {}, 'y': {}, 'z': {}}
#                 }
#
#             # 获取数值并保留两位小数
#             values = df[col].round(2).tolist()
#
#             # 存储数据到对应的方向
#             data_by_id[record_id][position][f'{direction}_values'] = values
#
#             # 计算stats
#             data_by_id[record_id][position]['stats'][direction] = calculate_stats(frequency, values)
#
#     return data_by_id
#
#
# def generate_sql(data_by_id, output_file):
#     """生成SQL更新语句"""
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write("-- NTF Curve Update SQL\n")
#         f.write("-- Generated automatically\n\n")
#
#         for record_id, positions in sorted(data_by_id.items(), key=lambda x: int(x[0])):
#             # 构建JSON对象
#             ntf_curve = {
#                 'front': positions['front'],
#                 'middle': positions['middle'],
#                 'rear': positions['rear']
#             }
#
#             # 转换为JSON字符串（紧凑格式）
#             json_str = json.dumps(ntf_curve, ensure_ascii=False, separators=(',', ':'))
#
#             # 转义单引号和反斜杠（MySQL要求）
#             json_str_escaped = json_str.replace('\\', '\\\\').replace("'", "\\'")
#
#             # 生成UPDATE语句
#             sql = f"UPDATE `ntf_test_result` SET `ntf_curve` = '{json_str_escaped}' WHERE `id` = {record_id};\n"
#             f.write(sql)
#
#         f.write(f"\n-- Total {len(data_by_id)} records updated\n")
#
#
# def main():
#     print("开始处理Excel文件...")
#     try:
#         data_by_id = process_excel(EXCEL_FILE)
#
#         print(f"\n找到 {len(data_by_id)} 条记录")
#
#         # 显示找到的所有ID
#         print(f"ID列表: {sorted([int(id) for id in data_by_id.keys()])}")
#
#         print("\n生成SQL文件...")
#         generate_sql(data_by_id, OUTPUT_SQL)
#
#         print(f"完成！SQL文件已保存到: {OUTPUT_SQL}")
#
#         # 打印第一条记录作为示例
#         if data_by_id:
#             first_id = sorted(data_by_id.keys(), key=lambda x: int(x))[0]
#             print(f"\n示例 (ID={first_id}):")
#             example_data = {
#                 'front': data_by_id[first_id]['front'],
#                 'middle': data_by_id[first_id]['middle'],
#                 'rear': data_by_id[first_id]['rear']
#             }
#             # 只打印部分数据，避免输出太长
#             print(f"  Front频率点数: {len(example_data['front']['frequency']) if example_data['front'] else 0}")
#             print(f"  Middle频率点数: {len(example_data['middle']['frequency']) if example_data['middle'] else 0}")
#             print(f"  Rear频率点数: {len(example_data['rear']['frequency']) if example_data['rear'] else 0}")
#
#             # 打印stats示例
#             if example_data['front']:
#                 print(f"\n  Front Stats示例:")
#                 print(json.dumps(example_data['front']['stats'], indent=4, ensure_ascii=False))
#
#     except FileNotFoundError:
#         print(f"错误: 找不到文件 '{EXCEL_FILE}'")
#     except Exception as e:
#         print(f"错误: {e}")
#         import traceback
#         traceback.print_exc()
#
#
# if __name__ == '__main__':
#     main()

# 重命名
# import os
#
# # 指定文件夹路径
# folder_path = r"C:\Users\wangfan\Desktop\已解密--wangyulei\悬架隔振率\03--测试结果曲线图"
#
# # 遍历文件夹中的所有文件
# for filename in os.listdir(folder_path):
#     # 获取文件的完整路径
#     old_file = os.path.join(folder_path, filename)
#
#     # 只处理文件，跳过文件夹
#     if os.path.isfile(old_file):
#         # 分离文件名和扩展名
#         name, ext = os.path.splitext(filename)
#
#         # 检查是否是图片文件（可根据需要添加更多格式）
#         if ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
#             # 构造新文件名
#             new_filename = f"{name}曲线图{ext}"
#             new_file = os.path.join(folder_path, new_filename)
#
#             # 重命名文件
#             os.rename(old_file, new_file)
#             print(f"已重命名: {filename} -> {new_filename}")
#
# print("所有图片文件重命名完成！")

