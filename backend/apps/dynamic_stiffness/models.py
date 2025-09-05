from django.db import models
from apps.modal.models import VehicleModel


class DynamicStiffnessTest(models.Model):
    """动刚度测试表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    test_date = models.DateField(verbose_name='测试时间')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, verbose_name='测试人员')
    analysis_engineer = models.CharField(max_length=50, verbose_name='分析人员')
    suspension_type = models.CharField(max_length=50, verbose_name='悬挂形式')
    test_photo_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试照片路径')

    class Meta:
        db_table = 'dynamic_stiffness_tests'
        verbose_name = '动刚度测试'
        verbose_name_plural = '动刚度测试'
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.part_name} - {self.test_date}"


class DynamicStiffnessData(models.Model):
    """动刚度数据表"""
    test = models.ForeignKey(DynamicStiffnessTest, on_delete=models.CASCADE, verbose_name='动刚度测试')
    subsystem = models.CharField(max_length=50, verbose_name='子系统')
    test_point = models.CharField(max_length=100, verbose_name='测点')
    
    # X方向目标值和各频率段数据
    target_stiffness_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='X方向目标值')
    freq_50_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='50Hz X方向')
    freq_80_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='80Hz X方向')
    freq_100_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='100Hz X方向')
    freq_125_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='125Hz X方向')
    freq_160_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='160Hz X方向')
    freq_200_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='200Hz X方向')
    freq_250_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='250Hz X方向')
    freq_315_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='315Hz X方向')
    freq_350_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='350Hz X方向')
    freq_400_x = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='400Hz X方向')
    
    # Y方向目标值和各频率段数据
    target_stiffness_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='Y方向目标值')
    freq_50_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='50Hz Y方向')
    freq_80_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='80Hz Y方向')
    freq_100_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='100Hz Y方向')
    freq_125_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='125Hz Y方向')
    freq_160_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='160Hz Y方向')
    freq_200_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='200Hz Y方向')
    freq_250_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='250Hz Y方向')
    freq_315_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='315Hz Y方向')
    freq_350_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='350Hz Y方向')
    freq_400_y = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='400Hz Y方向')
    
    # Z方向目标值和各频率段数据
    target_stiffness_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='Z方向目标值')
    freq_50_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='50Hz Z方向')
    freq_80_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='80Hz Z方向')
    freq_100_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='100Hz Z方向')
    freq_125_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='125Hz Z方向')
    freq_160_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='160Hz Z方向')
    freq_200_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='200Hz Z方向')
    freq_250_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='250Hz Z方向')
    freq_315_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='315Hz Z方向')
    freq_350_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='350Hz Z方向')
    freq_400_z = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name='400Hz Z方向')
    
    # 图片路径
    layout_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='测点布置图路径')
    curve_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试曲线图路径')

    class Meta:
        db_table = 'dynamic_stiffness_data'
        verbose_name = '动刚度数据'
        verbose_name_plural = '动刚度数据'
        ordering = ['subsystem', 'test_point']

    def __str__(self):
        return f"{self.test.vehicle_model.vehicle_model_name} - {self.subsystem} - {self.test_point}"
