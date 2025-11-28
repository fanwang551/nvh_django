from django.db import models


class WheelPerformance(models.Model):
    """存储不同车型的车轮性能参数。"""

    vehicle_model = models.ForeignKey(
        'modal.VehicleModel',
        on_delete=models.CASCADE,
        related_name='wheel_performances',
        verbose_name='车型信息'
    )
    tire_brand = models.CharField(max_length=100, verbose_name='轮胎品牌')
    tire_model = models.CharField(max_length=100, verbose_name='轮胎型号')
    is_silent = models.BooleanField(default=False, verbose_name='是否静音胎')
    rim_material = models.CharField(max_length=100, verbose_name='轮辋材质')
    rim_mass_mt = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='轮辋质量 M_T (kg)')
    resonance_peak_f1 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='共振峰 f1 (Hz)')
    anti_resonance_peak_f2 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='反共振峰 f2 (Hz)')
    rim_lateral_stiffness = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='轮辋侧向刚度 (kN/mm)')
    rim_stiffness_curve_url = models.CharField(max_length=255, verbose_name='轮辋刚度曲线图 URL')
    rim_stiffness_test_image_url = models.CharField(max_length=255, verbose_name='轮辋刚度测试图 URL')
    force_transfer_first_peak = models.DecimalField(max_digits=7, decimal_places=3, verbose_name='力传递一阶峰值')
    force_transfer_test_image_url = models.CharField(max_length=255, verbose_name='力传递测试图 URL')
    # {"dB":[],"frequency":[]}
    force_transfer_signal = models.JSONField(default=list, verbose_name='力传递一阶曲线信号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wheel_performance'
        verbose_name = '车轮性能'
        verbose_name_plural = '车轮性能'
        ordering = ['vehicle_model__vehicle_model_name', 'tire_brand', 'tire_model']

    def __str__(self) -> str:
        return f"{self.vehicle_model.vehicle_model_name} - {self.tire_brand} {self.tire_model}"
