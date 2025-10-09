from django.contrib import admin

from .models import NTFInfo, NTFTestResult


@admin.register(NTFInfo)
class NTFInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'vehicle_model', 'tester', 'test_time', 'location'
    )
    search_fields = ('vehicle_model__cle_model_code', 'tester', 'location')
    list_filter = ('test_time',)


@admin.register(NTFTestResult)
class NTFTestResultAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ntf_info', 'measurement_point', 'layout_image_url', 'created_at', 'updated_at'
    )
    search_fields = ('measurement_point', 'ntf_info__vehicle_model__cle_model_code')

