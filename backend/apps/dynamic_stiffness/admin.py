from django.contrib import admin
from .models import DynamicStiffnessTest, DynamicStiffnessData, VehicleMountIsolationTest, MountIsolationData


@admin.register(DynamicStiffnessTest)
class DynamicStiffnessTestAdmin(admin.ModelAdmin):
    list_display = ['vehicle_model', 'part_name', 'test_date', 'test_engineer', 'analysis_engineer']
    list_filter = ['test_date', 'part_name', 'test_engineer']
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
        ('鍩烘湰淇℃伅', {
            'fields': ('test', 'subsystem', 'test_point')
        }),
        ('X鏂瑰悜鏁版嵁', {
            'fields': (
                'target_stiffness_x',
                ('freq_50_x', 'freq_80_x', 'freq_100_x', 'freq_125_x', 'freq_160_x'),
                ('freq_200_x', 'freq_250_x', 'freq_315_x', 'freq_350_x', 'freq_400_x')
            )
        }),
        ('Y鏂瑰悜鏁版嵁', {
            'fields': (
                'target_stiffness_y',
                ('freq_50_y', 'freq_80_y', 'freq_100_y', 'freq_125_y', 'freq_160_y'),
                ('freq_200_y', 'freq_250_y', 'freq_315_y', 'freq_350_y', 'freq_400_y')
            )
        }),
        ('Z鏂瑰悜鏁版嵁', {
            'fields': (
                'target_stiffness_z',
                ('freq_50_z', 'freq_80_z', 'freq_100_z', 'freq_125_z', 'freq_160_z'),
                ('freq_200_z', 'freq_250_z', 'freq_315_z', 'freq_350_z', 'freq_400_z')
            )
        }),
        ('鍥剧墖淇℃伅', {
            'fields': ('layout_image', 'curve_image')
        })
    )


@admin.register(VehicleMountIsolationTest)
class VehicleMountIsolationTestAdmin(admin.ModelAdmin):
    list_display = ['vehicle_model', 'test_date', 'test_engineer', 'tire_pressure']
    list_filter = ['test_date', 'test_engineer']
    search_fields = ['vehicle_model__vehicle_model_name', 'test_engineer']
    ordering = ['-test_date']
    date_hierarchy = 'test_date'

    fieldsets = (
        ('鍩烘湰淇℃伅', {
            'fields': ('vehicle_model', 'test_date', 'test_location', 'test_engineer',  'tire_pressure')
        }),
        ('椹鹃┒鍛樺骇妞呭杞ㄦ尟鍔?AC OFF (m/s虏)', {
            'fields': ('seat_vib_x_ac_off', 'seat_vib_y_ac_off', 'seat_vib_z_ac_off')
        }),
        ('椹鹃┒鍛樺骇妞呭杞ㄦ尟鍔?AC ON (m/s虏)', {
            'fields': ('seat_vib_x_ac_on', 'seat_vib_y_ac_on', 'seat_vib_z_ac_on')
        }),
        ('鏂瑰悜鐩樻尟鍔?AC OFF (m/s虏)', {
            'fields': ('steering_vib_x_ac_off', 'steering_vib_y_ac_off', 'steering_vib_z_ac_off')
        }),
        ('鏂瑰悜鐩樻尟鍔?AC ON (m/s虏)', {
            'fields': ('steering_vib_x_ac_on', 'steering_vib_y_ac_on', 'steering_vib_z_ac_on')
        }),
        ('鍐呭櫔 AC OFF (dB)', {
            'fields': ('cabin_noise_front_ac_off', 'cabin_noise_rear_ac_off')
        }),
        ('鍐呭櫔 AC ON (dB)', {
            'fields': ('cabin_noise_front_ac_on', 'cabin_noise_rear_ac_on')
        })
    )


@admin.register(MountIsolationData)
class MountIsolationDataAdmin(admin.ModelAdmin):
    list_display = ['test', 'measuring_point', 'x_ac_off_isolation', 'y_ac_off_isolation', 'z_ac_off_isolation']
    list_filter = ['test_date', 'test_engineer']
    search_fields = ['test__vehicle_model__vehicle_model_name', 'measuring_point']
    ordering = ['test', 'measuring_point']

    fieldsets = (
        ('鍩烘湰淇℃伅', {
            'fields': ('test', 'measuring_point')
        }),
        ('X鏂瑰悜鏁版嵁', {
            'fields': (
                ('x_ac_off_isolation', 'x_ac_off_vibration'),
                ('x_ac_on_isolation', 'x_ac_on_vibration')
            )
        }),
        ('Y鏂瑰悜鏁版嵁', {
            'fields': (
                ('y_ac_off_isolation', 'y_ac_off_vibration'),
                ('y_ac_on_isolation', 'y_ac_on_vibration')
            )
        }),
        ('Z鏂瑰悜鏁版嵁', {
            'fields': (
                ('z_ac_off_isolation', 'z_ac_off_vibration'),
                ('z_ac_on_isolation', 'z_ac_on_vibration')
            )
        }),
        ('鍥剧墖淇℃伅', {
            'fields': ('layout_image_path', 'curve_image_path')
        })
    )
