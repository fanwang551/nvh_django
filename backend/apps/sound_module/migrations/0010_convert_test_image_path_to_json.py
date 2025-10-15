from django.db import migrations, models


def migrate_image_paths_forward(apps, schema_editor):
    VehicleSoundInsulationData = apps.get_model('sound_module', 'VehicleSoundInsulationData')
    VehicleReverberationData = apps.get_model('sound_module', 'VehicleReverberationData')

    # 车型隔声量
    for obj in VehicleSoundInsulationData.objects.all().only('id', 'test_image_path'):
        val = getattr(obj, 'test_image_path', None)
        if val is None or val == '':
            obj.test_image_path_tmp = []
        elif isinstance(val, list):
            obj.test_image_path_tmp = val
        else:
            # 旧字符串 -> 单元素列表
            obj.test_image_path_tmp = [str(val)]
        obj.save(update_fields=['test_image_path_tmp'])

    # 车型混响时间
    for obj in VehicleReverberationData.objects.all().only('id', 'test_image_path'):
        val = getattr(obj, 'test_image_path', None)
        if val is None or val == '':
            obj.test_image_path_tmp = []
        elif isinstance(val, list):
            obj.test_image_path_tmp = val
        else:
            obj.test_image_path_tmp = [str(val)]
        obj.save(update_fields=['test_image_path_tmp'])


def migrate_image_paths_backward(apps, schema_editor):
    VehicleSoundInsulationData = apps.get_model('sound_module', 'VehicleSoundInsulationData')
    VehicleReverberationData = apps.get_model('sound_module', 'VehicleReverberationData')

    # 将列表回退为首个元素或空字符串
    for obj in VehicleSoundInsulationData.objects.all().only('id', 'test_image_path'):
        val = getattr(obj, 'test_image_path_tmp', None)
        if isinstance(val, list) and val:
            obj.test_image_path = val[0]
        else:
            obj.test_image_path = ''
        obj.save(update_fields=['test_image_path'])

    for obj in VehicleReverberationData.objects.all().only('id', 'test_image_path'):
        val = getattr(obj, 'test_image_path_tmp', None)
        if isinstance(val, list) and val:
            obj.test_image_path = val[0]
        else:
            obj.test_image_path = ''
        obj.save(update_fields=['test_image_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('sound_module', '0009_alter_materialporosityflowresistance_options_and_more'),
    ]

    operations = [
        # 1) 新增临时JSON字段
        migrations.AddField(
            model_name='vehiclesoundinsulationdata',
            name='test_image_path_tmp',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='测试图片路径列表'),
        ),
        migrations.AddField(
            model_name='vehiclereverberationdata',
            name='test_image_path_tmp',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='测试图片路径列表'),
        ),

        # 2) 迁移数据到临时字段
        migrations.RunPython(migrate_image_paths_forward, reverse_code=migrate_image_paths_backward),

        # 3) 删除旧字段
        migrations.RemoveField(
            model_name='vehiclesoundinsulationdata',
            name='test_image_path',
        ),
        migrations.RemoveField(
            model_name='vehiclereverberationdata',
            name='test_image_path',
        ),

        # 4) 临时字段改名为正式字段名
        migrations.RenameField(
            model_name='vehiclesoundinsulationdata',
            old_name='test_image_path_tmp',
            new_name='test_image_path',
        ),
        migrations.RenameField(
            model_name='vehiclereverberationdata',
            old_name='test_image_path_tmp',
            new_name='test_image_path',
        ),
    ]

