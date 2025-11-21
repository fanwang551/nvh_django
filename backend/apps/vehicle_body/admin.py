from django.contrib import admin

from .models import SampleInfo, Substance, SubstancesTestDetail


@admin.register(SampleInfo)
class SampleInfoAdmin(admin.ModelAdmin):
    list_display = (
        'project_name',
        'part_name',
        'sample_no',
        'test_order_no',
        'test_date',
        'status',
    )
    search_fields = ('project_name', 'part_name', 'sample_no', 'test_order_no')
    list_filter = ('project_name', 'part_name', 'status', 'test_date')
    ordering = ('-id',)


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = (
        'substance_name_cn',
        'substance_name_en',
        'cas_no',
        'substance_type',
    )
    search_fields = ('substance_name_cn', 'substance_name_en', 'cas_no')
    list_filter = ('substance_type',)
    ordering = ('id',)


@admin.register(SubstancesTestDetail)
class SubstancesTestDetailAdmin(admin.ModelAdmin):
    list_display = (
        'sample',
        'substance',
        'concentration',
        'qij',
        'wih',
    )
    search_fields = (
        'sample__sample_no',
        'sample__project_name',
        'substance__substance_name_cn',
        'substance__cas_no',
    )
    list_filter = ('sample__project_name', 'sample__part_name')

