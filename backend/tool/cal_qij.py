import pandas as pd
import numpy as np
from datetime import datetime
import os

# ==================== 配置区 ====================
# 输入文件路径
SUBSTANCEINFO_FILE = 'substanceinfo.xlsx'
VOC_SAMPLE_INFO_FILE = 'voc_sample_info.xlsx'
SUBSTANCE_TEST_DETAILS_FILE = 'substance_test_details.xlsx'

# 输出文件路径
OUTPUT_FILE = 'substance_test_details_calculated.xlsx'
LOG_FILE = 'calculation_log.txt'


# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("物质测试详情计算程序")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 初始化日志
    log_messages = []

    try:
        # 1. 读取Excel文件
        print("步骤 1/5: 读取Excel文件...")
        substanceinfo_df = pd.read_excel(SUBSTANCEINFO_FILE)
        voc_sample_info_df = pd.read_excel(VOC_SAMPLE_INFO_FILE)
        substance_test_details_df = pd.read_excel(SUBSTANCE_TEST_DETAILS_FILE)

        print(f"  ✓ substanceinfo表: {len(substanceinfo_df)} 条记录")
        print(f"  ✓ voc_sample_info表: {len(voc_sample_info_df)} 条记录")
        print(f"  ✓ substance_test_details表: {len(substance_test_details_df)} 条记录\n")

        log_messages.append(f"总记录数: {len(substance_test_details_df)}")

        # 2. 数据验证
        print("步骤 2/5: 数据验证...")
        validate_data(substance_test_details_df, substanceinfo_df, log_messages)
        print()

        # 3. 数据关联
        print("步骤 3/5: 关联物质信息表...")
        merged_df = substance_test_details_df.merge(
            substanceinfo_df[['cas_no', 'odor_threshold', 'organic_threshold']],
            on='cas_no',
            how='left'
        )
        print(f"  ✓ 关联完成，共 {len(merged_df)} 条记录\n")

        # 4. 计算qij和wih
        print("步骤 4/5: 计算qij和wih...")
        calculate_qij_wih(merged_df, log_messages)
        print()

        # 5. 保存结果
        print("步骤 5/5: 保存结果...")
        # 只保留原始列和计算结果
        output_columns = substance_test_details_df.columns.tolist()
        result_df = merged_df[output_columns]

        result_df.to_excel(OUTPUT_FILE, index=False)
        print(f"  ✓ 结果已保存至: {OUTPUT_FILE}\n")

        # 6. 生成日志
        save_log(log_messages, result_df)

        # 7. 显示示例验证
        print("=" * 60)
        print("示例数据验证（前5条记录）:")
        print("=" * 60)
        display_sample_results(result_df)

        print("\n" + "=" * 60)
        print("计算完成！")
        print("=" * 60)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except FileNotFoundError as e:
        print(f"❌ 错误: 找不到文件 - {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def validate_data(test_details_df, substanceinfo_df, log_messages):
    """验证数据完整性"""
    # 检查必要列是否存在
    required_columns = ['cas_no', 'concentration', 'qij', 'wih']
    missing_columns = [col for col in required_columns if col not in test_details_df.columns]

    if missing_columns:
        raise ValueError(f"substance_test_details表缺少必要列: {missing_columns}")

    # 检查cas_no是否在substanceinfo表中
    test_cas_set = set(test_details_df['cas_no'].dropna())
    substance_cas_set = set(substanceinfo_df['cas_no'].dropna())
    missing_cas = test_cas_set - substance_cas_set

    if missing_cas:
        print(f"  ⚠ 警告: {len(missing_cas)} 个CAS编号在substanceinfo表中不存在")
        log_messages.append(f"缺失CAS编号数量: {len(missing_cas)}")
        log_messages.append(f"缺失的CAS编号: {', '.join(map(str, list(missing_cas)[:10]))}")
    else:
        print(f"  ✓ 所有CAS编号验证通过")


def calculate_qij_wih(df, log_messages):
    """计算qij和wih"""
    total_records = len(df)
    qij_success = 0
    qij_failed = 0
    wih_success = 0
    wih_failed = 0

    # 初始化结果列
    df['qij'] = np.nan
    df['wih'] = np.nan

    for idx, row in df.iterrows():
        concentration = row['concentration']
        odor_threshold = row['odor_threshold']
        organic_threshold = row['organic_threshold']

        # 计算qij
        if pd.notna(concentration) and pd.notna(odor_threshold) and odor_threshold != 0:
            try:
                df.at[idx, 'qij'] = round(concentration / odor_threshold, 3)
                qij_success += 1
            except Exception as e:
                qij_failed += 1
        else:
            qij_failed += 1

        # 计算wih
        if pd.notna(concentration) and pd.notna(organic_threshold) and organic_threshold != 0:
            try:
                df.at[idx, 'wih'] = round(concentration / organic_threshold, 3)
                wih_success += 1
            except Exception as e:
                wih_failed += 1
        else:
            wih_failed += 1

    # 记录统计信息
    print(f"  qij计算:")
    print(f"    ✓ 成功: {qij_success} 条")
    print(f"    ✗ 失败: {qij_failed} 条 (阈值缺失或为0)")
    print(f"  wih计算:")
    print(f"    ✓ 成功: {wih_success} 条")
    print(f"    ✗ 失败: {wih_failed} 条 (阈值缺失或为0)")

    log_messages.append(f"\nqij计算统计:")
    log_messages.append(f"  成功: {qij_success}")
    log_messages.append(f"  失败: {qij_failed}")
    log_messages.append(f"\nwih计算统计:")
    log_messages.append(f"  成功: {wih_success}")
    log_messages.append(f"  失败: {wih_failed}")


def save_log(log_messages, result_df):
    """保存计算日志"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("物质测试详情计算日志\n")
        f.write("=" * 60 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for msg in log_messages:
            f.write(msg + "\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("异常记录详情（阈值缺失）\n")
        f.write("=" * 60 + "\n")

        # 记录qij计算失败的记录
        qij_failed = result_df[result_df['qij'].isna()]
        if len(qij_failed) > 0:
            f.write(f"\nqij计算失败记录 ({len(qij_failed)}条):\n")
            for idx, row in qij_failed.head(20).iterrows():
                f.write(f"  ID: {row.get('id', 'N/A')}, CAS: {row['cas_no']}, "
                        f"浓度: {row['concentration']}, 气味阈值: {row.get('odor_threshold', 'N/A')}\n")

        # 记录wih计算失败的记录
        wih_failed = result_df[result_df['wih'].isna()]
        if len(wih_failed) > 0:
            f.write(f"\nwih计算失败记录 ({len(wih_failed)}条):\n")
            for idx, row in wih_failed.head(20).iterrows():
                f.write(f"  ID: {row.get('id', 'N/A')}, CAS: {row['cas_no']}, "
                        f"浓度: {row['concentration']}, 有机物阈值: {row.get('organic_threshold', 'N/A')}\n")

    print(f"  ✓ 日志已保存至: {LOG_FILE}")


def display_sample_results(df):
    """显示示例结果"""
    display_columns = ['id', 'cas_no', 'concentration', 'qij', 'wih']
    available_columns = [col for col in display_columns if col in df.columns]

    sample_df = df[available_columns].head(5)

    # 格式化输出
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', lambda x: f'{x:.3f}' if pd.notna(x) else 'NULL')

    print(sample_df.to_string(index=False))

    # 特别验证第一条记录（如果是甲醛）
    if len(df) > 0:
        first_row = df.iloc[0]
        if first_row['cas_no'] == '50-00-0':
            print("\n特别验证 - 甲醛记录 (CAS: 50-00-0):")
            print(f"  浓度: {first_row['concentration']}")
            print(f"  qij: {first_row['qij']} (预期: 3.000)")
            print(f"  wih: {first_row['wih']} (预期: 1.800)")


if __name__ == "__main__":
    main()
