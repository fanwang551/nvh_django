from django.core.management.base import BaseCommand
from django.db import transaction
from apps.dynamic_stiffness.models import VehicleSuspensionIsolationTest, SuspensionIsolationData
from apps.modal.models import VehicleModel
from decimal import Decimal
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = '初始化悬架隔振率测试数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有悬架隔振率数据后重新初始化',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清空现有悬架隔振率数据...')
            SuspensionIsolationData.objects.all().delete()
            VehicleSuspensionIsolationTest.objects.all().delete()

        self.stdout.write('开始初始化悬架隔振率测试数据...')

        # 获取车型数据
        vehicle_models = list(VehicleModel.objects.all())
        if not vehicle_models:
            self.stdout.write(
                self.style.ERROR('未找到车型数据，请先初始化车型数据')
            )
            return

        # 测点列表
        measuring_points = [
            '前左悬架',
            '前右悬架', 
            '后左悬架',
            '后右悬架',
            '前副车架',
            '后副车架'
        ]

        # 悬挂形式列表
        suspension_types = [
            '麦弗逊式独立悬架',
            '双横臂独立悬架',
            '多连杆独立悬架',
            '扭力梁式悬架'
        ]

        # 测试地点列表
        test_locations = [
            'NVH实验室',
            '整车试验场',
            '四立柱试验台',
            '半消声室'
        ]

        # 测试人员列表
        test_engineers = ['李工', '王工', '张工', '刘工', '陈工']

        # 测试工况列表
        test_conditions = [
            '怠速工况',
            '2000rpm工况',
            '3000rpm工况',
            '怠速+空调开启',
            '2000rpm+空调开启'
        ]

        with transaction.atomic():
            test_count = 0
            data_count = 0

            # 为每个车型创建测试数据
            for vehicle_model in vehicle_models:
                # 为每个车型创建1-2个测试
                num_tests = random.randint(1, 2)
                
                for test_idx in range(num_tests):
                    # 创建测试基本信息
                    test_date = date.today() - timedelta(days=random.randint(1, 365))
                    
                    test = VehicleSuspensionIsolationTest.objects.create(
                        vehicle_model=vehicle_model,
                        test_date=test_date,
                        test_location=random.choice(test_locations),
                        test_engineer=random.choice(test_engineers),
                        suspension_type=random.choice(suspension_types),
                        tire_pressure=f'{random.uniform(2.0, 2.5):.1f}bar',
                        test_condition=random.choice(test_conditions)
                    )
                    test_count += 1

                    # 为每个测试创建测点数据
                    selected_points = random.sample(measuring_points, random.randint(3, 6))
                    
                    for point in selected_points:
                        # 生成模拟数据
                        x_active = Decimal(str(round(random.uniform(0.1, 2.0), 6)))
                        x_passive = Decimal(str(round(random.uniform(0.01, 0.5), 6)))
                        x_isolation = Decimal(str(round(random.uniform(5.0, 25.0), 3)))

                        y_active = Decimal(str(round(random.uniform(0.1, 2.0), 6)))
                        y_passive = Decimal(str(round(random.uniform(0.01, 0.5), 6)))
                        y_isolation = Decimal(str(round(random.uniform(5.0, 25.0), 3)))

                        z_active = Decimal(str(round(random.uniform(0.1, 2.0), 6)))
                        z_passive = Decimal(str(round(random.uniform(0.01, 0.5), 6)))
                        z_isolation = Decimal(str(round(random.uniform(5.0, 25.0), 3)))

                        SuspensionIsolationData.objects.create(
                            test=test,
                            measuring_point=point,
                            x_active_value=x_active,
                            x_passive_value=x_passive,
                            x_isolation_rate=x_isolation,
                            y_active_value=y_active,
                            y_passive_value=y_passive,
                            y_isolation_rate=y_isolation,
                            z_active_value=z_active,
                            z_passive_value=z_passive,
                            z_isolation_rate=z_isolation,
                            layout_image_path=f'/media/suspension_isolation/layout_{test.id}_{point.replace(" ", "_")}.jpg',
                            curve_image_path=f'/media/suspension_isolation/curve_{test.id}_{point.replace(" ", "_")}.jpg'
                        )
                        data_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'悬架隔振率数据初始化完成！'
                f'创建了 {test_count} 个测试记录和 {data_count} 条数据记录'
            )
        )

    def generate_isolation_rate(self, active_value, passive_value):
        """计算隔振率"""
        try:
            if active_value > 0 and passive_value > 0:
                # 隔振率 = 20 * log10(主动端/被动端)
                import math
                return 20 * math.log10(float(active_value) / float(passive_value))
            else:
                return random.uniform(5.0, 25.0)
        except:
            return random.uniform(5.0, 25.0)