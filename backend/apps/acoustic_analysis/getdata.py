import numpy as np
import pandas as pd
import os
from pathlib import Path


def ensure_directory():
    """确保目标目录存在"""
    target_dir = r"D:\pythonProject\zlbbses\nvh_django\backend\media\dynamic_noise_data\dynamic_spectrum_data"
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    return target_dir


def generate_speed_excel(save_dir):
    """生成车速相关的Excel文件"""
    # 生成频率数组 (0-25600, 8600个点)
    frequencies = np.linspace(0, 25600, 8600).round(2)

    # 生成车速数组 (0-120, 300个点)
    speeds = np.linspace(0, 120, 300).round(2)

    # 生成随机dB(A)数据 (40-70)
    db_data = np.random.uniform(40, 70, (8600, 300)).round(2)

    # 创建DataFrame
    df = pd.DataFrame(db_data, columns=speeds)
    df.insert(0, 'frequency', frequencies)

    # 保存为Excel
    excel_file = os.path.join(save_dir, 'speed_noise_data.xlsx')
    df.to_excel(excel_file, index=False, sheet_name='Speed_Noise')
    print(f"✓ 已生成车速Excel文件: {excel_file}")

    return frequencies, speeds, db_data


def generate_rpm_excel(save_dir):
    """生成转速相关的Excel文件"""
    # 生成频率数组 (0-25600, 8600个点)
    frequencies = np.linspace(0, 25600, 8600).round(2)

    # 生成转速数组 (0-18000, 700个点)
    rpms = np.linspace(0, 18000, 700).round(2)

    # 生成随机dB(A)数据 (40-70)
    db_data = np.random.uniform(40, 70, (8600, 700)).round(2)

    # 创建DataFrame
    df = pd.DataFrame(db_data, columns=rpms)
    df.insert(0, 'frequency', frequencies)

    # 保存为Excel
    excel_file = os.path.join(save_dir, 'rpm_noise_data.xlsx')
    df.to_excel(excel_file, index=False, sheet_name='RPM_Noise')
    print(f"✓ 已生成转速Excel文件: {excel_file}")

    return frequencies, rpms, db_data


def convert_speed_to_npz(save_dir):
    """将车速Excel数据转换为NPZ格式"""
    freq_speed, speeds, db_speed = generate_speed_excel(save_dir)

    # 保存为NPZ文件
    npz_file = os.path.join(save_dir, 'speed_noise_data.npz')
    np.savez_compressed(
        npz_file,
        frequencies=freq_speed,
        speeds=speeds,
        db_data=db_speed
    )
    print(f"✓ 已生成车速NPZ文件: {npz_file}")

    return npz_file


def convert_rpm_to_npz(save_dir):
    """将转速Excel数据转换为NPZ格式"""
    freq_rpm, rpms, db_rpm = generate_rpm_excel(save_dir)

    # 保存为NPZ文件
    npz_file = os.path.join(save_dir, 'rpm_noise_data.npz')
    np.savez_compressed(
        npz_file,
        frequencies=freq_rpm,
        rpms=rpms,
        db_data=db_rpm
    )
    print(f"✓ 已生成转速NPZ文件: {npz_file}")

    return npz_file


def verify_npz(npz_file, data_type):
    """验证NPZ文件内容"""
    print("\n" + "=" * 60)
    print(f"{data_type}NPZ文件验证:")
    print("=" * 60)

    data = np.load(npz_file)

    print(f"\n【{data_type}数据】")
    print(f"  文件路径: {npz_file}")
    print(f"  频率范围: {data['frequencies'].min():.2f} - {data['frequencies'].max():.2f} Hz")
    print(f"  频率点数: {len(data['frequencies'])}")

    if data_type == "车速":
        param_name = "speeds"
        unit = "km/h"
    else:
        param_name = "rpms"
        unit = "RPM"

    print(f"  {data_type}范围: {data[param_name].min():.2f} - {data[param_name].max():.2f} {unit}")
    print(f"  {data_type}点数: {len(data[param_name])}")
    print(f"  dB(A)范围: {data['db_data'].min():.2f} - {data['db_data'].max():.2f}")
    print(f"  数据矩阵形状: {data['db_data'].shape}")

    print(f"\n【数据示例】")
    print(f"{data_type}数据前5行前5列:")
    print(data['db_data'][:5, :5])

    # 显示NPZ文件中的所有键
    print(f"\nNPZ文件包含的数据键: {list(data.keys())}")

    # 显示文件大小
    file_size = os.path.getsize(npz_file) / (1024 * 1024)  # 转换为MB
    print(f"文件大小: {file_size:.2f} MB")

    data.close()


def load_and_use_speed_npz(npz_file):
    """演示如何加载和使用车速NPZ文件"""
    print("\n" + "=" * 60)
    print("车速NPZ文件使用示例:")
    print("=" * 60)

    # 加载数据
    data = np.load(npz_file)

    # 示例1: 获取特定车速下的噪声数据
    speed_index = 150  # 中间某个车速
    speed_value = data['speeds'][speed_index]
    noise_at_speed = data['db_data'][:, speed_index]
    print(f"\n车速 {speed_value:.2f} km/h 时的噪声数据:")
    print(f"  频率点数: {len(noise_at_speed)}")
    print(f"  噪声范围: {noise_at_speed.min():.2f} - {noise_at_speed.max():.2f} dB(A)")

    # 示例2: 获取特定频率下的噪声数据
    freq_index = 4300  # 中间某个频率
    freq_value = data['frequencies'][freq_index]
    noise_at_freq = data['db_data'][freq_index, :]
    print(f"\n频率 {freq_value:.2f} Hz 时的噪声数据:")
    print(f"  车速点数: {len(noise_at_freq)}")
    print(f"  噪声范围: {noise_at_freq.min():.2f} - {noise_at_freq.max():.2f} dB(A)")

    data.close()


def load_and_use_rpm_npz(npz_file):
    """演示如何加载和使用转速NPZ文件"""
    print("\n" + "=" * 60)
    print("转速NPZ文件使用示例:")
    print("=" * 60)

    # 加载数据
    data = np.load(npz_file)

    # 示例1: 获取特定转速下的噪声数据
    rpm_index = 350  # 中间某个转速
    rpm_value = data['rpms'][rpm_index]
    noise_at_rpm = data['db_data'][:, rpm_index]
    print(f"\n转速 {rpm_value:.2f} RPM 时的噪声数据:")
    print(f"  频率点数: {len(noise_at_rpm)}")
    print(f"  噪声范围: {noise_at_rpm.min():.2f} - {noise_at_rpm.max():.2f} dB(A)")

    # 示例2: 获取特定频率下的噪声数据
    freq_index = 4300  # 中间某个频率
    freq_value = data['frequencies'][freq_index]
    noise_at_freq = data['db_data'][freq_index, :]
    print(f"\n频率 {freq_value:.2f} Hz 时的噪声数据:")
    print(f"  转速点数: {len(noise_at_freq)}")
    print(f"  噪声范围: {noise_at_freq.min():.2f} - {noise_at_freq.max():.2f} dB(A)")

    data.close()


if __name__ == "__main__":
    print("开始生成噪声数据文件...")
    print("=" * 60)

    # 确保目标目录存在
    save_directory = ensure_directory()
    print(f"\n目标目录: {save_directory}")
    print(f"目录已创建/确认存在\n")

    # 生成车速Excel和NPZ文件
    print("【步骤1: 生成车速数据】")
    speed_npz = convert_speed_to_npz(save_directory)

    # 生成转速Excel和NPZ文件
    print("\n【步骤2: 生成转速数据】")
    rpm_npz = convert_rpm_to_npz(save_directory)

    # 验证车速NPZ文件
    verify_npz(speed_npz, "车速")

    # 验证转速NPZ文件
    verify_npz(rpm_npz, "转速")

    # 演示如何使用车速NPZ文件
    load_and_use_speed_npz(speed_npz)

    # 演示如何使用转速NPZ文件
    load_and_use_rpm_npz(rpm_npz)

    print("\n" + "=" * 60)
    print("✓ 所有文件生成完成!")
    print("=" * 60)
    print(f"\n保存位置: {save_directory}")
    print("\n生成的文件:")
    print("  1. speed_noise_data.xlsx  - 车速噪声Excel (8600频率 × 300车速)")
    print("  2. speed_noise_data.npz   - 车速噪声NPZ文件")
    print("  3. rpm_noise_data.xlsx    - 转速噪声Excel (8600频率 × 700转速)")
    print("  4. rpm_noise_data.npz     - 转速噪声NPZ文件")

    print("\n" + "=" * 60)
    print("使用方法:")
    print("=" * 60)
    print("\n# 加载车速数据:")
    print(f"data = np.load(r'{os.path.join(save_directory, 'speed_noise_data.npz')}')")
    print("frequencies = data['frequencies']  # 频率数组")
    print("speeds = data['speeds']            # 车速数组")
    print("db_values = data['db_data']        # dB(A)数据矩阵")

    print("\n# 加载转速数据:")
    print(f"data = np.load(r'{os.path.join(save_directory, 'rpm_noise_data.npz')}')")
    print("frequencies = data['frequencies']  # 频率数组")
    print("rpms = data['rpms']                # 转速数组")
    print("db_values = data['db_data']        # dB(A)数据矩阵")

    # 列出目录中的所有文件
    print("\n" + "=" * 60)
    print("目录文件列表:")
    print("=" * 60)
    for file in os.listdir(save_directory):
        file_path = os.path.join(save_directory, file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"  {file} ({file_size:.2f} MB)")
