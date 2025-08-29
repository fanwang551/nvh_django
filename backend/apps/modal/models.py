from django.db import models


class VehicleModel(models.Model):
    """车型信息表"""
    cle_model_code = models.CharField(max_length=50, unique=True, verbose_name='车型代码')
    vehicle_model_name = models.CharField(max_length=100, verbose_name='车型名称')
    vin = models.CharField(max_length=50, unique=True, verbose_name='VIN码')
    drive_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='驱动类型')
    configuration = models.CharField(max_length=200, null=True, blank=True, verbose_name='具体配置')
    production_year = models.IntegerField(null=True, blank=True, verbose_name='生产年份')

    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='状态')

    class Meta:
        db_table = 'vehicle_models'
        verbose_name = '车型信息'
        verbose_name_plural = '车型信息'
        ordering = ['id']

    def __str__(self):
        return f"{self.cle_model_code} - {self.vehicle_model_name}"


class Component(models.Model):
    """零部件表"""
    component_name = models.CharField(max_length=100, verbose_name='零件名称')
    category = models.CharField(max_length=100, verbose_name='分类')
    component_brand = models.CharField(max_length=100, null=True, blank=True, verbose_name='零件品牌')
    component_model = models.CharField(max_length=100, null=True, blank=True, verbose_name='零件规格型号')
    component_code = models.CharField(max_length=50, unique=True, verbose_name='零件代码')

    class Meta:
        db_table = 'components'
        verbose_name = '零部件'
        verbose_name_plural = '零部件'
        ordering = ['id']

    def __str__(self):
        return f"{self.component_code} - {self.component_name}"


class TestProject(models.Model):
    """测试项目表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车辆')
    component = models.ForeignKey(Component, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='零件')
    test_type = models.CharField(max_length=200, verbose_name='测试类型')
    test_date = models.DateField(verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, verbose_name='测试工程师')
    test_status = models.CharField(max_length=200, null=True, blank=True, verbose_name='测试状态')
    excitation_method = models.CharField(max_length=100, null=True, blank=True, verbose_name='激励方式')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'test_projects'
        verbose_name = '测试项目'
        verbose_name_plural = '测试项目'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.test_type}"


class ModalData(models.Model):
    """模态数据表"""
    test_project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='测试项目')
    frequency = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='频率(Hz)')
    damping_ratio = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='阻尼比')
    mode_shape_description = models.TextField(null=True, blank=True, verbose_name='模态振型描述')
    mode_shape_file = models.CharField(max_length=255, null=True, blank=True, verbose_name='GIF动图文件路径')
    test_photo_file = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试照片文件路径')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    updated_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='修改人员')

    class Meta:
        db_table = 'modal_data'
        verbose_name = '模态数据'
        verbose_name_plural = '模态数据'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.test_project.project_code} - {self.frequency}Hz"
