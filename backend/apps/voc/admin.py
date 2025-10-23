from django.contrib import admin
from .models import SampleInfo, VocResult


@admin.register(SampleInfo)
class SampleInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_model', 'part_name', 'status', 'test_order_no', 'sample_no']
    list_filter = ['status', 'development_stage', 'vehicle_model']
    search_fields = ['part_name', 'test_order_no', 'sample_no']
    list_per_page = 20


@admin.register(VocResult)
class VocResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'sample', 'benzene', 'toluene', 'formaldehyde', 'tvoc', 'test_date']
    list_filter = ['test_date', 'sample__status']
    search_fields = ['sample__sample_no', 'sample__part_name']
    list_per_page = 20
