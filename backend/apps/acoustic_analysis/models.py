from django.db import models


class ConditionMeasurePoint(models.Model):
    """工况测点维度表：仅存储工况与测点"""

    class MeasureType(models.TextChoices):
        NOISE = 'noise', '噪声'
        VIBRATION = 'vibration', '振动'
        SPEED = 'speed', '转速'

    work_condition = models.CharField(max_length=100, verbose_name='工况', db_index=True)
    measure_point = models.CharField(max_length=100, verbose_name='测点', db_index=True)
    measure_type = models.CharField(
        max_length=20,
        choices=MeasureType.choices,
        default=MeasureType.NOISE,
        verbose_name='测点类型',
        db_index=True,
    )

    class Meta:
        db_table = 'condition_measure_point'
        verbose_name = '工况测点'
        verbose_name_plural = '工况测点'
        indexes = [
            models.Index(fields=['work_condition', 'measure_point'], name='idx_cm_wc_mp'),
            models.Index(fields=['measure_type'], name='idx_cm_measure_type'),
        ]
        ordering = ['work_condition', 'measure_point']

    def __str__(self) -> str:
        return f"{self.work_condition} - {self.measure_point}"


class AcousticTestData(models.Model):
    """声学测试数据表（频谱、总声压级等）"""

    vehicle_model = models.ForeignKey(
        'modal.VehicleModel',
        on_delete=models.CASCADE,
        related_name='acoustic_test_data',
        verbose_name='车型信息'
    )

    condition_point = models.ForeignKey(
        'acoustic_analysis.ConditionMeasurePoint',
        on_delete=models.PROTECT,
        related_name='test_data',
        verbose_name='工况测点'
    )

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

    class Meta:
        # 继续复用原表名，避免不必要的物理表重命名
        db_table = 'test_data_all'
        verbose_name = '声学测试数据'
        verbose_name_plural = '声学测试数据'
        indexes = [
            models.Index(fields=['vehicle_model', 'condition_point'], name='idx_vm_cp'),
            models.Index(fields=['test_date'], name='idx_test_date'),
            # 关键复合索引：匹配常用过滤+排序 (vm, cp, test_date, id)
            # 可显著降低 ORDER BY -test_date,-id LIMIT 1 的 filesort 压力
            models.Index(fields=['vehicle_model', 'condition_point', 'test_date', 'id'], name='idx_vm_cp_date_id'),
        ]
        ordering = [
            'vehicle_model_id',
            'condition_point__work_condition',
            'condition_point__measure_point',
            '-test_date',
            '-id',
        ]

    def __str__(self) -> str:
        wc = getattr(self.condition_point, 'work_condition', '')
        mp = getattr(self.condition_point, 'measure_point', '')
        return f"{self.vehicle_model_id} - {wc} - {mp}"


class DynamicNoiseData(models.Model):
    """动态噪声数据表"""

    vehicle_model_id = models.IntegerField(verbose_name='车型ID', db_index=True)
    condition_measure_point = models.ForeignKey(
        ConditionMeasurePoint,
        on_delete=models.CASCADE,
        verbose_name='工况测点',
        related_name='dynamic_noise_data',
    )

    class XAxisType(models.TextChoices):
        SPEED = 'speed', '车速'
        RPM = 'rpm', '转速'

    x_axis_type = models.CharField(
        max_length=20,
        choices=XAxisType.choices,
        verbose_name='横轴类型',
        db_index=True,
    )
    # 数据格式: {"speed/rpm": [...], "dB(A)": [...]}
    sound_pressure_curve = models.JSONField(verbose_name='声压级曲线数据')
    # 数据格式: {"speed/rpm": [...], "%AI": [...]}
    speech_clarity_curve = models.JSONField(verbose_name='语音清晰度曲线数据')

    noise_analysis_image = models.CharField(max_length=500, verbose_name='噪声分析图路径', blank=True)
    audio_file = models.CharField(max_length=500, verbose_name='音频文件路径(.wav)', blank=True)
    spectrum_file = models.CharField(max_length=500, verbose_name='三维频谱文件路径(.pptx)', blank=True)
    spectrum_image_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='频谱图路径',
        help_text='存储频谱图的相对路径或URL',
    )

    class Meta:
        verbose_name = '动态噪声数据'
        verbose_name_plural = verbose_name
        unique_together = ['vehicle_model_id', 'condition_measure_point']
        indexes = [
            models.Index(fields=['vehicle_model_id'], name='idx_dyn_vm'),
            models.Index(fields=['condition_measure_point'], name='idx_dyn_cmp'),
            models.Index(fields=['x_axis_type'], name='idx_dyn_x_axis'),
        ]

    def __str__(self):
        cmp_obj = getattr(self, 'condition_measure_point', None)
        wc = getattr(cmp_obj, 'work_condition', '')
        mp = getattr(cmp_obj, 'measure_point', '')
        return f"{self.vehicle_model_id} - {wc} - {mp}"
