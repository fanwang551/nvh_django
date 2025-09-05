#!/usr/bin/env python
"""
创建整车悬置隔振率测试数据的脚本
"""
import os
import sys
import django
from datetime import date

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.dynamic_stiffness.models import VehicleMountIsolationTest, MountIsolationData
from apps.modal.models import VehicleModel

def create_test_data():
    """创建测试数据"""
    print("开始创建整车悬置隔振率测试数据...")
    
    # 获取或创建车型
    vehicle_model, created = VehicleModel.objects.get_or_create(
        vehicle_model_name="五菱宏光MINI EV",
        defaults={
            'cle_model_code': 'WLHG_MINI_EV_001',
            'vin': 'LZWACAGA5MA999999',
            'drive_type': 'RWD',
            'configuration': '电动版',
            'production_year': 2024,
            'status': 'active'
        }
    )
    
    if created:
        print(f"创建车型: {vehicle_model.vehicle_model_name}")
    else:
        print(f"使用现有车型: {vehicle_model.vehicle_model_name}")
    
    # 创建或更新测试基本信息
    test, created = VehicleMountIsolationTest.objects.get_or_create(
        vehicle_model=vehicle_model,
        test_date=date(2024, 3, 15),
        defaults={
            'test_location': '上汽通用五菱试验场',
            'test_engineer': '张工程师',
            'suspension_type': '前麦弗逊后扭力梁',
            'tire_pressure': '前轮2.2bar，后轮2.0bar',
            # 座椅导轨振动数据 AC OFF
            'seat_vib_x_ac_off': 0.025,
            'seat_vib_y_ac_off': 0.023,
            'seat_vib_z_ac_off': 0.014,
            # 座椅导轨振动数据 AC ON
            'seat_vib_x_ac_on': 0.032,
            'seat_vib_y_ac_on': 0.028,
            'seat_vib_z_ac_on': 0.019,
            # 方向盘振动数据 AC OFF
            'steering_vib_x_ac_off': 0.018,
            'steering_vib_y_ac_off': 0.021,
            'steering_vib_z_ac_off': 0.016,
            # 方向盘振动数据 AC ON
            'steering_vib_x_ac_on': 0.024,
            'steering_vib_y_ac_on': 0.027,
            'steering_vib_z_ac_on': 0.022,
            # 内噪声数据 AC OFF
            'cabin_noise_front_ac_off': 45.2,
            'cabin_noise_rear_ac_off': 43.8,
            # 内噪声数据 AC ON
            'cabin_noise_front_ac_on': 48.5,
            'cabin_noise_rear_ac_on': 46.3
        }
    )
    
    if created:
        print(f"创建测试记录: {test}")
    else:
        print(f"使用现有测试记录: {test}")
    
    # 创建测点数据
    measuring_points_data = [
        {
            'measuring_point': '左前悬置',
            'x_ac_off_isolation': 25.3, 'x_ac_off_vibration': 0.012,
            'x_ac_on_isolation': 31.2, 'x_ac_on_vibration': 0.015,
            'y_ac_off_isolation': 23.1, 'y_ac_off_vibration': 0.011,
            'y_ac_on_isolation': 22.8, 'y_ac_on_vibration': 0.018,
            'z_ac_off_isolation': 14.5, 'z_ac_off_vibration': 0.042,
            'z_ac_on_isolation': 14.2, 'z_ac_on_vibration': 0.045,
        },
        {
            'measuring_point': '右前悬置',
            'x_ac_off_isolation': 24.8, 'x_ac_off_vibration': 0.013,
            'x_ac_on_isolation': 30.5, 'x_ac_on_vibration': 0.016,
            'y_ac_off_isolation': 22.9, 'y_ac_off_vibration': 0.012,
            'y_ac_on_isolation': 23.1, 'y_ac_on_vibration': 0.019,
            'z_ac_off_isolation': 15.1, 'z_ac_off_vibration': 0.041,
            'z_ac_on_isolation': 14.8, 'z_ac_on_vibration': 0.044,
        },
        {
            'measuring_point': '后悬置',
            'x_ac_off_isolation': 26.2, 'x_ac_off_vibration': 0.010,
            'x_ac_on_isolation': 32.1, 'x_ac_on_vibration': 0.014,
            'y_ac_off_isolation': 24.3, 'y_ac_off_vibration': 0.009,
            'y_ac_on_isolation': 24.8, 'y_ac_on_vibration': 0.017,
            'z_ac_off_isolation': 16.7, 'z_ac_off_vibration': 0.038,
            'z_ac_on_isolation': 16.2, 'z_ac_on_vibration': 0.041,
        }
    ]
    
    for point_data in measuring_points_data:
        mount_data, created = MountIsolationData.objects.get_or_create(
            test=test,
            measuring_point=point_data['measuring_point'],
            defaults=point_data
        )
        
        if created:
            print(f"创建测点数据: {mount_data.measuring_point}")
        else:
            print(f"更新测点数据: {mount_data.measuring_point}")
            # 更新数据
            for key, value in point_data.items():
                if key != 'measuring_point':
                    setattr(mount_data, key, value)
            mount_data.save()
    
    print("测试数据创建完成！")
    print(f"车型数量: {VehicleModel.objects.count()}")
    print(f"测试记录数量: {VehicleMountIsolationTest.objects.count()}")
    print(f"测点数据数量: {MountIsolationData.objects.count()}")

if __name__ == '__main__':
    create_test_data()
