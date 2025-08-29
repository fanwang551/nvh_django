from django.core.management.base import BaseCommand
from django.db import transaction
from apps.modal.models import VehicleModel, Component, TestProject, ModalData
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = '初始化模态数据测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化模态数据...')
        
        with transaction.atomic():
            # 清空现有数据
            ModalData.objects.all().delete()
            TestProject.objects.all().delete()
            Component.objects.all().delete()
            VehicleModel.objects.all().delete()
            
            # 创建车型数据
            vehicles = [
                {
                    'cle_model_code': 'WL_HONGGUANG_2024',
                    'vehicle_model_name': '五菱宏光PLUS 2024款',
                    'vin': 'LZWACAGA5MA123456',
                    'drive_type': 'FWD',
                    'configuration': '1.5L 手动舒适型',
                    'production_year': 2024,
                },
                {
                    'cle_model_code': 'WL_RONGGUANG_2024',
                    'vehicle_model_name': '五菱荣光新卡 2024款',
                    'vin': 'LZWACAGA5MA123457',
                    'drive_type': 'RWD',
                    'configuration': '1.5L 标准型',
                    'production_year': 2024,
                },
                {
                    'cle_model_code': 'BJ_510_2024',
                    'vehicle_model_name': '宝骏510 2024款',
                    'vin': 'LZWACAGA5MA123458',
                    'drive_type': 'FWD',
                    'configuration': '1.5L CVT豪华型',
                    'production_year': 2024,
                },
                {
                    'cle_model_code': 'BJ_730_2024',
                    'vehicle_model_name': '宝骏730 2024款',
                    'vin': 'LZWACAGA5MA123459',
                    'drive_type': 'FWD',
                    'configuration': '1.5T 手动精英型',
                    'production_year': 2024,
                }
            ]
            
            vehicle_objects = []
            for vehicle_data in vehicles:
                vehicle = VehicleModel.objects.create(**vehicle_data)
                vehicle_objects.append(vehicle)
                self.stdout.write(f'创建车型: {vehicle.vehicle_model_name}')
            
            # 创建零件数据
            components = [
                {
                    'component_name': '发动机悬置',
                    'category': '动力总成',
                    'component_brand': 'Continental',
                    'component_model': 'EM-2023-001',
                    'component_code': 'ENG_MOUNT_001',
                },
                {
                    'component_name': '变速箱悬置',
                    'category': '动力总成',
                    'component_brand': 'ZF',
                    'component_model': 'TM-2023-002',
                    'component_code': 'TRANS_MOUNT_002',
                },
                {
                    'component_name': '前悬架弹簧',
                    'category': '悬架系统',
                    'component_brand': 'Bilstein',
                    'component_model': 'FS-2023-003',
                    'component_code': 'FRONT_SPRING_003',
                },
                {
                    'component_name': '后悬架减震器',
                    'category': '悬架系统',
                    'component_brand': 'Monroe',
                    'component_model': 'RS-2023-004',
                    'component_code': 'REAR_SHOCK_004',
                },
                {
                    'component_name': '车身框架',
                    'category': '车身结构',
                    'component_brand': 'OEM',
                    'component_model': 'BF-2023-005',
                    'component_code': 'BODY_FRAME_005',
                }
            ]
            
            component_objects = []
            for comp_data in components:
                component = Component.objects.create(**comp_data)
                component_objects.append(component)
                self.stdout.write(f'创建零件: {component.component_name}')
            
            # 创建测试项目数据
            test_projects = []
            project_counter = 1
            
            for vehicle in vehicle_objects:
                for component in component_objects[:3]:  # 每个车型测试前3个零件
                    project = TestProject.objects.create(
                        vehicle_model=vehicle,
                        component=component,
                        test_type='模态测试',
                        test_date=date(2024, 8, 15 + project_counter),
                        test_location='NVH实验室',
                        test_engineer='张工程师',
                        test_status='已完成',
                        excitation_method='锤击法',
                        notes=f'{vehicle.vehicle_model_name} {component.component_name} 模态测试'
                    )
                    test_projects.append(project)
                    project_counter += 1
                    self.stdout.write(f'创建测试项目: ID-{project.id}')
            
            # 创建模态数据
            modal_counter = 1
            for project in test_projects:
                # 每个测试项目创建3-5个模态数据
                frequencies = [25.5, 45.2, 78.9, 125.6, 189.3]
                damping_ratios = [0.02, 0.035, 0.041, 0.028, 0.055]
                descriptions = [
                    '第一阶弯曲模态',
                    '第一阶扭转模态', 
                    '第二阶弯曲模态',
                    '局部振动模态',
                    '高频复合模态'
                ]
                
                for i in range(3):  # 每个项目3个模态数据
                    modal_data = ModalData.objects.create(
                        test_project=project,
                        frequency=Decimal(str(frequencies[i])),
                        damping_ratio=Decimal(str(damping_ratios[i])),
                        mode_shape_description=descriptions[i],
                        mode_shape_file=f'/media/modal_shapes/modal_{modal_counter:03d}.gif',
                        test_photo_file=f'/media/test_photos/test_{modal_counter:03d}.jpg',
                        notes=f'项目ID-{project.id} - {descriptions[i]}',
                        updated_by='系统初始化'
                    )
                    modal_counter += 1
                    self.stdout.write(f'创建模态数据: {modal_data.frequency}Hz')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'数据初始化完成！\n'
                f'- 车型: {VehicleModel.objects.count()} 个\n'
                f'- 零件: {Component.objects.count()} 个\n'
                f'- 测试项目: {TestProject.objects.count()} 个\n'
                f'- 模态数据: {ModalData.objects.count()} 条'
            )
        )
