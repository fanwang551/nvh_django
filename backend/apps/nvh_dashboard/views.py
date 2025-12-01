from collections import Counter, defaultdict
from datetime import date

from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from utils.response import Response
from apps.modal.models import AirtightnessImage, AirtightnessTest, VehicleModel
from apps.sound_module.models import (
    SoundInsulationData,
    VehicleSoundInsulationData,
    VehicleReverberationData,
)
from apps.acoustic_analysis.models import AcousticTestData, ConditionMeasurePoint
from apps.NTF.models import NTFInfo
from apps.vehicle_body.models import SampleInfo


def _build_month_labels(end_date: date, months: int = 36):
    labels = []
    year = end_date.year
    month = end_date.month
    for _ in range(months):
        labels.append(f'{year:04d}-{month:02d}')
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    labels.reverse()
    return labels


@api_view(['GET'])
@permission_classes([AllowAny])
def home_dashboard(request):
    """
    NVH 首页聚合数据

    返回结构示例：
    {
      "kpis": {...},
      "trend_36_months": {...},
      "test_type_distribution": [...],
      "vehicle_performance": [...],
      "noise_radar": {...},
      "odor_bars": [...]
    }
    """
    today = timezone.localdate()

    # === KPI 指标 ===
    airtight_count = AirtightnessTest.objects.count()
    vehicle_sound_count = VehicleSoundInsulationData.objects.count()
    acoustic_count = AcousticTestData.objects.count()
    ntf_count = NTFInfo.objects.count()
    voc_sample_count = SampleInfo.objects.count()
    reverberation_count = VehicleReverberationData.objects.count()

    total_tests = (
        airtight_count
        + vehicle_sound_count
        + acoustic_count
        + ntf_count
        + voc_sample_count
        + reverberation_count
    )

    current_year = today.year
    try:
        year_tests = (
            AirtightnessTest.objects.filter(test_date__year=current_year).count()
            + VehicleSoundInsulationData.objects.filter(test_date__year=current_year).count()
            + AcousticTestData.objects.filter(test_date__year=current_year).count()
            + NTFInfo.objects.filter(test_time__year=current_year).count()
            + SampleInfo.objects.filter(test_date__year=current_year).count()
            + VehicleReverberationData.objects.filter(test_date__year=current_year).count()
        )
    except Exception:
        # 如果部分表缺少时间字段或时间数据异常，本年度试验数暂时置为 0，避免首页报错
        year_tests = 0

    vehicle_models_count = VehicleModel.objects.filter(status='active').count()

    kpis = {
        'total_tests': total_tests,
        'year_tests': year_tests,
        'vehicle_models': vehicle_models_count,
        'samples': voc_sample_count,
    }

    # === 36 个月趋势 ===
    trend_36_months = {
        'months': [],
        'counts': [],
    }

    try:
        month_counter: Counter[str] = Counter()

        def add_month_counts(qs, date_field: str):
            """
            通用的月度计数聚合工具：
            - 按月份对给定 queryset 进行分组
            - 将每月记录数累加进 month_counter
            """
            annotated = (
                qs.annotate(month=TruncMonth(date_field))
                .values('month')
                .annotate(count=Count('id'))
            )
            for item in annotated:
                month = item['month']
                if not month:
                    continue
                label = month.strftime('%Y-%m')
                month_counter[label] += item['count']

        # 1、月度趋势图统计来源：
        # AirtightnessTest，AirtightnessImage，VehicleReverberationData，
        # SoundInsulationData，VehicleSoundInsulationData，SampleInfo，NTFInfo
        add_month_counts(AirtightnessTest.objects.all(), 'test_date')
        add_month_counts(AirtightnessImage.objects.all(), 'test_date')
        add_month_counts(VehicleReverberationData.objects.all(), 'test_date')
        add_month_counts(SoundInsulationData.objects.all(), 'test_date')
        add_month_counts(VehicleSoundInsulationData.objects.all(), 'test_date')
        add_month_counts(SampleInfo.objects.all(), 'test_date')
        add_month_counts(NTFInfo.objects.all(), 'test_time')

        month_labels = _build_month_labels(today, months=36)
        trend_counts = [int(month_counter.get(label, 0)) for label in month_labels]

        trend_36_months = {
            'months': month_labels,
            'counts': trend_counts,
        }
    except Exception:
        # 如果某些表缺少时间字段或时间数据异常，则不返回趋势数据，避免首页报错
        trend_36_months = {
            'months': [],
            'counts': [],
        }

    # === 各类试验分布 ===
    test_type_distribution = [
        {'key': 'airtight', 'label': '气密性', 'count': int(airtight_count)},
        {
            'key': 'acoustic',
            'label': '声学',
            'count': int(vehicle_sound_count + acoustic_count + reverberation_count),
        },
        {'key': 'ntf', 'label': 'NTF', 'count': int(ntf_count)},
        {'key': 'voc', 'label': 'VOC/气味', 'count': int(voc_sample_count)},
    ]

    # === 最新车型性能看板 ===
    latest_airtight_subquery = (
        AirtightnessTest.objects.filter(vehicle_model=OuterRef('pk'))
        .order_by('-test_date', '-id')
        .values('uncontrolled_leakage')[:1]
    )
    latest_sound_subquery = (
        VehicleSoundInsulationData.objects.filter(vehicle_model=OuterRef('pk'))
        .order_by('-test_date', '-id')
        .values('sound_insulation_performance')[:1]
    )

    vehicles_qs = (
        VehicleModel.objects.filter(status='active')
        .annotate(
            latest_uncontrolled_leakage=Subquery(latest_airtight_subquery),
            latest_sound_performance=Subquery(latest_sound_subquery),
        )
        .filter(
            Q(latest_uncontrolled_leakage__isnull=False)
            | Q(latest_sound_performance__isnull=False)
        )
        .order_by('-production_year', '-id')[:50]
    )

    vehicle_performance = []
    for vm in vehicles_qs:
        vehicle_performance.append(
            {
                'vehicle_model_id': vm.id,
                'vehicle_model_name': vm.vehicle_model_name,
                'production_year': vm.production_year,
                'drive_type': vm.drive_type,
                'suspension_type': vm.suspension_type,
                'configuration': vm.configuration,
                'sunroof_type': vm.sunroof_type,
                'uncontrolled_leakage': vm.latest_uncontrolled_leakage,
                'sound_insulation_performance': vm.latest_sound_performance,
            }
        )

    # === 雷达图：各工况噪声分析 ===
    radar_condition_ids = [1, 5, 7, 9, 11, 13]
    condition_qs = ConditionMeasurePoint.objects.filter(id__in=radar_condition_ids)
    condition_map = {}
    for cmp_obj in condition_qs:
        condition_map[cmp_obj.id] = {
            'id': cmp_obj.id,
            'work_condition': cmp_obj.work_condition,
            'measure_point': cmp_obj.measure_point,
            'label': cmp_obj.work_condition,
        }

    ordered_condition_ids = [cid for cid in radar_condition_ids if cid in condition_map]
    radar_conditions = [condition_map[cid] for cid in ordered_condition_ids]

    noise_radar = {
        'conditions': radar_conditions,
        'series': [],
    }

    if ordered_condition_ids:
        latest_records = (
            AcousticTestData.objects.filter(
                condition_point_id__in=ordered_condition_ids,
                rms_value__isnull=False,
            )
            .order_by('-test_date', '-id')
            .values('vehicle_model_id', 'test_date')
        )

        picked_vehicle_ids = []
        seen = set()
        for item in latest_records:
            vm_id = item['vehicle_model_id']
            if vm_id in seen:
                continue
            seen.add(vm_id)
            picked_vehicle_ids.append(vm_id)
            if len(picked_vehicle_ids) >= 3:
                break

        if picked_vehicle_ids:
            vehicle_names = dict(
                VehicleModel.objects.filter(id__in=picked_vehicle_ids).values_list(
                    'id', 'vehicle_model_name'
                )
            )
            vm_point_values: dict[int, dict[int, float]] = defaultdict(dict)
            for vm_id in picked_vehicle_ids:
                for cp_id in ordered_condition_ids:
                    latest_value = (
                        AcousticTestData.objects.filter(
                            vehicle_model_id=vm_id,
                            condition_point_id=cp_id,
                            rms_value__isnull=False,
                        )
                        .order_by('-test_date', '-id')
                        .values_list('rms_value', flat=True)
                        .first()
                    )
                    if latest_value is not None:
                        vm_point_values[vm_id][cp_id] = float(latest_value)

            for vm_id in picked_vehicle_ids:
                vm_values = vm_point_values.get(vm_id, {})
                values = [vm_values.get(cid) for cid in ordered_condition_ids]
                noise_radar['series'].append(
                    {
                        'vehicle_model_id': vm_id,
                        'vehicle_model_name': vehicle_names.get(vm_id, str(vm_id)),
                        'values': values,
                    }
                )

    # === 气味柱状图：最近 5 个整车样品 ===
    odor_samples_qs = (
        SampleInfo.objects.filter(part_name__icontains='整车')
        .order_by('-test_date', '-id')[:5]
    )
    odor_bars = []
    for sample in odor_samples_qs:
        odor_bars.append(
            {
                'id': sample.id,
                'project_name': sample.project_name,
                'development_stage': sample.development_stage,
                'status': sample.status,
                'part_name': sample.part_name,
                'test_date': sample.test_date,
                'odor_static_front': sample.odor_static_front,
                'odor_dynamic_front': sample.odor_dynamic_front,
                'odor_static_rear': sample.odor_static_rear,
                'odor_dynamic_rear': sample.odor_dynamic_rear,
                'odor_mean': sample.odor_mean,
            }
        )

    data = {
        'kpis': kpis,
        'trend_36_months': trend_36_months,
        'test_type_distribution': test_type_distribution,
        'vehicle_performance': vehicle_performance,
        'noise_radar': noise_radar,
        'odor_bars': odor_bars,
    }
    return Response.success(data=data, message='获取 NVH 首页数据成功')
