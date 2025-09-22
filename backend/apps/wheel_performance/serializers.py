from rest_framework import serializers

from apps.wheel_performance.models import WheelPerformance


class WheelPerformanceSerializer(serializers.ModelSerializer):
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)

    class Meta:
        model = WheelPerformance
        fields = (
            'id',
            'vehicle_model',
            'vehicle_model_name',
            'tire_brand',
            'tire_model',
            'is_silent',
            'rim_material',
            'rim_mass_mt',
            'resonance_peak_f1',
            'anti_resonance_peak_f2',
            'rim_lateral_stiffness',
            'rim_stiffness_curve_url',
            'rim_stiffness_test_image_url',
            'force_transfer_first_peak',
            'force_transfer_test_image_url',
            'force_transfer_signal',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class WheelPerformanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelPerformance
        fields = (
            'vehicle_model',
            'tire_brand',
            'tire_model',
            'is_silent',
            'rim_material',
            'rim_mass_mt',
            'resonance_peak_f1',
            'anti_resonance_peak_f2',
            'rim_lateral_stiffness',
            'rim_stiffness_curve_url',
            'rim_stiffness_test_image_url',
            'force_transfer_first_peak',
            'force_transfer_test_image_url',
            'force_transfer_signal',
        )
