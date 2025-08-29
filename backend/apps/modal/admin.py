from django.contrib import admin
from .models import VehicleModel, Component, TestProject, ModalData


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['cle_model_code', 'vehicle_model_name', 'vin', 'drive_type', 'production_year', 'status', 'created_at']
    list_filter = ['status', 'drive_type', 'production_year', 'created_at']
    search_fields = ['cle_model_code', 'vehicle_model_name', 'vin']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['component_code', 'component_name', 'category', 'component_brand', 'component_model', 'created_at']
    list_filter = ['category', 'component_brand', 'created_at']
    search_fields = ['component_code', 'component_name', 'category', 'component_brand']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(TestProject)
class TestProjectAdmin(admin.ModelAdmin):
    list_display = ['project_code', 'vehicle_model', 'component', 'test_type', 'test_date', 'test_engineer', 'test_status']
    list_filter = ['test_status', 'test_type', 'test_date', 'created_at']
    search_fields = ['project_code', 'test_type', 'test_engineer']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['vehicle_model', 'component']


@admin.register(ModalData)
class ModalDataAdmin(admin.ModelAdmin):
    list_display = ['test_project', 'frequency', 'damping_ratio', 'mode_shape_description', 'updated_by', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['test_project__project_code', 'mode_shape_description', 'updated_by']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['test_project']
