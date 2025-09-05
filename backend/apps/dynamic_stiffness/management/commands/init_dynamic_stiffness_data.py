from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from decimal import Decimal
from apps.dynamic_stiffness.models import DynamicStiffnessTest, DynamicStiffnessData
from apps.modal.models import VehicleModel


class Command(BaseCommand):
    help = '初始化动刚度测试数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新创建',
        )

    def handle(self, *args, **options):
        if options['clear']:
            DynamicStiffnessData.objects.all().delete()
            DynamicStiffnessTest.objects.all().delete()
            self.stdout.write(self.style.WARNING('已清除所有现有动刚度数据'))

        # 获取所有激活状态的车型
        vehicle_models = VehicleModel.objects.filter(status='active')
        
        if not vehicle_models.exists():
            self.stdout.write(
                self.style.ERROR('没有找到激活状态的车型，请先初始化车型数据')
            )
            return

        # 零件名称列表
        part_names = ['白车身']
        
        # 子系统列表
        subsystems = ['前悬硬点', '后悬硬点', '动力硬点']
        
        # 测点配置
        test_points_config = {
            '前悬硬点': [
                '左前减震器安装点', '右前减震器安装点', 
                '左前摆臂安装点', '右前摆臂安装点',
                '左前稳定杆安装点', '右前稳定杆安装点'
            ],
            '后悬硬点': [
                '左后减震器安装点', '右后减震器安装点',
                '左后摆臂安装点', '右后摆臂安装点', 
                '左后稳定杆安装点', '右后稳定杆安装点'
            ],
            '动力硬点': [
                '发动机左悬置点', '发动机右悬置点',
                '变速箱悬置点', '后悬置点'
            ]
        }
        
        # 测试工程师和分析工程师列表
        test_engineers = ['张工', '李工', '王工', '刘工', '陈工']
        analysis_engineers = ['赵分析师', '钱分析师', '孙分析师', '李分析师']
        test_locations = ['NVH试验室A', 'NVH试验室B', '动力学试验室']
        suspension_types = ['麦弗逊式独立悬挂', '双叉臂独立悬挂', '多连杆独立悬挂', '扭力梁非独立悬挂']

        created_tests = 0
        created_data = 0

        for vehicle_model in vehicle_models:
            for part_name in part_names:
                # 为每个车型的每个零件创建1-2个测试记录
                test_count = random.randint(1, 2)
                
                for i in range(test_count):
                    # 生成测试日期（最近6个月内）
                    days_ago = random.randint(1, 180)
                    test_date = date.today() - timedelta(days=days_ago)
                    
                    # 创建动刚度测试记录
                    test = DynamicStiffnessTest.objects.create(
                        vehicle_model=vehicle_model,
                        part_name=part_name,
                        test_date=test_date,
                        test_location=random.choice(test_locations),
                        test_engineer=random.choice(test_engineers),
                        analysis_engineer=random.choice(analysis_engineers),
                        suspension_type=random.choice(suspension_types),
                        test_photo_path=f'/media/dynamic_stiffness/test_photos/test_{vehicle_model.id}_{i+1}.jpg'
                    )
                    
                    created_tests += 1
                    self.stdout.write(f'创建测试记录: {vehicle_model.vehicle_model_name} - {part_name}')
                    
                    # 为每个测试创建动刚度数据
                    for subsystem in subsystems:
                        test_points = test_points_config[subsystem]
                        
                        for test_point in test_points:
                            # 生成动刚度数据
                            data = DynamicStiffnessData.objects.create(
                                test=test,
                                subsystem=subsystem,
                                test_point=test_point,
                                
                                # X方向数据
                                target_stiffness_x=self.generate_random_decimal(1000.0, 5000.0),
                                freq_50_x=self.generate_random_decimal(800.0, 4500.0),
                                freq_80_x=self.generate_random_decimal(850.0, 4600.0),
                                freq_100_x=self.generate_random_decimal(900.0, 4700.0),
                                freq_125_x=self.generate_random_decimal(950.0, 4800.0),
                                freq_160_x=self.generate_random_decimal(1000.0, 4900.0),
                                freq_200_x=self.generate_random_decimal(1050.0, 5000.0),
                                freq_250_x=self.generate_random_decimal(1100.0, 5100.0),
                                freq_315_x=self.generate_random_decimal(1150.0, 5200.0),
                                freq_350_x=self.generate_random_decimal(1200.0, 5300.0),
                                freq_400_x=self.generate_random_decimal(1250.0, 5400.0),
                                
                                # Y方向数据
                                target_stiffness_y=self.generate_random_decimal(1200.0, 5200.0),
                                freq_50_y=self.generate_random_decimal(1000.0, 4700.0),
                                freq_80_y=self.generate_random_decimal(1050.0, 4800.0),
                                freq_100_y=self.generate_random_decimal(1100.0, 4900.0),
                                freq_125_y=self.generate_random_decimal(1150.0, 5000.0),
                                freq_160_y=self.generate_random_decimal(1200.0, 5100.0),
                                freq_200_y=self.generate_random_decimal(1250.0, 5200.0),
                                freq_250_y=self.generate_random_decimal(1300.0, 5300.0),
                                freq_315_y=self.generate_random_decimal(1350.0, 5400.0),
                                freq_350_y=self.generate_random_decimal(1400.0, 5500.0),
                                freq_400_y=self.generate_random_decimal(1450.0, 5600.0),
                                
                                # Z方向数据
                                target_stiffness_z=self.generate_random_decimal(1500.0, 6000.0),
                                freq_50_z=self.generate_random_decimal(1300.0, 5500.0),
                                freq_80_z=self.generate_random_decimal(1350.0, 5600.0),
                                freq_100_z=self.generate_random_decimal(1400.0, 5700.0),
                                freq_125_z=self.generate_random_decimal(1450.0, 5800.0),
                                freq_160_z=self.generate_random_decimal(1500.0, 5900.0),
                                freq_200_z=self.generate_random_decimal(1550.0, 6000.0),
                                freq_250_z=self.generate_random_decimal(1600.0, 6100.0),
                                freq_315_z=self.generate_random_decimal(1650.0, 6200.0),
                                freq_350_z=self.generate_random_decimal(1700.0, 6300.0),
                                freq_400_z=self.generate_random_decimal(1750.0, 6400.0),
                                
                                # 图片路径
                                layout_image=f'/media/dynamic_stiffness/layout/{subsystem}_{test_point}_layout.jpg',
                                curve_image=f'/media/dynamic_stiffness/curves/{subsystem}_{test_point}_curve.jpg'
                            )
                            
                            created_data += 1

        self.stdout.write(
            self.style.SUCCESS(f'成功创建 {created_tests} 条测试记录和 {created_data} 条动刚度数据')
        )
        
        # 提示用户关于图片文件
        self.stdout.write(
            self.style.WARNING(
                '\n注意：示例数据使用了虚拟图片路径。'
                '\n实际使用时，请确保以下目录存在相应的图片文件：'
                '\n- backend/media/dynamic_stiffness/test_photos/'
                '\n- backend/media/dynamic_stiffness/layout/'
                '\n- backend/media/dynamic_stiffness/curves/'
                '\n或者上传真实的图片文件并更新数据库中的路径。'
            )
        )

    def generate_random_decimal(self, min_val, max_val):
        """生成指定范围内的随机小数，保留6位小数"""
        # 有5%的概率返回None（表示未测试或数据缺失）
        if random.random() < 0.05:
            return None
        
        value = random.uniform(min_val, max_val)
        return Decimal(str(round(value, 6)))
