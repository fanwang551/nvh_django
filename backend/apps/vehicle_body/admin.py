from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

from .models import SampleInfo, Substance, SubstancesTestDetail


class SampleInfoResource(resources.ModelResource):
    class Meta:
        model = SampleInfo
        import_id_fields = ('id',)
        fields = (
            'id',
            'project_name',
            'part_name',
            'development_stage',
            'status',
            'test_order_no',
            'sample_no',
            'sample_image_url',
            'test_date',
            'benzene',
            'toluene',
            'ethylbenzene',
            'xylene',
            'styrene',
            'formaldehyde',
            'acetaldehyde',
            'acrolein',
            'acetone',
            'tvoc',
            'odor_static_front',
            'odor_static_rear',
            'odor_dynamic_front',
            'odor_dynamic_rear',
            'odor_mean',
        )
        use_transactions = True

    def save_instance(self, instance, is_create, *args, **kwargs):
        if not is_create:
            raise ValidationError('记录已存在，禁止覆盖导入，请检查导入文件中的 id。')
        return super().save_instance(instance, is_create, *args, **kwargs)


@admin.register(SampleInfo)
class SampleInfoAdmin(ImportExportModelAdmin):
    resource_class = SampleInfoResource
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
    readonly_fields = ('sample_image_preview',)

    def sample_image_preview(self, obj):
        if not obj or not obj.sample_image_url:
            return "无图片"
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" style="max-height:240px; max-width:100%; border:1px solid #ddd; padding:4px;" />'
            '</a>',
            obj.sample_image_url.url
        )

    sample_image_preview.short_description = "图片预览"

    fieldsets = (
        ('基本信息', {'fields': (
            'project_name', 'part_name', 'status',
            'sample_no', 'test_order_no', 'test_date',
            'sample_image_url', 'sample_image_preview',
        )}),
        ('检测数据', {'fields': (
            'benzene', 'toluene', 'ethylbenzene', 'xylene', 'styrene',
            'formaldehyde', 'acetaldehyde', 'acrolein', 'acetone', 'tvoc',
            'odor_static_front', 'odor_static_rear', 'odor_dynamic_front', 'odor_dynamic_rear', 'odor_mean',
        )}),
    )

class SubstanceResource(resources.ModelResource):
    class Meta:
        model = Substance
        import_id_fields = ('cas_no',)
        fields = (
            'substance_name_cn',
            'substance_name_en',
            'cas_no',
            'substance_type',
            'odor_threshold',
            'organic_threshold',
            'limit_value',
            'odor_character',
            'main_usage',
            'remark',
        )
        use_transactions = True

    def save_instance(self, instance, is_create, *args, **kwargs):
        if not is_create:
            raise ValidationError('记录已存在，禁止覆盖导入，请检查导入文件中的 CAS 号。')
        return super().save_instance(instance, is_create, *args, **kwargs)


@admin.register(Substance)
class SubstanceAdmin(ImportExportModelAdmin):
    resource_class = SubstanceResource
    list_display = (
        'substance_name_cn',
        'substance_name_en',
        'cas_no',
        'substance_type',
    )
    search_fields = ('substance_name_cn', 'substance_name_en', 'cas_no')
    list_filter = ('substance_type',)
    ordering = ('id',)


class SubstancesTestDetailResource(resources.ModelResource):
    sample = fields.Field(
        column_name='sample_id',
        attribute='sample',
        widget=ForeignKeyWidget(SampleInfo, 'id'),
    )
    substance = fields.Field(
        column_name='cas_no',
        attribute='substance',
        widget=ForeignKeyWidget(Substance, 'cas_no'),
    )

    class Meta:
        model = SubstancesTestDetail
        import_id_fields = ('sample', 'substance')
        fields = (
            'sample',
            'substance',
            'concentration',
            'retention_time',
            'match_degree',
            'concentration_ratio',
            'qij',
            'wih',
        )
        use_transactions = True

    def save_instance(self, instance, is_create, *args, **kwargs):
        if not is_create:
            raise ValidationError('记录已存在，禁止覆盖导入，请检查导入文件中的样品和物质组合。')
        return super().save_instance(instance, is_create, *args, **kwargs)


@admin.register(SubstancesTestDetail)
class SubstancesTestDetailAdmin(ImportExportModelAdmin):
    resource_class = SubstancesTestDetailResource
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
