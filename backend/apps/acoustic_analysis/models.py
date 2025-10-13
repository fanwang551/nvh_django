from django.db import models


class TestDataAll(models.Model):
    """声学测试数据表（频谱、总声压级等）"""

    vehicle_model = models.ForeignKey(
        'modal.VehicleModel',
        on_delete=models.CASCADE,
        related_name='acoustic_test_data',
        verbose_name='车型信息'
    )
    work_condition = models.CharField(max_length=100, verbose_name='工况')
    measure_point = models.CharField(max_length=100, verbose_name='测点')

    # 频谱数据（约12000个数据点）
    # 格式：{"frequency": [...], "dB": [...]}
    spectrum_json = models.JSONField(null=True, blank=True, verbose_name='频谱数据JSON')

    # 总声压级数据（约20个数据点）
    # 格式：{"time": [...], "OA": [...]}
    oa_json = models.JSONField(null=True, blank=True, verbose_name='总声压级JSON')

    # 语音清晰度与有效值
    speech_clarity = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='语音清晰度')
    rms_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='有效值')

    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'test_data_all'
        verbose_name = '声学测试数据'
        verbose_name_plural = '声学测试数据'
        indexes = [
            models.Index(fields=['vehicle_model', 'work_condition', 'measure_point'], name='idx_vm_wc_mp'),
            models.Index(fields=['test_date'], name='idx_test_date'),
        ]
        ordering = ['vehicle_model_id', 'work_condition', 'measure_point', '-test_date', '-created_at']

    def __str__(self) -> str:
        return f"{self.vehicle_model_id} - {self.work_condition} - {self.measure_point}"

