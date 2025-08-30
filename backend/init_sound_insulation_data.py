#!/usr/bin/env python3
"""
初始化隔声量数据
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

from apps.sound_module.models import SoundInsulationArea, SoundInsulationData
from apps.modal.models import VehicleModel


def init_sound_insulation_areas():
    """初始化隔声区域数据"""
    areas = [
        {'area_name': '前围', 'description': '发动机舱与驾驶室之间的隔声区域'},
        {'area_name': '前挡', 'description': '前挡风玻璃隔声区域'},
        {'area_name': '后挡', 'description': '后挡风玻璃隔声区域'},
        {'area_name': '左前门', 'description': '左前车门隔声区域'},
        {'area_name': '左后门', 'description': '左后车门隔声区域'},
        {'area_name': '右前门', 'description': '右前车门隔声区域'},
        {'area_name': '右后门', 'description': '右后车门隔声区域'},
    ]
    
    created_count = 0
    for area_data in areas:
        area, created = SoundInsulationArea.objects.get_or_create(
            area_name=area_data['area_name'],
            defaults={'description': area_data['description']}
        )
        if created:
            created_count += 1
            print(f"✅ 创建区域: {area.area_name}")
        else:
            print(f"⚠️  区域已存在: {area.area_name}")
    
    print(f"\n🎉 区域初始化完成！新创建 {created_count} 个区域")
    return SoundInsulationArea.objects.all()


def generate_frequency_data():
    """生成随机的频率隔声量数据"""
    # 隔声量一般在10-60dB之间，低频较低，高频较高
    base_values = {
        'freq_200': random.uniform(15.0, 25.0),
        'freq_250': random.uniform(18.0, 28.0),
        'freq_315': random.uniform(20.0, 30.0),
        'freq_400': random.uniform(22.0, 32.0),
        'freq_500': random.uniform(25.0, 35.0),
        'freq_630': random.uniform(28.0, 38.0),
        'freq_800': random.uniform(30.0, 40.0),
        'freq_1000': random.uniform(32.0, 42.0),
        'freq_1250': random.uniform(35.0, 45.0),
        'freq_1600': random.uniform(37.0, 47.0),
        'freq_2000': random.uniform(40.0, 50.0),
        'freq_2500': random.uniform(42.0, 52.0),
        'freq_3150': random.uniform(45.0, 55.0),
        'freq_4000': random.uniform(47.0, 57.0),
        'freq_5000': random.uniform(48.0, 58.0),
        'freq_6300': random.uniform(50.0, 60.0),
        'freq_8000': random.uniform(52.0, 62.0),
        'freq_10000': random.uniform(54.0, 64.0),
    }
    
    # 转换为Decimal类型
    return {key: Decimal(str(round(value, 2))) for key, value in base_values.items()}


def init_sound_insulation_data():
    """初始化隔声量测试数据"""
    areas = SoundInsulationArea.objects.all()
    vehicle_models = VehicleModel.objects.filter(status='active')
    
    if not areas.exists():
        print("❌ 请先初始化区域数据")
        return
    
    if not vehicle_models.exists():
        print("❌ 没有找到激活的车型数据")
        return
    
    test_locations = ['上海实验室', '北京实验室', '广州实验室', '成都实验室']
    test_engineers = ['张工', '李工', '王工', '刘工', '陈工']
    
    created_count = 0
    
    # 为每个车型在每个区域创建测试数据（但不是全部，模拟真实情况）
    for vehicle in vehicle_models:
        # 随机选择3-5个区域有数据
        selected_areas = random.sample(list(areas), random.randint(3, min(5, len(areas))))
        
        for area in selected_areas:
            # 检查是否已存在数据
            if SoundInsulationData.objects.filter(vehicle_model=vehicle, area=area).exists():
                print(f"⚠️  数据已存在: {vehicle.vehicle_model_name} - {area.area_name}")
                continue
            
            # 生成频率数据
            frequency_data = generate_frequency_data()
            
            # 创建隔声量数据
            sound_data = SoundInsulationData.objects.create(
                vehicle_model=vehicle,
                area=area,
                **frequency_data,
                test_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                test_location=random.choice(test_locations),
                test_engineer=random.choice(test_engineers),
                test_image_path=f'/media/sound_insulation/{vehicle.cle_model_code}_{area.area_name}_test.jpg',
                remarks=f'{vehicle.vehicle_model_name}在{area.area_name}区域的隔声量测试数据'
            )
            
            created_count += 1
            print(f"✅ 创建数据: {vehicle.vehicle_model_name} - {area.area_name}")
    
    print(f"\n🎉 隔声量数据初始化完成！新创建 {created_count} 条数据")


def main():
    """主函数"""
    print("🚀 开始初始化隔声量数据...")
    
    # 1. 初始化区域数据
    print("\n📍 第一步：初始化区域数据")
    init_sound_insulation_areas()
    
    # 2. 初始化隔声量测试数据
    print("\n📊 第二步：初始化隔声量测试数据")
    init_sound_insulation_data()
    
    print("\n✨ 所有数据初始化完成！")
    
    # 显示统计信息
    area_count = SoundInsulationArea.objects.count()
    data_count = SoundInsulationData.objects.count()
    vehicle_count = VehicleModel.objects.filter(
        soundinsulationdata__isnull=False
    ).distinct().count()
    
    print(f"\n📈 数据统计:")
    print(f"   - 隔声区域: {area_count} 个")
    print(f"   - 隔声量数据: {data_count} 条")
    print(f"   - 涉及车型: {vehicle_count} 个")


if __name__ == '__main__':
    main()
