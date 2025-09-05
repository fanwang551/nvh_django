from django.contrib import admin
from .models import (
    SoundInsulationArea, SoundInsulationData, VehicleSoundInsulationData,
    VehicleReverberationData, SoundAbsorptionCoefficients, SoundInsulationCoefficients,
    MaterialPorosityFlowResistance
)


@admin.register(SoundInsulationArea)
class SoundInsulationAreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'area_name', 'description']
    search_fields = ['area_name']
    ordering = ['id']


@admin.register(SoundInsulationData)
class SoundInsulationDataAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vehicle_model', 'area', 'test_date', 'test_location',
        'test_engineer', 'created_at'
    ]
    list_filter = ['area', 'test_date', 'test_location', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'area__area_name', 'test_engineer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('vehicle_model', 'area')
        }),
        ('频率数据 (Hz)', {
            'fields': (
                ('freq_200', 'freq_250', 'freq_315', 'freq_400'),
                ('freq_500', 'freq_630', 'freq_800', 'freq_1000'),
                ('freq_1250', 'freq_1600', 'freq_2000', 'freq_2500'),
                ('freq_3150', 'freq_4000', 'freq_5000', 'freq_6300'),
                ('freq_8000', 'freq_10000')
            ),
            'classes': ('collapse',)
        }),
        ('测试信息', {
            'fields': ('test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks')
        })
    )


@admin.register(VehicleSoundInsulationData)
class VehicleSoundInsulationDataAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vehicle_model', 'test_date', 'test_location',
        'test_engineer', 'created_at'
    ]
    list_filter = ['test_date', 'test_location', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'vehicle_model__cle_model_code', 'test_engineer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('vehicle_model',)
        }),
        ('频率数据 (Hz)', {
            'fields': (
                ('freq_200', 'freq_250', 'freq_315', 'freq_400'),
                ('freq_500', 'freq_630', 'freq_800', 'freq_1000'),
                ('freq_1250', 'freq_1600', 'freq_2000', 'freq_2500'),
                ('freq_3150', 'freq_4000', 'freq_5000', 'freq_6300'),
                ('freq_8000', 'freq_10000')
            ),
            'classes': ('collapse',)
        }),
        ('测试信息', {
            'fields': ('test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks')
        })
    )


@admin.register(VehicleReverberationData)
class VehicleReverberationDataAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vehicle_model', 'test_date', 'test_location',
        'test_engineer', 'created_at'
    ]
    list_filter = ['test_date', 'test_location', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'vehicle_model__cle_model_code', 'test_engineer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('vehicle_model',)
        }),
        ('混响时间数据 (Hz)', {
            'fields': (
                ('freq_400', 'freq_500', 'freq_630', 'freq_800'),
                ('freq_1000', 'freq_1250', 'freq_1600', 'freq_2000'),
                ('freq_2500', 'freq_3150', 'freq_4000', 'freq_5000'),
                ('freq_6300', 'freq_8000', 'freq_10000')
            ),
            'classes': ('collapse',)
        }),
        ('测试信息', {
            'fields': ('test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks')
        })
    )


@admin.register(SoundAbsorptionCoefficients)
class SoundAbsorptionCoefficientsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'part_name', 'material_composition', 'weight', 'thickness',
        'manufacturer', 'test_institution', 'created_at'
    ]
    list_filter = ['part_name', 'manufacturer', 'test_institution', 'test_date']
    search_fields = ['part_name', 'material_composition', 'manufacturer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('part_name', 'material_composition', 'manufacturer', 'test_institution', 'thickness', 'weight')
        }),
        ('测试值 (125Hz-10000Hz)', {
            'fields': (
                ('test_value_125', 'test_value_160', 'test_value_200', 'test_value_250'),
                ('test_value_315', 'test_value_400', 'test_value_500', 'test_value_630'),
                ('test_value_800', 'test_value_1000', 'test_value_1250', 'test_value_1600'),
                ('test_value_2000', 'test_value_2500', 'test_value_3150', 'test_value_4000'),
                ('test_value_5000', 'test_value_6300', 'test_value_8000', 'test_value_10000')
            ),
            'classes': ('collapse',)
        }),
        ('目标值 (125Hz-10000Hz)', {
            'fields': (
                ('target_value_125', 'target_value_160', 'target_value_200', 'target_value_250'),
                ('target_value_315', 'target_value_400', 'target_value_500', 'target_value_630'),
                ('target_value_800', 'target_value_1000', 'target_value_1250', 'target_value_1600'),
                ('target_value_2000', 'target_value_2500', 'target_value_3150', 'target_value_4000'),
                ('target_value_5000', 'target_value_6300', 'target_value_8000', 'target_value_10000')
            ),
            'classes': ('collapse',)
        }),
        ('测试信息', {
            'fields': ('test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks')
        })
    )


@admin.register(SoundInsulationCoefficients)
class SoundInsulationCoefficientsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'part_name', 'material_composition', 'test_type', 'weight', 'thickness',
        'manufacturer', 'test_institution', 'created_at'
    ]
    list_filter = ['part_name', 'test_type', 'manufacturer', 'test_institution', 'test_date']
    search_fields = ['part_name', 'material_composition', 'manufacturer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('part_name', 'material_composition', 'test_type', 'manufacturer', 'test_institution', 'thickness', 'weight')
        }),
        ('测试值 (125Hz-10000Hz)', {
            'fields': (
                ('test_value_125', 'test_value_160', 'test_value_200', 'test_value_250'),
                ('test_value_315', 'test_value_400', 'test_value_500', 'test_value_630'),
                ('test_value_800', 'test_value_1000', 'test_value_1250', 'test_value_1600'),
                ('test_value_2000', 'test_value_2500', 'test_value_3150', 'test_value_4000'),
                ('test_value_5000', 'test_value_6300', 'test_value_8000', 'test_value_10000')
            ),
            'classes': ('collapse',)
        }),
        ('目标值 (125Hz-10000Hz)', {
            'fields': (
                ('target_value_125', 'target_value_160', 'target_value_200', 'target_value_250'),
                ('target_value_315', 'target_value_400', 'target_value_500', 'target_value_630'),
                ('target_value_800', 'target_value_1000', 'target_value_1250', 'target_value_1600'),
                ('target_value_2000', 'target_value_2500', 'target_value_3150', 'target_value_4000'),
                ('target_value_5000', 'target_value_6300', 'target_value_8000', 'target_value_10000')
            ),
            'classes': ('collapse',)
        }),
        ('测试信息', {
            'fields': ('test_image_path', 'test_date', 'test_location', 'test_engineer', 'remarks')
        })
    )


@admin.register(MaterialPorosityFlowResistance)
class MaterialPorosityFlowResistanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'part_name', 'material_composition', 'material_manufacturer',
        'thickness_mm', 'weight_per_area', 'density', 'porosity_percent',
        'flow_resistance', 'test_engineer', 'created_at'
    ]
    list_filter = ['part_name', 'material_manufacturer', 'test_institution', 'test_engineer', 'created_at']
    search_fields = ['part_name', 'material_composition', 'material_manufacturer', 'test_engineer']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('part_name', 'material_composition', 'material_manufacturer', 'test_institution')
        }),
        ('物理参数', {
            'fields': (
                ('thickness_mm', 'weight_per_area', 'density'),
                ('porosity_percent', 'porosity_deviation_percent'),
                ('flow_resistance', 'flow_resistance_deviation')
            )
        }),
        ('测试信息', {
            'fields': ('test_time', 'test_engineer', 'remarks')
        })
    )
