from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.dynamic_stiffness.models import VehicleMountIsolationTest, MountIsolationData
from apps.modal.models import VehicleModel
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = '初始化悬置隔振率测试数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新初始化',
        )

    def handle(self, *args, **options):
        if options['clear']:
            MountIsolationData.objects.all().delete()
            VehicleMountIsolationTest.objects.all().delete()
            self.stdout.write(self.style.WARNING('已清除所有现有悬置隔振率数据'))

        # 获取所有激活状态的车型
        vehicle_models = VehicleModel.objects.filter(status='active')
        
        if not vehicle_models.exists():
            self.stdout.write(
                self.style.ERROR('没有找到激活状态的车型，请先初始化车型数据')
            )
            return

        # 测点配置
        measuring_points = [
            '左悬置', '右悬置', '后悬置', '变速箱悬置'
        ]
        
        # 悬挂形式列表
        suspension_types = ['麦弗逊式独立悬挂', '双叉臂式独立悬挂', '多连杆式独立悬挂', '扭力梁式悬挂']
        
        # 测试人员列表
        test_engineers = ['张工程师', '李工程师', '王工程师', '刘工程师', '陈工程师']

        created_tests = 0
        created_data = 0

        for vehicle_model in vehicle_models:
            # 为每个车型创建1-2个测试记录
            test_count = random.randint(1, 2)
            
            for i in range(test_count):
                # 创建测试基本信息
                test_date = date.today() - timedelta(days=random.randint(1, 365))
                
                test = VehicleMountIsolationTest.objects.create(
                    vehicle_model=vehicle_model,
                    test_date=test_date,
                    test_location=random.choice(['上海试验场', '北京试验场', '广州试验场', '成都试验场']),
                    test_engineer=random.choice(test_engineers),
                    suspension_type=random.choice(suspension_types),
                    tire_pressure=f"{random.uniform(2.0, 2.5):.1f}bar",
                    
                    # 驾驶员座椅导轨振动 (m/s²)
                    seat_vib_x=round(random.uniform(0.005, 0.020), 4),
                    seat_vib_y=round(random.uniform(0.005, 0.020), 4),
                    seat_vib_z=round(random.uniform(0.010, 0.030), 4),
                    
                    # 方向盘振动 (m/s²)
                    steering_vib_x=round(random.uniform(0.003, 0.015), 4),
                    steering_vib_y=round(random.uniform(0.003, 0.015), 4),
                    steering_vib_z=round(random.uniform(0.005, 0.020), 4),
                    
                    # 内噪 (dB)
                    cabin_noise_front=round(random.uniform(35.0, 45.0), 1),
                    cabin_noise_rear=round(random.uniform(37.0, 47.0), 1)
                )
                created_tests += 1

                # 为每个测试创建测点数据
                for measuring_point in measuring_points:
                    # 生成合理的隔振率和振动数据
                    # AC OFF状态的数据
                    x_ac_off_isolation = round(random.uniform(15.0, 35.0), 1)
                    x_ac_off_vibration = round(random.uniform(0.005, 0.050), 3)
                    x_ac_on_isolation = round(random.uniform(18.0, 38.0), 1)
                    x_ac_on_vibration = round(random.uniform(0.005, 0.050), 3)
                    
                    y_ac_off_isolation = round(random.uniform(12.0, 32.0), 1)
                    y_ac_off_vibration = round(random.uniform(0.005, 0.050), 3)
                    y_ac_on_isolation = round(random.uniform(15.0, 35.0), 1)
                    y_ac_on_vibration = round(random.uniform(0.005, 0.050), 3)
                    
                    z_ac_off_isolation = round(random.uniform(10.0, 25.0), 1)
                    z_ac_off_vibration = round(random.uniform(0.010, 0.080), 3)
                    z_ac_on_isolation = round(random.uniform(12.0, 28.0), 1)
                    z_ac_on_vibration = round(random.uniform(0.010, 0.080), 3)

                    MountIsolationData.objects.create(
                        test=test,
                        measuring_point=measuring_point,
                        
                        # X方向数据
                        x_ac_off_isolation=x_ac_off_isolation,
                        x_ac_off_vibration=x_ac_off_vibration,
                        x_ac_on_isolation=x_ac_on_isolation,
                        x_ac_on_vibration=x_ac_on_vibration,
                        
                        # Y方向数据
                        y_ac_off_isolation=y_ac_off_isolation,
                        y_ac_off_vibration=y_ac_off_vibration,
                        y_ac_on_isolation=y_ac_on_isolation,
                        y_ac_on_vibration=y_ac_on_vibration,
                        
                        # Z方向数据
                        z_ac_off_isolation=z_ac_off_isolation,
                        z_ac_off_vibration=z_ac_off_vibration,
                        z_ac_on_isolation=z_ac_on_isolation,
                        z_ac_on_vibration=z_ac_on_vibration,
                        
                        # 图片路径（示例路径）
                        layout_image_path=f'/static/images/mount_isolation/{vehicle_model.cle_model_code}_{measuring_point}_layout.jpg',
                        curve_image_path=f'/static/images/mount_isolation/{vehicle_model.cle_model_code}_{measuring_point}_curve.jpg'
                    )
                    created_data += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'成功创建 {created_tests} 个悬置隔振率测试记录和 {created_data} 条测试数据'
            )
        )
