import json
from collections import OrderedDict, defaultdict
from decimal import Decimal
from typing import Dict, Iterable, List, Sequence, Tuple

from django.db.models import Q

from apps.acoustic_analysis.models import AcousticTestData, ConditionMeasurePoint, DynamicNoiseData
from apps.dynamic_stiffness.models import SuspensionIsolationData
from apps.modal.models import AirtightnessTest, VehicleModel
from apps.sound_module.models import VehicleSoundInsulationData
from apps.wheel_performance.models import WheelPerformance

from .constants import (
    ACCELERATION_POINT_CANDIDATES,
    AIR_CONDITION_POINTS,
    CRUISE_RADAR_POINTS,
    SOUND_INSULATION_FREQ_FIELDS,
    SPEECH_CLARITY_POINTS,
    SUSPENSION_MEASURE_POINTS,
    SUSPENSION_FRONT_POINT_CANDIDATES,
    SUSPENSION_REAR_POINT_CANDIDATES,
)


def to_float(value):
    if value in (None, ''):
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def parse_json_field(value):
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


def normalize_numeric_list(values):
    if not isinstance(values, list):
        return []
    normalized = []
    for item in values:
        val = to_float(item)
        if val is None:
            continue
        normalized.append(val)
    return normalized


def pick_value_list(series_dict, candidate_keys: Sequence[str]):
    if not isinstance(series_dict, dict):
        return None
    for key in candidate_keys:
        value = series_dict.get(key)
        if isinstance(value, list) and value:
            return value
    for value in series_dict.values():
        if isinstance(value, list) and value:
            return value
    return None


def build_curve_pairs(series_data, x_keys: Sequence[str], y_keys: Sequence[str]):
    if series_data is None:
        return []
    if isinstance(series_data, list):
        pairs = []
        for entry in series_data:
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                x_val = to_float(entry[0])
                y_val = to_float(entry[1])
            elif isinstance(entry, dict):
                x_val = to_float(entry.get('x') or entry.get('frequency') or entry.get('Hz')or entry.get('speed'))
                y_val = to_float(entry.get('y') or entry.get('value') or entry.get('dB') or entry.get('dB(A)'))
            else:
                continue
            if x_val is None or y_val is None:
                continue
            pairs.append([x_val, y_val])
        return pairs
    if isinstance(series_data, dict):
        x_list = normalize_numeric_list(pick_value_list(series_data, x_keys))
        y_list = normalize_numeric_list(pick_value_list(series_data, y_keys))
        length = min(len(x_list), len(y_list))
        return [[x_list[i], y_list[i]] for i in range(length)]
    return []


def parse_force_transfer_signal(signal):
    data = parse_json_field(signal)
    if data is None:
        return []

    # 先按通用规则解析为 [x, y] 数对
    pairs = build_curve_pairs(
        data,
        x_keys=['frequency','Hz', 'freq', 'speed', 'rpm'],
        y_keys=['dB', 'db', 'dB(A)', 'value', 'values'],
    )

    if not pairs:
        return []

    # 为兼容 WheelPerformance 查询页，对可能出现的「频率 / dB 维度对调」做一次自动纠正：
    # - 频率通常在 [0, 300]（或更高），最大值 >= 80
    # - dB 幅值通常在 [-100, 100]，整体跨度不超过 ~120dB
    xs = [to_float(p[0]) for p in pairs if to_float(p[0]) is not None]
    ys = [to_float(p[1]) for p in pairs if to_float(p[1]) is not None]

    if xs and ys:
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        x_range = x_max - x_min
        y_range = y_max - y_min

        def looks_like_freq(v_min, v_max):
            return v_max >= 80 and v_max <= 1000

        def looks_like_db(v_min, v_max, v_range):
            return v_range <= 120 and v_max <= 120 and v_min >= -120

        freq_looks_db = looks_like_db(x_min, x_max, x_range)
        db_looks_freq = y_max >= 80
        x_is_freq = looks_like_freq(x_min, x_max)
        y_is_db = looks_like_db(y_min, y_max, y_range)

        # 若当前 x 更像 dB、y 更像频率，则整体对调坐标轴
        if (not x_is_freq) and (not y_is_db) and freq_looks_db and db_looks_freq:
            pairs = [[p[1], p[0]] for p in pairs]

    # 若频率最大值在 30~40 之间，视为以 0.5 为步长但单位偏小，按 10 倍缩放到 0-300 区间
    max_freq = max((to_float(item[0]) or 0 for item in pairs), default=0)
    if 0 < max_freq <= 40:
        scaled = []
        for freq, value in pairs:
            scaled.append([round(freq * 10, 4), value])
        pairs = scaled
    pairs.sort(key=lambda item: item[0])
    return pairs


def load_vehicle_map(vehicle_ids: Sequence[int]) -> Dict[int, dict]:
    vehicles = (
        VehicleModel.objects.filter(id__in=vehicle_ids)
        .values(
            'id',
            'vehicle_model_name',
            'cle_model_code',
            'drive_type',
            'energy_type',
            'suspension_type',
            'subframe_type',
            'front_windshield',
            'side_door_glass',
        )
    )
    return {vehicle['id']: vehicle for vehicle in vehicles}


def load_condition_points(condition_point_ids: Iterable[int]) -> Dict[int, dict]:
    lookup = {}
    qs = ConditionMeasurePoint.objects.filter(id__in=list(condition_point_ids)).values(
        'id', 'measure_point', 'work_condition'
    )
    for item in qs:
        lookup[item['id']] = item
    return lookup


def fetch_latest_acoustic_values(
    vehicle_ids: Sequence[int], condition_point_ids: Sequence[int], value_field: str
) -> Dict[Tuple[int, int], float]:
    if not condition_point_ids:
        return {}
    qs = (
        AcousticTestData.objects.filter(
            vehicle_model_id__in=vehicle_ids,
            condition_point_id__in=condition_point_ids,
        )
        .order_by('vehicle_model_id', 'condition_point_id', '-test_date', '-id')
        .values('vehicle_model_id', 'condition_point_id', value_field)
    )
    results: Dict[Tuple[int, int], float] = {}
    for row in qs:
        key = (row['vehicle_model_id'], row['condition_point_id'])
        if key in results:
            continue
        value = to_float(row.get(value_field))
        if value is None:
            continue
        results[key] = value
    return results


def fetch_radar_rms_map(
    vehicle_ids: Sequence[int], condition_point_ids: Sequence[int]
) -> Dict[int, Dict[int, float]]:
    if not vehicle_ids or not condition_point_ids:
        return {}

    rows = (
        AcousticTestData.objects.filter(
            vehicle_model_id__in=vehicle_ids,
            condition_point_id__in=condition_point_ids,
            rms_value__isnull=False,
        )
        .values('vehicle_model_id', 'condition_point_id', 'rms_value')
    )

    values_map: Dict[int, Dict[int, float]] = defaultdict(dict)
    for row in rows:
        value = to_float(row.get('rms_value'))
        if value is None:
            continue
        values_map[row['vehicle_model_id']][row['condition_point_id']] = value
    return values_map


def build_radar_section(vehicle_ids, vehicle_map, condition_lookup):
    sections = {}
    for key, point_ids in CRUISE_RADAR_POINTS.items():
        if not point_ids:
            sections[key] = {'conditions': [], 'indicators': [], 'series': []}
            continue

        indicator_items = []
        for pid in point_ids:
            meta = condition_lookup.get(pid, {})
            indicator_items.append(
                {
                    'id': pid,
                    'label': meta.get('measure_point') or meta.get('work_condition') or f'测点{pid}',
                    'work_condition': meta.get('work_condition'),
                    'measure_point': meta.get('measure_point'),
                }
            )

        values_map = fetch_radar_rms_map(vehicle_ids, point_ids)
        series = []
        for vid in vehicle_ids:
            vehicle_values = values_map.get(vid, {})
            ordered_values = [vehicle_values.get(pid) for pid in point_ids]
            if not any(value is not None for value in ordered_values):
                continue
            series.append(
                {
                    'vehicle_id': vid,
                    'vehicle_model_name': vehicle_map.get(vid, {}).get('vehicle_model_name', str(vid)),
                    'values': ordered_values,
                }
            )

        sections[key] = {
            'conditions': indicator_items,
            'indicators': [dict(item) for item in indicator_items],
            'series': series,
        }
    return sections


def build_air_condition_section(vehicle_ids, vehicle_map, condition_lookup):
    sections = {}
    for key, point_ids in AIR_CONDITION_POINTS.items():
        # 按测点顺序直接映射为空调档位：第1个测点为1档，第2个为2档，以此类推
        gear_labels = [f'{index + 1}档' for index in range(len(point_ids))]

        values_map = fetch_latest_acoustic_values(vehicle_ids, point_ids, 'rms_value')
        series = []
        for vid in vehicle_ids:
            series.append({
                'vehicle_id': vid,
                'vehicle_model_name': vehicle_map.get(vid, {}).get('vehicle_model_name', str(vid)),
                 'values': [values_map.get((vid, pid)) for pid in point_ids],
            })
        sections[key] = {
            'points': point_ids,
            'gears': gear_labels,
            'series': series,
        }
    return sections


def build_acceleration_section(vehicle_ids, main_vehicle_id, vehicle_map, condition_lookup):
    sections = {}
    for key, candidates in ACCELERATION_POINT_CANDIDATES.items():
        existing_ids = set(
            DynamicNoiseData.objects.filter(
                vehicle_model_id__in=vehicle_ids,
                condition_measure_point_id__in=candidates,
            ).values_list('condition_measure_point_id', flat=True)
        )
        target_id = None
        for candidate in candidates:
            if candidate in existing_ids:
                target_id = candidate
                break
        if not target_id:
            sections[key] = {'series': [], 'x_axis_type': None}
            continue

        rows = list(
            DynamicNoiseData.objects.filter(
                vehicle_model_id__in=vehicle_ids,
                condition_measure_point_id=target_id,
            ).select_related('condition_measure_point')
        )
        axis_type = None
        for row in rows:
            if row.vehicle_model_id == main_vehicle_id and row.x_axis_type:
                axis_type = row.x_axis_type.lower()
                break
        series = []
        for row in rows:
            # 仅展示单位与主车型一致的数据
            if axis_type and row.x_axis_type and row.x_axis_type.lower() != axis_type:
                continue
            pairs = build_curve_pairs(
                parse_json_field(row.sound_pressure_curve),
                x_keys=['speed', 'rpm', 'speed/rpm', 'Speed', 'km/h'],
                y_keys=['dB(A)', 'value', 'values', 'sound_pressure', 'Sound Pressure'],
            )
            if not pairs:
                continue
            series.append({
                'vehicle_id': row.vehicle_model_id,
                'vehicle_model_name': vehicle_map.get(row.vehicle_model_id, {}).get('vehicle_model_name', str(row.vehicle_model_id)),
                'x_axis_type': row.x_axis_type,
                'data': pairs,
            })
        sections[key] = {
            'condition_point_id': target_id,
            'condition_point_name': condition_lookup.get(target_id, {}).get('measure_point'),
            'x_axis_type': axis_type,
            'series': series,
        }
    return sections


def build_chassis_section(vehicle_ids, vehicle_map):
    wheel_records = (
        WheelPerformance.objects.filter(vehicle_model_id__in=vehicle_ids)
        .select_related('vehicle_model')
        .order_by('vehicle_model_id', 'id')
    )
    record_map = {}
    for record in wheel_records:
        if record.vehicle_model_id in record_map:
            continue
        record_map[record.vehicle_model_id] = record

    table_rows = []
    chart_series = []
    for vid in vehicle_ids:
        wheel = record_map.get(vid)
        vm = vehicle_map.get(vid, {})
        table_rows.append({
            'vehicle_id': vid,
            'vehicle_model_name': vm.get('vehicle_model_name', str(vid)),
            'suspension_type': vm.get('suspension_type'),
            'subframe_type': vm.get('subframe_type'),
            'tire_brand': getattr(wheel, 'tire_brand', None),
            'tire_model': getattr(wheel, 'tire_model', None),
            'is_silent': getattr(wheel, 'is_silent', None),
            'rim_lateral_stiffness': to_float(getattr(wheel, 'rim_lateral_stiffness', None)),
        })
        if wheel and wheel.force_transfer_signal:
            series_data = parse_force_transfer_signal(wheel.force_transfer_signal)
            if series_data:
                chart_series.append({
                    'vehicle_id': vid,
                    'vehicle_model_name': vm.get('vehicle_model_name', str(vid)),
                    'data': series_data,
                })

    # 悬架隔振率
    susp_qs = (
        SuspensionIsolationData.objects
        .filter(
            test__vehicle_model_id__in=vehicle_ids,
            measuring_point__in=SUSPENSION_MEASURE_POINTS,
        )
        .select_related('test__vehicle_model')
        .order_by(
            'test__vehicle_model_id',
            'measuring_point',
            '-test__test_date',
            '-id',
        )
    )
    suspension_map = defaultdict(dict)
    for item in susp_qs:
        key = (item.test.vehicle_model_id, item.measuring_point)
        if key in suspension_map[item.test.vehicle_model_id]:
            continue
        suspension_map[item.test.vehicle_model_id][item.measuring_point] = item

    categories = [
        '前减振器-X',
        '前减振器-Y',
        '前减振器-Z',
        '后减振器-X',
        '后减振器-Y',
        '后减振器-Z',
    ]

    suspension_series = []
    for vid in vehicle_ids:
        mp_data = suspension_map.get(vid, {})
        values = []
        front_data = None
        for measure_point in SUSPENSION_FRONT_POINT_CANDIDATES:
            if measure_point in mp_data:
                front_data = mp_data[measure_point]
                break

        rear_data = None
        for measure_point in SUSPENSION_REAR_POINT_CANDIDATES:
            if measure_point in mp_data:
                rear_data = mp_data[measure_point]
                break

        for data in (front_data, rear_data):
            if data is None:
                values.extend([None, None, None])
            else:
                values.extend([
                    to_float(getattr(data, 'x_isolation_rate', None)),
                    to_float(getattr(data, 'y_isolation_rate', None)),
                    to_float(getattr(data, 'z_isolation_rate', None)),
                ])
        suspension_series.append({
            'vehicle_id': vid,
            'vehicle_model_name': vehicle_map.get(vid, {}).get('vehicle_model_name', str(vid)),
            'data': values,
        })

    return {
        'parameters': table_rows,
        'force_transfer': chart_series,
        'suspension_isolation': {
            'categories': categories,
            'series': suspension_series,
        },
    }


def build_acoustic_package_section(vehicle_ids, vehicle_map, condition_lookup):
    sound_map = {
        item.vehicle_model_id: item
        for item in VehicleSoundInsulationData.objects.filter(vehicle_model_id__in=vehicle_ids)
    }
    airtight_map = OrderedDict()
    airtight_qs = (
        AirtightnessTest.objects.filter(vehicle_model_id__in=vehicle_ids)
        .order_by('vehicle_model_id', '-test_date', '-id')
        .values('vehicle_model_id', 'uncontrolled_leakage')
    )
    for item in airtight_qs:
        if item['vehicle_model_id'] in airtight_map:
            continue
        airtight_map[item['vehicle_model_id']] = to_float(item['uncontrolled_leakage'])

    clarity_values = fetch_latest_acoustic_values(
        vehicle_ids,
        list(SPEECH_CLARITY_POINTS.values()),
        'speech_clarity',
    )

    table_rows = []
    for vid in vehicle_ids:
        vm = vehicle_map.get(vid, {})
        table_rows.append({
            'vehicle_id': vid,
            'vehicle_model_name': vm.get('vehicle_model_name', str(vid)),
            'suspension_type': vm.get('suspension_type'),
            'front_windshield': vm.get('front_windshield'),
            'side_door_glass': vm.get('side_door_glass'),
            'sound_insulation_performance': to_float(
                getattr(sound_map.get(vid), 'sound_insulation_performance', None)
            ),
            'uncontrolled_leakage': airtight_map.get(vid),
            'speech_clarity_100': clarity_values.get((vid, SPEECH_CLARITY_POINTS['speed_100'])),
            'speech_clarity_120': clarity_values.get((vid, SPEECH_CLARITY_POINTS['speed_120'])),
        })

    frequency_series = []
    for vid in vehicle_ids:
        sound_item = sound_map.get(vid)
        if not sound_item:
            continue
        values = []
        for freq in SOUND_INSULATION_FREQ_FIELDS:
            attr = getattr(sound_item, f'freq_{freq}', None)
            values.append(to_float(attr))
        frequency_series.append({
            'vehicle_id': vid,
            'vehicle_model_name': vehicle_map.get(vid, {}).get('vehicle_model_name', str(vid)),
            'values': values,
        })

    return {
        'table': table_rows,
        'insulation_curve': {
            'frequencies': SOUND_INSULATION_FREQ_FIELDS,
            'series': frequency_series,
        },
        'clarity_points': [
            {
                'id': SPEECH_CLARITY_POINTS['speed_100'],
                'label': condition_lookup.get(SPEECH_CLARITY_POINTS['speed_100'], {}).get('measure_point') or '测点11',
            },
            {
                'id': SPEECH_CLARITY_POINTS['speed_120'],
                'label': condition_lookup.get(SPEECH_CLARITY_POINTS['speed_120'], {}).get('measure_point') or '测点13',
            },
        ],
    }


def build_benchmark_payload(main_vehicle_id: int, vehicle_ids: Sequence[int], include_chassis: bool, include_acoustic: bool):
    vehicle_map = load_vehicle_map(vehicle_ids)
    all_condition_ids = set()
    for ids in CRUISE_RADAR_POINTS.values():
        all_condition_ids.update(ids)
    for ids in AIR_CONDITION_POINTS.values():
        all_condition_ids.update(ids)
    for ids in ACCELERATION_POINT_CANDIDATES.values():
        all_condition_ids.update(ids)
    all_condition_ids.update(SPEECH_CLARITY_POINTS.values())
    condition_lookup = load_condition_points(all_condition_ids)

    payload = {
        'vehicles': {
            'main': vehicle_map.get(main_vehicle_id),
            'benchmarks': [
                vehicle_map[vid] for vid in vehicle_ids if vid != main_vehicle_id and vid in vehicle_map
            ],
            'all': [vehicle_map[vid] for vid in vehicle_ids if vid in vehicle_map],
        },
        'cruise_radar': build_radar_section(vehicle_ids, vehicle_map, condition_lookup),
        'air_condition': build_air_condition_section(vehicle_ids, vehicle_map, condition_lookup),
        'acceleration': build_acceleration_section(vehicle_ids, main_vehicle_id, vehicle_map, condition_lookup),
    }

    if include_chassis:
        payload['chassis'] = build_chassis_section(vehicle_ids, vehicle_map)
    if include_acoustic:
        payload['acoustic_package'] = build_acoustic_package_section(vehicle_ids, vehicle_map, condition_lookup)
    return payload
