#!/usr/bin/env python
"""
修改动刚度测试数据，创建一些小于目标值的数据用于测试红色显示功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.dynamic_stiffness.models import DynamicStiffnessData
from decimal import Decimal

def modify_test_data():
    """修改测试数据，创建一些小于目标值的情况"""
    
    # 获取前几条数据
    data_list = DynamicStiffnessData.objects.all()[:5]
    
    for i, data in enumerate(data_list):
        print(f"修改数据 {i+1}: {data.subsystem} - {data.test_point}")
        
        # 修改X方向的一些频率值，使其小于目标值
        if data.target_stiffness_x:
            target_x = float(data.target_stiffness_x)
            data.freq_50_x = Decimal(str(target_x * 0.8))  # 80% 的目标值
            data.freq_100_x = Decimal(str(target_x * 0.9))  # 90% 的目标值
            data.freq_200_x = Decimal(str(target_x * 1.2))  # 120% 的目标值（大于目标值）
            
        # 修改Y方向的一些频率值
        if data.target_stiffness_y:
            target_y = float(data.target_stiffness_y)
            data.freq_80_y = Decimal(str(target_y * 0.7))  # 70% 的目标值
            data.freq_125_y = Decimal(str(target_y * 0.95))  # 95% 的目标值
            data.freq_250_y = Decimal(str(target_y * 1.1))  # 110% 的目标值（大于目标值）
            
        # 修改Z方向的一些频率值
        if data.target_stiffness_z:
            target_z = float(data.target_stiffness_z)
            data.freq_160_z = Decimal(str(target_z * 0.85))  # 85% 的目标值
            data.freq_315_z = Decimal(str(target_z * 0.92))  # 92% 的目标值
            data.freq_400_z = Decimal(str(target_z * 1.15))  # 115% 的目标值（大于目标值）
        
        data.save()
        print(f"  - 已修改数据，创建了一些小于目标值的测试数据")
    
    print(f"\n✅ 成功修改了 {len(data_list)} 条数据")
    print("现在可以在前端测试红色显示功能了！")

if __name__ == '__main__':
    modify_test_data()
