from django.contrib import admin

from .models import ConditionMeasurePoint, AcousticTestData, DynamicNoiseData


@admin.register(ConditionMeasurePoint)
class ConditionMeasurePointAdmin(admin.ModelAdmin):
    list_display = ('work_condition', 'measure_point', 'measure_type')
    search_fields = ('work_condition', 'measure_point')
    list_filter = ('measure_type',)
    ordering = ('work_condition', 'measure_point')


@admin.register(AcousticTestData)
class AcousticTestDataAdmin(admin.ModelAdmin):
    list_display = ('vehicle_model', 'condition_point', 'test_date')
    search_fields = (
        'vehicle_model__vehicle_model_name',
        'condition_point__work_condition',
        'condition_point__measure_point',
    )
    list_filter = ('test_date', 'condition_point__measure_type')
    date_hierarchy = 'test_date'


@admin.register(DynamicNoiseData)
class DynamicNoiseDataAdmin(admin.ModelAdmin):
    list_display = ('vehicle_model_id', 'condition_measure_point', 'x_axis_type')
    search_fields = (
        'vehicle_model_id',
        'condition_measure_point__work_condition',
        'condition_measure_point__measure_point',
    )
    list_filter = ('x_axis_type',)

