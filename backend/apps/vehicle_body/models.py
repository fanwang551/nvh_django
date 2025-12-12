from django.db import models
from decimal import Decimal, InvalidOperation


class SampleInfo(models.Model):
    """样品信息表 - 整合VOC和气味数据"""

    # 基本信息
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    development_stage = models.CharField(max_length=50, null=True, blank=True, verbose_name='开发阶段')
    status = models.CharField(max_length=20, null=True, blank=True, verbose_name='状态')
    test_order_no = models.CharField(max_length=50, verbose_name='检测委托单号')
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


class Substance(models.Model):
    """物质库表（独立于apps.voc）"""
    SUBSTANCE_TYPE_CHOICES = [
        ('standard', '行标规定'),
        ('custom', '自定义'),
    ]

    substance_name_cn = models.CharField(max_length=200, null=True, blank=True, verbose_name='物质中文名')
    substance_name_en = models.CharField(max_length=200, null=True, blank=True, verbose_name='物质英文名')
    cas_no = models.CharField(max_length=50, unique=True, verbose_name='CAS号')
    substance_type = models.CharField(max_length=20, choices=SUBSTANCE_TYPE_CHOICES, default='custom', verbose_name='物质类型')
    odor_threshold = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='嗅阈值(μg/m³)')
    organic_threshold = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='有机物阈值')
    limit_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='限值')
    odor_character = models.CharField(max_length=200, null=True, blank=True, verbose_name='气味特性')
    main_usage = models.TextField(null=True, blank=True, verbose_name='主要用途')
    remark = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'substanceInfo'
        verbose_name = '物质库'
        verbose_name_plural = '物质库'
        ordering = ['id']
        indexes = [
            models.Index(fields=['cas_no']),
            models.Index(fields=['substance_name_cn']),
        ]

    def __str__(self):
        return f"{self.substance_name_cn} ({self.cas_no})"


class SubstancesTestDetail(models.Model):
    """VOC及全谱物质浓度明细表（独立于apps.voc）"""

    sample = models.ForeignKey(SampleInfo, on_delete=models.CASCADE, related_name='substance_details', verbose_name='所属样品')
    # 通过 CAS 号进行外键关联
    substance = models.ForeignKey(
        Substance,
        to_field='cas_no',
        db_column='cas_no',
        on_delete=models.CASCADE,
        verbose_name='物质'
    )

    # 检测数据
    concentration = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='浓度(μg/m³)')
    retention_time = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='保留时间')
    match_degree = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='匹配度(%)')
    concentration_ratio = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name='浓度占比(%)')

    # 自动计算字段
    qij = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='气味阈稀释倍数 Qij')
    wih = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='有机物阈稀释倍数 Wih')

    def save(self, *args, **kwargs):
        """保存时自动计算 Qij 和 Wih"""
        try:
            if self.substance and self.substance.odor_threshold and self.substance.odor_threshold > 0:
                self.qij = (self.concentration or Decimal('0')) / self.substance.odor_threshold
        except (InvalidOperation, ZeroDivisionError):
            self.qij = None
        try:
            if self.substance and self.substance.organic_threshold and self.substance.organic_threshold > 0:
                self.wih = (self.concentration or Decimal('0')) / self.substance.organic_threshold
        except (InvalidOperation, ZeroDivisionError):
            self.wih = None
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'substance_test_details'
        verbose_name = 'VOC浓度明细'
        verbose_name_plural = 'VOC浓度明细'
        unique_together = [['sample', 'substance']]
