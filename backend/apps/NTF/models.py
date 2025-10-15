from django.db import models


class NTFInfo(models.Model):
    """NTF 测试元数据（保持不变）"""

    vehicle_model = models.ForeignKey(
        'modal.VehicleModel',
        on_delete=models.CASCADE,
        related_name='ntf_infos',
        verbose_name='车型信息'
    )
    tester = models.CharField(max_length=50, verbose_name='测试人员')
    test_time = models.DateTimeField(verbose_name='测试时间')
    location = models.CharField(max_length=100, verbose_name='测试地点')

    

    class Meta:
        db_table = 'NTF_info'
        verbose_name = 'NTF测试信息'
        verbose_name_plural = 'NTF测试信息'
        ordering = ['-test_time']

    def __str__(self) -> str:
        code = getattr(self.vehicle_model, 'cle_model_code', None) or ''
        return f"{code} - {self.test_time:%Y-%m-%d}"


def _default_ntf_curve() -> dict:
    """新结构默认空对象；各位置(front/middle/rear)可缺失或为 null。"""
    return {}


class NTFTestResult(models.Model):
    """NTF 测试结果（精简版）

    仅保留测点、布置图 URL 与曲线 JSON：
    ntf_curve 示例结构：
    {
      "front": {
        "frequency": [20, 20.25, ...],
        "x_values": [...],
        "y_values": [...],
        "z_values": [...],
        "stats": {
          "x": {"max_20_200": 0.85, "max_200_500": 0.92},
          "y": {"max_20_200": 0.78, "max_200_500": 0.88},
          "z": {"max_20_200": 0.95, "max_200_500": 1.02}
        }
      },
      "middle": null,
      "rear": { ... }
    }
    """

    ntf_info = models.ForeignKey(
        NTFInfo,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='NTF信息'
    )
    measurement_point = models.CharField(max_length=100, verbose_name='测点')
    layout_image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='测点布置图URL')

    # 新 JSON 曲线结构
    ntf_curve = models.JSONField(default=_default_ntf_curve, blank=True, verbose_name='NTF曲线数据')

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
