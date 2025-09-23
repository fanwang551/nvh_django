from decimal import Decimal
from typing import Dict, List

from rest_framework import serializers

from apps.NTF.models import NTFInfo, NTFTestResult


class NTFInfoListSerializer(serializers.ModelSerializer):
    vehicle_model_name = serializers.CharField(source='vehicle_model.vehicle_model_name', read_only=True)
    vehicle_model_code = serializers.CharField(source='vehicle_model.cle_model_code', read_only=True)

    class Meta:
        model = NTFInfo
        fields = (
            'id',
            'vehicle_model',
            'vehicle_model_code',
            'vehicle_model_name',
            'tester',
            'test_time',
            'location',
            'seat_count',
            'development_stage',
        )


class NTFInfoDetailSerializer(serializers.ModelSerializer):
    vehicle = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    seat_columns = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    heatmap = serializers.SerializerMethodField()

    class Meta:
        model = NTFInfo
        fields = (
            'id',
            'vehicle',
            'tester',
            'test_time',
            'location',
            'sunroof_type',
            'suspension_type',
            'seat_count',
            'development_stage',
            'images',
            'seat_columns',
            'results',
            'heatmap',
        )

    @staticmethod
    def _clean_decimal(value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def _seat_layout(seat_count: int) -> List[Dict[str, str]]:
        layout: List[Dict[str, str]] = [{'key': 'front', 'label': '前排'}]
        if seat_count and seat_count >= 3:
            layout.append({'key': 'rear', 'label': '后排'})
        if seat_count and seat_count > 5:
            layout.insert(1, {'key': 'middle', 'label': '中排'})
        return layout

    def get_vehicle(self, obj: NTFInfo) -> Dict[str, str]:
        vehicle = obj.vehicle_model
        return {
            'id': vehicle.id,
            'code': vehicle.cle_model_code,
            'name': vehicle.vehicle_model_name,
            'vin': vehicle.vin,
            'drive_type': vehicle.drive_type,
        }

    def get_images(self, obj: NTFInfo) -> Dict[str, str]:
        return {
            'front': obj.front_row_image,
            'middle': obj.middle_row_image,
            'rear': obj.rear_row_image,
        }

    def get_seat_columns(self, obj: NTFInfo) -> List[Dict[str, str]]:
        return self._seat_layout(obj.seat_count)

    def get_results(self, obj: NTFInfo) -> List[Dict[str, object]]:
        seat_layout = self._seat_layout(obj.seat_count)
        seats = [seat['key'] for seat in seat_layout]
        data: List[Dict[str, object]] = []
        direction_map = [
            ('X', 'X方向', 'x'),
            ('Y', 'Y方向', 'y'),
            ('Z', 'Z方向', 'z'),
        ]
        for result in obj.test_results.all().order_by('measurement_point'):
            for code, label, prefix in direction_map:
                target = getattr(result, f"{prefix}_target_value")
                front = getattr(result, f"{prefix}_front_row_value")
                middle = getattr(result, f"{prefix}_middle_row_value")
                rear = getattr(result, f"{prefix}_rear_row_value")
                row = {
                    'measurement_point': result.measurement_point,
                    'direction': code,
                    'direction_label': label,
                    'target': self._clean_decimal(target),
                    'front': self._clean_decimal(front),
                    'middle': self._clean_decimal(middle),
                    'rear': self._clean_decimal(rear),
                    'available_columns': seats,
                }
                data.append(row)
        return data

    def get_heatmap(self, obj: NTFInfo) -> Dict[str, object]:
        frequency_axis: List[float] = []
        points_axis: List[str] = []
        matrix: List[List[float]] = []

        for result in obj.test_results.all().order_by('measurement_point'):
            curve = result.ntf_curve or {}
            frequencies = curve.get('frequency') or []
            values = curve.get('values') or []
            if not frequency_axis and frequencies:
                frequency_axis = [float(f) for f in frequencies]
            if values:
                points_axis.append(f"{result.measurement_point}")
                matrix.append([float(v) for v in values])

        return {
            'frequency': frequency_axis,
            'points': points_axis,
            'matrix': matrix,
        }


class NTFInfoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTFInfo
        fields = '__all__'


class NTFTestResultCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTFTestResult
        fields = '__all__'

