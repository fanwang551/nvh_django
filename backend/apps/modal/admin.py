from django.contrib import admin
from .models import VehicleModel, Component, TestProject, ModalData, AirtightnessTest


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['cle_model_code', 'vehicle_model_name', 'vin', 'drive_type', 'production_year', 'status']
    list_filter = ['status', 'drive_type', 'production_year']
    search_fields = ['cle_model_code', 'vehicle_model_name', 'vin']
    ordering = ['id']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['component_code', 'component_name', 'category', 'component_brand', 'component_model']
    list_filter = ['category', 'component_brand']
    search_fields = ['component_code', 'component_name', 'category', 'component_brand']
    ordering = ['id']


@admin.register(TestProject)
class TestProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_model', 'component', 'test_type', 'test_date', 'test_engineer', 'test_status']
    list_filter = ['test_status', 'test_type', 'test_date', 'created_at']
    search_fields = ['test_type', 'test_engineer']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['vehicle_model', 'component']


@admin.register(ModalData)
class ModalDataAdmin(admin.ModelAdmin):
    list_display = ['test_project', 'frequency', 'damping_ratio', 'mode_shape_description', 'updated_by', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['test_project__id', 'mode_shape_description', 'updated_by']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['test_project']


@admin.register(AirtightnessTest)
class AirtightnessTestAdmin(admin.ModelAdmin):
    list_display = ['vehicle_model', 'test_date', 'test_engineer', 'uncontrolled_leakage', 'created_at']
    list_filter = ['test_date', 'test_engineer', 'created_at']
    search_fields = ['vehicle_model__vehicle_model_name', 'vehicle_model__cle_model_code', 'test_engineer']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
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
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
