from decimal import Decimal
from typing import Dict, List, Optional
import math

from rest_framework import serializers

from apps.NTF.models import NTFInfo, NTFTestResult


POS_LABEL = {
    'front': '前排',
    'middle': '中排',
    'rear': '后排',
}


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
        )


def _is_finite_number(value) -> bool:
    try:
        f = float(value)
        return math.isfinite(f)
    except (TypeError, ValueError):
        return False


def _to_float(value) -> Optional[float]:
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _to_float_list(values, limit_len: int | None = None):
    arr: List[float] = []
    for v in values or []:
        f = _to_float(v)
        if f is not None:
            arr.append(f)
    if limit_len is not None:
        arr = arr[:limit_len]
    return arr


def _seat_layout(seat_count: int | None) -> List[Dict[str, str]]:
    layout: List[Dict[str, str]] = [{'key': 'front', 'label': '前排'}]
    if seat_count and seat_count > 5:
        layout.append({'key': 'middle', 'label': '中排'})
    if seat_count and seat_count >= 3:
        layout.append({'key': 'rear', 'label': '后排'})
    return layout


def _curve_branch(curve: dict, pos_key: str) -> dict:
    branch = (curve or {}).get(pos_key)
    return branch or {}


def _stats_value(curve: dict, pos_key: str, dir_key: str, band: str) -> Optional[float]:
    branch = _curve_branch(curve, pos_key)
    stats = (branch or {}).get('stats') or {}
    d = (stats or {}).get(dir_key) or {}
    key = 'max_20_200' if band == '20-200Hz' else 'max_200_500'
    return _to_float(d.get(key))


def _values_series(curve: dict, pos_key: str, dir_key: str) -> List[Optional[float]]:
    branch = _curve_branch(curve, pos_key)
    key = f"{dir_key}_values"
    return [( _to_float(v) ) for v in (branch.get(key) or [])]


def _frequency(curve: dict, pos_key: str) -> List[float]:
    branch = _curve_branch(curve, pos_key)
    return _to_float_list(branch.get('frequency') or [])


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
            'point_images',
            'seat_columns',
            'results',
            'heatmap',
        )

    def get_vehicle(self, obj: NTFInfo) -> Dict[str, str]:
        vehicle = obj.vehicle_model
        return {
            'id': vehicle.id,
            'code': vehicle.cle_model_code,
            'name': vehicle.vehicle_model_name,
            'vin': vehicle.vin,
            'drive_type': vehicle.drive_type,
            'production_year': vehicle.production_year,
            'energy_type': getattr(vehicle, 'energy_type', None),
            'suspension_type': getattr(vehicle, 'suspension_type', None),
            'sunroof_type': getattr(vehicle, 'sunroof_type', None),
            'seat_count': getattr(vehicle, 'seat_count', None),
        }

    def get_seat_columns(self, obj: NTFInfo) -> List[Dict[str, str]]:
        return _seat_layout(getattr(obj.vehicle_model, 'seat_count', None))

    def get_results(self, obj: NTFInfo) -> List[Dict[str, object]]:
        seats = [c['key'] for c in _seat_layout(getattr(obj.vehicle_model, 'seat_count', None))]
        bands = ['20-200Hz', '200-500Hz']
        dirs = [('X', 'x', 'X方向'), ('Y', 'y', 'Y方向'), ('Z', 'z', 'Z方向')]
        data: List[Dict[str, object]] = []

        for result in obj.test_results.all().order_by('measurement_point'):
            curve = result.ntf_curve or {}
            for code, dir_key, label in dirs:
                for band in bands:
                    row = {
                        'measurement_point': result.measurement_point,
                        'direction': code,
                        'direction_label': label,
                        'band': band,
                        'target': 60.0,
                        'front': _stats_value(curve, 'front', dir_key, band) if 'front' in seats else None,
                        'middle': _stats_value(curve, 'middle', dir_key, band) if 'middle' in seats else None,
                        'rear': _stats_value(curve, 'rear', dir_key, band) if 'rear' in seats else None,
                        'available_columns': seats,
                    }
                    data.append(row)
        return data

    def get_heatmap(self, obj: NTFInfo) -> Dict[str, object]:
        frequency_axis: List[float] = []
        points_axis: List[str] = []
        matrix: List[List[Optional[float]]] = []

        # 选取第一个非空分支作为频率轴
        for result in obj.test_results.all().order_by('measurement_point'):
            curve = result.ntf_curve or {}
            for pos in ('front', 'middle', 'rear'):
                freqs = _frequency(curve, pos)
                if freqs:
                    frequency_axis = freqs
                    break
            if frequency_axis:
                break

        for result in obj.test_results.all().order_by('measurement_point'):
            curve = result.ntf_curve or {}
            for pos in ('front', 'middle', 'rear'):
                pos_label = POS_LABEL.get(pos, pos)
                for code, dir_key, _ in [('X', 'x', 'X方向'), ('Y', 'y', 'Y方向'), ('Z', 'z', 'Z方向')]:
                    series = _values_series(curve, pos, dir_key)
                    if series:
                        if frequency_axis:
                            series = series[:len(frequency_axis)]
                        name = f"{obj.vehicle_model.vehicle_model_name}_{result.measurement_point}_{pos_label}_{code}"
                        points_axis.append(name)
                        matrix.append(series)

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

