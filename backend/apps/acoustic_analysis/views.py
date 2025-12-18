from collections import defaultdict
import os
from urllib.parse import quote

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.conf import settings
from django.db.models import Q
from django.core.files.storage import default_storage
from django.http import FileResponse

from utils.response import Response
from apps.acoustic_analysis.models import AcousticTestData, ConditionMeasurePoint, DynamicNoiseData
from apps.acoustic_analysis.serializers import (
    WorkConditionListSerializer,
    MeasurePointListSerializer,
    AcousticQuerySerializer,
    AcousticTableItemSerializer,
    SteadyStateQuerySerializer,
    DynamicWorkConditionSerializer,
    DynamicMeasurePointSerializer,
    DynamicNoiseQuerySerializer,
    DynamicNoiseTableSerializer,
)
from apps.modal.models import VehicleModel


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

STEADY_STATE_CHART_DEFINITIONS = [
    {
        'chart_key': 'noise_rms',
        'measure_type': ConditionMeasurePoint.MeasureType.NOISE,
        'metric': 'rms',
        'field': 'rms_value',
        'title': '噪声有效值对比',
        'unit': 'dB(A)',
    },
    {
        'chart_key': 'noise_speech',
        'measure_type': ConditionMeasurePoint.MeasureType.NOISE,
        'metric': 'speech_clarity',
        'field': 'speech_clarity',
        'title': '语音清晰度对比',
        'unit': '%',
    },
    {
        'chart_key': 'vibration_rms',
        'measure_type': ConditionMeasurePoint.MeasureType.VIBRATION,
        'metric': 'rms',
        'field': 'rms_value',
        'title': '振动有效值对比',
        'unit': 'm/s²',
    },
    {
        'chart_key': 'speed_rpm',
        'measure_type': ConditionMeasurePoint.MeasureType.SPEED,
        'metric': 'rpm',
        'field': 'rms_value',
        'title': '转速对比',
        'unit': 'rpm',
    },
]

STEADY_STATE_CHART_LOOKUP = {
    (item['measure_type'], item['metric']): item for item in STEADY_STATE_CHART_DEFINITIONS
}

STEADY_STATE_CHARTS_BY_TYPE = {}
for _chart in STEADY_STATE_CHART_DEFINITIONS:
    STEADY_STATE_CHARTS_BY_TYPE.setdefault(_chart['measure_type'], []).append(_chart)


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
    # 返回带有测点类型的信息，便于前端限制不同类型测点混选
    values = (
        qs.values('condition_point__measure_point', 'condition_point__measure_type')
        .distinct()
        .order_by('condition_point__measure_type', 'condition_point__measure_point')
    )
    data = [
        {
            'measure_point': item['condition_point__measure_point'],
            'measure_type': item['condition_point__measure_type'],
        }
        for item in values
    ]
    return Response.success(data=data, message='获取测点选项成功')


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
    return None


def _get_frequency_list(series_dict):
    """从序列字典中提取频率列表，支持多种键名"""
    if not isinstance(series_dict, dict):
        return None
    # 按优先级尝试不同的键名
    for key in ['frequency', 'freq', 'Hz', 'hz', 'Frequency', 'FREQUENCY']:
        value = series_dict.get(key)
        if isinstance(value, list) and len(value):
            return value
    return None

def _build_media_url(path, request):
    if not path:
        return ''
    try:
        url = default_storage.url(path)
    except Exception:
        url = path
    try:
        return request.build_absolute_uri(url)
    except Exception:
        return url


def _build_curve_pairs(curve_dict, x_keys, y_keys):
    """从曲线字典中提取 x/y 列表并组装为 [x, y] 对"""
    if isinstance(curve_dict, str):
        try:
            import json
            curve_dict = json.loads(curve_dict)
        except Exception:
            return []
    if not isinstance(curve_dict, dict):
        return []
    x_list = _normalize_numeric_list(_pick_value_list(curve_dict, x_keys))
    y_list = _normalize_numeric_list(_pick_value_list(curve_dict, y_keys))
    length = min(len(x_list), len(y_list))
    return [[x_list[i], y_list[i]] for i in range(length)]


@api_view(['POST'])
@permission_classes([AllowAny])
def query_acoustic_data(request):
    serializer = AcousticQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']
    measure_points = serializer.validated_data['measure_points']

    spectrum_series = []
    oa_series = []
    table_items = []
    used_measure_types = set()

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

                measure_type = getattr(
                    obj.condition_point,
                    'measure_type',
                    ConditionMeasurePoint.MeasureType.NOISE,
                )

                if used_measure_types and measure_type not in used_measure_types:
                    return Response.bad_request(
                        message='当前仅支持查询同一测点类型的数据，请调整测点选择',
                    )
                used_measure_types.add(measure_type)

                meta = MEASURE_TYPE_META.get(
                    measure_type,
                    MEASURE_TYPE_META[ConditionMeasurePoint.MeasureType.NOISE]
                )

                # 修改这里：使用新的 _get_frequency_list 函数
                spectrum = _safe_parse_series(obj.spectrum_json) or {}
                freq_raw = _get_frequency_list(spectrum)  # 改用新函数
                freq = _normalize_numeric_list(freq_raw)

                spectrum_values_raw = _pick_value_list(
                    spectrum,
                    ['dB', 'dB(A)', 'value', 'values', 'amplitude', 'amplitudes']
                )
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

                # OA 数据处理（时间轴也可以类似处理）
                oa = _safe_parse_series(obj.oa_json) or {}
                # 如果需要，也可以为时间轴创建类似函数
                times_raw = _pick_value_list(oa, ['time', 'Time', 't', 'T'])
                times = _normalize_numeric_list(times_raw)

                oa_values_raw = _pick_value_list(
                    oa,
                    ['OA', 'dB(A)', 'dBA', 'value', 'values']
                )
                oa_values = _normalize_numeric_list(oa_values_raw)

                stats = None
                if oa_values:
                    try:
                        max_val = max(oa_values)
                        min_val = min(oa_values)
                        avg_val = sum(oa_values) / len(oa_values)
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
    return Response.success(
        data={
            'spectrum_series': spectrum_series,
            'oa_series': oa_series,
            'table': table_data
        },
        message='查询成功'
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def query_steady_state_data(request):
    serializer = SteadyStateQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = list(dict.fromkeys(serializer.validated_data['work_conditions']))
    measure_points = list(dict.fromkeys(serializer.validated_data['measure_points']))

    if not work_conditions or not measure_points:
        return Response.success(data={'charts': []}, message='查询成功')

    qs = (
        AcousticTestData.objects
        .select_related('vehicle_model', 'condition_point')
        # 避免在排序时将大体积 JSON 字段（频谱/总声压级）搬入临时表，降低内存占用
        .defer('spectrum_json', 'oa_json')
        .filter(
            vehicle_model_id__in=vehicle_model_ids,
            condition_point__work_condition__in=work_conditions,
            condition_point__measure_point__in=measure_points,
        )
        .order_by(
            'vehicle_model_id',
            # 与索引 idx_vm_cp_date_id 对齐，避免跨表字段排序导致的大排序与临时表
            'condition_point_id',
            '-test_date',
            '-id',
        )
    )

    latest_records = {}
    for obj in qs:
        cp = obj.condition_point
        if not cp:
            continue
        combo_key = (obj.vehicle_model_id, cp.work_condition, cp.measure_point)
        if combo_key in latest_records:
            continue
        latest_records[combo_key] = obj

    series_buckets = defaultdict(dict)
    for obj in latest_records.values():
        cp = obj.condition_point
        if not cp:
            continue
        measure_type = getattr(cp, 'measure_type', ConditionMeasurePoint.MeasureType.NOISE)
        chart_candidates = STEADY_STATE_CHARTS_BY_TYPE.get(measure_type)
        if not chart_candidates:
            continue
        for meta in chart_candidates:
            value = getattr(obj, meta['field'], None)
            if value in (None, ''):
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            bucket_key = (measure_type, meta['metric'])
            series_key = (obj.vehicle_model_id, cp.measure_point)
            entry = series_buckets[bucket_key].setdefault(series_key, {
                'name': f"{getattr(obj.vehicle_model, 'vehicle_model_name', str(obj.vehicle_model_id))}-{cp.measure_point}",
                'vehicle_model_name': getattr(obj.vehicle_model, 'vehicle_model_name', str(obj.vehicle_model_id)),
                'measure_point': cp.measure_point,
                'measure_type': measure_type,
                'metric': meta['metric'],
                'values': {},
            })
            entry['values'][cp.work_condition] = numeric_value

    charts = []
    for meta in STEADY_STATE_CHART_DEFINITIONS:
        bucket = series_buckets.get((meta['measure_type'], meta['metric']))
        if not bucket:
            continue
        sorted_series = sorted(
            bucket.values(),
            key=lambda item: (item['vehicle_model_name'], item['measure_point']),
        )
        chart = {
            'chart_key': meta['chart_key'],
            'title': meta['title'],
            'unit': meta['unit'],
            'measure_type': meta['measure_type'],
            'metric': meta['metric'],
            'work_conditions': work_conditions,
            'series': [],
        }
        for series in sorted_series:
            values = [series['values'].get(wc) for wc in work_conditions]
            chart['series'].append({
                'name': series['name'],
                'vehicle_model_name': series['vehicle_model_name'],
                'measure_point': series['measure_point'],
                'measure_type': series['measure_type'],
                'metric': series['metric'],
                'values': values,
            })
        charts.append(chart)

    return Response.success(data={'charts': charts}, message='查询成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dynamic_work_conditions(request):
    serializer = DynamicWorkConditionSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response.bad_request(message='参数错误', data=serializer.errors)
    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    values = (
        DynamicNoiseData.objects
        .filter(vehicle_model_id__in=vehicle_model_ids)
        .values_list('condition_measure_point__work_condition', flat=True)
        .distinct()
        .order_by('condition_measure_point__work_condition')
    )
    return Response.success(data=list(values), message='获取工况选项成功')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dynamic_measure_points(request):
    serializer = DynamicMeasurePointSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response.bad_request(message='参数错误', data=serializer.errors)
    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']
    values = (
        DynamicNoiseData.objects
        .filter(
            vehicle_model_id__in=vehicle_model_ids,
            condition_measure_point__work_condition__in=work_conditions,
        )
        .values(
            'condition_measure_point__measure_point',
            'condition_measure_point__measure_type',
        )
        .distinct()
        .order_by('condition_measure_point__measure_type', 'condition_measure_point__measure_point')
    )
    data = [
        {
            'measure_point': item['condition_measure_point__measure_point'],
            'measure_type': item['condition_measure_point__measure_type'],
        }
        for item in values
    ]
    return Response.success(data=data, message='获取测点选项成功')


@api_view(['POST'])
@permission_classes([AllowAny])
def query_dynamic_noise(request):
    serializer = DynamicNoiseQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response.bad_request(message='查询参数错误', data=serializer.errors)

    vehicle_model_ids = serializer.validated_data['vehicle_model_ids']
    work_conditions = serializer.validated_data['work_conditions']
    measure_points = serializer.validated_data['measure_points']
    page = serializer.validated_data['page']
    page_size = serializer.validated_data['page_size']

    qs = (
        DynamicNoiseData.objects
        .select_related('condition_measure_point')
        .filter(
            vehicle_model_id__in=vehicle_model_ids,
            condition_measure_point__work_condition__in=work_conditions,
            condition_measure_point__measure_point__in=measure_points,
        )
        .order_by('vehicle_model_id', 'condition_measure_point__work_condition', 'condition_measure_point__measure_point')
    )

    total = qs.count()
    start = (page - 1) * page_size
    rows = list(qs[start:start + page_size])

    sound_pressure_series = []
    speech_clarity_series = []
    axis_types = set()
    legend_names = set()

    vehicle_names = dict(VehicleModel.objects.filter(id__in=vehicle_model_ids).values_list('id', 'vehicle_model_name'))

    for obj in rows:
        cmp_obj = obj.condition_measure_point
        wc = getattr(cmp_obj, 'work_condition', '')
        mp = getattr(cmp_obj, 'measure_point', '')
        vm_name = vehicle_names.get(obj.vehicle_model_id, str(obj.vehicle_model_id))
        series_name = f"{vm_name}-{wc}-{mp}"
        legend_names.add(series_name)

        if obj.x_axis_type:
            axis_types.add(obj.x_axis_type)

        sp_pairs = _build_curve_pairs(
            obj.sound_pressure_curve,
            ['speed', 'rpm', 'speed/rpm', 'km/h'],
            ['dB(A)', 'value', 'values'],
        )
        if sp_pairs:
            sound_pressure_series.append({
                'name': series_name,
                'x_axis_type': obj.x_axis_type,
                'data': sp_pairs,
            })

        sc_pairs = _build_curve_pairs(
            obj.speech_clarity_curve,
            ['speed', 'rpm', 'speed/rpm', 'km/h'],
            ['%AI', 'value', 'values'],
        )
        if sc_pairs:
            speech_clarity_series.append({
                'name': series_name,
                'x_axis_type': obj.x_axis_type,
                'data': sc_pairs,
            })

    table_data = DynamicNoiseTableSerializer(rows, many=True, context={'request': request}).data
    for item, obj in zip(table_data, rows):
        item['vehicle_model_name'] = vehicle_names.get(obj.vehicle_model_id, str(obj.vehicle_model_id))
        item['noise_analysis_url'] = _build_media_url(obj.noise_analysis_image, request)
        item['audio_url'] = _build_media_url(obj.audio_file, request)
        item['spectrum_url'] = _build_media_url(obj.spectrum_file, request)
        item['spectrum_image_url'] = _build_media_url(getattr(obj, 'spectrum_image_path', ''), request)

    return Response.success(
        data={
            'sound_pressure': sound_pressure_series,
            'speech_clarity': speech_clarity_series,
            'axis_types': sorted(axis_types),
            'legend': list(legend_names),
            'table': {
                'count': total,
                'page': page,
                'page_size': page_size,
                'results': table_data,
            },
        },
        message='查询成功',
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dynamic_spectrum_data(request, pk: int):
    try:
        obj = DynamicNoiseData.objects.select_related('condition_measure_point').get(pk=pk)
    except DynamicNoiseData.DoesNotExist:
        return Response.not_found(message='数据不存在')
    if not obj.spectrum_file:
        return Response.bad_request(message='当前记录未上传频谱数据')

    # 将数据库中存储的路径（可能包含 /media/ 前缀或起始斜杠）规范化为
    # 相对于 MEDIA_ROOT 的路径，再拼接成磁盘绝对路径
    raw_path = str(obj.spectrum_file)
    rel_path = raw_path.replace('\\', '/').strip()
    # 去掉开头的斜杠，避免在 Windows 上被当作磁盘根路径处理
    rel_path = rel_path.lstrip('/')
    media_prefix = (settings.MEDIA_URL or '').lstrip('/')  # 例如 'media/'
    if media_prefix and rel_path.startswith(media_prefix):
        rel_path = rel_path[len(media_prefix):]
        rel_path = rel_path.lstrip('/')

    media_root = os.path.abspath(settings.MEDIA_ROOT)
    file_path = os.path.abspath(os.path.join(media_root, rel_path))
    # 防止路径越界
    if not file_path.startswith(media_root):
        return Response.bad_request(message='频谱文件路径非法')
    if not os.path.exists(file_path):
        return Response.bad_request(message='频谱文件不存在')

    # 直接返回 PPTX 文件用于浏览器预览或下载
    filename = os.path.basename(file_path) or 'spectrum.pptx'
    name_root, ext = os.path.splitext(filename)
    if not ext:
        filename = f'{filename}.pptx'

    try:
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        )
    except OSError:
        return Response.bad_request(message='频谱文件无法读取')

    quoted_name = quote(filename)
    # 使用 attachment 形式；是否在浏览器中直接预览由浏览器自身决定
    response['Content-Disposition'] = (
        f'attachment; filename="{quoted_name}"; filename*=UTF-8\'\'{quoted_name}'
    )
    return response
