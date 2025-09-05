#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.sound_module.models import MaterialPorosityFlowResistance
from decimal import Decimal

def create_test_data():
    """创建材料孔隙率流阻测试数据"""
    
    # 检查是否已有数据
    if MaterialPorosityFlowResistance.objects.exists():
        print("数据库中已存在材料孔隙率流阻数据，跳过创建")
        return
    
    test_data = [
        {
            'part_name': '发动机舱隔音垫',
            'material_composition': 'PU泡沫+无纺布',
            'material_manufacturer': '3M公司',
            'test_institution': '清华大学声学实验室',
            'thickness_mm': Decimal('15.5'),
            'weight_per_area': Decimal('850.0'),
            'density': Decimal('55.0'),
            'porosity_percent': Decimal('85.2'),
            'porosity_deviation_percent': Decimal('2.1'),
            'flow_resistance': Decimal('12500.0'),
            'flow_resistance_deviation': Decimal('350.0'),
            'test_engineer': '张工程师',
            'remarks': '符合车规要求'
        },
        {
            'part_name': '车门隔音材料',
            'material_composition': '丁基橡胶+铝箔',
            'material_manufacturer': '住友化学',
            'test_institution': '同济大学NVH实验室',
            'thickness_mm': Decimal('8.0'),
            'weight_per_area': Decimal('1200.0'),
            'density': Decimal('150.0'),
            'porosity_percent': Decimal('45.8'),
            'porosity_deviation_percent': Decimal('1.5'),
            'flow_resistance': Decimal('25000.0'),
            'flow_resistance_deviation': Decimal('800.0'),
            'test_engineer': '李工程师',
            'remarks': '高频隔音效果优异'
        },
        {
            'part_name': '地毯吸音层',
            'material_composition': '聚酯纤维+PET无纺布',
            'material_manufacturer': '巴斯夫',
            'test_institution': '华南理工大学',
            'thickness_mm': Decimal('12.0'),
            'weight_per_area': Decimal('650.0'),
            'density': Decimal('54.2'),
            'porosity_percent': Decimal('92.5'),
            'porosity_deviation_percent': Decimal('3.2'),
            'flow_resistance': Decimal('8500.0'),
            'flow_resistance_deviation': Decimal('250.0'),
            'test_engineer': '王工程师',
            'remarks': '环保材料，符合VOC标准'
        },
        {
            'part_name': '顶棚吸音材料',
            'material_composition': '玻璃纤维+聚氨酯',
            'material_manufacturer': '欧文斯科宁',
            'test_institution': '北京理工大学',
            'thickness_mm': Decimal('20.0'),
            'weight_per_area': Decimal('750.0'),
            'density': Decimal('37.5'),
            'porosity_percent': Decimal('88.9'),
            'porosity_deviation_percent': Decimal('2.8'),
            'flow_resistance': Decimal('9800.0'),
            'flow_resistance_deviation': Decimal('420.0'),
            'test_engineer': '赵工程师',
            'remarks': '轻量化设计'
        },
        {
            'part_name': '后备箱隔音板',
            'material_composition': 'EVA泡沫+铝箔',
            'material_manufacturer': '杜邦',
            'test_institution': '西北工业大学',
            'thickness_mm': Decimal('10.0'),
            'weight_per_area': Decimal('950.0'),
            'density': Decimal('95.0'),
            'porosity_percent': Decimal('65.3'),
            'porosity_deviation_percent': Decimal('1.8'),
            'flow_resistance': Decimal('18500.0'),
            'flow_resistance_deviation': Decimal('650.0'),
            'test_engineer': '陈工程师',
            'remarks': '防水防潮性能优异'
        }
    ]
    
    # 批量创建数据
    created_count = 0
    for data in test_data:
        try:
            MaterialPorosityFlowResistance.objects.create(**data)
            created_count += 1
            print(f"创建数据: {data['part_name']} - {data['material_composition']}")
        except Exception as e:
            print(f"创建数据失败: {data['part_name']} - {str(e)}")
    
    print(f"\n测试数据创建完成！共创建 {created_count} 条记录")

if __name__ == '__main__':
    create_test_data()
