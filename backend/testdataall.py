import os
import json
import pandas as pd
import pymysql


def create_connection():
    """创建到 MySQL 的连接（UTF-8），优先读取环境变量。"""
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '3306'))
    database = os.getenv('DB_NAME', 'nvh_database')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '123456')

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            db=database,
            user=user,
            password=password,
            charset='utf8mb4',
            autocommit=False,
            cursorclass=pymysql.cursors.Cursor,
        )
        print("✅ 成功连接到 MySQL 数据库")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def insert_test_data(connection, excel_file: str):
    """从 Excel 写入 test_data_all：只插入 spectrum_json、vehicle_model_id、condition_point_id、test_date。

    Excel 结构（两行表头）：
    - 第1列：frequency（Hz）
    - 第1行（从第2列起）：测点ID（1、2、3…）
    - 第2行：单位或列名（第1列为 frequency（Hz），其他列为 dB(A)）
    数据区：每行是一个频率点对应所有测点的声压级。
    本脚本按“列”为单位插入：每个测点一条记录。
    """
    try:
        # 读取两行表头
        df = pd.read_excel(excel_file, engine='openpyxl', header=[0, 1])

        if df.shape[1] < 2:
            raise ValueError('Excel 列数不足，至少需要一列频率和一列测点数据')

        # 频率列在第1列，过滤掉空频率行，保证频率和 dB(A) 对齐
        freq_series_all = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        valid_mask = freq_series_all.notna()
        frequency_values = freq_series_all[valid_mask].astype(float).tolist()

        vehicle_model_id = 7
        test_date = '2025-09-11'

        insert_sql = (
            "INSERT INTO test_data_all (spectrum_json, vehicle_model_id, condition_point_id, test_date) "
            "VALUES (%s, %s, %s, %s)"
        )

        cur = connection.cursor()
        success_count = 0
        error_count = 0

        # 从第2列起，每列代表一个测点
        for col_idx in range(1, df.shape[1]):
            col = df.columns[col_idx]

            # 解析测点ID：优先取多级表头的第1级
            id_label = col[0] if isinstance(col, tuple) else col
            try:
                condition_point_id = int(float(str(id_label).strip()))
            except Exception:
                error_count += 1
                print(f"⚠️ 跳过第{col_idx + 1}列，无法解析测点ID：{col}")
                continue

            try:
                # 该测点的 dB(A)，按有效频率行筛选并四舍五入
                db_all = pd.to_numeric(df.iloc[:, col_idx], errors='coerce')
                db_masked = db_all[valid_mask]
                db_values = [round(float(x), 2) if pd.notna(x) else None for x in db_masked.tolist()]

                spectrum_json = {
                    "frequency": frequency_values,
                    "dB(A)": db_values,
                }
                spectrum_json_str = json.dumps(spectrum_json, ensure_ascii=False)

                cur.execute(
                    insert_sql,
                    (spectrum_json_str, vehicle_model_id, condition_point_id, test_date),
                )
                success_count += 1
                print(f"✅ 已插入测点ID: {condition_point_id}")
            except Exception as e:
                error_count += 1
                print(f"⚠️ 插入测点ID {condition_point_id} 失败: {e}")

        connection.commit()
        print("\n" + "=" * 50)
        print("插入完成")
        print(f"成功: {success_count} 条")
        print(f"失败: {error_count} 条")
        print("=" * 50)

        try:
            cur.close()
        except Exception:
            pass

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        try:
            connection.rollback()
        except Exception:
            pass


def main():
    # Excel 文件路径：默认使用与脚本同目录下的 “稳态数据1.xlsx”
    script_dir = os.path.dirname(os.path.abspath(__file__))
    EXCEL_FILE = os.path.join(script_dir, '稳态数据1.xlsx')

    print("开始导入数据…")
    print(f"Excel 文件: {EXCEL_FILE}")
    print(f"车型ID: 1")
    print(f"测试日期: 2025-09-11")
    print("=" * 50 + "\n")

    conn = create_connection()
    if conn:
        insert_test_data(conn, EXCEL_FILE)
        try:
            conn.close()
            print("\n数据库连接已关闭")
        except Exception:
            pass
    else:
        print("无法连接到数据库，已退出")


if __name__ == "__main__":
    main()

