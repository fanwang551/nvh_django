#!/usr/bin/env python3
"""
生成更多NVH模态数据用于对比功能测试
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.modal.models import VehicleModel, Component, TestProject, ModalData

def generate_more_test_data():
    """生成更多测试数据"""
    
    print("🚀 开始生成更多NVH模态测试数据...")
    
    # 获取现有数据
    existing_vehicles = list(VehicleModel.objects.all())
    existing_components = list(Component.objects.all())
    
    print(f"现有车型数量: {len(existing_vehicles)}")
    print(f"现有零件数量: {len(existing_components)}")
    
    # 定义更多测试状态
    test_statuses = [
        '自由状态', '整车状态', '已完成', '半装配状态', 
        '悬置状态', '约束状态', '激励状态', '静态测试'
    ]
    
    # 定义更多振型类型
    mode_types = [
        '第一阶弯曲模态', '第二阶弯曲模态', '第三阶弯曲模态',
        '第一阶扭转模态', '第二阶扭转模态', '第三阶扭转模态',
        '局部振动模态', '高频复合模态', '轴向振动模态',
        '径向振动模态', '混合振动模态', '共振模态'
    ]
    
    # 频率范围 (Hz)
    frequency_ranges = {
        '第一阶弯曲模态': (15.0, 35.0),
        '第二阶弯曲模态': (45.0, 85.0),
        '第三阶弯曲模态': (90.0, 130.0),
        '第一阶扭转模态': (25.0, 55.0),
        '第二阶扭转模态': (65.0, 105.0),
        '第三阶扭转模态': (110.0, 150.0),
        '局部振动模态': (80.0, 200.0),
        '高频复合模态': (150.0, 300.0),
        '轴向振动模态': (30.0, 70.0),
        '径向振动模态': (40.0, 90.0),
        '混合振动模态': (60.0, 120.0),
        '共振模态': (20.0, 180.0)
    }
    
    # 阻尼比范围
    damping_ranges = (0.015, 0.08)
    
    created_projects = 0
    created_modal_data = 0
    
    # 为每个车型和零件组合创建更多测试项目
    for vehicle in existing_vehicles:
        for component in existing_components:
            # 为每个组合创建2-4个不同测试状态的项目
            num_projects = random.randint(2, 4)
            selected_statuses = random.sample(test_statuses, min(num_projects, len(test_statuses)))
            
            for i, test_status in enumerate(selected_statuses):
                # 检查是否已存在相同的测试项目
                existing_project = TestProject.objects.filter(
                    vehicle_model=vehicle,
                    component=component,
                    test_status=test_status
                ).first()
                
                if existing_project:
                    project = existing_project
                else:
                    # 创建新的测试项目
                    project = TestProject.objects.create(
                        vehicle_model=vehicle,
                        component=component,
                        test_type='模态测试',
                        test_date=date.today() - timedelta(days=random.randint(1, 365)),
                        test_location='NVH实验室',
                        test_engineer=random.choice(['张工程师', '李工程师', '王工程师', '刘工程师']),
                        test_status=test_status,
                        excitation_method=random.choice(['锤击法', '激振器法', '环境激励法']),
                        notes=f'{vehicle.vehicle_model_name} {component.component_name} {test_status}模态测试'
                    )
                    created_projects += 1
                
                # 为每个测试项目创建3-6个模态数据
                existing_modal_count = ModalData.objects.filter(test_project=project).count()
                if existing_modal_count < 3:  # 如果现有数据少于3个，补充到6个
                    num_modes = random.randint(6 - existing_modal_count, 8)
                    selected_modes = random.sample(mode_types, min(num_modes, len(mode_types)))
                    
                    for mode_type in selected_modes:
                        # 检查是否已存在相同振型的数据
                        existing_modal = ModalData.objects.filter(
                            test_project=project,
                            mode_shape_description=mode_type
                        ).first()
                        
                        if not existing_modal:
                            # 根据振型类型生成合理的频率
                            freq_range = frequency_ranges.get(mode_type, (20.0, 200.0))
                            frequency = round(random.uniform(freq_range[0], freq_range[1]), 2)
                            
                            # 生成阻尼比
                            damping_ratio = round(random.uniform(damping_ranges[0], damping_ranges[1]), 3)
                            
                            # 创建模态数据
                            modal_data = ModalData.objects.create(
                                test_project=project,
                                frequency=Decimal(str(frequency)),
                                damping_ratio=Decimal(str(damping_ratio)),
                                mode_shape_description=mode_type,
                                mode_shape_file=f'/media/modal_shapes/modal_{vehicle.id}_{component.id}_{hash(mode_type) % 1000:03d}.gif',
                                test_photo_file=f'/media/test_photos/test_{vehicle.id}_{component.id}_{hash(mode_type) % 1000:03d}.jpg',
                                notes=f'{project.id} - {mode_type} - {frequency}Hz',
                                updated_by='数据生成脚本'
                            )
                            created_modal_data += 1
    
    print(f"\n✅ 数据生成完成!")
    print(f"新创建测试项目: {created_projects} 个")
    print(f"新创建模态数据: {created_modal_data} 条")
    
    # 显示最终统计
    total_vehicles = VehicleModel.objects.count()
    total_components = Component.objects.count()
    total_projects = TestProject.objects.count()
    total_modal_data = ModalData.objects.count()
    
    print(f"\n📊 数据库总计:")
    print(f"车型总数: {total_vehicles}")
    print(f"零件总数: {total_components}")
    print(f"测试项目总数: {total_projects}")
    print(f"模态数据总数: {total_modal_data}")
    
    # 显示每个零件的数据分布
    print(f"\n📈 各零件数据分布:")
    for component in existing_components:
        modal_count = ModalData.objects.filter(test_project__component=component).count()
        vehicle_count = VehicleModel.objects.filter(testproject__component=component).distinct().count()
        status_count = TestProject.objects.filter(component=component).values('test_status').distinct().count()
        print(f"{component.component_name}: {modal_count}条模态数据, {vehicle_count}个车型, {status_count}种测试状态")

if __name__ == "__main__":
    generate_more_test_data()
