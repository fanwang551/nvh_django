from django.contrib import admin

from .models import WheelPerformance


@admin.register(WheelPerformance)
class WheelPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle_model',
        'tire_brand',
        'tire_model',
        'is_silent',
        'rim_material',
        'rim_mass_mt',
        'resonance_peak_f1',
        'anti_resonance_peak_f2',
        'rim_lateral_stiffness',
        'force_transfer_first_peak',
    )
    search_fields = ('tire_brand', 'tire_model', 'vehicle_model__vehicle_model_name')
    list_filter = ('is_silent', 'rim_material')
