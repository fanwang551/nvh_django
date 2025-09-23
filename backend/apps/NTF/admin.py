from django.contrib import admin

from .models import NTFInfo, NTFTestResult


@admin.register(NTFInfo)
class NTFInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'vehicle_model', 'tester', 'test_time', 'location', 'seat_count', 'development_stage'
    )
    search_fields = ('vehicle_model__cle_model_code', 'tester', 'location')
    list_filter = ('development_stage', 'seat_count', 'sunroof_type', 'suspension_type')


@admin.register(NTFTestResult)
class NTFTestResultAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ntf_info', 'measurement_point',
        'x_target_value', 'y_target_value', 'z_target_value'
    )
    search_fields = ('measurement_point', 'ntf_info__vehicle_model__cle_model_code')

