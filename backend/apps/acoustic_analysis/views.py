from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Q

from utils.response import Response
from apps.acoustic_analysis.models import AcousticTestData, ConditionMeasurePoint
from apps.acoustic_analysis.serializers import (
    WorkConditionListSerializer,
    MeasurePointListSerializer,
    AcousticQuerySerializer,
    AcousticTableItemSerializer,
)


MEASURE_TYPE_META = {
    ConditionMeasurePoint.MeasureType.NOISE: {
        'spectrum_unit': 'dB',
        'oa_unit': 'dB',
    },
    ConditionMeasurePoint.MeasureType.VIBRATION: {
        'spectrum_unit': 'm/s²',
        'oa_unit': 'm/s²',
    },
    ConditionMeasurePoint.MeasureType.SPEED: {
        'spectrum_unit': None,
        'oa_unit': None,
    },
}


@api_view(['GET'])
@permission_classes([AllowAny])
def get_work_conditions(request):
    serializer = WorkConditionListSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response.bad_request(message='参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    qs = AcousticTestData.objects.filter(vehicle_model_id__in=vehicle_model_ids)
    values = (
        qs.values_list('condition_point__work_condition', flat=True)
        .distinct()
        .order_by('condition_point__work_condition')
    )
    return Response.success(data=list(values), message='获取工况选项成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_measure_points(request):
    serializer = MeasurePointListSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response.bad_request(message='参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']

    qs = AcousticTestData.objects.filter(
        vehicle_model_id__in=vehicle_model_ids,
        condition_point__work_condition__in=work_conditions,
    )
    values = (
        qs.values_list('condition_point__measure_point', flat=True)
        .distinct()
        .order_by('condition_point__measure_point')
    )
    return Response.success(data=list(values), message='获取测点选项成功')


def _safe_parse_series(raw):
    if raw is None:
        return None
    data = raw
    # 后端JSONField应为dict；若为字符串，尝试解析
    if isinstance(data, str):
        try:
            import json
            data = json.loads(data)
        except Exception:
            return None
    if not isinstance(data, dict):
        return None
    return data


def _normalize_numeric_list(raw):
    if not isinstance(raw, list):
        return []
    normalized = []
    for item in raw:
        if isinstance(item, (int, float)):
            # 排除 NaN
            if isinstance(item, float) and (item != item):
                continue
            normalized.append(float(item))
            continue
        if isinstance(item, str):
            text = item.strip()
            if not text or text.lower() == 'nan':
                continue
            try:
                normalized.append(float(text))
            except Exception:
                continue
    return normalized


def _pick_value_list(series_dict, preferred_keys):
    if not isinstance(series_dict, dict):
        return None
    for key in preferred_keys:
        value = series_dict.get(key)
        if isinstance(value, list) and len(value):
            return value
    for key, value in series_dict.items():
        if key in ('frequency', 'time'):
            continue
        if isinstance(value, list) and len(value):
            return value
    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def query_acoustic_data(request):
    serializer = AcousticQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']
    measure_points = serializer.validated_data['measure_points']

    # 新实现：逐组合取最新一条记录
    # 关键点：先用轻量查询仅取 id（按 test_date/id 排序），显著降低 MySQL filesort 内存占用
    # 然后再按 id 取完整对象，避免在大 JSON 行上排序导致 1038 Out of sort memory
    spectrum_series = []
    oa_series = []
    table_items = []
    for vm_id in vehicle_model_ids:
        for wc in work_conditions:
            for mp in measure_points:
                latest_id = (
                    AcousticTestData.objects
                    .filter(
                        vehicle_model_id=vm_id,
                        condition_point__work_condition=wc,
                        condition_point__measure_point=mp,
                    )
                    .order_by('-test_date', '-id')
                    .values_list('id', flat=True)
                    .first()
                )
                if not latest_id:
                    continue

                obj = (
                    AcousticTestData.objects
                    .select_related('vehicle_model', 'condition_point')
                    .get(id=latest_id)
                )
                if not obj:
                    continue
                vm_name = getattr(obj.vehicle_model, 'vehicle_model_name', str(vm_id))
                series_name = f"{vm_name}-{wc}-{mp}"
                measure_type = getattr(obj.condition_point, 'measure_type', ConditionMeasurePoint.MeasureType.NOISE)
                meta = MEASURE_TYPE_META.get(measure_type, MEASURE_TYPE_META[ConditionMeasurePoint.MeasureType.NOISE])
                spectrum = _safe_parse_series(obj.spectrum_json) or {}
                freq_raw = spectrum.get('frequency') if isinstance(spectrum, dict) else None
                freq = _normalize_numeric_list(freq_raw)
                spectrum_values_raw = _pick_value_list(spectrum, ['dB', 'dB(A)', 'value', 'values', 'amplitude', 'amplitudes'])
                spectrum_values = _normalize_numeric_list(spectrum_values_raw)
                if (
                    measure_type != ConditionMeasurePoint.MeasureType.SPEED
                    and freq
                    and spectrum_values
                ):
                    length = min(len(freq), len(spectrum_values))
                    spectrum_series.append({
                        'name': series_name,
                        'measure_type': measure_type,
                        'unit': meta['spectrum_unit'],
                        'frequency': freq[:length],
                        'values': spectrum_values[:length],
                    })
                oa = _safe_parse_series(obj.oa_json) or {}
                times_raw = oa.get('time') if isinstance(oa, dict) else None
                times = _normalize_numeric_list(times_raw)
                oa_values_raw = _pick_value_list(oa, ['OA', 'dB(A)', 'dBA', 'value', 'values'])
                oa_values = _normalize_numeric_list(oa_values_raw)
                stats = None
                if oa_values:
                    try:
                        max_val = max(oa_values); min_val = min(oa_values); avg_val = sum(oa_values) / len(oa_values)
                        stats = {'max': max_val, 'min': min_val, 'avg': avg_val}
                    except Exception:
                        stats = None
                if (
                    measure_type != ConditionMeasurePoint.MeasureType.SPEED
                    and times
                    and oa_values
                ):
                    length = min(len(times), len(oa_values))
                    oa_series.append({
                        'name': series_name,
                        'measure_type': measure_type,
                        'unit': meta['oa_unit'],
                        'time': times[:length],
                        'values': oa_values[:length],
                        'stats': stats,
                    })
                table_items.append(obj)
    table_data = AcousticTableItemSerializer(table_items, many=True).data
    return Response.success(data={'spectrum_series': spectrum_series, 'oa_series': oa_series, 'table': table_data}, message='查询成功')

    # 说明：此前这里有一段尝试“批量拉取再内存去重”的代码，
    # 在数据量大时会触发数据库端大排序与临时表，风险更高，已移除。
