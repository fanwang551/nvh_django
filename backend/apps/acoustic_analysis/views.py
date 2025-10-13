from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Q

from utils.response import Response
from apps.acoustic_analysis.models import TestDataAll
from apps.acoustic_analysis.serializers import (
    WorkConditionListSerializer,
    MeasurePointListSerializer,
    AcousticQuerySerializer,
    AcousticTableItemSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_work_conditions(request):
    serializer = WorkConditionListSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response.bad_request(message='参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    qs = TestDataAll.objects.filter(vehicle_model_id__in=vehicle_model_ids)
    values = (
        qs.values_list('work_condition', flat=True)
        .distinct()
        .order_by('work_condition')
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

    qs = TestDataAll.objects.filter(
        vehicle_model_id__in=vehicle_model_ids,
        work_condition__in=work_conditions,
    )
    values = (
        qs.values_list('measure_point', flat=True)
        .distinct()
        .order_by('measure_point')
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


@api_view(['POST'])
@permission_classes([AllowAny])
def query_acoustic_data(request):
    serializer = AcousticQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']
    measure_points = serializer.validated_data['measure_points']

    # 构建组合并查询每个组合的最新一条记录
    spectrum_series = []
    oa_series = []
    table_items = []

    # 为避免N^3数据库查询，这里一次性拉取并在内存中过滤
    qs = (
        TestDataAll.objects.select_related('vehicle_model')
        .filter(
            vehicle_model_id__in=vehicle_model_ids,
            work_condition__in=work_conditions,
            measure_point__in=measure_points,
        )
        .order_by('vehicle_model_id', 'work_condition', 'measure_point', '-test_date', '-created_at')
        .only(
            'id', 'vehicle_model_id', 'work_condition', 'measure_point',
            'spectrum_json', 'oa_json', 'speech_clarity', 'rms_value', 'test_date', 'created_at',
            'vehicle_model__vehicle_model_name',
        )
    )

    # 取每个 (vm,wc,mp) 的第一条（最新）
    picked = {}
    for obj in qs:
        key = (obj.vehicle_model_id, obj.work_condition, obj.measure_point)
        if key not in picked:
            picked[key] = obj

    # 组装输出
    for (vm_id, wc, mp), obj in picked.items():
        vm_name = getattr(obj.vehicle_model, 'vehicle_model_name', str(vm_id))
        series_name = f"{vm_name}-{wc}-{mp}"

        spectrum = _safe_parse_series(obj.spectrum_json) or {}
        freq = spectrum.get('frequency') if isinstance(spectrum, dict) else None
        db_vals = spectrum.get('dB') if isinstance(spectrum, dict) else None
        if isinstance(freq, list) and isinstance(db_vals, list) and len(freq) and len(db_vals):
            spectrum_series.append({
                'name': series_name,
                'frequency': [float(x) for x in freq if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')],
                'dB': [float(x) for x in db_vals if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')],
            })

        oa = _safe_parse_series(obj.oa_json) or {}
        times = oa.get('time') if isinstance(oa, dict) else None
        oa_values = oa.get('OA') if isinstance(oa, dict) else None
        stats = None
        if isinstance(oa_values, list) and len(oa_values):
            try:
                nums = [float(x) for x in oa_values if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')]
                if nums:
                    max_val = max(nums)
                    min_val = min(nums)
                    avg_val = sum(nums) / len(nums)
                    stats = {
                        'max': max_val,
                        'min': min_val,
                        'avg': avg_val,
                    }
            except Exception:
                stats = None

        if isinstance(times, list) and isinstance(oa_values, list) and len(times) and len(oa_values):
            oa_series.append({
                'name': series_name,
                'time': [float(x) for x in times if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')],
                'OA': [float(x) for x in oa_values if isinstance(x, (int, float, str)) and str(x).strip() not in ('', 'nan')],
                'stats': stats,
            })

        table_items.append(obj)

    table_data = AcousticTableItemSerializer(table_items, many=True).data
    return Response.success(data={
        'spectrum_series': spectrum_series,
        'oa_series': oa_series,
        'table': table_data,
    }, message='查询成功')

