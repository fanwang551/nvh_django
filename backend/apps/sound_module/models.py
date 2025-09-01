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
    test_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='测试图片路径')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sound_insulation_data'
        verbose_name = '隔声量数据'
        verbose_name_plural = '隔声量数据'
        ordering = ['-created_at']
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
    test_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='测试图片路径')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'vehicle_sound_insulation_data'
        verbose_name = '车型隔声量数据'
        verbose_name_plural = '车型隔声量数据'
        ordering = ['-created_at']
        unique_together = ['vehicle_model']  # 每个车型只能有一条隔声量数据

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - 车型隔声量"
