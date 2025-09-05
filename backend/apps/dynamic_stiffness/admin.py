from django.contrib import admin
from .models import DynamicStiffnessTest, DynamicStiffnessData


@admin.register(DynamicStiffnessTest)
class DynamicStiffnessTestAdmin(admin.ModelAdmin):
    list_display = ['vehicle_model', 'part_name', 'test_date', 'test_engineer', 'analysis_engineer', 'suspension_type']
    list_filter = ['test_date', 'part_name', 'suspension_type', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'part_name', 'test_engineer', 'analysis_engineer']
    ordering = ['-test_date']
    date_hierarchy = 'test_date'


@admin.register(DynamicStiffnessData)
class DynamicStiffnessDataAdmin(admin.ModelAdmin):
    list_display = ['test', 'subsystem', 'test_point', 'target_stiffness_x', 'target_stiffness_y', 'target_stiffness_z']
    list_filter = ['subsystem', 'test_point', 'test__part_name']
    search_fields = ['test__vehicle_model__vehicle_model_name', 'subsystem', 'test_point']
    ordering = ['test', 'subsystem', 'test_point']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('test', 'subsystem', 'test_point')
        }),
        ('X方向数据', {
            'fields': (
                'target_stiffness_x',
                ('freq_50_x', 'freq_80_x', 'freq_100_x', 'freq_125_x', 'freq_160_x'),
                ('freq_200_x', 'freq_250_x', 'freq_315_x', 'freq_350_x', 'freq_400_x')
            )
        }),
        ('Y方向数据', {
            'fields': (
                'target_stiffness_y',
                ('freq_50_y', 'freq_80_y', 'freq_100_y', 'freq_125_y', 'freq_160_y'),
                ('freq_200_y', 'freq_250_y', 'freq_315_y', 'freq_350_y', 'freq_400_y')
            )
        }),
        ('Z方向数据', {
            'fields': (
                'target_stiffness_z',
                ('freq_50_z', 'freq_80_z', 'freq_100_z', 'freq_125_z', 'freq_160_z'),
                ('freq_200_z', 'freq_250_z', 'freq_315_z', 'freq_350_z', 'freq_400_z')
            )
        }),
        ('图片信息', {
            'fields': ('layout_image', 'curve_image')
        })
    )
