from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
import os
from apps.modal.models import VehicleModel, AirtightnessImage


class Command(BaseCommand):
    help = '初始化气密性测试图片数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新创建',
        )

    def handle(self, *args, **options):
        if options['clear']:
            AirtightnessImage.objects.all().delete()
            self.stdout.write(self.style.WARNING('已清除所有现有气密性图片数据'))

        # 获取所有激活状态的车型
        vehicle_models = VehicleModel.objects.filter(status='active')
        
        if not vehicle_models.exists():
            self.stdout.write(
                self.style.ERROR('没有找到激活状态的车型，请先初始化车型数据')
            )
            return

        # 示例图片路径（实际项目中这些图片应该存在于media目录）
        sample_images = {
            'front_compartment': [
                '/media/airtightness/front_compartment_01.jpg',
                '/media/airtightness/front_compartment_02.jpg',
                '/media/airtightness/front_compartment_03.jpg',
                '/media/airtightness/front_compartment_04.jpg',
                '/media/airtightness/front_compartment_05.jpg',
            ],
            'door': [
                '/media/airtightness/door_01.jpg',
                '/media/airtightness/door_02.jpg',
                '/media/airtightness/door_03.jpg',
                '/media/airtightness/door_04.jpg',
                '/media/airtightness/door_05.jpg',
            ],
            'tailgate': [
                '/media/airtightness/tailgate_01.jpg',
                '/media/airtightness/tailgate_02.jpg',
                '/media/airtightness/tailgate_03.jpg',
                '/media/airtightness/tailgate_04.jpg',
                '/media/airtightness/tailgate_05.jpg',
            ]
        }

        created_count = 0
        
        for vehicle_model in vehicle_models:
            # 为每个车型创建1条图片记录
            # 生成上传日期（最近3个月内）
            days_ago = random.randint(1, 90)
            upload_date = date.today() - timedelta(days=days_ago)
            
            # 随机选择图片
            front_image = random.choice(sample_images['front_compartment'])
            door_image = random.choice(sample_images['door'])
            tailgate_image = random.choice(sample_images['tailgate'])
            
            # 创建气密性图片记录
            airtightness_image = AirtightnessImage.objects.create(
                vehicle_model=vehicle_model,
                front_compartment_image=front_image,
                door_image=door_image,
                tailgate_image=tailgate_image,
                upload_date=upload_date,
                notes=f'{vehicle_model.vehicle_model_name}气密性测试图片'
            )
            
            created_count += 1
            self.stdout.write(f'为车型 {vehicle_model.vehicle_model_name} 创建气密性图片记录')
        
        self.stdout.write(
            self.style.SUCCESS(f'成功创建 {created_count} 条气密性图片数据')
        )
        
        # 提示用户关于图片文件
        self.stdout.write(
            self.style.WARNING(
                '\n注意：示例数据使用了虚拟图片路径。'
                '\n实际使用时，请确保以下目录存在相应的图片文件：'
                '\n- backend/media/airtightness/'
                '\n或者上传真实的图片文件并更新数据库中的路径。'
            )
        )
