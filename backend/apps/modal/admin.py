from django.contrib import admin
from django.core.exceptions import ValidationError
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

from .models import VehicleModel, Component, TestProject, ModalData, AirtightnessTest


class TestProjectResource(resources.ModelResource):
    vehicle_model = fields.Field(
        column_name='vehicle_model_id',
        attribute='vehicle_model',
        widget=ForeignKeyWidget(VehicleModel, 'id'),
    )
    component = fields.Field(
        column_name='component_id',
        attribute='component',
        widget=ForeignKeyWidget(Component, 'id'),
    )

    class Meta:
        model = TestProject
        import_id_fields = ('id',)
        fields = (
            'id',
            'test_type',
            'test_date',
            'test_location',
            'test_engineer',
            'test_status',
            'excitation_method',
            'notes',
            'component',
            'vehicle_model',
        )
        use_transactions = True

    def save_instance(self, instance, is_create, *args, **kwargs):
        if not is_create:
            raise ValidationError('记录已存在，禁止覆盖导入，请检查导入文件中的 id。')
        return super().save_instance(instance, is_create, *args, **kwargs)


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['cle_model_code', 'vehicle_model_name', 'vin', 'drive_type', 'production_year', 'status']
    list_filter = ['status', 'drive_type', 'production_year']
    search_fields = ['cle_model_code', 'vehicle_model_name', 'vin']
    ordering = ['id']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['component_name', 'category', 'component_brand', 'component_model']
    list_filter = ['category', 'component_brand']
    search_fields = ['component_name', 'category', 'component_brand']
    ordering = ['id']


@admin.register(TestProject)
class TestProjectAdmin(ImportExportModelAdmin):
    resource_class = TestProjectResource
    list_display = ['id', 'vehicle_model', 'component', 'test_type', 'test_date', 'test_engineer', 'test_status']
    list_filter = ['test_status', 'test_type', 'test_date']
    search_fields = ['test_type', 'test_engineer']
    ordering = ['-id']
    raw_id_fields = ['vehicle_model', 'component']


class ModalDataResource(resources.ModelResource):
    test_project = fields.Field(
        column_name='test_project_id',
        attribute='test_project',
        widget=ForeignKeyWidget(TestProject, 'id'),
    )

    class Meta:
        model = ModalData
        import_id_fields = ('id',)
        fields = (
            'id',
            'frequency',
            'damping_ratio',
            'mode_shape_description',
            'mode_shape_file',
            'test_photo_file',
            'notes',
            'test_project',
        )
        use_transactions = True

    def save_instance(self, instance, is_create, *args, **kwargs):
        if not is_create:
            raise ValidationError('记录已存在，禁止覆盖导入，请检查导入文件中的 id。')
        return super().save_instance(instance, is_create, *args, **kwargs)


@admin.register(ModalData)
class ModalDataAdmin(ImportExportModelAdmin):
    resource_class = ModalDataResource
    list_display = ['test_project', 'frequency', 'damping_ratio', 'mode_shape_description']
    list_filter = []
    search_fields = ['test_project__id', 'mode_shape_description']
    ordering = ['-id']
    raw_id_fields = ['test_project']


@admin.register(AirtightnessTest)
class AirtightnessTestAdmin(admin.ModelAdmin):
    list_display = ['vehicle_model', 'test_date', 'test_engineer', 'uncontrolled_leakage']
    list_filter = ['test_date', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'vehicle_model__cle_model_code', 'test_engineer']
    ordering = ['-id']
    raw_id_fields = ['vehicle_model']

    fieldsets = (
        ('基本信息', {
            'fields': ('vehicle_model', 'test_date', 'test_engineer', 'test_location', 'notes')
        }),
        ('整车泄漏量', {
            'fields': ('uncontrolled_leakage',)
        }),
        ('阀系统', {
            'fields': ('left_pressure_valve', 'right_pressure_valve', 'ac_circulation_valve')
        }),
        ('门系统', {
            'fields': ('right_door_drain_hole', 'tailgate_drain_hole', 'right_door_outer_seal',
                      'right_door_outer_opening', 'side_mirrors')
        }),
        ('其他区域', {
            'fields': ('body_shell_leakage', 'other_area')
        }),
        ('时间信息', {
            'fields': (),
            'classes': ('collapse',)
        })
    )
