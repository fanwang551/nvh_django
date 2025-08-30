from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.modal.models import VehicleModel, AirtightnessTest
import random
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = '初始化气密性测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化气密性测试数据...')
        
        # 获取所有激活的车型
        vehicle_models = VehicleModel.objects.filter(status='active')
        
        if not vehicle_models.exists():
            self.stdout.write(self.style.ERROR('没有找到激活的车型，请先添加车型数据'))
            return
        
        # 清除现有的气密性测试数据
        AirtightnessTest.objects.all().delete()
        self.stdout.write('已清除现有气密性测试数据')
        
        # 测试工程师列表
        engineers = ['张工', '李工', '王工', '刘工', '陈工']
        test_locations = ['试验室A', '试验室B', '试验室C', '户外测试场']
        
        created_count = 0
        
        for vehicle_model in vehicle_models:
            # 为每个车型创建1-2条测试记录
            test_count = random.randint(1, 2)
            
            for i in range(test_count):
                # 生成测试日期（最近6个月内）
                days_ago = random.randint(1, 180)
                test_date = date.today() - timedelta(days=days_ago)
                
                # 创建气密性测试数据
                airtightness_test = AirtightnessTest.objects.create(
                    vehicle_model=vehicle_model,
                    test_date=test_date,
                    test_engineer=random.choice(engineers),
                    test_location=random.choice(test_locations),
                    
                    # 整车不可控泄漏量 (通常在10-50 SCFM之间)
                    uncontrolled_leakage=self.generate_random_decimal(15.0, 45.0),
                    
                    # 阀系统 (通常在1-8 SCFM之间)
                    left_pressure_valve=self.generate_random_decimal(1.0, 6.0),
                    right_pressure_valve=self.generate_random_decimal(1.0, 6.0),
                    ac_circulation_valve=self.generate_random_decimal(2.0, 8.0),
                    
                    # 门系统 (通常在0.5-5 SCFM之间)
                    right_door_drain_hole=self.generate_random_decimal(0.5, 3.0),
                    tailgate_drain_hole=self.generate_random_decimal(0.8, 4.0),
                    right_door_outer_seal=self.generate_random_decimal(1.0, 5.0),
                    right_door_outer_opening=self.generate_random_decimal(0.5, 3.5),
                    side_mirrors=self.generate_random_decimal(0.3, 2.0),
                    
                    # 白车身和其他区域 (通常在2-12 SCFM之间)
                    body_shell_leakage=self.generate_random_decimal(3.0, 12.0),
                    other_area=self.generate_random_decimal(1.0, 8.0),
                    
                    notes=f'第{i+1}次测试记录'
                )
                
                created_count += 1
                self.stdout.write(f'为车型 {vehicle_model.vehicle_model_name} 创建测试记录 {i+1}')
        
        self.stdout.write(
            self.style.SUCCESS(f'成功创建 {created_count} 条气密性测试数据')
        )
    
    def generate_random_decimal(self, min_val, max_val):
        """生成指定范围内的随机小数，保留1位小数"""
        # 有10%的概率返回None（表示未测试或数据缺失）
        if random.random() < 0.1:
            return None
        
        value = random.uniform(min_val, max_val)
        return Decimal(f'{value:.1f}')
