from django.db import models


class VehicleModel(models.Model):
    """车型信息表"""
    cle_model_code = models.CharField(max_length=50, null=True, blank=True, verbose_name='车型代码')
    vehicle_model_name = models.CharField(max_length=100, verbose_name='车型名称')
    vin = models.CharField(max_length=50, unique=True, verbose_name='VIN码')
    drive_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='驱动类型')
    configuration = models.CharField(max_length=200, null=True, blank=True, verbose_name='具体配置')
    production_year = models.IntegerField(null=True, blank=True, verbose_name='生产年份')

    # 新增字段：能源形式、悬挂形式、天窗形式、座位数
    energy_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='能源形式')
    suspension_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='悬挂形式')
    sunroof_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='天窗形式')
    seat_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='座位数')
    subframe_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='副车架形式')
    front_windshield = models.CharField(max_length=50, null=True, blank=True, verbose_name='前挡玻璃')
    side_door_glass = models.CharField(max_length=50, null=True, blank=True, verbose_name='侧门玻璃')
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    # 对标车型字段
    benchmark_vehicle = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benchmarked_by',
        verbose_name='对标车型'
    )


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

    created_at = None
    updated_at = None

    class Meta:
        db_table = 'components'
        verbose_name = '零部件'
        verbose_name_plural = '零部件'
        ordering = ['id']

    def __str__(self):
        return f"{self.component_name} ({self.category})"


class TestProject(models.Model):
    """测试项目表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车辆')
    component = models.ForeignKey(Component, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='零件')
    test_type = models.CharField(max_length=200, null=True, blank=True, verbose_name='测试类型')
    test_date = models.DateField(null=True, blank=True, verbose_name='测试日期')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    test_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name='测试工程师')
    test_status = models.CharField(max_length=200, null=True, blank=True, verbose_name='测试状态')
    excitation_method = models.CharField(max_length=100, null=True, blank=True, verbose_name='激励方式')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')
    

    class Meta:
        db_table = 'test_projects'
        verbose_name = '测试项目'
        verbose_name_plural = '测试项目'
        ordering = ['-id']

    def __str__(self):
        return f"{self.id} - {self.test_type}"


class ModalData(models.Model):
    """模态数据表"""
    test_project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='测试项目')
    frequency = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='频率(Hz)')
    damping_ratio = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True, verbose_name='阻尼比')
    mode_shape_description = models.TextField(null=True, blank=True, verbose_name='模态振型描述')
    mode_shape_file = models.CharField(max_length=255, null=True, blank=True, verbose_name='GIF动图文件路径')
    test_photo_file = models.CharField(max_length=255, null=True, blank=True, verbose_name='测试照片文件路径')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')


    class Meta:
        db_table = 'modal_data'
        verbose_name = '模态数据'
        verbose_name_plural = '模态数据'
        ordering = ['-id']

    def __str__(self):
        return f"{self.test_project.id} - {self.frequency}Hz"


class AirtightnessTest(models.Model):
    """气密性测试数据表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    test_date = models.DateField(verbose_name='测试日期')
    test_engineer = models.CharField(max_length=50, verbose_name='测试工程师')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')

    # 整车不可控泄漏量
    uncontrolled_leakage = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='整车不可控泄漏量(SCFM)')

    # 阀系统
    left_pressure_valve = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='左侧泄压阀(SCFM)')
    right_pressure_valve = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='右侧泄压阀(SCFM)')
    ac_circulation_valve = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='空调内外循环阀(SCFM)')

    # 门系统
    right_door_drain_hole = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='右侧门漏液孔(SCFM)')
    tailgate_drain_hole = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='尾门漏液孔(SCFM)')
    right_door_outer_seal = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='右侧门外水切(SCFM)')
    right_door_outer_opening = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='右侧门外开(SCFM)')
    side_mirrors = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='两侧外后视镜(SCFM)')

    # 白车身和其他区域
    body_shell_leakage = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='白车身泄漏量(SCFM)')
    other_area = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='其他区域(SCFM)')

    # 备注信息
    notes = models.TextField(null=True, blank=True, verbose_name='备注')


    class Meta:
        db_table = 'airtightness_tests'
        verbose_name = '气密性测试'
        verbose_name_plural = '气密性测试'
        ordering = ['-id']

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - {self.test_date}"


class AirtightnessImage(models.Model):
    """气密性测试图片表"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, verbose_name='车型')
    test_date = models.DateField(null=True, blank=True,verbose_name='测试日期')
    test_engineer = models.CharField(max_length=50,null=True, blank=True, verbose_name='测试工程师')
    test_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试地点')
    # 三个位置的图片路径
    front_compartment_image = models.ImageField(upload_to='airtightness/',max_length=255, null=True, blank=True, verbose_name='前舱图片路径')
    door_image = models.ImageField(upload_to='airtightness/',max_length=255, null=True, blank=True, verbose_name='车门图片路径')
    tailgate_image = models.ImageField(upload_to='airtightness/',max_length=255, null=True, blank=True, verbose_name='尾门图片路径')

    notes = models.TextField(null=True, blank=True, verbose_name='备注')


    class Meta:
        db_table = 'airtightness_images'
        verbose_name = '气密性测试图片'
        verbose_name_plural = '气密性测试图片'
        ordering = ['-id']

    def __str__(self):
        return f"{self.vehicle_model.vehicle_model_name} - 气密性图片"
