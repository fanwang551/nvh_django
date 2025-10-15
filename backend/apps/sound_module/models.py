from django.db import models
from apps.modal.models import VehicleModel


class SoundInsulationArea(models.Model):
    """隔声区域表"""
    area_name = models.CharField(max_length=50, unique=True, verbose_name='区域名称')
    description = models.TextField(null=True, blank=True, verbose_name='区域描述')

    class Meta:
        db_table = 'sound_insulation_areas'
        verbose_name = '隔声区域'
        verbose_name_plural = '隔声区域'
        ordering = ['id']

    def __str__(self):
        return self.area_name


class SoundInsulationData(models.Model):
    """隔声量数据表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    area = models.ForeignKey(SoundInsulationArea, on_delete=models.CASCADE, verbose_name='区域')

    # 18个频率的隔声量数据
    freq_200 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='200Hz隔声量(dB)')
    freq_250 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='250Hz隔声量(dB)')
    freq_315 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='315Hz隔声量(dB)')
    freq_400 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='400Hz隔声量(dB)')
    freq_500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='500Hz隔声量(dB)')
    freq_630 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='630Hz隔声量(dB)')
    freq_800 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='800Hz隔声量(dB)')
    freq_1000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1000Hz隔声量(dB)')
    freq_1250 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1250Hz隔声量(dB)')
    freq_1600 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1600Hz隔声量(dB)')
    freq_2000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2000Hz隔声量(dB)')
    freq_2500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2500Hz隔声量(dB)')
    freq_3150 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='3150Hz隔声量(dB)')
    freq_4000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='4000Hz隔声量(dB)')
    freq_5000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='5000Hz隔声量(dB)')
    freq_6300 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='6300Hz隔声量(dB)')
    freq_8000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='8000Hz隔声量(dB)')
    freq_10000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='10000Hz隔声量(dB)')

    # 测试相关信息
    # 改为JSON数组，支持多张图片路径
    test_image_path = models.JSONField(default=list, null=True, blank=True, verbose_name='测试图片路径列表')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 时间戳

    class Meta:
        db_table = 'sound_insulation_data'
        verbose_name = '隔声量数据'
        verbose_name_plural = '隔声量数据'
        ordering = ['-id']
        unique_together = ['vehicle_model', 'area']  # 每个车型在每个区域只能有一条数据

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.area.area_name}"


class VehicleSoundInsulationData(models.Model):
    """车型隔声量数据表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')

    # 18个频率的隔声量数据
    freq_200 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='200Hz隔声量(dB)')
    freq_250 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='250Hz隔声量(dB)')
    freq_315 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='315Hz隔声量(dB)')
    freq_400 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='400Hz隔声量(dB)')
    freq_500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='500Hz隔声量(dB)')
    freq_630 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='630Hz隔声量(dB)')
    freq_800 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='800Hz隔声量(dB)')
    freq_1000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1000Hz隔声量(dB)')
    freq_1250 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1250Hz隔声量(dB)')
    freq_1600 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1600Hz隔声量(dB)')
    freq_2000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2000Hz隔声量(dB)')
    freq_2500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2500Hz隔声量(dB)')
    freq_3150 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='3150Hz隔声量(dB)')
    freq_4000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='4000Hz隔声量(dB)')
    freq_5000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='5000Hz隔声量(dB)')
    freq_6300 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='6300Hz隔声量(dB)')
    freq_8000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='8000Hz隔声量(dB)')
    freq_10000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='10000Hz隔声量(dB)')

    # 测试相关信息
    # 改为JSON数组，支持多张图片路径
    test_image_path = models.JSONField(default=list, null=True, blank=True, verbose_name='测试图片路径列表')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 移除时间戳：created_at/updated_at

    class Meta:
        db_table = 'vehicle_sound_insulation_data'
        verbose_name = '车型隔声量数据'
        verbose_name_plural = '车型隔声量数据'
        ordering = ['-id']
        unique_together = ['vehicle_model']  # 每个车型只能有一条隔声量数据

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - 车型隔声量"


class VehicleReverberationData(models.Model):
    """车辆混响时间数据表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')

    # 15个频率的混响时间数据 (400-10000Hz)
    freq_400 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='400Hz混响时间(s)')
    freq_500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='500Hz混响时间(s)')
    freq_630 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='630Hz混响时间(s)')
    freq_800 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='800Hz混响时间(s)')
    freq_1000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1000Hz混响时间(s)')
    freq_1250 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1250Hz混响时间(s)')
    freq_1600 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='1600Hz混响时间(s)')
    freq_2000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2000Hz混响时间(s)')
    freq_2500 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='2500Hz混响时间(s)')
    freq_3150 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='3150Hz混响时间(s)')
    freq_4000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='4000Hz混响时间(s)')
    freq_5000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='5000Hz混响时间(s)')
    freq_6300 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='6300Hz混响时间(s)')
    freq_8000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='8000Hz混响时间(s)')
    freq_10000 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='10000Hz混响时间(s)')

    # 测试相关信息
    test_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='测试图片路径')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 移除时间戳：created_at/updated_at

    class Meta:
        db_table = 'vehicle_reverberation_data'
        verbose_name = '车辆混响时间数据'
        verbose_name_plural = '车辆混响时间数据'
        ordering = ['-id']
        unique_together = ['vehicle_model']  # 每个车型只能有一条混响时间数据

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - 混响时间"


class SoundAbsorptionCoefficients(models.Model):
    """吸声系数表"""
    part_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='零件名称')
    material_composition = models.CharField(max_length=100, null=True, blank=True, verbose_name='材料组成')
    manufacturer = models.CharField(max_length=100, null=True, blank=True, verbose_name='材料厂家')
    test_institution = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试机构')
    thickness = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='厚度(mm)')
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='克重(g/m²)')
    
    # 测试值字段 (125Hz-10000Hz)
    test_value_125 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='125Hz测试值')
    test_value_160 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='160Hz测试值')
    test_value_200 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='200Hz测试值')
    test_value_250 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='250Hz测试值')
    test_value_315 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='315Hz测试值')
    test_value_400 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='400Hz测试值')
    test_value_500 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='500Hz测试值')
    test_value_630 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='630Hz测试值')
    test_value_800 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='800Hz测试值')
    test_value_1000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1000Hz测试值')
    test_value_1250 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1250Hz测试值')
    test_value_1600 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1600Hz测试值')
    test_value_2000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='2000Hz测试值')
    test_value_2500 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='2500Hz测试值')
    test_value_3150 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='3150Hz测试值')
    test_value_4000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='4000Hz测试值')
    test_value_5000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='5000Hz测试值')
    test_value_6300 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='6300Hz测试值')
    test_value_8000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='8000Hz测试值')
    test_value_10000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='10000Hz测试值')
    
    # 目标值字段 (125Hz-10000Hz)
    target_value_125 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='125Hz目标值')
    target_value_160 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='160Hz目标值')
    target_value_200 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='200Hz目标值')
    target_value_250 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='250Hz目标值')
    target_value_315 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='315Hz目标值')
    target_value_400 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='400Hz目标值')
    target_value_500 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='500Hz目标值')
    target_value_630 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='630Hz目标值')
    target_value_800 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='800Hz目标值')
    target_value_1000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1000Hz目标值')
    target_value_1250 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1250Hz目标值')
    target_value_1600 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='1600Hz目标值')
    target_value_2000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='2000Hz目标值')
    target_value_2500 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='2500Hz目标值')
    target_value_3150 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='3150Hz目标值')
    target_value_4000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='4000Hz目标值')
    target_value_5000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='5000Hz目标值')
    target_value_6300 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='6300Hz目标值')
    target_value_8000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='8000Hz目标值')
    target_value_10000 = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True, verbose_name='10000Hz目标值')
    
    # 测试相关信息
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    test_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='测试图片路径')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')
    
    # 移除时间戳：created_at/updated_at

    class Meta:
        db_table = 'sound_absorption_coefficients'
        verbose_name = '吸声系数'
        verbose_name_plural = '吸声系数'
        ordering = ['-id']

    def __str__(self):
        return f"零件{self.part_name} - 材料{self.material_composition} - {self.weight}g/m²"


class SoundInsulationCoefficients(models.Model):
    """隔声量系数表"""
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    material_composition = models.CharField(max_length=200, verbose_name='材料组成')
    test_type = models.CharField(max_length=20, choices=[
        ('vertical', '垂直入射法'),
        ('wall_mount', '上墙法')
    ], verbose_name='测试类型')
    manufacturer = models.CharField(max_length=100, null=True, blank=True, verbose_name='材料厂家')
    test_institution = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试机构')
    thickness = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='厚度(mm)')
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='克重(g/m²)')

    # 测试值字段 (125Hz-10000Hz) - 隔声量单位为dB
    test_value_125 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='125Hz隔声量(dB)')
    test_value_160 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='160Hz隔声量(dB)')
    test_value_200 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='200Hz隔声量(dB)')
    test_value_250 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='250Hz隔声量(dB)')
    test_value_315 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='315Hz隔声量(dB)')
    test_value_400 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='400Hz隔声量(dB)')
    test_value_500 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='500Hz隔声量(dB)')
    test_value_630 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='630Hz隔声量(dB)')
    test_value_800 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='800Hz隔声量(dB)')
    test_value_1000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1000Hz隔声量(dB)')
    test_value_1250 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1250Hz隔声量(dB)')
    test_value_1600 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1600Hz隔声量(dB)')
    test_value_2000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='2000Hz隔声量(dB)')
    test_value_2500 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='2500Hz隔声量(dB)')
    test_value_3150 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='3150Hz隔声量(dB)')
    test_value_4000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='4000Hz隔声量(dB)')
    test_value_5000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='5000Hz隔声量(dB)')
    test_value_6300 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='6300Hz隔声量(dB)')
    test_value_8000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='8000Hz隔声量(dB)')
    test_value_10000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='10000Hz隔声量(dB)')

    # 目标值字段 (125Hz-10000Hz) - 隔声量单位为dB
    target_value_125 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='125Hz目标隔声量(dB)')
    target_value_160 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='160Hz目标隔声量(dB)')
    target_value_200 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='200Hz目标隔声量(dB)')
    target_value_250 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='250Hz目标隔声量(dB)')
    target_value_315 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='315Hz目标隔声量(dB)')
    target_value_400 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='400Hz目标隔声量(dB)')
    target_value_500 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='500Hz目标隔声量(dB)')
    target_value_630 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='630Hz目标隔声量(dB)')
    target_value_800 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='800Hz目标隔声量(dB)')
    target_value_1000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1000Hz目标隔声量(dB)')
    target_value_1250 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1250Hz目标隔声量(dB)')
    target_value_1600 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='1600Hz目标隔声量(dB)')
    target_value_2000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='2000Hz目标隔声量(dB)')
    target_value_2500 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='2500Hz目标隔声量(dB)')
    target_value_3150 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='3150Hz目标隔声量(dB)')
    target_value_4000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='4000Hz目标隔声量(dB)')
    target_value_5000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='5000Hz目标隔声量(dB)')
    target_value_6300 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='6300Hz目标隔声量(dB)')
    target_value_8000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='8000Hz目标隔声量(dB)')
    target_value_10000 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='10000Hz目标隔声量(dB)')

    # 测试相关信息
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    test_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='测试图片路径')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 移除时间戳：created_at/updated_at

    class Meta:
        db_table = 'sound_insulation_coefficients'
        verbose_name = '隔声量系数'
        verbose_name_plural = '隔声量系数'
        ordering = ['-id']

    def __str__(self):
        return f"零件{self.part_name} - 材料{self.material_composition} - {self.get_test_type_display()} - {self.weight}g/m²"


class MaterialPorosityFlowResistance(models.Model):
    """材料孔隙率流阻表"""
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    material_composition = models.CharField(max_length=200, verbose_name='材料组成')
    material_manufacturer = models.CharField(max_length=100, null=True, blank=True, verbose_name='材料厂家')
    test_institution = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试机构')
    thickness_mm = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='厚度(mm)')
    weight_per_area = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='克重(g/m²)')
    density = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='密度(kg/m³)')
    porosity_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='孔隙率(%)')
    porosity_deviation_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='孔隙率偏差(%)')
    flow_resistance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='流阻率(Pa·s/m²)')
    flow_resistance_deviation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='流阻率偏差(Pa·s/m²)')
    test_time = models.DateTimeField(null=True, blank=True, verbose_name='测试时间')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    # 移除时间戳：created_at/updated_at
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'material_porosity_flow_resistance'
        verbose_name = '材料孔隙率流阻'
        verbose_name_plural = '材料孔隙率流阻'
        ordering = ['-id']

    def __str__(self):
        return f"零件{self.part_name} - 材料{self.material_composition} - {self.thickness_mm}mm"
