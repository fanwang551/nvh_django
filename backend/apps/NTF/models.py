from django.db import models


class NTFInfo(models.Model):
    """NTF test metadata."""

    vehicle_model = models.ForeignKey(
        'modal.VehicleModel',
        on_delete=models.CASCADE,
        related_name='ntf_infos',
        verbose_name='车型信息'
    )
    tester = models.CharField(max_length=50, verbose_name='测试人员')
    test_time = models.DateTimeField(verbose_name='测试时间')
    location = models.CharField(max_length=100, verbose_name='测试地点')
    sunroof_type = models.CharField(max_length=50, verbose_name='天窗形式')
    suspension_type = models.CharField(max_length=50, verbose_name='悬挂形式')
    seat_count = models.PositiveSmallIntegerField(verbose_name='座位数')
    front_row_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='前排测试图片路径')
    middle_row_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='中排测试图片路径')
    rear_row_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='后排测试图片路径')
    development_stage = models.CharField(max_length=50, verbose_name='开发阶段')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'NTF_info'
        verbose_name = 'NTF测试信息'
        verbose_name_plural = 'NTF测试信息'
        ordering = ['-test_time']

    def __str__(self) -> str:
        return f"{self.vehicle_model.cle_model_code} - {self.test_time:%Y-%m-%d}"


def _default_ntf_curve() -> dict:
    return {
        'frequency': [],
        'x_values': [],
        'y_values': [],
        'z_values': [],
    }


class NTFTestResult(models.Model):
    """NTF test result per measurement point with X/Y/Z directions."""

    ntf_info = models.ForeignKey(
        NTFInfo,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='NTF信息'
    )
    measurement_point = models.CharField(max_length=100, verbose_name='测点')

    # X 方向
    x_target_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='X方向目标(dB)')
    x_front_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='X方向前排(dB)')
    x_middle_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='X方向中排(dB)')
    x_rear_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='X方向后排(dB)')

    # 单一曲线：每个测点包含 XYZ 三个方向数据
    # 结构：{frequency: [], x_values: [], y_values: [], z_values: []}
    # 兼容历史数据：若为 {frequency: [], values: []}，序列化层做兼容处理
    ntf_curve = models.JSONField(default=_default_ntf_curve, blank=True, verbose_name='NTF原始数据')

    # Y 方向
    y_target_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Y方向目标(dB)')
    y_front_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Y方向前排(dB)')
    y_middle_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Y方向中排(dB)')
    y_rear_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Y方向后排(dB)')

    # Z 方向
    z_target_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Z方向目标(dB)')
    z_front_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Z方向前排(dB)')
    z_middle_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Z方向中排(dB)')
    z_rear_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Z方向后排(dB)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'NTF_test_result'
        verbose_name = 'NTF测试结果'
        verbose_name_plural = 'NTF测试结果'
        unique_together = ('ntf_info', 'measurement_point')
        ordering = ['measurement_point']

    def __str__(self) -> str:
        return f"{self.ntf_info_id} - {self.measurement_point}"

