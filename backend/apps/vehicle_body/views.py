from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Max, Count
from django.db.models.functions import ExtractMonth
from django.utils import timezone

from utils.response import Response
from .models import SampleInfo, SubstancesTestDetail, Substance
from .serializers import VocOdorDataSerializer, SubstancesTestListItemSerializer, SubstancesTestDetailSerializer, SubstanceSerializer


def _safe_distinct_count(queryset, field_name):
    """辅助：对指定字段做去重计数时忽略None/空字符串"""
    return (
        queryset
        .exclude(**{f"{field_name}__isnull": True})
        .exclude(**{field_name: ''})
        .values_list(field_name, flat=True)
        .distinct()
        .count()
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def data_list(request):
    """获取VOC/气味数据列表（基于新SampleInfo，兼容旧前端所需结构）"""
    try:
        page = int(request.GET.get('page', 1) or 1)
        page_size = int(request.GET.get('page_size', 10) or 10)

        queryset = SampleInfo.objects.all().order_by('-id')

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = VocOdorDataSerializer(page_obj, many=True)
        return Response.success(data={
            'results': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size
            }
        }, message='获取数据成功')
    except Exception as e:
        return Response.error(message=f'获取数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def iaq_dashboard(request):
    """整车空气质量（IAQ）大屏数据"""
    try:
        now = timezone.now()
        current_year = now.year

        base_qs = SampleInfo.objects.all()
        project_total = _safe_distinct_count(base_qs, 'project_name')
        sample_total = base_qs.count()
        substance_total = Substance.objects.count()
        annual_test_total = base_qs.filter(test_date__year=current_year).count()

        def _gauge_payload(field_name):
            data_qs = base_qs.exclude(**{f"{field_name}__isnull": True})
            vehicle_qs = data_qs.filter(part_name='整车')
            parts_qs = data_qs.exclude(part_name='整车')
            return {
                'vehicle': {
                    'cumulative_total': vehicle_qs.count(),
                    'annual_total': vehicle_qs.filter(test_date__year=current_year).count()
                },
                'parts': {
                    'cumulative_total': parts_qs.count(),
                    'annual_total': parts_qs.filter(test_date__year=current_year).count()
                }
            }

        voc_gauge = _gauge_payload('tvoc')
        odor_gauge = _gauge_payload('odor_mean')

        latest_projects = (
            base_qs.exclude(project_name__isnull=True)
            .exclude(project_name__exact='')
            .values('project_name')
            .annotate(last_test=Max('test_date'), latest_id=Max('id'))
            .order_by('-last_test', '-latest_id')[:5]
        )
        top_project_names = [row['project_name'] for row in latest_projects]

        def _project_counts(names):
            if not names:
                return {}
            rows = (
                base_qs.filter(project_name__in=names)
                .values('project_name')
                .annotate(
                    vehicle_tests=Count('id', filter=Q(part_name='整车')),
                    part_tests=Count('id', filter=~Q(part_name='整车'))
                )
            )
            return {row['project_name']: row for row in rows}

        top_counts = _project_counts(top_project_names)
        project_comparison = []
        for name in top_project_names:
            record = top_counts.get(name, {})
            project_comparison.append({
                'project_name': name,
                'vehicle_tests': record.get('vehicle_tests', 0),
                'part_tests': record.get('part_tests', 0)
            })

        monthly_rows = (
            base_qs.filter(test_date__year=current_year)
            .annotate(month=ExtractMonth('test_date'))
            .values('month')
            .annotate(count=Count('id'))
        )
        monthly_map = {row['month']: row['count'] for row in monthly_rows if row['month'] is not None}
        monthly_trend = [{'month': m, 'value': monthly_map.get(m, 0)} for m in range(1, 13)]

        latest_records = []
        for sample in base_qs.order_by('-test_date', '-id')[:40]:
            latest_records.append({
                'id': sample.id,
                'test_date': sample.test_date.isoformat() if sample.test_date else None,
                'project_name': sample.project_name,
                'part_name': sample.part_name,
                'status': sample.status,
                'sample_no': sample.sample_no,
                'tvoc': float(sample.tvoc) if sample.tvoc is not None else None,
                'odor_mean': float(sample.odor_mean) if sample.odor_mean is not None else None
            })

        return Response.success(data={
            'timestamp': now.isoformat(),
            'kpis': {
                'project_total': project_total,
                'sample_total': sample_total,
                'substance_total': substance_total,
                'annual_test_total': annual_test_total,
                'refresh_interval_seconds': 86400
            },
            'voc_gauge': voc_gauge,
            'odor_gauge': odor_gauge,
            'project_comparison': project_comparison,
            'monthly_trend': monthly_trend,
            'latest_records': latest_records
        }, message='获取IAQ大屏数据成功')
    except Exception as e:
        return Response.error(message=f'获取IAQ大屏数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def project_name_options(request):
    """获取项目名称选项（去重，只返回项目名称）
    返回结构：[{ value: 项目名称, label: 项目名称, project_name: 项目名称 }]
    """
    try:
        names_qs = (
            SampleInfo.objects
            .exclude(project_name__isnull=True)
            .exclude(project_name='')
            .values_list('project_name', flat=True)
            .distinct()
        )

        # 排序（按项目名称）
        unique_names = sorted(set(names_qs))

        options = [
            {
                'value': name,
                'label': name,
                'project_name': name,
            }
            for name in unique_names
        ]

        return Response.success(data=options, message='获取项目名称选项成功')
    except Exception as e:
        return Response.error(message=f'获取项目名称选项失败: {str(e)}')


def _apply_filters(qs, filters):
    project_names = filters.get('project_names', []) or []
    if project_names:
        qs = qs.filter(project_name__in=project_names)

    part_names = filters.get('part_names', []) or []
    if part_names:
        part_names = list(part_names)
        has_whole_vehicle = '整车' in part_names
        has_other_parts = any(name != '整车' for name in part_names)

        if has_whole_vehicle and has_other_parts:
            # 出现“整车 + 其他零部件”混合时，按照前端约定：
            # 选择非“整车”零部件时，自动排除“整车”数据
            part_names = [name for name in part_names if name != '整车']

        if part_names:
            qs = qs.filter(part_name__in=part_names)

    statuses = filters.get('statuses', []) or []
    if statuses:
        qs = qs.filter(status__in=statuses)

    development_stages = filters.get('development_stages', []) or []
    if development_stages:
        qs = qs.filter(development_stage__in=development_stages)

    test_order_no = filters.get('test_order_no') or ''
    if test_order_no:
        qs = qs.filter(test_order_no__icontains=test_order_no)

    sample_no = filters.get('sample_no') or ''
    if sample_no:
        qs = qs.filter(sample_no__icontains=sample_no)

    test_date_range = filters.get('test_date_range') or []
    if isinstance(test_date_range, (list, tuple)) and len(test_date_range) == 2:
        # 处理前端传来的 ISO 8601 格式日期字符串，提取日期部分
        from datetime import datetime
        start_date = test_date_range[0]
        end_date = test_date_range[1]
        
        # 如果是字符串格式，尝试解析并转换为日期
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
            
        qs = qs.filter(test_date__range=[start_date, end_date])

    return qs


@api_view(['GET'])
@permission_classes([AllowAny])
def row_chart_data(request):
    """单行VOC图表数据（基于样品ID）"""
    try:
        result_id = request.GET.get('result_id')
        if not result_id:
            return Response.error(message='缺少result_id参数')

        try:
            current = SampleInfo.objects.get(id=result_id)
        except SampleInfo.DoesNotExist:
            return Response.error(message='数据不存在')

        project = current.project_name
        is_whole_vehicle = (current.part_name == '整车')

        if is_whole_vehicle:
            queryset = SampleInfo.objects.filter(project_name=project, part_name='整车')
        else:
            queryset = SampleInfo.objects.filter(project_name=project, part_name=current.part_name)

        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "丙酮", "TVOC"]
        fields = ["benzene", "toluene", "xylene", "ethylbenzene",
                  "styrene", "formaldehyde", "acetaldehyde", "acetone", "tvoc"]

        series_map = {}
        for s in queryset:
            if is_whole_vehicle:
                series_name = f"{s.status or '未知'}-{s.development_stage or '未知'}"
            else:
                series_name = f"{s.part_name or '未知'}-{s.development_stage or '未知'}"

            values = [float(getattr(s, f) or 0) for f in fields]
            if series_name not in series_map:
                series_map[series_name] = {
                    'name': series_name,
                    'data': values,
                    'type': 'bar'
                }

        return Response.success(data={
            'xAxis': x_axis,
            'series': list(series_map.values()),
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part',
            'project_name': project,
            'part_name': current.part_name
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['POST'])
@permission_classes([AllowAny])
def filtered_voc_chart_data(request):
    """基于筛选条件的VOC图表数据"""
    try:
        filters = request.data.get('filters', {}) or {}
        limit = int(request.data.get('limit', 10) or 10)

        queryset = SampleInfo.objects.all()
        queryset = _apply_filters(queryset, filters)
        queryset = queryset.order_by('-id')[:limit]

        x_axis = ["苯", "甲苯", "二甲苯", "乙苯", "苯乙烯", "甲醛", "乙醛", "丙酮", "TVOC"]
        fields = ["benzene", "toluene", "xylene", "ethylbenzene",
                  "styrene", "formaldehyde", "acetaldehyde", "acetone", "tvoc"]

        series = []
        for s in queryset:
            values = [float(getattr(s, f) or 0) for f in fields]
            series.append({
                'name': f"{s.project_name}-{s.sample_no}",
                'data': values,
                'type': 'bar',
                'part_name': s.part_name,
                'raw_data': {
                    'vehicle_model': s.project_name,
                    'sample_no': s.sample_no,
                    'status': s.status,
                    'stage': s.development_stage
                }
            })

        is_whole_vehicle = all((it.get('part_name') == '整车') for it in series) if series else False
        return Response.success(data={
            'xAxis': x_axis,
            'series': series,
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part'
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def odor_row_chart_data(request):
    """单行气味图表数据（基于样品ID）"""
    try:
        result_id = request.GET.get('result_id')
        if not result_id:
            return Response.error(message='缺少result_id参数')

        try:
            current = SampleInfo.objects.get(id=result_id)
        except SampleInfo.DoesNotExist:
            return Response.error(message='数据不存在')

        project = current.project_name
        is_whole_vehicle = (current.part_name == '整车')

        if is_whole_vehicle:
            queryset = SampleInfo.objects.filter(project_name=project, part_name='整车')
            x_axis = ["动态-前排", "动态-后排", "静态-前排", "静态-后排", "气味均值"]
            fields = ["odor_dynamic_front", "odor_dynamic_rear", "odor_static_front", "odor_static_rear", "odor_mean"]
        else:
            queryset = SampleInfo.objects.filter(project_name=project, part_name=current.part_name)
            x_axis = ["气味均值"]
            fields = ["odor_mean"]

        series_map = {}
        for s in queryset:
            if is_whole_vehicle:
                series_name = f"{project}-{s.development_stage or '未知'}"
            else:
                series_name = f"{current.part_name}-{s.development_stage or '未知'}"

            values = [float(getattr(s, f) or 0) for f in fields]
            if series_name not in series_map:
                series_map[series_name] = {
                    'name': series_name,
                    'data': values,
                    'type': 'bar'
                }

        return Response.success(data={
            'xAxis': x_axis,
            'series': list(series_map.values()),
            'scenario': 'whole_vehicle' if is_whole_vehicle else 'part'
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['POST'])
@permission_classes([AllowAny])
def filtered_odor_chart_data(request):
    """基于筛选条件的气味图表数据"""
    try:
        filters = request.data.get('filters', {}) or {}
        limit = int(request.data.get('limit', 10) or 10)

        queryset = SampleInfo.objects.all()
        queryset = _apply_filters(queryset, filters)
        queryset = queryset.order_by('-id')[:limit]

        # 气味图采用固定5项（与旧端一致）
        x_axis = ["动态-前排", "动态-后排", "静态-前排", "静态-后排", "气味均值"]
        fields = ["odor_dynamic_front", "odor_dynamic_rear", "odor_static_front", "odor_static_rear", "odor_mean"]

        series = []
        for s in queryset:
            values = [float(getattr(s, f) or 0) for f in fields]
            series.append({
                'name': f"{s.project_name}-{s.sample_no}",
                'data': values,
                'type': 'bar',
                'part_name': s.part_name,
                'raw_data': {
                    'vehicle_model': s.project_name,
                    'sample_no': s.sample_no,
                    'status': s.status,
                    'stage': s.development_stage
                }
            })

        return Response.success(data={
            'xAxis': x_axis,
            'series': series
        }, message='获取图表数据成功')
    except Exception as e:
        return Response.error(message=f'获取图表数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def substances_test_list(request):
    """获取全谱检测测试信息列表（以 SampleInfo 为测试记录）"""
    try:
        page = int(request.GET.get('page', 1) or 1)
        page_size = int(request.GET.get('page_size', 10) or 10)

        # 仅返回存在明细数据的样品
        sample_ids = SubstancesTestDetail.objects.values_list('sample_id', flat=True).distinct()
        queryset = SampleInfo.objects.filter(id__in=sample_ids).order_by('-id')

        # 可选过滤（兼容简单筛选）
        project_name = request.GET.get('project_name') or None
        part_name = request.GET.get('part_name') or None
        status_val = request.GET.get('status') or None
        development_stage = request.GET.get('development_stage') or None
        test_order_no = request.GET.get('test_order_no') or None
        sample_no = request.GET.get('sample_no') or None
        test_date_start = request.GET.get('test_date_start') or None
        test_date_end = request.GET.get('test_date_end') or None

        if project_name:
            queryset = queryset.filter(project_name=project_name)
        if part_name:
            queryset = queryset.filter(part_name__icontains=part_name)
        if status_val:
            queryset = queryset.filter(status=status_val)
        if development_stage:
            queryset = queryset.filter(development_stage=development_stage)
        if test_order_no:
            queryset = queryset.filter(test_order_no__icontains=test_order_no)
        if sample_no:
            queryset = queryset.filter(sample_no__icontains=sample_no)
        if test_date_start and test_date_end:
            queryset = queryset.filter(test_date__range=[test_date_start, test_date_end])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = SubstancesTestListItemSerializer(page_obj, many=True)
        return Response.success(data={
            'results': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'page_size': page_size
            }
        }, message='获取全谱检测数据成功')
    except Exception as e:
        return Response.error(message=f'获取全谱检测数据失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def substances_test_detail(request):
    """获取全谱检测明细数据（test_id 即 SampleInfo.id）"""
    try:
        test_id = request.GET.get('test_id')
        if not test_id:
            return Response.error(message='缺少test_id参数')

        try:
            sample = SampleInfo.objects.get(id=test_id)
        except SampleInfo.DoesNotExist:
            return Response.error(message='样品不存在')

        details = SubstancesTestDetail.objects.select_related('substance').filter(sample=sample).order_by('id')
        serializer = SubstancesTestDetailSerializer(details, many=True)
        return Response.success(data=serializer.data, message='获取全谱物质明细成功')
    except Exception as e:
        return Response.error(message=f'获取全谱物质明细失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def substance_detail(request):
    """获取物质详细信息（以 cas_no 查询）"""
    try:
        # 为兼容前端当前传参名，这里仍接收 substance_id，但其值为 cas_no
        cas_no = request.GET.get('substance_id') or request.GET.get('cas_no')
        if not cas_no:
            return Response.error(message='缺少物质标识（cas_no）')

        try:
            substance = Substance.objects.get(cas_no=cas_no)
        except Substance.DoesNotExist:
            return Response.error(message='物质不存在')

        serializer = SubstanceSerializer(substance)
        return Response.success(data=serializer.data, message='获取物质详情成功')
    except Exception as e:
        return Response.error(message=f'获取物质详情失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def contribution_top25(request):
    """
    车身VOC贡献度TOP25（按项目名称）
    入参：project_name（必填）
    规则：
      - 仅纳入该项目名下样品
      - 排除 part_name = '整车'
      - 必须存在 SubstancesTestDetail 关联记录
    计算：
      - 样品Oi = Σ qij（忽略None），样品Vi = Σ wih（忽略None）
      - 按 part_name 聚合同一零部件多阶段样品，取均值 avg_Oi/avg_Vi
      - GOi/GVi = (avg_Oi/Σavg_Oi)×100 / (avg_Vi/Σavg_Vi)×100
    返回：
      - insufficient: 当唯一零件数 < 35 时，返回提示与已有零件清单
      - 否则返回 goi_top25 / gvi_top25（各自独立排序）
    """
    try:
        project_name = (request.GET.get('project_name') or '').strip()
        if not project_name:
            return Response.bad_request(message='缺少必要参数：project_name')

        # 样品基础集：同项目、排除“整车”、零件名有效
        samples_qs = (
            SampleInfo.objects
            .filter(project_name=project_name)
            .exclude(part_name='整车')
            .exclude(part_name__isnull=True)
            .exclude(part_name__exact='')
        )

        # 仅保留存在明细的样品（通过关联记录过滤）
        sample_ids_with_details = SubstancesTestDetail.objects.filter(
            sample__project_name=project_name
        ).values_list('sample_id', flat=True).distinct()
        samples_qs = samples_qs.filter(id__in=sample_ids_with_details)

        # 唯一零件数量判断
        # unique_part_names = list(
        #     samples_qs.values_list('part_name', flat=True).distinct()
        # )
        # 使用 set() 确保去重
        all_part_names = samples_qs.values_list('part_name', flat=True)
        unique_part_names = list(set(all_part_names))
        unique_count = len(unique_part_names)
        if unique_count < 35:
            unique_part_names.sort()
            return Response.success(data={
                'project_name': project_name,
                'parts_count': unique_count,
                'insufficient': True,
                'part_names': unique_part_names
            }, message=f'零部件数需≥35，当前项目仅有{unique_count}个零部件，数据不足')

        # Step 1：每个样品的 Oi/Vi（一次聚合到样品层）
        sample_rows = list(
            samples_qs
            .annotate(oi=Sum('substance_details__qij'), vi=Sum('substance_details__wih'))
            .values('part_name', 'oi', 'vi')
        )

        # Step 2：按 part_name 聚合并取均值（None按0处理）
        from collections import defaultdict
        oi_by_part = defaultdict(list)
        vi_by_part = defaultdict(list)
        for row in sample_rows:
            part = row['part_name']
            oi = row['oi'] if row['oi'] is not None else 0
            vi = row['vi'] if row['vi'] is not None else 0
            oi_by_part[part].append(float(oi))
            vi_by_part[part].append(float(vi))

        def mean(lst):
            return (sum(lst) / len(lst)) if lst else 0.0

        part_avg_list = []
        for part in oi_by_part.keys() | vi_by_part.keys():
            avg_oi = mean(oi_by_part.get(part, []))
            avg_vi = mean(vi_by_part.get(part, []))
            part_avg_list.append({'part_name': part, 'avg_oi': avg_oi, 'avg_vi': avg_vi})

        # Step 3：全局归一化计算贡献度
        zoi = sum(p['avg_oi'] for p in part_avg_list)
        zvi = sum(p['avg_vi'] for p in part_avg_list)

        goi_items = []
        gvi_items = []
        for p in part_avg_list:
            goi = (p['avg_oi'] / zoi * 100.0) if zoi > 0 else 0.0
            gvi = (p['avg_vi'] / zvi * 100.0) if zvi > 0 else 0.0
            goi_items.append({'part_name': p['part_name'], 'goi': goi})
            gvi_items.append({'part_name': p['part_name'], 'gvi': gvi})

        goi_items.sort(key=lambda x: x['goi'], reverse=True)
        gvi_items.sort(key=lambda x: x['gvi'], reverse=True)

        goi_top25 = [
            {'rank': idx + 1, 'part_name': item['part_name'], 'goi': item['goi']}
            for idx, item in enumerate(goi_items[:25])
        ]
        gvi_top25 = [
            {'rank': idx + 1, 'part_name': item['part_name'], 'gvi': item['gvi']}
            for idx, item in enumerate(gvi_items[:25])
        ]

        return Response.success(data={
            'project_name': project_name,
            'parts_count': unique_count,
            'insufficient': False,
            'goi_top25': goi_top25,
            'gvi_top25': gvi_top25,
        }, message='获取贡献度TOP25成功')
    except Exception as e:
        return Response.error(message=f'获取贡献度TOP25失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def vehicle_sample_options(request):
    """
    整车样品下拉选项：返回存在全谱明细的整车样品组合
    结构：[{ key, label, project_name, status, development_stage, test_order_no, sample_no }]
    """
    try:
        sample_ids = SubstancesTestDetail.objects.values_list('sample_id', flat=True).distinct()
        qs = (
            SampleInfo.objects
            .filter(id__in=sample_ids, part_name='整车')
            .exclude(project_name__isnull=True)
            .exclude(project_name__exact='')
            .exclude(test_order_no__isnull=True)
            .exclude(test_order_no__exact='')
            .exclude(sample_no__isnull=True)
            .exclude(sample_no__exact='')
            .order_by('-id')
        )

        seen = set()
        options = []
        for s in qs:
            # 使用项目 + 状态 + 开发阶段 + 委托单号 + 样品编号 作为唯一组合键
            combo = (s.project_name, s.status or '', s.development_stage or '', s.test_order_no, s.sample_no)
            if combo in seen:
                continue
            seen.add(combo)
            label = f"{s.project_name}-{s.status or ''}-{s.test_order_no}-{s.sample_no}"
            key = f"{s.project_name}||{s.status or ''}||{s.development_stage or ''}||{s.test_order_no}||{s.sample_no}"
            options.append({
                'key': key,
                'label': label,
                'project_name': s.project_name,
                'status': s.status,
                'development_stage': s.development_stage,
                'test_order_no': s.test_order_no,
                'sample_no': s.sample_no,
            })

        return Response.success(data=options, message='获取整车样品选项成功')
    except Exception as e:
        return Response.error(message=f'获取整车样品选项失败: {str(e)}')


def _fmt3(v):
    if v is None:
        return None
    try:
        return f"{float(v):.3f}"
    except Exception:
        return None


@api_view(['GET'])
@permission_classes([AllowAny])
def traceability_substances(request):
    """
    获取整车样品下的物质列表（下拉数据源）
    入参：project_name, test_order_no, sample_no, status(可选), development_stage(可选)
    返回：[{ cas_no, substance_name_cn, substance_name_en, concentration }]
    """
    try:
        project_name = (request.GET.get('project_name') or '').strip()
        test_order_no = (request.GET.get('test_order_no') or '').strip()
        sample_no = (request.GET.get('sample_no') or '').strip()
        status = (request.GET.get('status') or '').strip()
        development_stage = (request.GET.get('development_stage') or '').strip()
        if not (project_name and test_order_no and sample_no):
            return Response.bad_request(message='缺少必要参数：project_name/test_order_no/sample_no')

        sample_qs = SampleInfo.objects.filter(
            project_name=project_name,
            test_order_no=test_order_no,
            sample_no=sample_no,
            part_name='整车'
        )
        if status:
            sample_qs = sample_qs.filter(status=status)
        if development_stage:
            sample_qs = sample_qs.filter(development_stage=development_stage)
        sample = sample_qs.order_by('-test_date', '-id').first()
        if not sample:
            return Response.not_found(message='整车样品不存在')

        details = (
            SubstancesTestDetail.objects
            .select_related('substance')
            .filter(sample=sample)
            .order_by('-concentration', 'id')
        )
        data = []
        for d in details:
            sub = d.substance
            data.append({
                'cas_no': getattr(sub, 'cas_no', None),
                'substance_name_cn': getattr(sub, 'substance_name_cn', None),
                'substance_name_en': getattr(sub, 'substance_name_en', None),
                'concentration': _fmt3(d.concentration),
            })

        return Response.success(data=data, message='获取物质列表成功')
    except Exception as e:
        return Response.error(message=f'获取物质列表失败: {str(e)}')


@api_view(['POST'])
@permission_classes([AllowAny])
def traceability_ranking(request):
    """
    所选物质的整车检测详情及 Top5 零件排名（Qij/Wih）
    入参JSON：{ project_name, test_order_no, sample_no, status(可选), development_stage(可选), selected_substances: [cas_no, ...] }
    返回：[{ cas_no, substance_id, substance_name_cn, substance_name_en, substance_info, retention_time, match_degree, concentration_ratio, concentration, odor_top5, organic_top5 }]
    说明：所有数值统一三位小数字符串；odor_top5=按Qij排序，organic_top5=按Wih排序
    """
    try:
        body = request.data or {}
        project_name = (body.get('project_name') or '').strip()
        test_order_no = (body.get('test_order_no') or '').strip()
        sample_no = (body.get('sample_no') or '').strip()
        status = (body.get('status') or '').strip()
        development_stage = (body.get('development_stage') or '').strip()
        selected = body.get('selected_substances') or []

        if not (project_name and test_order_no and sample_no):
            return Response.bad_request(message='缺少必要参数：project_name/test_order_no/sample_no')
        if not isinstance(selected, (list, tuple)) or not selected:
            return Response.bad_request(message='缺少所选物质：selected_substances')

        vehicle_sample_qs = SampleInfo.objects.filter(
            project_name=project_name,
            test_order_no=test_order_no,
            sample_no=sample_no,
            part_name='整车'
        )
        if status:
            vehicle_sample_qs = vehicle_sample_qs.filter(status=status)
        if development_stage:
            vehicle_sample_qs = vehicle_sample_qs.filter(development_stage=development_stage)
        vehicle_sample = vehicle_sample_qs.order_by('-test_date', '-id').first()
        if not vehicle_sample:
            return Response.not_found(message='整车样品不存在')

        results = []

        for cas_no in selected:
            # 整车样品中该物质的检测详情
            in_vehicle_detail = (
                SubstancesTestDetail.objects.select_related('substance')
                .filter(sample=vehicle_sample, substance__cas_no=cas_no)
                .order_by('-id')
                .first()
            )

            if not in_vehicle_detail:
                try:
                    sub = Substance.objects.get(cas_no=cas_no)
                except Substance.DoesNotExist:
                    sub = None
                results.append({
                    'cas_no': cas_no,
                    'substance_id': cas_no,
                    'substance_name_cn': getattr(sub, 'substance_name_cn', None),
                    'substance_name_en': getattr(sub, 'substance_name_en', None),
                    'substance_info': SubstanceSerializer(sub).data if sub else None,
                    'retention_time': None,
                    'match_degree': None,
                    'concentration_ratio': None,
                    'concentration': None,
                    'odor_top5': [],
                    'organic_top5': [],
                })
                continue

            sub = in_vehicle_detail.substance
            base_qs = SubstancesTestDetail.objects.filter(
                sample__project_name=project_name,
                substance__cas_no=cas_no
            ).exclude(sample__part_name='整车')

            # Top5 by Qij
            qij_agg = (
                base_qs.values('sample__part_name')
                .annotate(max_qij=Max('qij'))
                .exclude(sample__part_name__isnull=True)
                .exclude(sample__part_name__exact='')
                .exclude(max_qij__isnull=True)
                .order_by('-max_qij')[:5]
            )
            odor_top5 = []
            for row in qij_agg:
                part = row['sample__part_name']
                max_qij = row['max_qij']
                record = base_qs.filter(sample__part_name=part, qij=max_qij).order_by('-id').first()
                if record:
                    odor_top5.append({
                        'part_name': part,
                        'qij': _fmt3(record.qij),
                        'wih': _fmt3(record.wih),
                        'concentration': _fmt3(record.concentration),
                    })

            # Top5 by Wih
            wih_agg = (
                base_qs.values('sample__part_name')
                .annotate(max_wih=Max('wih'))
                .exclude(sample__part_name__isnull=True)
                .exclude(sample__part_name__exact='')
                .exclude(max_wih__isnull=True)
                .order_by('-max_wih')[:5]
            )
            organic_top5 = []
            for row in wih_agg:
                part = row['sample__part_name']
                max_wih = row['max_wih']
                record = base_qs.filter(sample__part_name=part, wih=max_wih).order_by('-id').first()
                if record:
                    organic_top5.append({
                        'part_name': part,
                        'qij': _fmt3(record.qij),
                        'wih': _fmt3(record.wih),
                        'concentration': _fmt3(record.concentration),
                    })

            results.append({
                'cas_no': cas_no,
                'substance_id': cas_no,
                'substance_name_cn': getattr(sub, 'substance_name_cn', None),
                'substance_name_en': getattr(sub, 'substance_name_en', None),
                'substance_info': SubstanceSerializer(sub).data if sub else None,
                'retention_time': _fmt3(in_vehicle_detail.retention_time),
                'match_degree': in_vehicle_detail.match_degree,
                'concentration_ratio': _fmt3(in_vehicle_detail.concentration_ratio),
                'concentration': _fmt3(in_vehicle_detail.concentration),
                'odor_top5': odor_top5,
                'organic_top5': organic_top5,
            })

        return Response.success(data={'substances': results}, message='获取溯源排名成功')
    except Exception as e:
        return Response.error(message=f'获取溯源排名失败: {str(e)}')
