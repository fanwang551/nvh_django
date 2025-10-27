from django.db import models
from apps.modal.models import VehicleModel


class SampleInfo(models.Model):
    """样品信息表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    part_name = models.CharField(max_length=100, verbose_name='零件名称')
    development_stage = models.CharField(max_length=50, null=True, blank=True, verbose_name='开发阶段')
    status = models.CharField(max_length=20,null=True, blank=True, verbose_name='状态')
    test_order_no = models.CharField(max_length=50, verbose_name='检测委托单号')
    sample_no = models.CharField(max_length=50, verbose_name='样品编号')
    sample_image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='样品图URL')
    
    class Meta:
        db_table = 'sample_info'
        verbose_name = '样品信息'
        verbose_name_plural = '样品信息'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['vehicle_model']),
            models.Index(fields=['sample_no']),
        ]

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.part_name} - {self.sample_no}"


class VocOdorResult(models.Model):
    """VOC和气味检测结果表"""
    sample = models.ForeignKey(SampleInfo, on_delete=models.CASCADE, verbose_name='样品')
    
    # VOC检测数据
    benzene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='苯 (mg/m³)')
    toluene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='甲苯 (mg/m³)')
    ethylbenzene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='乙苯 (mg/m³)')
    xylene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='二甲苯 (mg/m³)')
    styrene = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='苯乙烯 (mg/m³)')
    formaldehyde = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='甲醛 (mg/m³)')
    acetaldehyde = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='乙醛 (mg/m³)')
    acrolein = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='丙烯醛 (mg/m³)')
    tvoc = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='TVOC (mg/m³)')
    test_date = models.DateField(null=True, blank=True, verbose_name='检测时间')
    
    # 气味检测数据
    static_front = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='静态-前排')
    static_rear = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='静态-后排')
    dynamic_front = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='动态-前排')
    dynamic_rear = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='动态-后排')
    odor_mean = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='气味均值')
    
    class Meta:
        db_table = 'voc_odor_result'
        verbose_name = 'VOC和气味检测结果'
        verbose_name_plural = 'VOC和气味检测结果'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['sample']),
            models.Index(fields=['test_date']),
        ]

    def __str__(self):
        return f"{self.sample.sample_no} - VOC/气味检测结果"


# 保留别名以兼容旧代码
VocResult = VocOdorResult


class Substance(models.Model):
    """物质库表"""
    substance_name_cn = models.CharField(max_length=100, verbose_name='物质中文名')
    substance_name_en = models.CharField(max_length=100, null=True, blank=True, verbose_name='物质英文名')
    cas_no = models.CharField(max_length=50, unique=True, verbose_name='CAS号')
    odor_threshold = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='嗅阈值(μg/m³)')
    organic_threshold = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='有机物阈值')
    limit_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='限值')
    odor_character = models.CharField(max_length=200, null=True, blank=True, verbose_name='气味特性')
    main_usage = models.TextField(null=True, blank=True, verbose_name='主要用途')
    remark = models.TextField(null=True, blank=True, verbose_name='备注')
    
    class Meta:
        db_table = 'substances'
        verbose_name = '物质库'
        verbose_name_plural = '物质库'
        ordering = ['id']
        indexes = [
            models.Index(fields=['cas_no']),
            models.Index(fields=['substance_name_cn']),
        ]
    
    def __str__(self):
        return f"{self.substance_name_cn} ({self.cas_no})"


class SubstancesTest(models.Model):
    """全谱检测主表"""
    sample = models.ForeignKey(SampleInfo, on_delete=models.CASCADE, verbose_name='样品')
    oi = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='气味污染指数Oi')
    goi = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='气味污染贡献度GOi')
    vi = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='有机污染指数Vi')
    gvi = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='有机污染贡献度GVi')
    test_date = models.DateTimeField(null=True, blank=True, verbose_name='检测时间')
    
    class Meta:
        db_table = 'substances_test'
        verbose_name = '全谱检测主表'
        verbose_name_plural = '全谱检测主表'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['sample']),
            models.Index(fields=['test_date']),
        ]
    
    def __str__(self):
        return f"{self.sample.sample_no} - 全谱检测"


class SubstancesTestDetail(models.Model):
    """全谱检测明细表"""
    substances_test = models.ForeignKey(SubstancesTest, on_delete=models.CASCADE, related_name='details', verbose_name='全谱检测主表')
    substance = models.ForeignKey(Substance, on_delete=models.CASCADE, verbose_name='物质')
    retention_time = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='保留时间')
    match_degree = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='匹配度(0-100)')
    concentration = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name='浓度(μg/m³)')
    concentration_ratio = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name='浓度占比(%)')
    dilution_oij = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='稀释倍数Oij')
    dilution_wih = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='挥发性有机物阈稀释倍数Wih')
    
    class Meta:
        db_table = 'substances_test_detail'
        verbose_name = '全谱检测明细'
        verbose_name_plural = '全谱检测明细'
        ordering = ['id']
        indexes = [
            models.Index(fields=['substances_test']),
            models.Index(fields=['substance']),
        ]
    
    def __str__(self):
        return f"{self.substances_test.sample.sample_no} - {self.substance.substance_name_cn}"
