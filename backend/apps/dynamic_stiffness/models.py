from django.db import models
from apps.modal.models import VehicleModel


class DynamicStiffnessTest(models.Model):
    """动刚度测试表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试时间')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试人员')
    analysis_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='分析人员')
    test_photo_path = models.JSONField(default=list, null=True, blank=True, verbose_name='测试照片路径')

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
    target_stiffness_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                             verbose_name='X方向目标值')
    freq_50_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='50Hz X方向')
    # 新增：63Hz X方向，两位小数
    freq_63_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='63Hz X方向')
    freq_80_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='80Hz X方向')
    freq_100_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='100Hz X方向')
    freq_125_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='125Hz X方向')
    freq_160_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='160Hz X方向')
    freq_200_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='200Hz X方向')
    freq_250_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='250Hz X方向')
    freq_315_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='315Hz X方向')
    freq_350_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='350Hz X方向')
    freq_400_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='400Hz X方向')

    # Y方向目标值和各频率段数据
    target_stiffness_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                             verbose_name='Y方向目标值')
    freq_50_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='50Hz Y方向')
    # 新增：63Hz Y方向，两位小数
    freq_63_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='63Hz Y方向')
    freq_80_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='80Hz Y方向')
    freq_100_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='100Hz Y方向')
    freq_125_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='125Hz Y方向')
    freq_160_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='160Hz Y方向')
    freq_200_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='200Hz Y方向')
    freq_250_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='250Hz Y方向')
    freq_315_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='315Hz Y方向')
    freq_350_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='350Hz Y方向')
    freq_400_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='400Hz Y方向')

    # Z方向目标值和各频率段数据
    target_stiffness_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                             verbose_name='Z方向目标值')
    freq_50_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='50Hz Z方向')
    # 新增：63Hz Z方向，两位小数
    freq_63_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='63Hz Z方向')
    freq_80_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='80Hz Z方向')
    freq_100_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='100Hz Z方向')
    freq_125_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='125Hz Z方向')
    freq_160_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='160Hz Z方向')
    freq_200_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='200Hz Z方向')
    freq_250_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='250Hz Z方向')
    freq_315_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='315Hz Z方向')
    freq_350_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='350Hz Z方向')
    freq_400_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='400Hz Z方向')

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


class VehicleMountIsolationTest(models.Model):
    """整车悬置隔振率测试基本信息表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    test_date = models.DateField(verbose_name='测试时间')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, verbose_name='测试人员')
    suspension_type = models.CharField(max_length=50, verbose_name='悬挂形式')
    tire_pressure = models.CharField(max_length=50, null=True, blank=True, verbose_name='实测胎压')

    # 驾驶员座椅导轨振动 AC OFF (m/s²)
    seat_vib_x_ac_off = models.FloatField(null=True, blank=True, verbose_name='座椅导轨X方向振动 AC OFF')
    seat_vib_y_ac_off = models.FloatField(null=True, blank=True, verbose_name='座椅导轨Y方向振动 AC OFF')
    seat_vib_z_ac_off = models.FloatField(null=True, blank=True, verbose_name='座椅导轨Z方向振动 AC OFF')

    # 驾驶员座椅导轨振动 AC ON (m/s²)
    seat_vib_x_ac_on = models.FloatField(null=True, blank=True, verbose_name='座椅导轨X方向振动 AC ON')
    seat_vib_y_ac_on = models.FloatField(null=True, blank=True, verbose_name='座椅导轨Y方向振动 AC ON')
    seat_vib_z_ac_on = models.FloatField(null=True, blank=True, verbose_name='座椅导轨Z方向振动 AC ON')

    # 方向盘振动 AC OFF (m/s²)
    steering_vib_x_ac_off = models.FloatField(null=True, blank=True, verbose_name='方向盘X方向振动 AC OFF')
    steering_vib_y_ac_off = models.FloatField(null=True, blank=True, verbose_name='方向盘Y方向振动 AC OFF')
    steering_vib_z_ac_off = models.FloatField(null=True, blank=True, verbose_name='方向盘Z方向振动 AC OFF')

    # 方向盘振动 AC ON (m/s²)
    steering_vib_x_ac_on = models.FloatField(null=True, blank=True, verbose_name='方向盘X方向振动 AC ON')
    steering_vib_y_ac_on = models.FloatField(null=True, blank=True, verbose_name='方向盘Y方向振动 AC ON')
    steering_vib_z_ac_on = models.FloatField(null=True, blank=True, verbose_name='方向盘Z方向振动 AC ON')

    # 内噪 AC OFF (dB)
    cabin_noise_front_ac_off = models.FloatField(null=True, blank=True, verbose_name='前排内噪 AC OFF')
    cabin_noise_rear_ac_off = models.FloatField(null=True, blank=True, verbose_name='后排内噪 AC OFF')

    # 内噪 AC ON (dB)
    cabin_noise_front_ac_on = models.FloatField(null=True, blank=True, verbose_name='前排内噪 AC ON')
    cabin_noise_rear_ac_on = models.FloatField(null=True, blank=True, verbose_name='后排内噪 AC ON')

    class Meta:
        db_table = 'vehicle_mount_isolation_tests'
        verbose_name = '整车悬置隔振率测试'
        verbose_name_plural = '整车悬置隔振率测试'
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.test_date}"


class MountIsolationData(models.Model):
    """悬置隔振率试验数据表"""
    test = models.ForeignKey(VehicleMountIsolationTest, on_delete=models.CASCADE, verbose_name='测试基本信息')
    measuring_point = models.CharField(max_length=100, verbose_name='测点名称')

    # X方向数据
    x_ac_off_isolation = models.FloatField(null=True, blank=True, verbose_name='X方向AC OFF隔振率(dB)')
    x_ac_off_vibration = models.FloatField(null=True, blank=True, verbose_name='X方向AC OFF 2阶被动端振动(m/s²)')
    x_ac_on_isolation = models.FloatField(null=True, blank=True, verbose_name='X方向AC ON隔振率(dB)')
    x_ac_on_vibration = models.FloatField(null=True, blank=True, verbose_name='X方向AC ON 2阶被动端振动(m/s²)')

    # Y方向数据
    y_ac_off_isolation = models.FloatField(null=True, blank=True, verbose_name='Y方向AC OFF隔振率(dB)')
    y_ac_off_vibration = models.FloatField(null=True, blank=True, verbose_name='Y方向AC OFF 2阶被动端振动(m/s²)')
    y_ac_on_isolation = models.FloatField(null=True, blank=True, verbose_name='Y方向AC ON隔振率(dB)')
    y_ac_on_vibration = models.FloatField(null=True, blank=True, verbose_name='Y方向AC ON 2阶被动端振动(m/s²)')

    # Z方向数据
    z_ac_off_isolation = models.FloatField(null=True, blank=True, verbose_name='Z方向AC OFF隔振率(dB)')
    z_ac_off_vibration = models.FloatField(null=True, blank=True, verbose_name='Z方向AC OFF 2阶被动端振动(m/s²)')
    z_ac_on_isolation = models.FloatField(null=True, blank=True, verbose_name='Z方向AC ON隔振率(dB)')
    z_ac_on_vibration = models.FloatField(null=True, blank=True, verbose_name='Z方向AC ON 2阶被动端振动(m/s²)')

    # 图片路径
    layout_image_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试布置图路径')
    curve_image_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试数据曲线图路径')

    class Meta:
        db_table = 'mount_isolation_data'
        verbose_name = '悬置隔振率试验数据'
        verbose_name_plural = '悬置隔振率试验数据'
        ordering = ['measuring_point']

    def __str__(self):
        return f"{self.test.vehicle_model.vehicle_model_name} - {self.measuring_point}"


class VehicleSuspensionIsolationTest(models.Model):
    """整车悬架隔振率测试基本信息表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    test_date = models.DateField(verbose_name='测试时间')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, verbose_name='测试人员')
    suspension_type = models.CharField(max_length=50, verbose_name='悬挂形式')
    tire_pressure = models.CharField(max_length=50, null=True, blank=True, verbose_name='实测胎压')
    test_condition = models.CharField(max_length=200, null=True, blank=True, verbose_name='测试工况')

    class Meta:
        db_table = 'vehicle_suspension_isolation_tests'
        verbose_name = '整车悬架隔振率测试'
        verbose_name_plural = '整车悬架隔振率测试'
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.test_date}"


class SuspensionIsolationData(models.Model):
    """悬架隔振率试验数据表"""
    test = models.ForeignKey(VehicleSuspensionIsolationTest, on_delete=models.CASCADE, verbose_name='测试基本信息')
    measuring_point = models.CharField(max_length=100, verbose_name='测点名称')

    # X方向数据 - 遵循数据精度要求：主动端/被动端使用Decimal(10,6)，隔振率使用Decimal(8,3)
    x_active_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                         verbose_name='X方向主动端(m/s²)')
    x_passive_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                          verbose_name='X方向被动端(m/s²)')
    x_isolation_rate = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True,
                                           verbose_name='X方向隔振率(dB)')

    # Y方向数据
    y_active_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                         verbose_name='Y方向主动端(m/s²)')
    y_passive_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                          verbose_name='Y方向被动端(m/s²)')
    y_isolation_rate = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True,
                                           verbose_name='Y方向隔振率(dB)')

    # Z方向数据
    z_active_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                         verbose_name='Z方向主动端(m/s²)')
    z_passive_value = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                          verbose_name='Z方向被动端(m/s²)')
    z_isolation_rate = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True,
                                           verbose_name='Z方向隔振率(dB)')

    # 图片路径
    layout_image_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试布置图路径')
    curve_image_path = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试数据曲线图路径')

    class Meta:
        db_table = 'suspension_isolation_data'
        verbose_name = '悬架隔振率试验数据'
        verbose_name_plural = '悬架隔振率试验数据'
        ordering = ['measuring_point']

    def __str__(self):
        return f"{self.test.vehicle_model.vehicle_model_name} - {self.measuring_point}"
