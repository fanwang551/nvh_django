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


class NTFTestResult(models.Model):
    """NTF test result row."""

    DIRECTION_CHOICES = [
        ('X', 'X方向'),
        ('Y', 'Y方向'),
        ('Z', 'Z方向'),
    ]

    ntf_info = models.ForeignKey(
        NTFInfo,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='NTF信息'
    )
    measurement_point = models.CharField(max_length=100, verbose_name='测点')
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, verbose_name='方向')
    target_value = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='目标值(dB)')
    front_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='前排值(dB)')
    middle_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='中排值(dB)')
    rear_row_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='后排值(dB)')
    # ntf_curve expects {'frequency': [...], 'values': [...]} for echarts heatmap
    ntf_curve = models.JSONField(default=dict, verbose_name='NTF原始数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'NTF_test_result'
        verbose_name = 'NTF测试结果'
        verbose_name_plural = 'NTF测试结果'
        unique_together = ('ntf_info', 'measurement_point', 'direction')
        ordering = ['measurement_point', 'direction']

    def __str__(self) -> str:
        return f"{self.ntf_info_id} - {self.measurement_point} - {self.direction}"

    @property
    def frequency(self):
        return self.ntf_curve.get('frequency', [])

    @property
    def values(self):
        return self.ntf_curve.get('values', [])
