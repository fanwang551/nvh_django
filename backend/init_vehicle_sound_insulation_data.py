#!/usr/bin/env python3
"""
初始化车型隔声量数据
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.sound_module.models import VehicleSoundInsulationData
from apps.modal.models import VehicleModel


def clear_existing_data():
    """清空现有的车型隔声量数据"""
    print("正在清空现有的车型隔声量数据...")
    VehicleSoundInsulationData.objects.all().delete()
    print("现有数据已清空")


def create_vehicle_sound_insulation_data():
    """创建车型隔声量测试数据"""
    print("正在创建车型隔声量测试数据...")
    
    # 获取所有激活的车型
    vehicle_models = VehicleModel.objects.filter(status='active')
    
    if not vehicle_models.exists():
        print("警告：没有找到激活的车型数据")
        return
    
    # 18个频率点
    frequencies = [200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]
    
    # 测试工程师列表
    engineers = ['张工', '李工', '王工', '刘工', '陈工']
    
    # 测试地点列表
    locations = ['上汽通用五菱试验中心', '柳州基地试验室', '青岛基地试验室', '重庆基地试验室']
    
    created_count = 0
    
    for vehicle in vehicle_models:
        try:
            # 为每个车型生成隔声量数据
            frequency_data = {}
            
            # 生成符合实际的隔声量数据（一般在15-45dB之间，低频较低，高频较高）
            for freq in frequencies:
                if freq <= 500:
                    # 低频段：15-25dB
                    base_value = random.uniform(15.0, 25.0)
                elif freq <= 2000:
                    # 中频段：20-35dB
                    base_value = random.uniform(20.0, 35.0)
                else:
                    # 高频段：25-45dB
                    base_value = random.uniform(25.0, 45.0)
                
                # 添加一些随机变化
                value = base_value + random.uniform(-3.0, 3.0)
                frequency_data[f'freq_{freq}'] = round(Decimal(str(value)), 2)
            
            # 创建车型隔声量数据
            vehicle_sound_data = VehicleSoundInsulationData.objects.create(
                vehicle_model=vehicle,
                **frequency_data,
                test_image_path=f'/static/test_images/vehicle_sound/{vehicle.cle_model_code}_sound_test.jpg',
                test_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                test_location=random.choice(locations),
                test_engineer=random.choice(engineers),
                remarks=f'{vehicle.vehicle_model_name}车型隔声量测试数据'
            )
            
            created_count += 1
            print(f"✓ 已创建车型 {vehicle.vehicle_model_name} 的隔声量数据")
            
        except Exception as e:
            print(f"✗ 创建车型 {vehicle.vehicle_model_name} 的隔声量数据失败: {str(e)}")
    
    print(f"\n车型隔声量数据创建完成！共创建 {created_count} 条数据")


def main():
    """主函数"""
    print("=" * 60)
    print("车型隔声量数据初始化脚本")
    print("=" * 60)
    
    try:
        # 清空现有数据
        clear_existing_data()
        
        # 创建车型隔声量数据
        create_vehicle_sound_insulation_data()
        
        print("\n" + "=" * 60)
        print("车型隔声量数据初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"初始化过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
