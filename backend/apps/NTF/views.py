from typing import Dict, List, Optional, Set

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.NTF.models import NTFInfo, NTFTestResult
from apps.NTF.serializers import (
    NTFInfoDetailSerializer,
    NTFInfoListSerializer,
)
from utils.response import Response


POS_LABEL = {
    'front': '前排',
    'middle': '中排',
    'rear': '后排',
}


def _seat_layout(seat_count: int | None):
    layout = [{'key': 'front', 'label': '前排'}]
    if seat_count and seat_count > 5:
        layout.append({'key': 'middle', 'label': '中排'})
    if seat_count and seat_count >= 3:
        layout.append({'key': 'rear', 'label': '后排'})
    return layout


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


def _normalize_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(',') if v.strip()]


def _collect_filtered_queryset(params) -> List[NTFTestResult]:
    vehicle_ids = _normalize_csv(params.get('vehicle_ids'))
    points = _normalize_csv(params.get('points'))
    positions = set(_normalize_csv(params.get('positions')))
    directions = set(_normalize_csv(params.get('directions')))

    qs = NTFTestResult.objects.select_related('ntf_info__vehicle_model').all()
    if vehicle_ids:
        qs = qs.filter(ntf_info__vehicle_model_id__in=vehicle_ids)
    if points:
        qs = qs.filter(measurement_point__in=points)

    results = list(qs)

    def _has_branch(curve: dict, pos: str) -> bool:
        b = (curve or {}).get(pos)
        return bool(b)

    def _has_dir(curve: dict, pos: str, d: str) -> bool:
        b = (curve or {}).get(pos) or {}
        values_key = f"{d}_values"
        stats_key = d
        has_values = bool((b.get(values_key) or []))
        has_stats = bool(((b.get('stats') or {}).get(stats_key) or {}))
        return has_values or has_stats

    # Apply in-memory position/direction filters (JSONField, flexible)
    if positions:
        results = [r for r in results if any(_has_branch(r.ntf_curve, p) for p in positions)]
    if directions:
        results = [r for r in results if any(_has_dir(r.ntf_curve, p, d) for p in (positions or {'front','middle','rear'}) for d in directions)]

    return results


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_filters(request):
    """返回级联过滤项：车型/测点/位置/方向（根据入参收敛）。"""
    results = _collect_filtered_queryset(request.GET)

    vehicle_set: Set[int] = set()
    vehicles_data: Dict[int, Dict[str, object]] = {}
    points_set: Set[str] = set()
    pos_set: Set[str] = set()
    dir_set: Set[str] = set()

    for r in results:
        vm = r.ntf_info.vehicle_model
        vehicle_set.add(vm.id)
        if vm.id not in vehicles_data:
            vehicles_data[vm.id] = {
                'id': vm.id,
                'vehicle_model_name': vm.vehicle_model_name,
                'cle_model_code': vm.cle_model_code,
            }
        points_set.add(r.measurement_point)
        curve = r.ntf_curve or {}
        for pos in ('front', 'middle', 'rear'):
            b = (curve or {}).get(pos)
            if b:
                pos_set.add(pos)
                stats = (b.get('stats') or {})
                for d in ('x', 'y', 'z'):
                    if stats.get(d) or (b.get(f'{d}_values') or []):
                        dir_set.add(d)

    data = {
        'vehicles': [vehicles_data[i] for i in vehicle_set],
        'measurement_points': sorted(points_set),
        'positions': sorted(pos_set, key=lambda x: ['front','middle','rear'].index(x) if x in ('front','middle','rear') else 9),
        'directions': sorted(dir_set, key=lambda x: ['x','y','z'].index(x) if x in ('x','y','z') else 9),
    }
    return Response.success(data=data, message='获取NTF过滤项成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def ntf_query(request):
    """综合查询：多车型/多测点/可选位置与方向，输出结果表与热力图。"""
    vehicle_ids = _normalize_csv(request.GET.get('vehicle_ids'))
    if not vehicle_ids:
        return Response.bad_request(message='缺少参数：vehicle_ids')

    results = _collect_filtered_queryset(request.GET)
    if not results:
        return Response.success(data={
            'seat_columns': [],
            'vehicles': [],
            'results': [],
            'heatmap': {'frequency': [], 'points': [], 'matrix': []},
        }, message='未找到匹配的NTF数据')

    # 车辆信息卡片
    vehicle_cards: List[Dict[str, object]] = []
    vehicle_seen: Set[int] = set()
    for r in results:
        vm = r.ntf_info.vehicle_model
        if vm.id in vehicle_seen:
            continue
        vehicle_seen.add(vm.id)
        info = r.ntf_info
        vehicle_cards.append({
            'vehicle_id': vm.id,
            'vehicle_model_name': vm.vehicle_model_name,
            'vehicle_model_code': vm.cle_model_code,
            'vin': vm.vin,
            'production_year': vm.production_year,
            'energy_type': getattr(vm, 'energy_type', None),
            'suspension_type': getattr(vm, 'suspension_type', None),
            'sunroof_type': getattr(vm, 'sunroof_type', None),
            'seat_count': getattr(vm, 'seat_count', None),
            'tester': info.tester,
            'location': info.location,
            'test_time': info.test_time,
        })

    # 统一座位列：来自传入 positions 或由数据推断
    requested_positions = _normalize_csv(request.GET.get('positions'))
    if requested_positions:
        seat_columns = [{'key': p, 'label': POS_LABEL.get(p, p)} for p in requested_positions]
    else:
        # 推断：如任一结果存在该分支，即纳入
        pos_keys = []
        for p in ('front', 'middle', 'rear'):
            for r in results:
                if (r.ntf_curve or {}).get(p):
                    pos_keys.append(p)
                    break
        seat_columns = [{'key': p, 'label': POS_LABEL.get(p, p)} for p in pos_keys or ['front']]

    seat_keys = [c['key'] for c in seat_columns]

    # 结果表：每个测点 × 方向 × 频段（两行）
    bands = ['20-200Hz', '200-500Hz']
    results_rows: List[Dict[str, object]] = []
    for r in sorted(results, key=lambda x: (x.ntf_info.vehicle_model.vehicle_model_name, x.measurement_point)):
        vm = r.ntf_info.vehicle_model
        curve = r.ntf_curve or {}
        for code, dir_key, label in (('X','x','X方向'), ('Y','y','Y方向'), ('Z','z','Z方向')):
            for band in bands:
                row = {
                    'vehicle_model_name': vm.vehicle_model_name,
                    'vehicle_model_code': vm.cle_model_code,
                    'measurement_point': r.measurement_point,
                    'direction': code,
                    'direction_label': label,
                    'band': band,
                    'target': 60.0,
                    'available_columns': seat_keys,
                    'layout_image_url': getattr(r, 'layout_image_url', None),
                }
                for p in seat_keys:
                    branch = (curve or {}).get(p) or {}
                    stats = (branch.get('stats') or {}).get(dir_key) or {}
                    key = 'max_20_200' if band == '20-200Hz' else 'max_200_500'
                    row[p] = stats.get(key)
                results_rows.append(row)

    # 热力图：点名 车型名_测点_位置_方向
    # 频率轴：取第一个非空分支 frequency
    frequency_axis: List[float] = []
    for r in results:
        for p in seat_keys:
            branch = (r.ntf_curve or {}).get(p) or {}
            freqs = branch.get('frequency') or []
            if freqs:
                frequency_axis = [float(x) for x in freqs]
                break
        if frequency_axis:
            break

    heat_points: List[str] = []
    heat_matrix: List[List[Optional[float]]] = []

    requested_dirs = _normalize_csv(request.GET.get('directions')) or ['x','y','z']
    for r in results:
        vm = r.ntf_info.vehicle_model
        for p in seat_keys:
            branch = (r.ntf_curve or {}).get(p) or {}
            for d_code, d_key in (('X','x'), ('Y','y'), ('Z','z')):
                if d_key not in requested_dirs:
                    continue
                values = branch.get(f'{d_key}_values') or []
                if values:
                    series: List[Optional[float]] = []
                    for v in values:
                        try:
                            f = float(v)
                        except (TypeError, ValueError):
                            f = None
                        series.append(f)
                    if frequency_axis:
                        series = series[:len(frequency_axis)]
                    heat_points.append(f"{vm.vehicle_model_name}_{r.measurement_point}_{POS_LABEL.get(p,p)}_{d_code}")
                    heat_matrix.append(series)

    data = {
        'seat_columns': seat_columns,
        'vehicles': vehicle_cards,
        'results': results_rows,
        'heatmap': {
            'frequency': frequency_axis,
            'points': heat_points,
            'matrix': heat_matrix,
        }
    }
    return Response.success(data=data, message='获取NTF综合查询结果成功')

