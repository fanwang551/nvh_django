from django.contrib import admin
from .models import SoundInsulationArea, SoundInsulationData, VehicleSoundInsulationData, VehicleReverberationData, VehicleReverberationData


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
