from decimal import Decimal
from typing import Dict, List
import math

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
    seat_columns = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    heatmap = serializers.SerializerMethodField()
    point_images = serializers.SerializerMethodField()

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
            'point_images',
            'seat_columns',
            'results',
            'heatmap',
        )

    @staticmethod
    def _is_finite_number(value) -> bool:
        try:
            f = float(value)
            return math.isfinite(f)
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _to_float(value):
        """Safely convert to float; return None if not finite."""
        try:
            f = float(value)
            return f if math.isfinite(f) else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float_list(values, limit_len: int | None = None):
        arr = []
        for v in values or []:
            f = NTFInfoDetailSerializer._to_float(v)
            if f is not None:
                arr.append(f)
        if limit_len is not None:
            arr = arr[:limit_len]
        return arr

    @staticmethod
    def _clean_decimal(value):
        # Accept Decimal or numeric-like values; return None for non-finite
        if isinstance(value, Decimal) or isinstance(value, (int, float, str)):
            f = NTFInfoDetailSerializer._to_float(value)
            return f
        return None

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
            if not frequency_axis and frequencies:
                frequency_axis = self._to_float_list(frequencies)

            # 优先新结构：x_values / y_values / z_values
            x_vals = curve.get('x_values') or []
            y_vals = curve.get('y_values') or []
            z_vals = curve.get('z_values') or []
            expected_len = len(frequency_axis) if frequency_axis else None

            # 热力图展示 X、Y、Z 三个方向
            added_any = False
            if x_vals:
                row = self._to_float_list(x_vals, expected_len)
                if row:
                    points_axis.append(f"{result.measurement_point}_X")
                    matrix.append(row)
                    added_any = True
            if y_vals:
                row = self._to_float_list(y_vals, expected_len)
                if row:
                    points_axis.append(f"{result.measurement_point}_Y")
                    matrix.append(row)
                    added_any = True
            if z_vals:
                row = self._to_float_list(z_vals, expected_len)
                if row:
                    points_axis.append(f"{result.measurement_point}_Z")
                    matrix.append(row)
                    added_any = True

            # 兼容历史数据：旧结构 {frequency: [], values: []}
            if not added_any:
                old_values = curve.get('values') or []
                if old_values:
                    row = self._to_float_list(old_values, expected_len)
                    if row:
                        points_axis.append(f"{result.measurement_point}")
                        matrix.append(row)

        return {
            'frequency': frequency_axis,
            'points': points_axis,
            'matrix': matrix,
        }

    def get_point_images(self, obj: NTFInfo) -> List[Dict[str, str]]:
        data: List[Dict[str, str]] = []
        for result in obj.test_results.all().order_by('measurement_point'):
            if getattr(result, 'layout_image_url', None):
                data.append({
                    'measurement_point': result.measurement_point,
                    'url': result.layout_image_url,
                })
        return data


class NTFInfoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTFInfo
        fields = '__all__'


class NTFTestResultCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTFTestResult
        fields = '__all__'

