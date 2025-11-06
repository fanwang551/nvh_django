from django.db import models


class SampleInfo(models.Model):
    """样品信息表 - 整合VOC和气味数据"""

    # 基本信息
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    development_stage = models.CharField(max_length=50, null=True, blank=True, verbose_name='开发阶段')
    status = models.CharField(max_length=20, null=True, blank=True, verbose_name='状态')
    test_order_no = models.CharField(max_length=50, verbose_name='检测委托单号', unique=True)
    sample_no = models.CharField(max_length=50, verbose_name='样品编号', db_index=True)
    sample_image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='样品图URL')
    test_date = models.DateField(null=True, blank=True, verbose_name='检测时间')

    # VOC检测数据（10项）
    benzene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='苯')
    toluene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='甲苯')
    ethylbenzene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='乙苯')
    xylene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='二甲苯')
    styrene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='苯乙烯')
    formaldehyde = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='甲醛')
    acetaldehyde = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='乙醛')
    acrolein = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='丙烯醛')
    acetone = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='丙酮')
    tvoc = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='TVOC')

    # 气味检测数据（4项 + 均值）
    odor_static_front = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='静态-前排')
    odor_static_rear = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='静态-后排')
    odor_dynamic_front = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='动态-前排')
    odor_dynamic_rear = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='动态-后排')
    odor_mean = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='气味均值')

    class Meta:
        db_table = 'voc_sample_info'
        verbose_name = '样品信息'
        verbose_name_plural = '样品信息'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['project_name']),
            models.Index(fields=['part_name']),
            models.Index(fields=['sample_no']),
            models.Index(fields=['test_date']),
        ]

    def __str__(self):
        return f"{self.project_name} - {self.part_name} - {self.sample_no}"

