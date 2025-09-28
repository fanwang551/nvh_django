from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.NTF.models import NTFInfo, NTFTestResult
from apps.NTF.serializers import (
    NTFInfoDetailSerializer,
    NTFInfoListSerializer,
)
from utils.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_list(request):
    queryset = NTFInfo.objects.select_related('vehicle_model').all()

    vehicle_model = request.GET.get('vehicle_model')
    if vehicle_model:
        queryset = queryset.filter(vehicle_model_id=vehicle_model)

    queryset = queryset.order_by('-test_time')
    serializer = NTFInfoListSerializer(queryset, many=True)
    return Response.success(data=serializer.data, message='获取NTF测试信息成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_detail(request, pk):
    try:
        instance = NTFInfo.objects.select_related('vehicle_model').prefetch_related('test_results').get(pk=pk)
    except NTFInfo.DoesNotExist:
        return Response.not_found(message='NTF测试信息不存在')

    serializer = NTFInfoDetailSerializer(instance)
    return Response.success(data=serializer.data, message='获取NTF测试详情成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_info_by_vehicle(request, vehicle_id):
    instance = (
        NTFInfo.objects.select_related('vehicle_model')
        .prefetch_related('test_results')
        .filter(vehicle_model_id=vehicle_id)
        .order_by('-test_time')
        .first()
    )

    if not instance:
        return Response.not_found(message='未找到该车型的NTF测试信息')

    serializer = NTFInfoDetailSerializer(instance)
    return Response.success(data=serializer.data, message='获取车型NTF测试详情成功')


def _seat_layout(seat_count: int):
    layout = [{'key': 'front', 'label': '前排'}]
    if seat_count and seat_count >= 3:
        layout.append({'key': 'rear', 'label': '后排'})
    if seat_count and seat_count > 5:
        layout.insert(1, {'key': 'middle', 'label': '中排'})
    return layout


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_measurement_points(request):
    """Return distinct measurement points, optionally filtered by vehicle ids."""
    vehicle_ids = request.GET.get('vehicle_ids')
    qs = NTFTestResult.objects.all()
    if vehicle_ids:
        id_list = [int(v) for v in vehicle_ids.split(',') if v.strip().isdigit()]
        if id_list:
            qs = qs.filter(ntf_info__vehicle_model_id__in=id_list)
    points = (
        qs.order_by('measurement_point')
        .values_list('measurement_point', flat=True)
        .distinct()
    )
    return Response.success(data=list(points), message='获取测点列表成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_query(request):
    """
    Aggregate NTF results by multiple vehicles and measurement points.

    Query params:
      - vehicle_ids: comma-separated vehicle_model ids (required)
      - points: comma-separated measurement points (optional)
    """
    vehicle_ids = request.GET.get('vehicle_ids')
    if not vehicle_ids:
        return Response.bad_request(message='缺少参数：vehicle_ids')

    id_list = [int(v) for v in vehicle_ids.split(',') if v.strip().isdigit()]
    if not id_list:
        return Response.bad_request(message='参数 vehicle_ids 非法')

    raw_points = request.GET.get('points')
    point_list = [p.strip() for p in raw_points.split(',')] if raw_points else []
    if point_list:
        point_list = [p for p in point_list if p]

    # Collect latest NTFInfo for each vehicle id
    infos: list[NTFInfo] = []
    for vid in id_list:
        info = (
            NTFInfo.objects.select_related('vehicle_model')
            .prefetch_related('test_results')
            .filter(vehicle_model_id=vid)
            .order_by('-test_time')
            .first()
        )
        if info:
            infos.append(info)

    if not infos:
        return Response.success(data={
            'seat_columns': [],
            'results': [],
            'heatmap': {'frequency': [], 'points': [], 'matrix': []},
        }, message='未找到匹配的NTF数据')

    # Determine unified seat columns across all selected vehicles
    has_middle = any(info.seat_count and info.seat_count > 5 for info in infos)
    has_rear = any(info.seat_count and info.seat_count >= 3 for info in infos)
    seat_columns = [{'key': 'front', 'label': '前排'}]
    if has_middle:
        seat_columns.append({'key': 'middle', 'label': '中排'})
    if has_rear:
        seat_columns.append({'key': 'rear', 'label': '后排'})

    # Build results table rows and heatmap
    results_rows = []
    frequency_axis = []
    heat_points = []
    heat_matrix = []

    for info in infos:
        vehicle_name = info.vehicle_model.vehicle_model_name
        vehicle_code = info.vehicle_model.cle_model_code

        result_qs = info.test_results.all().order_by('measurement_point')
        if point_list:
            result_qs = result_qs.filter(measurement_point__in=point_list)

        for res in result_qs:
            # Table rows
            for code, label, prefix in (('X', 'X方向', 'x'), ('Y', 'Y方向', 'y'), ('Z', 'Z方向', 'z')):
                row = {
                    'vehicle_model_name': vehicle_name,
                    'vehicle_model_code': vehicle_code,
                    'measurement_point': res.measurement_point,
                    'direction': code,
                    'direction_label': label,
                    'target': getattr(res, f'{prefix}_target_value'),
                    'front': getattr(res, f'{prefix}_front_row_value'),
                    'middle': getattr(res, f'{prefix}_middle_row_value'),
                    'rear': getattr(res, f'{prefix}_rear_row_value'),
                    'available_columns': [c['key'] for c in _seat_layout(info.seat_count)],
                }
                results_rows.append(row)

            # Heatmap rows
            curve = res.ntf_curve or {}
            if not frequency_axis:
                freqs = curve.get('frequency') or []
                if freqs:
                    frequency_axis = [float(x) for x in freqs]

            for dir_key, values_key in (('x', 'x_values'), ('y', 'y_values'), ('z', 'z_values')):
                values = curve.get(values_key) or []
                if values:
                    series = []
                    for v in values:
                        try:
                            f = float(v)
                        except (TypeError, ValueError):
                            f = None
                        series.append(f)
                    heat_points.append(f"{vehicle_name}_{res.measurement_point}_{dir_key}")
                    heat_matrix.append(series)

            # Fallback for legacy single "values" array
            if not any(curve.get(k) for k in ('x_values', 'y_values', 'z_values')):
                old_values = curve.get('values') or []
                if old_values:
                    series = []
                    for v in old_values:
                        try:
                            f = float(v)
                        except (TypeError, ValueError):
                            f = None
                        series.append(f)
                    heat_points.append(f"{vehicle_name}_{res.measurement_point}")
                    heat_matrix.append(series)

    data = {
        'seat_columns': seat_columns,
        'results': results_rows,
        'heatmap': {
            'frequency': frequency_axis,
            'points': heat_points,
            'matrix': heat_matrix,
        }
    }
    return Response.success(data=data, message='获取NTF综合查询结果成功')

