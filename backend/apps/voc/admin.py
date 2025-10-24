from django.contrib import admin
from .models import SampleInfo, VocOdorResult


@admin.register(SampleInfo)
class SampleInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_model', 'part_name', 'status', 'test_order_no', 'sample_no']
    list_filter = ['status', 'development_stage', 'vehicle_model']
    search_fields = ['part_name', 'test_order_no', 'sample_no']
    list_per_page = 20


@admin.register(VocOdorResult)
class VocOdorResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'sample', 'benzene', 'toluene', 'formaldehyde', 'tvoc', 'static_front', 'odor_mean', 'test_date']
    list_filter = ['test_date', 'sample__status']
    search_fields = ['sample__sample_no', 'sample__part_name']
    list_per_page = 20
    fieldsets = (
        ('样品信息', {
            'fields': ('sample', 'test_date')
        }),
        ('VOC检测数据', {
            'fields': ('benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene', 
                      'formaldehyde', 'acetaldehyde', 'acrolein', 'tvoc')
        }),
        ('气味检测数据', {
            'fields': ('static_front', 'static_rear', 'dynamic_front', 'dynamic_rear', 'odor_mean')
        }),
    )
